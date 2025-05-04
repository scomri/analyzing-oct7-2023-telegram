# Sentiment Analysis Notebooks

This README describes the collection of Jupyter notebooks used to implement the methodology for analyzing Telegram‐based sentiment dynamics around the October 7, 2023 conflict. 

Each notebook corresponds to one of the methodological subsections in the project paper.

---

## Directory Contents
```plaintext
sentiment_analysis/
    ├── sentiment_analysis_1.ipynb                  # Sentiment classification pipeline 
    ├── sentiment_agg_by_time_2.ipynb               # Sentiment aggregation by time intervals 
    ├── sentiment_time_series_3.ipynb               # Time-series diagnostics & decomposition 
    ├── sentiment_time_series_by_type_4.ipynb       # Group-type aggregated time-series 
    ├── sentiment_event_detection_5.ipynb           # Change-point & event detection 
    └── sentiment_events_analysis_6.ipynb           # Event correlation & statistical testing
```

---

## Prerequisites

- **Python** ≥ 3.11  
- **Jupyter Notebook** or **JupyterLab**  
- **Key Python packages** (install with `pip install`):
  - `pandas numpy matplotlib seaborn nltk transformers torch statsmodels ruptures scipy plotly`
- **NLTK data** (for tokenization):
    ```bash
    python -m nltk.downloader punkt
    ```
  
---

## Execution Order & Usage

### Sentiment Analysis `sentiment_analysis_1.ipynb`
- Language detection and text normalization (Hebrew↔Arabic). 
- Apply DicataBERT-Sentiment (Hebrew) and CAMeLBERT-DA (Arabic) to generate per‐message sentiment labels and confidence scores. 
- Outputs a consolidated DataFrame or CSV of message‐level predictions.

### Sentiment Aggregation by Time `sentiment_agg_by_time_2.ipynb`
- Load message‐level sentiment. 
- Compute hourly, daily, and weekly aggregates:
  - Net Sentiment _(%Pos − %Neg)_
  - Sentiment Index _((#Pos − #Neg)/(#Total) × 100)_
- Message volumes and average confidence. 
- Save aggregated CSVs for time‐series analysis.

### Sentiment Time Series Analysis `sentiment_time_series_3.ipynb`
- Import daily aggregates. 
- Smooth series with moving averages. 
- Decompose into trend, seasonal, residual components (classical decomposition). 
- Test stationarity (ADF, KPSS) and examine residuals (ACF, Ljung–Box).

### Group-Type Time Series by Language/Ideology `sentiment_time_series_by_type_4.ipynb`
- Merge channel metadata (language & ideological class). 
- Generate separate daily series for each group type. 
- Visualize 14-day rolling trends and boxplots. 
- Compute cross‐language correlations and run Granger causality tests.

### Sentiment Event Detection `sentiment_event_detection_5.ipynb`
- Load Hebrew and Arabic daily sentiment series.
- Apply multiple change‐point algorithms (CUSUM, PELT).
- Perform time-lagged cross‐correlation (±20 days).
- Consolidate detected dates into a ranked list of significant sentiment events.

### Sentiment Event Correlation Analysis️ `sentiment_events_analysis_6.ipynb`
- Import detected event dates and Wikipedia‐extracted conflict periods. 
- Overlay sentiment trajectories with conflict phase ranges. 
- Window‐based tests (t-tests, ANOVA) on pre/during/post‐event sentiment. 
- Linear regression models with time & event dummy controls. 
- Compare sentiment divergence across ideological and linguistic subgroups.


---

## Methodology Mapping

| Notebook                          | Methodology Subsection                   |
|-----------------------------------|------------------------------------------|
| `sentiment_analysis_1.ipynb`      | Sentiment Analysis                       |
| `sentiment_agg_by_time_2.ipynb`   | Sentiment Time Series Analysis (Aggregation) |
| `sentiment_time_series_3.ipynb`   | Sentiment Time Series Analysis (Diagnostics) |
| `sentiment_time_series_by_type_4.ipynb` | Group-Type Aggregated Time Series     |
| `sentiment_event_detection_5.ipynb` | Sentiment Event Detection              |
| `sentiment_events_analysis_6.ipynb` | Sentiment Event Correlation Analysis   |


---

## Customization

- **Parameter tuning:**
  - Change aggregation windows (e.g., add monthly). 
  - Adjust change‐point detection sensitivity or window lengths.

- **Model updates:**
  - Swap in fine‐tuned or alternative sentiment models.

- **Additional analyses:**
  - Extend event correlation with external data sources (e.g., news volumes).