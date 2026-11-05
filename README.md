# Kerala Daily Rainfall – ETL Pipeline

## Objective
Build an ETL pipeline that turns the raw Kerala daily rainfall file into a clean,
analysis-ready dataset (plus summary reports) that can be reused in future Data Science projects.

## Data Source
| Question | Answer |
|---|---|
| **Data source** | Kerala manual daily rainfall station data, 2021 (`rainfall_1.csv`). The column layout (LGD codes, basin/tributary, acquisition time) matches Indian government water-resources data such as India-WRIS. https://nwdp.nwic.gov.in/dataset/rainfall-kerala-surface-water-manual-daily/resource/d175f1f6-cccf-4980-97ab-877650d05074 |
| **Why chosen** | Real open-government data, large enough (53,162 rows) to need proper cleaning, and rainfall is useful for forecasting, flood and agriculture projects. |
| **Information it contains** | Station name, district, tehsil, river/basin details, latitude/longitude, date-time of reading, and daily rainfall in mm for stations across Kerala. |
| **Type** | Structured (rows and columns). |
| **Format** | CSV, 20 columns. |
| **Update frequency** | Rainfall is recorded manually every day; this file is a static snapshot covering 01 Jan 2021 – 31 Dec 2021. |

## ETL Workflow
```
Data Source (raw_data/rainfall_1.csv)
        │
        ▼
Extract   – read CSV, show records/columns, save raw copy
        │
        ▼
Validate  – missing values, duplicates, negative rainfall
        │
        ▼
Clean     – rename, de-duplicate, drop columns, standardize text,
        │   fill missing, parse dates, fix types, remove invalid rows
        ▼
Transform – date parts, season, rainfall category, station total + rank, sort
        │
        ▼
Generate Reports (summary, district, monthly, seasonal, top/bottom 10 ...)
        │
        ▼
Load      – save to reports/ and output/
```

## Project Structure
```
Kerala_Rainfall_ETL/
├── raw_data/        rainfall_1.csv, rainfall_raw_copy.csv
├── reports/         all generated reports (CSV)
├── screenshots/     screenshots of pipeline run and outputs
├── output/          analysis_ready_rainfall.csv
├── pipeline.py
├── README.md
└── requirements.txt
```

## How to Run
```
pip install -r requirements.txt
python pipeline.py
```

## List of Transformations (and why)
| # | Transformation | Why it was necessary |
|---|---|---|
| T1 | Rename columns to snake_case | Names with spaces/brackets are hard to use in code |
| T2 | Remove duplicate rows | Would double-count rainfall |
| T3 | Remove unwanted columns (row id + 4 columns >90% empty) | Block, Village, Subtributary, SubSubtributary carry no information |
| T4 | Standardize text (trim, Title Case) | Same name must not appear as two values |
| T5 | Handle missing values (river/basin → "Unknown") | Keeps all rows without guessing values |
| T6 | Convert date format (`06012021  08:30:00 AM` → datetime) | Needed for sorting and monthly analysis |
| T7 | Change data types | Correct int/float types for codes, coordinates, rainfall |
| T8 | Remove invalid values (bad dates, negative rainfall, coordinates outside Kerala) | Cannot be real observations |
| T8b | Remove duplicate station-day readings | One reading per station per day |
| T9 | Split date into year / month / month name / weekday | Easy monthly and trend analysis |
| T10 | Create season column | Kerala rainfall is monsoon-driven |
| T11 | Create rainfall category (IMD classes) | Describes intensity of each reading |
| T12 | Aggregation + ranking (station total and rank) | Quickly identify wettest stations |
| T13 | Sort by station and date | Ready for time-series use |

The pipeline also writes `reports/transformation_log.csv` showing the row counts after each step.

## Reports Generated (in `reports/`)
1. `cleaned_data.csv` – complete cleaned dataset
2. `summary_statistics.csv` – count, mean, std, min, quartiles, max
3. `district_wise_report.csv` – region-wise totals and averages
4. `monthly_report.csv` – month-wise rainfall
5. `seasonal_report.csv` – season-wise rainfall
6. `rainfall_category_report.csv` – count and % of each rainfall class
7. `top10_rainiest_days.csv`
8. `top10_stations_by_avg_rainfall.csv`
9. `bottom10_stations_by_avg_rainfall.csv`
10. `highest_lowest_values.csv`
11. `transformation_log.csv`

## Challenges Faced
- Dates were stored as text in `DDMMYYYY  hh:mm:ss AM` format with a double space.
- Four columns were almost entirely empty and river details were missing for some stations.
- 640 duplicate station-day readings had to be removed (53,162 → 52,522 rows).
- Stations have uneven coverage (134 to 685 readings each), and the file has no zero-rainfall readings, so averages describe rainy-day readings and should not be treated as true yearly averages.

## Learning Outcomes
- Designing an Extract → Transform → Load pipeline with separate functions
- Cleaning and validating real government data with pandas
- Creating derived columns (season, category, rank) and summary reports
- Working as a team on one codebase

## Future Improvements
- Pull data directly from the source API instead of a downloaded file
- Add a calendar of all days so missing days can be treated as zero or unknown
- Add charts/dashboard for the reports
- Add unit tests and logging to a file
- Support multiple years of data
