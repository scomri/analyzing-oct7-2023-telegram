# Telegram Messages Extraction Module

This sub-README describes the `telegram_extractor` code module for fetching messages from a set of Telegram groups and storing them in a local SQLite database.

---

## Directory Structure

```plaintext
telegram_groups_messages/
    ├── main.py 
    ├── messages_database.py
    ├── telegram_extractor.py
    ├── <telegran_session>.session
    ├── consts.py
    └── groups_messages_eda.ipynb
```

---

## Prerequisites

- **Python** ≥ 3.11  
- **SQLite** (bundled with Python)
- **Dependencies**:
  - `telethon`
  - `tqdm`
  - `wakepy`
  - `python-dotenv`
  - `emoji`
  - `pytz`

Install via:

```bash
pip install telethon tqdm wakepy python-dotenv emoji pytz
```

---

## Configuration

### Environment variables
Create a file named `.env` in the project root with:
```dotenv
API_ID=<your Telegram API ID>
API_HASH=<your Telegram API hash>
PHONE_NUMBER=<your Telegram phone number>
PASSWORD_2FA=<your Telegram 2FA password>
```

### Constants: Group mapping
Ensure `TELEGRAM_GROUPS_MAP` (imported in `main.py`) lists all target group identifiers.


---

## Usage
1. Adjust the extraction window in `main.py`:
```python
israel_tz = ZoneInfo("Asia/Jerusalem")
start_local = datetime(2023, 10, 6, 0, 0, 0, tzinfo=israel_tz)
end_local   = datetime(2025, 2, 21, 23, 59, 59, tzinfo=israel_tz)
```
2. Run the script:
```bash
python main.py
```

3. **Output:**
A SQLite database at `data/telegram_data.db` with a table named `groups_messages` containing all extracted messages.

---

## Module Reference

### `main.py` 
- Defines local timezone and extraction dates. 
- Iterates over `TELEGRAM_GROUPS_MAP`. 
- Uses `TelegramExtractor` to pull and store messages.

### `messages_database.py`
- `MessageData`: A `@dataclass` representing each message and derived metrics (timestamps, word/emoji counts, etc.).
- `MessageDatabase`:
  - `create_table(table_name)`: Creates the main table with a composite primary key and relevant indexes. 
  - `insert_messages(...)`: Batch-inserts `MessageData` instances, serializing complex fields as JSON. 
  - Helpers for schema migrations (`add_column_if_not_exists`, `create_index_if_not_exists`).

### `telegram_extractor.py`
- `TelegramExtractor`:
  - Loads credentials via `dotenv`. 
  - `connect_client`: Authenticates and returns an active `TelegramClient`.
  - `_handle_rate_limit`: Awaits on `FloodWaitError`.
  - `_process_message`:
    - Converts raw `message` to `MessageData` (handles UTC ↔ Asia/Jerusalem, forwards, replies, reactions, text metrics).
  - `_process_message_with_media_types`: Extracts metadata for documents, photos, polls, and web pages. 
  - `extract_messages`:
    - Paginates via `GetHistoryRequest`. 
    - Filters messages by date, processes them, and inserts into the database. 
    - Stops when reaching messages older than `start_date`.

---

##  Customization

### Add new features
- Extend `MessageData` and update `messages_database.py` to store extra fields. 
- Use `MessageDatabase.add_column_if_not_exists` for safe migrations.

### Customize groups
- Modify `TELEGRAM_GROUPS_MAP` to add or remove channels.

### Error handling & logging
- Logging is configured at `INFO` level; adjust in `telegram_extractor.py` as needed.

