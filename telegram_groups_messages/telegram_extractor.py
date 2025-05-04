import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError
from datetime import datetime, timezone
import asyncio
import logging
import os
from typing import List, Any
from dotenv import load_dotenv
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageMediaWebPage,
    DocumentAttributeFilename,
    ReactionEmoji
)
import emoji

from telegram_groups_messages.messages_database import MessageData, MessageDatabase
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramExtractor:
    """
    A class to extract messages from a Telegram group and store them in a SQLite database.

    Attributes:
        api_id (str): The API ID for the Telegram client.
        api_hash (str): The API hash for the Telegram client.
        phone (str): The phone number associated with the Telegram account.
        two_fa (str): The two-factor authentication password for the Telegram account.
        session_name (str): The session name for the Telegram client.
        batch_size (int): The number of messages to fetch in each batch.
        rate_limit_delay (float): The delay in seconds to wait between requests to avoid rate limiting.
        db (MessageDatabase): The database object to store messages.
        table (str): The name of the table to store messages in.
    """
    def __init__(self, table_name: str, session_name: str = 'war_analysis_session'):
        """
        Initializes the TelegramExtractor with the specified table name and session name.

        Args:
            table_name (str): The name of the table to store messages in.
            session_name (str, optional): The session name for the Telegram client. Defaults to 'war_analysis_session'.
        """
        # Load environment variables
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.phone = os.getenv('PHONE_NUMBER')  # Add phone
        self.two_fa = os.getenv('PASSWORD_2FA')  # Add 2FA password

        # Set default values
        self.session_name = session_name
        self.batch_size = 100
        self.rate_limit_delay = 1.5

        # Initialize the database and table
        self.db = MessageDatabase('data/telegram_data.db')
        self.table = table_name
        self.db.create_table(self.table)  # This call will create the table if it doesn't exist already

    @property
    async def connect_client(self) -> TelegramClient:
        """
        Connects to the Telegram client using the provided session name, API ID, and API hash.

        Starts the client with the phone number and two-factor authentication password.
        Checks if the user is authorized and logs the connection status.

        Returns:
            TelegramClient: The connected Telegram client.

        Raises:
            Exception: If authentication with Telegram fails.
        """
        client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await client.start(phone=self.phone, password=self.two_fa)

        if not await client.is_user_authorized():
            logger.error("Failed to authenticate with Telegram")
            logger.exception("Authentication failed")
            raise Exception("Authentication failed")

        logger.info("Successfully connected to Telegram")
        return client

    async def _handle_rate_limit(self, e: FloodWaitError):
        """
        Handles the rate limit error by logging a warning and waiting for the specified time.

        Args:
            e (FloodWaitError): The exception raised due to rate limiting, containing the wait time in seconds.
        """
        wait_time = e.seconds
        logger.warning(f"Rate limited. Waiting {wait_time} seconds")
        await asyncio.sleep(wait_time)

    def _process_message(self, message, group_name) -> MessageData:
        """
        Processes a Telegram message and converts it into a MessageData object, including:
          - Local timezone handling (Asia/Jerusalem)
          - Extended forward info (channel ID, post author, date, etc.)
          - Detailed media type/attributes (document, photo, poll, webpage, fallback)
          - Emoji count using the emoji library
          - Basic metrics (word count, day_of_week, etc.)

        Args:
            message: The Telegram message object (from Telethon).
            group_name (str): The name of the Telegram group/channel.

        Returns:
            MessageData: An object containing the processed message data.
        """

        # ----------------------------------------------------------------------------
        # 1) Timezone Handling
        # ----------------------------------------------------------------------------
        # Telethon messages are often UTC or naive, so ensure we treat them as UTC:
        utc_date = message.date.replace(tzinfo=timezone.utc)
        # Convert to local time (Asia/Jerusalem):
        local_tz = pytz.timezone("Asia/Jerusalem")
        local_date = utc_date.astimezone(local_tz)

        # ----------------------------------------------------------------------------
        # 2) Extended Forward Info
        # ----------------------------------------------------------------------------
        forward_info = None
        if message.fwd_from:
            forward_info = {
                "forwarded_from_id": str(message.fwd_from.from_id) if message.fwd_from.from_id else None,
                "forwarded_channel_id": getattr(message.fwd_from, "channel_id", None),
                "forwarded_channel_post": getattr(message.fwd_from, "channel_post", None),
                "forwarded_post_author": getattr(message.fwd_from, "post_author", None),
                "forwarded_date": (
                    message.fwd_from.date.strftime("%Y-%m-%d %H:%M:%S")
                    if message.fwd_from.date else None
                ),
            }

        # also capture the "forwards" count:
        forward_count = getattr(message, 'forwards', None)

        # ----------------------------------------------------------------------------
        # 3) Media Handling
        # ----------------------------------------------------------------------------
        media_type, media_attributes = self._process_message_with_media_types(message)

        # ----------------------------------------------------------------------------
        # 4) Reactions (if present)
        # ----------------------------------------------------------------------------
        reactions = None
        if hasattr(message, 'reactions') and message.reactions:
            reactions = []
            for r in message.reactions.results:
                if isinstance(r.reaction, ReactionEmoji):
                    reactions.append({
                        "emoji": r.reaction.emoticon,
                        "count": r.count
                    })
                else:
                    # Fallback for custom or unknown reaction type
                    reactions.append({
                        "emoji": str(r.reaction),
                        "count": r.count
                    })

        # ----------------------------------------------------------------------------
        # 5) Construct and Return the MessageData object
        # ----------------------------------------------------------------------------

        # Word count and emoji count:
        text_content = message.message or ""

        return MessageData(
            group_name=group_name,
            message_id=message.id,

            # Local time with DST included:
            utc_date=utc_date.strftime("%Y-%m-%d %H:%M:%S%z"),  # e.g. "2025-03-31 10:45:00+0000"
            local_date=local_date.strftime("%Y-%m-%d %H:%M:%S%z"),  # e.g. "2025-03-31 13:45:00+0300"

            text=text_content,
            sender_id=message.sender_id,
            reply_to_msg_id=message.reply_to_msg_id,

            # Extended forward data:
            forwarded_from=forward_info,
            forward_count=forward_count,

            # Media details:
            media_type=media_type,
            media_attributes=media_attributes,

            # Entities:
            entities=[
                {
                    "type": str(e.type) if hasattr(e, "type") else e.__class__.__name__,
                    "offset": e.offset,
                    "length": e.length
                }
                for e in message.entities
            ] if message.entities else None,

            # Views and reactions:
            views=getattr(message, 'views', None),
            reactions=reactions,

            # Time-based fields (local):
            hour=local_date.hour,
            day_of_week=local_date.weekday(),
            month=local_date.month,
            week_of_year=int(local_date.strftime("%U")),

            # Basic text metrics:
            word_count=len(text_content.split()) if text_content else 0,
            emoji_count=len(emoji.emoji_list(text_content)) if text_content else 0
        )

    def _process_message_with_media_types(self, message):
        """
        Processes a Telegram message to handle several media types: Document, Photo, Poll, and WebPage.

        Args:
            message: The Telegram message object to process.

        Returns:
            tuple: A tuple containing:
                - media_type (str or None): The type of media (e.g., 'document', 'photo', 'poll', 'webpage') or None if no media.
                - media_attributes (dict): A dictionary of media attributes specific to the media type.
        """

        media_type = None
        media_attributes = {}

        if not message.media:
            return media_type, media_attributes

        # Identify media type
        if isinstance(message.media, MessageMediaDocument) and message.document:
            media_type = "document"

            # Extract common fields
            media_attributes["document_id"] = message.document.id
            media_attributes["mime_type"] = getattr(message.document, "mime_type", None)
            media_attributes["size"] = getattr(message.document, "size", None)

            # Attempt to find a filename attribute (if any)
            filename_attr = next(
                (
                    attr
                    for attr in message.document.attributes
                    if isinstance(attr, DocumentAttributeFilename)
                ),
                None
            )
            if filename_attr:
                media_attributes["filename"] = filename_attr.file_name

        elif isinstance(message.media, MessageMediaPhoto) and message.photo:
            media_type = "photo"
            media_attributes["photo_id"] = message.photo.id
            media_attributes["width"] = getattr(message.photo, "w", None)
            media_attributes["height"] = getattr(message.photo, "h", None)

        if isinstance(message.media, MessageMediaPoll) and message.media.poll:
            media_type = "poll"
            poll_obj = message.media.poll

            # poll_obj.question might be TextWithEntities or a regular string.
            question_text = poll_obj.question
            if hasattr(question_text, "text"):
                # If it's TextWithEntities, grab just the text
                question_text = question_text.text

            media_attributes["question"] = question_text
            media_attributes["multiple_choice"] = poll_obj.multiple_choice
            media_attributes["quiz"] = poll_obj.quiz

            # Each answer might also contain a text field that’s non-serializable.
            answers_list = []
            for answer in poll_obj.answers:
                ans_text = answer.text
                if hasattr(ans_text, "text"):
                    ans_text = ans_text.text

                answers_list.append({
                    "text": ans_text,
                    "option": answer.option.hex()  # raw bytes -> hex
                })
            media_attributes["answers"] = answers_list

        elif isinstance(message.media, MessageMediaWebPage) and message.media.webpage:
            media_type = "webpage"
            web_page = message.media.webpage

            # If the webpage is actually WebPageEmpty or another minimal type, skip the rest
            if type(web_page).__name__ == "WebPageEmpty":
                # Possibly store minimal or fallback data
                media_attributes["raw_object"] = str(web_page)
                return media_type, media_attributes

            # Otherwise, proceed (this implies we have a "real" WebPage)
            media_attributes["url"] = getattr(web_page, "url", None)
            media_attributes["site_name"] = getattr(web_page, "site_name", None)
            media_attributes["title"] = getattr(web_page, "title", None)
            media_attributes["description"] = getattr(web_page, "description", None)
            media_attributes["author"] = getattr(web_page, "author", None)
            media_attributes["embed_url"] = getattr(web_page, "embed_url", None)
            media_attributes["embed_type"] = getattr(web_page, "embed_type", None)

            # If the webpage includes a photo, document, etc., check for existence
            if getattr(web_page, "photo", None):
                media_attributes["photo_id"] = web_page.photo.id
            if getattr(web_page, "document", None):
                media_attributes["document_id"] = web_page.document.id

        else:
            # Fallback case: unknown or unhandled media type
            media_type = type(message.media).__name__
            media_attributes["raw_object"] = str(message.media)

        return media_type, media_attributes

    async def extract_messages(self, group: str, start_date: datetime, end_date: datetime) -> list[MessageData] | list[Any]:
        """
        Extracts messages from a specified Telegram group within a date range and stores them in a SQLite database.

        Args:
            group (str): The name of the Telegram group to extract messages from.
            start_date (datetime): The start date to extract messages from.
            end_date (datetime): The end date to extract messages until.

        Returns:
            list[MessageData] | list[Any]: A list of MessageData objects containing the extracted messages,
                or an empty list if an error occurs.
        """
        logger.info(f"\nStarting messages extraction for group '{group}' from {start_date} to {end_date}")

        # # Make input dates timezone-aware if they aren't already
        # if start_date.tzinfo is None:
        #     start_date = start_date.replace(tzinfo=timezone.utc)
        # if end_date.tzinfo is None:
        #     end_date = end_date.replace(tzinfo=timezone.utc)

        # --------------------------------------------------------------------------
        # 1) Convert local times to UTC if needed
        # --------------------------------------------------------------------------
        # If the user gave naive datetimes or a different tz, unify to UTC:
        if start_date.tzinfo is None:
            # If no tz is set, assume user meant local time – but we must choose how to handle. Typically, you'd do:
            logger.warning("start_date is naive; assuming Asia/Jerusalem.")
            start_date = pytz.timezone("Asia/Jerusalem").localize(start_date)
        if end_date.tzinfo is None:
            logger.warning("end_date is naive; assuming Asia/Jerusalem.")
            end_date = pytz.timezone("Asia/Jerusalem").localize(end_date)
        # Convert them to UTC
        start_date_utc = start_date.astimezone(pytz.utc)
        end_date_utc = end_date.astimezone(pytz.utc)

        # --------------------------------------------------------------------------
        # 2) Connect to Telegram
        # --------------------------------------------------------------------------
        # async with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
        client = await self.connect_client
        async with client:
            try:
                entity = await client.get_entity(group)
                offset_id = 0
                all_messages: List[MessageData] = []

                while True:
                    try:
                        logger.debug(f"Requesting batch of up to {self.batch_size} messages with offset_id={offset_id}")
                        history = await client(GetHistoryRequest(
                            peer=entity,
                            offset_id=offset_id,
                            offset_date=None,
                            add_offset=0,
                            limit=self.batch_size,
                            max_id=0,
                            min_id=0,
                            hash=0
                        ))

                        if not history.messages:
                            logger.info("No more messages returned by Telegram.")
                            break

                        logger.debug(f"Fetched {len(history.messages)} messages from Telegram API.")

                        # ------------------------------------------------------------------
                        # 3) Filter the Telegram messages by UTC
                        # ------------------------------------------------------------------
                        # Telethon message dates are naive or effectively in UTC.
                        # We attach tzinfo=UTC and compare with start_date_utc/end_date_utc.
                        valid_msgs = []
                        for msg in history.messages:
                            msg_utc_date = msg.date.replace(tzinfo=pytz.utc)  # ensure it's tz-aware
                            if start_date_utc <= msg_utc_date <= end_date_utc:
                                valid_msgs.append(msg)

                        # Process and insert them
                        if valid_msgs:
                            processed = [self._process_message(m, group) for m in valid_msgs]
                            all_messages.extend(processed)

                            self.db.insert_messages(processed, table_name=self.table)
                            logger.info(f"Inserted {len(processed)} messages of group {group}; total {len(all_messages)} in {self.table}")

                        # If the last message's date is older than start_date_utc, we can stop because all next messages will be older too.
                        last_msg_utc_date = history.messages[-1].date.replace(tzinfo=pytz.utc)
                        if last_msg_utc_date < start_date_utc:
                            logger.info("Reached messages older than the start_date, stopping extraction.")
                            break

                        offset_id = history.messages[-1].id
                        await asyncio.sleep(self.rate_limit_delay)

                    except FloodWaitError as e:
                        await self._handle_rate_limit(e)
                        continue

                logger.info(f"*** Finished processing {len(all_messages)} total messages from group '{group}'")
                return all_messages

            except Exception as e:
                logger.error(f"Error extracting messages: {e}")
                logger.exception("Error extracting messages")
                return []
