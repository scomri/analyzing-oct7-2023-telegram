# Analyzing The October 7, 2023 War Events Based on Telegram Channels

A framework for extracting, processing, and analyzing Telegram communications and related event data around the October 7, 2023 conflict. 

This project combines three key modules: message extraction, event parsing, and sentiment analysis, to map sentiment dynamics onto real‐world conflict timelines.

---

## Project Structure
```plaintext
. 
├── telegram_groups_messages/       # Telegram message extraction module 
├── wikipedia_events/               # Wikipedia conflict periods parsing module 
└── sentiment_analysis/             # Sentiment analysis & time-series notebooks 
```


---

## Modules

### 1. Telegram Message Extraction  
Fetches raw messages from selected Telegram groups and stores them in SQLite for downstream analysis.  
- **Location:** `telegram_groups_messages/`  
- **Core scripts:** `main.py`, `telegram_extractor.py`, `messages_database.py`  
- **Highlights:**  
  - Rate-limit handling, timezone normalization (Asia/Jerusalem), media metadata, message-level metrics.  
  - Composite-key SQLite schema with JSON serialization for complex fields.  
- _See module README_.

### 2. Wikipedia Events Parsing  
Builds a structured timeline of conflict phases by extracting dates and section titles from Wikipedia.  
- **Location:** `wikipedia_events/`  
- **Core scripts:** `wikipedia_dates_parser.py`, `wikipedia_titles_parser.py`, `time_periods_parser.py`  
- **Highlights:**  
  - HTML scraping and API calls to capture diverse date formats.  
  - Maps section headings to `(start_date, end_date, duration)` records for correlation.  
- _See module README_.

### 3. Sentiment Analysis & Time Series  
Applies multilingual sentiment models to the Telegram dataset, then aggregates, decomposes, and detects events in the sentiment series.  
- **Location:** `sentiment_analysis/`  
- **Core notebooks:**  
  1. `sentiment_analysis_1.ipynb` – Message-level sentiment labeling  
  2. `sentiment_agg_by_time_2.ipynb` – Hourly/daily/weekly aggregation  
  3. `sentiment_time_series_3.ipynb` – Decomposition & stationarity tests  
  4. `sentiment_time_series_by_type_4.ipynb` – Group-type comparisons & Granger tests  
  5. `sentiment_event_detection_5.ipynb` – Change-point & cross-correlation detection  
  6. `sentiment_events_analysis_6.ipynb` – Event correlation & statistical validation  
- **Highlights:**  
  - Hebrew (DicataBERT-Sentiment) and Arabic (CAMeLBERT-DA) classification.  
  - Net Sentiment & Sentiment Index metrics, CUSUM/PELT detection, t-tests/ANOVA, regression models.  
- _See module README_.


---

## Prerequisites

- **Python** ≥ 3.11  
- **SQLite** (built-in)  
- **Jupyter Notebook/Lab**  
- **Common packages**:
    ```bash
    pip install telethon tqdm wakepy python-dotenv emoji pytz requests beautifulsoup4 wikipedia-api nltk pandas numpy matplotlib nltk transformers torch statsmodels ruptures scipy plotly
  ```
  ```bash
  python -m nltk.downloader punkt
  ```
    
---

## Usage Workflow

### 1. Extract Telegram messages

```bash
cd telegram_groups_messages
python main.py
```

### 2. Parse Wikipedia conflict periods

```bash
cd ../wikipedia_events
python wikipedia_titles_parser.py
python wikipedia_dates_parser.py
python time_periods_parser.py
```

### 3. Run sentiment analysis pipeline

```bash
cd ../sentiment_analysis
jupyter nbconvert --to notebook --execute sentiment_analysis_1.ipynb
# repeat for each notebook in order 2 → 6
```

---

## Customization

- **Time windows & thresholds**: adjust in `main.py` and analysis notebooks 
- **Date formats & section depths**: extend regexes or recursion levels in parsers 
- **Models & metrics**: swap sentiment classifiers or add forecasting

