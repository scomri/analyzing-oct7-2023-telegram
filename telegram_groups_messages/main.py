import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from tqdm import tqdm
from wakepy.modes import keep

from telegram_groups_messages.consts import TELEGRAM_GROUPS_MAP
from telegram_groups_messages.telegram_extractor import TelegramExtractor

if __name__ == "__main__":

    israel_tz = ZoneInfo("Asia/Jerusalem")
    start_local = datetime(2023, 10, 6, 0, 0, 0, tzinfo=israel_tz)
    end_local = datetime(2025, 2, 21, 23, 59, 59, tzinfo=israel_tz)

    async def extract_all_groups_messages(groups_names, start, end):
        """
        Extracts messages for all specified Telegram groups within a given time range.

        Args:
            groups_names (iterable): An iterable of group names to extract messages from.
            start (datetime): The start datetime for the extraction period.
            end (datetime): The end datetime for the extraction period.
        """
        extractor = TelegramExtractor(table_name='groups_messages')
        for group in tqdm(groups_names, desc="Extracting messages from groups", unit="group", total=len(groups_names)):
            await extractor.extract_messages(group, start, end)

    # Run the extraction with local start/end
    with keep.running():
        asyncio.run(
            extract_all_groups_messages(
                groups_names=TELEGRAM_GROUPS_MAP.keys(),
                start=start_local,
                end=end_local
            )
        )