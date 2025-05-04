import sqlite3
from dataclasses import dataclass
import json
from typing import List, Dict, Optional


######################################################################################################

@dataclass
class MessageData:
    """
    A data class to represent a Telegram message.

    Attributes:
        group_name (Optional[str]): Name of the Telegram group/channel from which the message was extracted.
        message_id (int): Unique identifier of the message.
        utc_date (str): UTC timestamp of when the message was sent, in ISO-like format (e.g., "2025-03-31 10:45:00+0000").
        local_date (str): Local timestamp (Asia/Jerusalem) for the message, including DST offset (e.g., "2025-03-31 13:45:00+0300").
        text (str): The content/body of the message.
        sender_id (Optional[int]): Unique identifier of the sender (if available).
        reply_to_msg_id (Optional[int]): ID of the message this is replying to (if any).
        forwarded_from (Optional[Dict]): Detailed info about original sender/channel if the message is forwarded.
        forward_count (Optional[int]): How many times this message has been forwarded (if available).
        media_type (Optional[str]): Type of media attached (e.g., "document", "photo", "poll", "webpage").
        media_attributes (Dict): Structured metadata about the attached media (IDs, sizes, filenames, etc.).
        entities (Optional[List[Dict]]): A list of message entities (e.g., URLs, mentions) with offsets and lengths.
        views (Optional[int]): Number of views the message has received (channels only).
        reactions (Optional[List[Dict]]): A list of reaction objects (emoji + count).
        hour (int): Local hour of the day when the message was sent (0-23).
        day_of_week (int): Local day of the week (Monday=0, Sunday=6).
        month (int): Local month (1-12).
        week_of_year (int): Local week number of the year (0-53).
        word_count (int): Number of words in the message text.
        emoji_count (int): Number of emojis in the message text.
    """
    group_name: str
    message_id: int

    utc_date: str
    local_date: str

    text: str
    sender_id: Optional[int]
    reply_to_msg_id: Optional[int]

    forwarded_from: Optional[Dict]
    forward_count: Optional[int]

    media_type: Optional[str]
    media_attributes: Optional[Dict]

    entities: Optional[List[Dict]]
    views: Optional[int]
    reactions: Optional[List[Dict]]

    hour: Optional[int]
    day_of_week: Optional[int]
    month: Optional[int]
    week_of_year: Optional[int]

    word_count: Optional[int]
    emoji_count: Optional[int]


######################################################################################################

class MessageDatabase:
    def __init__(self, db_name: str):
        """
        Initializes the MessageDatabase instance.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        # self.create_table()

    def create_table(self, table_name):
        """
        Creates a new table in the SQLite database if it doesn't already exist.

        Args:
            table_name (str): The name of the table to create.

        The primary key is a composite key consisting of group_name and message_id.
        """

        # Create a new table if it doesn't exist
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                group_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,

                utc_date TEXT,
                local_date TEXT,

                text TEXT,
                sender_id INTEGER,
                reply_to_msg_id INTEGER,
                
                -- forwarded_from is a dictionary, also stored as JSON
                forwarded_from TEXT,
                -- New forward_count column
                forward_count INTEGER,

                media_type TEXT,
                -- media_attributes will usually be stored as JSON
                media_attributes TEXT,

                entities TEXT,
                views INTEGER,
                reactions TEXT,

                hour INTEGER,
                day_of_week INTEGER,
                month INTEGER,
                week_of_year INTEGER,
                word_count INTEGER,
                emoji_count INTEGER,

                PRIMARY KEY (group_name, message_id)
            )
        """)
        self.conn.commit()

        self.cur.execute(f"CREATE INDEX IF NOT EXISTS idx_messages_local_date ON {table_name} (local_date)")
        self.conn.commit()

    def insert_messages(self, messages: List[MessageData], batch_size: int = 1000, table_name: str = "messages"):
        """
        Inserts a list of messages into the specified SQLite table in batches.

        Args:
            messages (List[MessageData]): A list of MessageData objects to insert into the database.
            batch_size (int, optional): The number of messages to insert in each batch. Defaults to 1000.
            table_name (str, optional): The name of the table to insert the messages into. Defaults to "messages".
        """
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            self.cur.executemany(
                f"""INSERT INTO {table_name} (
                    group_name,
                    message_id,
                    utc_date,
                    local_date,
                    text,
                    sender_id,
                    reply_to_msg_id,
                    forward_count,
                    media_type,
                    media_attributes,
                    forwarded_from,
                    entities,
                    views,
                    reactions,
                    hour,
                    day_of_week,
                    month,
                    week_of_year,
                    word_count,
                    emoji_count
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )""",
                [
                    (
                        m.group_name,
                        m.message_id,

                        m.utc_date,
                        m.local_date,

                        m.text,
                        m.sender_id,
                        m.reply_to_msg_id,

                        m.forward_count,
                        m.media_type,
                        json.dumps(m.media_attributes) if m.media_attributes else None,

                        json.dumps(m.forwarded_from) if m.forwarded_from else None,
                        json.dumps(m.entities) if m.entities else None,

                        m.views,
                        json.dumps(m.reactions) if m.reactions else None,

                        m.hour,
                        m.day_of_week,
                        m.month,
                        m.week_of_year,
                        m.word_count,
                        m.emoji_count
                    )
                    for m in batch
                ]
            )
            self.conn.commit()

    def add_column_if_not_exists(self, table_name: str, column_name: str, column_definition: str):
        """
        Adds a new column to a table if it doesn't already exist.

        Args:
            table_name (str): The name of the table to modify.
            column_name (str): The name of the column to add.
            column_definition (str): The column type and any constraints (e.g., 'TEXT', 'INTEGER', etc.).
        """
        self.cur.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in self.cur.fetchall()]  # row[1] contains the column name.

        if column_name not in columns:
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            self.cur.execute(alter_query)
            self.conn.commit()
            print(f"Added column '{column_name}' to table '{table_name}'.")
        else:
            print(f"Column '{column_name}' already exists in table '{table_name}'.")

    def create_index_if_not_exists(self, index_name: str, table_name: str, column_name: str):
        """
        Creates an index on a table column if it doesn't already exist.

        Args:
            index_name (str): The name of the index.
            table_name (str): The name of the table.
            column_name (str): The column on which to create the index.
        """
        index_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
        self.cur.execute(index_query)
        self.conn.commit()
        print(f"Index '{index_name}' created on column '{column_name}' of table '{table_name}'.")

    # def create_new_table(self, new_table_name: str):
    #     """
    #     Create a new table with the specified name.
    #
    #     Args:
    #         new_table_name (str): The name of the new table to create.
    #     """
    #     self.cur.execute(f"""
    #         CREATE TABLE IF NOT EXISTS {new_table_name} (
    #             group_name TEXT NOT NULL,
    #             message_id INTEGER NOT NULL,
    #             date TEXT,
    #             text TEXT,
    #             sender_id INTEGER,
    #             reply_to_msg_id INTEGER,
    #             media_type TEXT,
    #             forwarded_from TEXT,
    #             entities TEXT,
    #             views INTEGER,
    #             reactions TEXT,
    #             hour INTEGER,
    #             day_of_week INTEGER,
    #             week_of_year INTEGER,
    #             word_count INTEGER,
    #             emoji_count INTEGER,
    #             PRIMARY KEY (group_name, message_id)
    #         )
    #     """)
    #     self.conn.commit()
    #
    #     # Create indexes as needed
    #     self.cur.execute(f"CREATE INDEX IF NOT EXISTS idx_messages_date ON {new_table_name} (date)")
    #     # For large data sets, you might also add an index on sender_id, etc.
    #
    #     self.conn.commit()


######################################################################################################


def migrate_old_messages_to_new_pk(db_path: str):
    """
    Migrates old messages to a new table with a composite primary key.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1) Rename the existing table
    #    (Assumes an old table named 'messages' with PK on 'message_id')
    cur.execute("ALTER TABLE messages RENAME TO old_messages;")
    conn.commit()

    # 2) Create the new table with the new primary key definition
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            group_name TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            date TEXT,
            text TEXT,
            sender_id INTEGER,
            reply_to_msg_id INTEGER,
            media_type TEXT,
            forwarded_from TEXT,
            entities TEXT,
            views INTEGER,
            reactions TEXT,
            hour INTEGER,
            day_of_week INTEGER,
            week_of_year INTEGER,
            word_count INTEGER,
            emoji_count INTEGER,
            PRIMARY KEY (group_name, message_id)
        )
    """)
    conn.commit()

    # 3) Copy data from the old table to the new one.
    #    If the old table did not contain a group_name or had NULL, you might need to handle that.
    #    Example below uses COALESCE to map NULL group_name to '' (empty string).
    #
    #    Also, if your old data can have collisions on (group_name, message_id), use 'INSERT OR IGNORE'
    #    or 'INSERT OR REPLACE' to handle duplicates gracefully.
    #
    #    The SELECT must list columns in the same order as the INSERT.
    #
    cur.execute("""
        INSERT INTO messages (
            group_name,
            message_id,
            date,
            text,
            sender_id,
            reply_to_msg_id,
            media_type,
            forwarded_from,
            entities,
            views,
            reactions,
            hour,
            day_of_week,
            week_of_year,
            word_count,
            emoji_count
        )
        SELECT
            COALESCE(group_name, '') AS group_name,
            message_id,
            date,
            text,
            sender_id,
            reply_to_msg_id,
            media_type,
            forwarded_from,
            entities,
            views,
            reactions,
            hour,
            day_of_week,
            week_of_year,
            word_count,
            emoji_count
        FROM old_messages
    """)
    conn.commit()

    # 4) Drop the old table now that the data is migrated
    cur.execute("DROP TABLE old_messages;")
    conn.commit()

    # 5) Optionally create any additional indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_date ON messages (date)")
    conn.commit()

    cur.close()
    conn.close()



if __name__ == "__main__":
    # Define database settings and new column details
    db_path = "../data/telegram/telegram_data.db"
    table_name = "messages"
    column_name = "group_name"
    column_definition = "TEXT"  # Use TEXT to store the group name

    # # Create an instance of your Database class
    # db = MessageDatabase(db_path)

    # # Step 1: Add the new column 'group_name' if it doesn't exist.
    # db.add_column_if_not_exists(table_name, column_name, column_definition)
    #
    # # Step 2: Update existing rows to set group_name to "abualiexpress" where the column is NULL.
    # with sqlite3.connect(db_path) as conn:
    #     cur = conn.cursor()
    #     update_query = f"UPDATE {table_name} SET {column_name} = ? WHERE {column_name} IS NULL"
    #     cur.execute(update_query, ("abualiexpress",))
    #     conn.commit()
    #     print("Updated existing rows with group_name = 'abualiexpress'")

    migrate_old_messages_to_new_pk(db_path)