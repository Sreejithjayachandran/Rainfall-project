# Kerala Daily Rainfall – ETL Pipeline & Exploratory Data Analysis

A team mini-project that builds an automated **Extract – Transform – Load (ETL)** pipeline and comprehensive **Exploratory Data Analysis (EDA)**. It turns raw Indian Government meteorological rainfall data (53,162 records with non-standard date strings, empty administrative hierarchies, duplicates, and missing values) into a clean, verified, analysis-ready dataset (52,522 rows × 24 columns) for future Data Science, climate analytics, flood prediction, and agricultural modeling projects.

---

## Contents
- [Objective](#objective)
- [Data Source](#data-source)
- [ETL Workflow](#etl-workflow)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Team and Responsibilities](#team-and-responsibilities)
- [Transformations](#transformations)
- [Reports Generated](#reports-generated)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Key Findings](#key-findings)
- [Challenges Faced](#challenges-faced)
- [Learning Outcomes](#learning-outcomes)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)

---

## Objective
The primary objective of this project is to construct a robust, production-grade, reproducible ETL pipeline that prepares raw meteorological telemetry into an analysis-ready dataset. 

Raw environmental data is notorious for formatting anomalies, irregular recording intervals, missing coordinates, and inconsistent geographical identifiers. By establishing strict automated validation rules, modular cleaning routines, meteorological feature engineering (such as IMD intensity categories and monsoon seasons), and automated reporting, downstream machine learning practitioners can bypass tedious preprocessing and start directly with predictive modeling (e.g., rainfall forecasting, flood inundation modeling, reservoir inflow optimization).

Every transformation step is systematically tracked and row-counted in `reports/transformation_log.csv`.

---

## Data Source

| Item | Detail |
|---|---|
| **Dataset** | Kerala Surface Water Manual Daily Rainfall Station Data |
| **Original Provider** | National Water Development Agency / National Water Informatics Centre (NWIC), Ministry of Jal Shakti, Government of India |
| **Direct Download** | [NWIC Kerala Manual Daily Rainfall Portal](https://nwdp.nwic.gov.in/dataset/rainfall-kerala-surface-water-manual-daily/resource/d175f1f6-cccf-4980-97ab-877650d05074) |
| **Format / Type** | CSV, Structured tabular data (20 original raw columns, 53,162 records) |
| **Temporal Coverage** | 01 January 2021 – 31 December 2021 (with continuous monitoring records) |
| **Geographic Scope** | All 14 districts of Kerala, covering 104+ dedicated rain-gauge stations |
| **Update Frequency** | Static historical snapshot derived from daily telemetry recordings |

---

## ETL Workflow

```
                        Data Source (raw_data/rainfall_1.csv)
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                             EXTRACT extract()                            |
    |  • Ingest CSV from raw_data/                                             |
    |  • Assert schema, dimension checks (53,162 rows × 20 cols)               |
    |  • Generate immutable raw backup (raw_data/rainfall_raw_copy.csv)        |
    |  • Responsibility: Member 2 (Jesvin)                                     |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                            VALIDATE validate()                           |
    |  • Verify required column headers & data boundary conditions             |
    |  • Detect null thresholds, corrupt dates, negative precipitation values  |
    |  • Responsibility: Member 2 (Jesvin)                                     |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                         TRANSFORM transform()                            |
    |                                                                          |
    |  [Stage 1: Cleaning & Structural Operations - Member 3 (Sreejith)]       |
    |  • Rename to snake_case, drop 4 non-informative sparse columns           |
    |  • De-duplicate identical rows & station-day conflicts (640 removed)     |
    |  • Normalize text (Title Case, trim), impute missing basins to "Unknown" |
    |  • Parse custom dates ('DDMMYYYY  hh:mm:ss AM'), cast numeric dtypes     |
    |  • Filter invalid rows (negative rain, out-of-boundary coordinates)      |
    |                                                                          |
    |  [Stage 2: Feature Engineering & Enrichment - Member 4 (Adharsh)]        |
    |  • Extract date components (year, month, month_name, day, day_name)      |
    |  • Map meteorological seasons (Southwest Monsoon, Post-Monsoon, etc.)   |
    |  • Classify IMD rainfall intensity (Very Light to Extremely Heavy)       |
    |  • Compute station total rainfall and statewide station ranking          |
    |  • Sort chronologically by station and observation date                  |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                    GENERATE REPORTS generate_reports()                   |
    |  • Produce 11 analytical summary reports in CSV format                   |
    |  • Summary stats, category/district/monthly/seasonal aggregations        |
    |  • Top 10 rainiest days, wettest/driest stations, highest/lowest values  |
    |  • Responsibility: Member 4 (Adharsh)                                    |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                               LOAD load()                                |
    |  • Persist clean analysis-ready dataset to output/ (52,522 × 24 cols)    |
    |  • Persist all 11 reports to reports/                                    |
    |  • Responsibility: Member 5 (Ajas)                                       |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                  EXPLORATORY DATA ANALYSIS (EDA/eda.ipynb)               |
    |  • 10 publication-grade Seaborn & Matplotlib visualizations              |
    |  • Member 1 (Aslaf)  – EDA_REPORT.md write-up & insight documentation   |
    |  • Member 2 (Jesvin) – Charts 2 & 4: Monthly Progression, Distributions |
    |  • Member 3 (Sreejith)– Charts 5 & 6: District Spread, Extreme Events   |
    |  • Member 4 (Adharsh)– Charts 3 & 8: Seasonality, River Basins          |
    |  • Member 5 (Ajas)  – Charts 1,7,9,10: Overview, Spatial, Correlation   |
    +──────────────────────────────────────────────────────────────────────────+
                                        │
                                        ▼
    +──────────────────────────────────────────────────────────────────────────+
    |                    DOCUMENTATION & REPO ARCHITECTURE                     |
    |  • README.md, dataset metadata, GitHub repository & quality assurance   |
    |  • Responsibility: Member 1 (Aslaf)                                      |
    +──────────────────────────────────────────────────────────────────────────+
```

---

## Project Structure

```
Rainfall-project/
├── raw_data/
│   ├── rainfall_1.csv                   # Untouched raw input data from government portal
│   └── rainfall_raw_copy.csv            # Automated extract archive copy
├── reports/                             # Generated analytical CSV reports (11 files)
│   ├── cleaned_data.csv                 # Complete cleaned dataset copy
│   ├── summary_statistics.csv           # Parametric & non-parametric distribution statistics
│   ├── district_wise_report.csv         # District-level rainfall aggregations
│   ├── monthly_report.csv               # Monthly rainfall progression and daily averages
│   ├── seasonal_report.csv              # Rainfall volume breakdown by monsoon season
│   ├── rainfall_category_report.csv     # Frequency & percentage distribution across IMD tiers
│   ├── top10_rainiest_days.csv          # Top 10 statewide heaviest deluge events
│   ├── top10_stations_by_avg_rainfall.csv # Top 10 wettest stations
│   ├── bottom10_stations_by_avg_rainfall.csv # Top 10 driest rain-shadow stations
│   ├── highest_lowest_values.csv        # Extreme statistical boundary metrics
│   └── transformation_log.csv           # Audit trail of row counts across all 14 steps
├── output/
│   ├── analysis_ready_rainfall.csv      # Production analysis-ready dataset (52,522 rows × 24 cols)
│   └── eda/                             # Rendered publication-grade EDA chart images (10 PNGs)
│       ├── 1_overview.png
│       ├── 2_monthly_rainfall.png
│       ├── 3_seasonality.png
│       ├── 4_distributions.png
│       ├── 5_district_spread.png
│       ├── 6_extreme_deluges.png
│       ├── 7_spatial_patterns.png
│       ├── 8_river_basins.png
│       ├── 9_station_performance.png
│       └── 10_correlation.png
├── screenshots/                         # Verification screenshots of pipeline execution
│   ├── Extract_data.png
│   ├── Cleaning.png
│   ├── Pipeline_Process1.png
│   ├── Pipeline_Process2.png
│   ├── Development_Report.png
│   └── etl_flow_diagram.png
├── EDA/                                 # Exploratory Data Analysis suite
│   ├── eda.ipynb                        # Interactive Colab/Jupyter notebook with 10 visual insights
│   ├── eda.py                           # Reusable Seaborn & Matplotlib plotting routines
│   └── EDA_REPORT.md                    # Formal markdown EDA analytical report
├── pipeline.py                          # Complete, self-contained, modular ETL pipeline script
├── requirements.txt                     # Production environment dependencies
└── README.md                            # Comprehensive project documentation
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ajasnizam/Rainfall-project.git
cd Rainfall-project
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Full ETL Pipeline
```bash
python pipeline.py
```
*The pipeline completes in approximately 2 to 3 seconds, logging every stage and writing the output files into `output/` and `reports/`.*

### 5. Run Exploratory Data Analysis
Open `EDA/eda.ipynb` in **VS Code**, **Jupyter Lab**, or upload to **Google Colab** and run all cells to reproduce the visual analysis.

---

## Team and Responsibilities

| Member | Name | Primary Role & Responsibilities | Key Deliverables |
|:---:|:---:|---|---|
| **Member 1** | **Aslaf** | **Documentation, QA & EDA Reporting**<br>Authored project documentation, schema definitions, dataset descriptions, transformation rationales, ensured GitHub standards compliance, and wrote the formal `EDA_REPORT.md` with interpretation of all visual insights. | `README.md`, `EDA/EDA_REPORT.md`, Dataset specs, Transformation log verification |
| **Member 2** | **Jesvin** | **Data Extraction, Validation & EDA (Time / Distribution)**<br>Built the `extract()` module, verified raw file integrity, performed dimensional assertions, handled missing file fallbacks, created raw archives, and produced EDA charts for monthly rainfall progression and numerical distributions. | `extract()`, `validate()`, `raw_data/rainfall_raw_copy.csv`, Chart 2 (`2_monthly_rainfall.png`), Chart 4 (`4_distributions.png`) |
| **Member 3** | **Sreejith** | **Data Cleaning, Structural Transformations & EDA (District / Extreme Events)**<br>Executed data de-duplication, missing value handling, column pruning, custom date-time string parsing, data type casting, anomaly filtering, and produced EDA charts examining district-level spread and extreme deluge events. | `transform()` Part 1 (Transformations T1–T9), Chart 5 (`5_district_spread.png`), Chart 6 (`6_extreme_deluges.png`) |
| **Member 4** | **Adharsh** | **Feature Engineering, Analytical Reporting & EDA (Seasonality / River Basins)**<br>Derived temporal attributes, IMD intensity categories, meteorological monsoon seasons, station aggregates, ranking logic, generated 11 CSV reports, and produced EDA charts for monsoon seasonality and river basin analysis. | `transform()` Part 2 (Transformations T10–T14), `generate_reports()`, 11 CSV reports, Chart 3 (`3_seasonality.png`), Chart 8 (`8_river_basins.png`) |
| **Member 5** | **Ajas**<br>*(Team Lead / Repo Owner)* | **Loading, Pipeline Orchestration & EDA (Overview / Spatial / Station / Correlation)**<br>Implemented `load()` and `run_etl_pipeline()`, architected `EDA/eda.ipynb` with Seaborn/Matplotlib, managed GitHub repo deployment, coordinated team integration, and produced the EDA overview, spatial pattern, station performance, and correlation charts. | `load()`, `run_etl_pipeline()`, `EDA/eda.ipynb`, `eda.py`, Chart 1 (`1_overview.png`), Chart 7 (`7_spatial_patterns.png`), Chart 9 (`9_station_performance.png`), Chart 10 (`10_correlation.png`) |

---

## Transformations

| # | Responsible Member | Transformation | Description | Why It Was Necessary |
|:---:|:---:|---|---|---|
| **T1** | Member 3 (Sreejith) | **Column Renaming** | Renamed cryptic and inconsistent headers with spaces/parentheses to standard `snake_case`. | Raw names like `Rainfall(mm)` and `Station Name` complicate programmatic access and cause syntax issues in queries. |
| **T2** | Member 3 (Sreejith) | **Exact Duplicate Removal** | Removed identical duplicate rows across all columns. | Duplicate entries distort aggregate rainfall totals and bias station averages. |
| **T3** | Member 3 (Sreejith) | **Unwanted Column Pruning** | Dropped `row_id`, `block_name`, `village_name`, `subtributary_name`, and `subsubtributary_name`. | Over 90% of values in these columns were missing or unpopulated, carrying zero predictive utility. |
| **T4** | Member 3 (Sreejith) | **Text Standardization** | Stripped leading/trailing whitespace and normalized district and station strings to Title Case. | Prevents duplicate categories caused by casing differences (e.g., `"WAYANAD"`, `"wayanad"`, and `"Wayanad"`). |
| **T5** | Member 3 (Sreejith) | **Missing Value Imputation** | Filled missing entries in `river_name` and `basin_name` with `"Unknown"`. | Avoids dropping valid rainfall records while preserving schema completeness for downstream grouping. |
| **T6** | Member 3 (Sreejith) | **Date-Time Parsing** | Converted custom date text strings (`"06012021  08:30:00 AM"`) into standard ISO datetime objects. | Raw string dates cannot be sorted chronologically or grouped by calendar periods. |
| **T7** | Member 3 (Sreejith) | **Data Type Casting** | Cast latitude, longitude, and rainfall to `float64`, and administrative LGD codes to integers. | Guarantees numerical precision for geographical mapping and mathematical aggregations. |
| **T8** | Member 3 (Sreejith) | **Invalid Value Filtering** | Screened out negative precipitation values and invalid coordinates outside Kerala's geographical boundaries. | Meteorological precipitation cannot be negative; corrupted sensor readings must not leak into analysis. |
| **T9** | Member 3 (Sreejith) | **Station-Day Deduplication** | Resolved multiple readings for the same station on the same calendar day by keeping the latest valid reading. | Ensures the foundational time-series assumption: exactly one daily rainfall observation per station per day (640 duplicates pruned). |
| **T10** | Member 4 (Adharsh) | **Date Decomposition** | Extracted `year`, `month`, `month_name`, `day`, and `day_name` into discrete columns. | Enables granular time-series analysis, monthly progress tracking, and day-of-week cyclical modeling. |
| **T11** | Member 4 (Adharsh) | **Meteorological Season Mapping** | Classified each date into standard Indian seasons: *Winter* (Jan–Feb), *Pre-Monsoon* (Mar–May), *Southwest Monsoon* (Jun–Sep), and *Post-Monsoon* (Oct–Dec). | Kerala's hydrological cycle is governed by monsoon seasonality; seasonal stratification is crucial for flood risk assessment. |
| **T12** | Member 4 (Adharsh) | **IMD Category Classification** | Categorized rainfall according to official IMD thresholds: *Very Light* (< 2.5 mm), *Light* (2.5–15.5 mm), *Moderate* (15.6–64.4 mm), *Heavy* (64.5–115.5 mm), *Very Heavy* (115.6–204.4 mm), and *Extremely Heavy* (≥ 204.5 mm). | Standardizes meteorological severity for disaster management and alert modeling. |
| **T13** | Member 4 (Adharsh) | **Station Aggregation & Ranking** | Computed annual cumulative rainfall per station (`station_total_rainfall_mm`) and assigned statewide ranks (`station_rank`). | Instantly identifies Kerala's most critical flood-prone catchment zones. |
| **T14** | Member 4 (Adharsh) | **Chronological & Spatial Sorting** | Sorted the dataset primarily by `station_name` and secondarily by `date_time`. | Optimizes the dataset layout for sequential time-series modeling and rolling-window computations. |

---

## Reports Generated

All reports are generated automatically by `generate_reports()` Member 4 (Adharsh) and saved as CSV files in `reports/`:

| Report File | Description & Contents |
|---|---|
| `cleaned_data.csv` | Full replica of the analysis-ready dataset (52,522 rows × 24 columns). |
| `summary_statistics.csv` | Comprehensive parametric and non-parametric statistics (count, mean, std, min, 25%, 50%, 75%, max) for numeric columns. |
| `district_wise_report.csv` | District-level aggregations: total precipitation, average daily rainfall, and record counts across all 14 districts. |
| `monthly_report.csv` | Month-by-month total rainfall, daily average, and active rain-gauge observation counts. |
| `seasonal_report.csv` | Breakdown across the 4 meteorological seasons showing cumulative volume and percentage contribution. |
| `rainfall_category_report.csv` | Observation count, percentage distribution, and cumulative volume across IMD intensity tiers. |
| `top10_rainiest_days.csv` | Top 10 heaviest statewide single-day rainfall recordings with date, station, district, and rainfall in mm. |
| `top10_stations_by_avg_rainfall.csv` | The 10 wettest rain-gauge stations in Kerala based on daily mean rainfall. |
| `bottom10_stations_by_avg_rainfall.csv` | The 10 driest stations (rain-shadow zones in eastern Idukki and southern Kerala). |
| `highest_lowest_values.csv` | Extreme boundary value summary identifying maximum and minimum records for rainfall, coordinates, and stations. |
| `transformation_log.csv` | Detailed step-by-step audit log recording row counts, columns, and operations after every transformation. |

---

## Exploratory Data Analysis (EDA)

Exploratory Data Analysis is documented in [`EDA/eda.ipynb`](EDA/eda.ipynb) and [`EDA/EDA_REPORT.md`](EDA/EDA_REPORT.md). All 10 visualizations are saved to `output/eda/`. EDA work is divided across the team as follows:

**Member 5 (Ajas) — Overview, Spatial, Station & Correlation:**
1. **Rainfall Intensity & Rain Days (`1_overview.png`)**: 81.6% of records qualify as official IMD rain days ($\ge 2.5\text{ mm}$). Most events fall into Light (40.7%) and Moderate (34.5%) bands, but severe deluges ($\ge 64.5\text{ mm}$) drive over 42% of runoff volume.
7. **Spatial Patterns (`7_spatial_patterns.png`)**: Stations north of $11^\circ\text{N}$ receive 24.5 mm/day vs 18.2 mm/day south of $9.5^\circ\text{N}$, with intense orographic enhancement along the Western Ghats windward slopes ($76.5^\circ\text{E}$–$77.2^\circ\text{E}$).
9. **Station Variations (`9_station_performance.png`)**: Wettest stations (Payyavoor at 37.3 mm/day, Ponmudi at 30.6 mm/day) accumulate over 5,000–6,000 mm annually, compared to rain-shadow stations averaging under 10–12 mm/day.
10. **Correlation Matrix (`10_correlation.png`)**: Latitude positively correlates with rainfall (+0.14), validating the wetter northern corridor. Dynamic atmospheric variance dominates daily weather over static coordinates.

**Member 2 (Jesvin) — Time Progression & Distributions:**
2. **Monthly Progression (`2_monthly_rainfall.png`)**: Volume surges in May, peaks decisively in **July** (280.6k mm across 9,193 readings, averaging 30.5 mm/day), and exhibits a secondary peak in **October** (113.4k mm) from the Northeast Monsoon.
4. **Numerical Distributions (`4_distributions.png`)**: Daily rainfall is heavily right-skewed (median 11.2 mm, mean 20.5 mm, std 25.8 mm). Outliers exceed 100 mm and reach up to 372.6 mm.

**Member 4 (Adharsh) — Seasonality & River Basins:**
3. **Monsoon Seasonality (`3_seasonality.png`)**: Southwest Monsoon (June–Sept) delivers 62.3% of total rainfall (665.3k mm), Post-Monsoon contributes 19.4% (207.6k mm), Pre-Monsoon adds 17.7%, and Winter is dry (1.3%).
8. **River Basins (`8_river_basins.png`)**: West Flowing Rivers and Periyar/Bharathappuzha catchments capture over 68% of total monitored runoff.

**Member 3 (Sreejith) — District Spread & Extreme Events:**
5. **District Spread (`5_district_spread.png`)**: Northern Malabar districts lead in intensity: Kannur records the highest mean daily rate (26.6 mm/day), followed by Ernakulam (24.0 mm) and Kasaragod (23.8 mm).
6. **Extreme Events (`6_extreme_deluges.png`)**: Exactly 58 events reached the IMD *Extremely Heavy* tier ($\ge 204.5\text{ mm}$). The state peak was 372.6 mm at Kalladi (Wayanad) on July 30, 2024.

**Member 1 (Aslaf) — EDA Documentation & Insight Reporting:**
Authored [`EDA/EDA_REPORT.md`](EDA/EDA_REPORT.md) — the formal written analysis summarizing findings, interpreting all 10 charts, and contextualizing results within Kerala's hydrological landscape.

---

## Key Findings
- **Total Ingested vs Clean Records**: 53,162 raw records cleaned down to **52,522 validated observations** across 14 districts and 104+ stations.
- **Monsoon Dominance**: The Southwest Monsoon contributes **62.3%** of annual water volume, with July serving as the peak hydrological hazard month.
- **Severe Deluges**: Although extreme deluges ($\ge 64.5\text{ mm}$) represent only **6.4%** of events, they account for over **42%** of statewide precipitation volume.
- **Microclimates & Spatial Disparity**: A **3.5× spatial disparity** exists between the Western Ghats windward stations (> 35 mm/day) and eastern rain-shadow stations (< 10 mm/day).
- **Extreme Event Peak**: State-level single-day maximum reached **372.6 mm** at Kalladi station in Wayanad district.

---

## Challenges Faced
1. **Custom Date-Time Formatting**: Timestamps were stored with non-standard spacing (`"06012021  08:30:00 AM"`), requiring custom parsing masks instead of generic date parsers.
2. **High Sparsity in Administrative Columns**: Columns like `block_name` and `subtributary_name` were over 90% unpopulated, necessitating strategic column pruning to optimize memory.
3. **Station-Day Duplicate Readings**: Over 640 conflicting station-day readings were detected and resolved to preserve strict 1-record-per-day time-series integrity.
4. **Extreme Distribution Skewness**: Rainfall data has a heavy right-skewed tail (kurtosis > 25), requiring log-transformed scales and non-parametric quartile metrics in summary reporting.
5. **Team Modularity & Git Workflow**: Dividing a single pipeline across 5 team members required strict input/output interface contracts so each member's stage passed clean data to the next.

---

## Learning Outcomes
- **Modular Pipeline Architecture**: Designing clean, testable, independent functions (`extract`, `validate`, `transform`, `generate_reports`, `load`) connected through a main orchestrator.
- **Automated Data Quality Auditing**: Establishing pre-transform validation checks and logging row counts after every step in `transformation_log.csv`.
- **Domain-Specific Feature Engineering**: Translating meteorological standards (IMD classification, monsoon seasons) into programmatic features.
- **Collaborative Engineering**: Practicing team branch management, commit hygiene, and structured code ownership across 5 developers.

---

## Future Improvements

The next planned phase for this project is integrating **Machine Learning** directly into the pipeline to transform it from a data preparation tool into a full predictive analytics system:

- **ML Pipeline Extension**: Add an `ml_pipeline()` stage to `pipeline.py` that trains and evaluates models on the analysis-ready dataset produced by `load()`.
- **Rainfall Forecasting (LSTM / ARIMA)**: Train Long Short-Term Memory (LSTM) recurrent networks and ARIMA seasonal models to forecast daily rainfall 24–48 hours ahead using station time-series data.
- **Extreme Event Classification (Random Forest / XGBoost)**: Build binary and multi-class classifiers to predict IMD *Heavy*, *Very Heavy*, and *Extremely Heavy* flood-risk events before they occur, enabling proactive disaster alerts.
- **Flood Inundation Modeling**: Combine station readings with elevation data (DEM) and basin geometry to map predicted flood-inundation zones at district level.
- **Live Ingestion via API**: Connect the `extract()` function to the National Water Informatics Centre (NWIC) REST API for scheduled daily updates, feeding fresh data directly into the ML models.
- **Interactive Dashboard**: Build a **Streamlit** real-time flood monitoring dashboard that displays model predictions, IMD alerts, and district-level risk maps alongside the generated EDA charts.
- **Database Storage**: Load the cleaned dataset and ML outputs into a **PostgreSQL / TimescaleDB** database with **PostGIS** geospatial indexing for scalable querying.

---

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes with clear messages (`git commit -m 'feat: add feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request for review by Team Lead **Ajas**.
