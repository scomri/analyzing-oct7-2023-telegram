# Wikipedia Events Parsing Module

This sub-README describes the suite of Python scripts for extracting and structuring date‐ and event‐related information from Wikipedia pages and section titles.

---

## Directory Structure

```plaintext
wikipedia_events/
    ├── time_periods_parser.py 
    ├── wikipedia_dates_parser.py 
    └── wikipedia_titles_parser.py
```

---

## Prerequisites

- **Python** ≥ 3.11  
- **Libraries** (install via `pip`):
  - `requests`
  - `beautifulsoup4`
  - `wikipedia-api`
  - `nltk`
- **NLTK data**:  
  ```bash
  pip install requests beautifulsoup4 wikipedia-api nltk
  python -c "import nltk; nltk.download('punkt')"
  ```

---

## Scripts

### 1. `time_periods_parser.py`

- **Purpose:**
Parse a CSV of Wikipedia section titles (with columns level, title, indented_title) to extract date/time periods, compute start/end dates and durations.

- **Key Functions:**
  - `extract_time_periods(input_csv, output_csv)`
  - `extract_period_info(matches)`

- **Input CSV:**
Must include at least these headers:
`level,title,indented_title`

- **Output CSV:**
Columns:
`title,period,start_date,end_date,duration_days,level,indented_title`

- **Usage:**
```bash
python time_periods_parser.py
```

### 2. `wikipedia_dates_parser.py`

- **Purpose:**
Fetch a Wikipedia article’s HTML, scan its paragraphs and headings for date patterns, and capture each date with its surrounding sentence.

- **Key Functions:**
  - `extract_wikipedia_dates(url)`
  - `write_to_csv(data, filename)`

- **Date Patterns Supported:**
  - Month Day, Year (e.g., “October 7, 2023”)
  - Day Month Year (e.g., “7 October 2023”)
  - DD.MM.YYYY / DD-MM-YYYY / DD/MM/YYYY 
  - Month Year (e.g., “October 2023”)

- **Output CSV:**
Columns:
`Date,Context`

- **Usage:**
```bash
python wikipedia_dates_parser.py
```

### 3. `wikipedia_titles_parser.py`

- **Purpose:**
Use the Wikipedia API to retrieve a page’s main title and hierarchical section titles, then save them as JSON and/or CSV.

- **Key Functions:**
  - `parse_wikipedia_titles_api(page_title)`
  - `save_to_json(data, filename)`
  - `save_to_csv(data, filename)`

- **Output Formats:**
  - JSON:
    ```json
    {
      "main_title": "...",
      "sections": [
        {"title": "...", "level": 2},
        ...
      ]
    }
    ```
  - CSV:
  Columns: `level,title,indented_title`

- **Usage:**
```bash
python wikipedia_titles_parser.py
```


---

## Customization

- **Input/Output Paths:** Edit the hardcoded paths in each `__main__` block or refactor to accept CLI arguments. 
- **Date Formats:** Extend the regex patterns in `wikipedia_dates_parser.py` or `time_periods_parser.py` for additional date representations. 
- **Section Levels:** Adjust the recursion in `wikipedia_titles_parser.py` to capture deeper or shallower heading levels.