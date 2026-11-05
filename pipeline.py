"""
Kerala Daily Rainfall ETL Pipeline
==================================
Extract   -> Ingest raw CSV, display record & column count, save raw copy (Member 2)
Transform -> Clean, validate, enrich the data and build analytical reports (Members 3 & 4)
Load      -> Save cleaned dataset to output/ and all reports to reports/ (Member 5)

Dependencies:
    pandas, numpy (ONLY - no other imports or external packages)

Execution:
    python pipeline.py
"""

import pandas as pd
import numpy as np

# --------------------------------------------------------------------------
# Paths and constants (pure string paths)
# --------------------------------------------------------------------------
SOURCE_FILE = "raw_data/rainfall_1.csv"
RAW_COPY = "raw_data/rainfall_raw_copy.csv"
OUTPUT_FILE = "output/analysis_ready_rainfall.csv"
REPORTS_DIR = "reports/"

COLUMN_MAP = {
    "SlNo": "sl_no",
    "Station": "station",
    "Agency": "agency",
    "State LGD Code": "state_lgd_code",
    "State": "state",
    "District LGD Code": "district_lgd_code",
    "District": "district",
    "Tehsil": "tehsil",
    "Block": "block",
    "Village": "village",
    "River": "river",
    "Basin": "basin",
    "Tributary": "tributary",
    "Subtributary": "subtributary",
    "SubSubtributary": "sub_subtributary",
    "Local River": "local_river",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Data Acquisition Time": "acquisition_time",
    "Manual Daily Rainfall (mm)": "rainfall_mm",
}

# Rough bounding box of Kerala to catch out-of-boundary coordinates
KERALA_LAT = (8.0, 13.0)
KERALA_LON = (74.5, 77.5)

# IMD (India Meteorological Department) daily rainfall classes (mm) using numpy infinity
RAIN_BINS = [0, 2.5, 15.6, 64.5, 115.6, 204.5, np.inf]
RAIN_LABELS = ["Very Light", "Light", "Moderate", "Heavy", "Very Heavy", "Extremely Heavy"]

SEASONS = {
    1: "Winter", 2: "Winter",
    3: "Pre-Monsoon", 4: "Pre-Monsoon", 5: "Pre-Monsoon",
    6: "Southwest Monsoon", 7: "Southwest Monsoon",
    8: "Southwest Monsoon", 9: "Southwest Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon", 12: "Post-Monsoon",
}


def _log(log, step, reason, before, after):
    """Record what each transformation did and why it was needed."""
    log.append({"step": step, "reason": reason, "rows_before": before, "rows_after": after})
    print(f"  [{step}] rows: {before} -> {after}")


# --------------------------------------------------------------------------
# STEP 5: EXTRACT (Member 2)
# --------------------------------------------------------------------------
def extract(source_file=SOURCE_FILE):
    """Read the raw CSV, display record & column count, and save copy in raw_data/."""
    print("\n=== STEP 5: EXTRACT (Member 2) ===")
    try:
        df = pd.read_csv(source_file)
    except FileNotFoundError:
        df = pd.read_csv("rainfall_1.csv")

    print(f"Source file       : {source_file}")
    print(f"Number of records : {len(df):,}")
    print(f"Number of columns : {df.shape[1]}")

    df.to_csv(RAW_COPY, index=False)
    print(f"Raw copy saved to : {RAW_COPY}")
    return df


def validate_data(df):
    """Quality check on the raw data (missing values, duplicates, negative values)."""
    print("\n--- Raw Data Validation ---")
    missing = df.isna().sum()
    print("Columns with missing values:")
    print(missing[missing > 0].to_string())
    print(f"Fully duplicated rows: {int(df.duplicated().sum())}")
    
    rainfall_numeric = pd.to_numeric(df["Manual Daily Rainfall (mm)"], errors="coerce")
    neg_count = int(np.sum(rainfall_numeric < 0))
    print(f"Negative rainfall values: {neg_count}")


# --------------------------------------------------------------------------
# STEP 6: TRANSFORM - Cleaning (Member 3)
# --------------------------------------------------------------------------
def t1_rename_columns(df, log):
    before = len(df)
    df = df.rename(columns=COLUMN_MAP)
    _log(log, "T1 Rename columns", "Convert to short snake_case names so they are easy to use in code", before, len(df))
    return df


def t2_remove_duplicates(df, log):
    before = len(df)
    subset_cols = [c for c in df.columns if c != "sl_no"]
    df = df.drop_duplicates(subset=subset_cols)
    _log(log, "T2 Remove duplicate rows", "Exact duplicates would double-count rainfall", before, len(df))
    return df


def t3_drop_unwanted_columns(df, log, threshold=0.9):
    before = len(df)
    sparse = [c for c in df.columns if df[c].isna().mean() > threshold]
    df = df.drop(columns=["sl_no"] + sparse)
    _log(log, "T3 Remove unwanted columns",
         f"Dropped row-id and columns >{int(threshold * 100)}% empty: {', '.join(sparse)}", before, len(df))
    return df


def t4_standardize_text(df, log):
    before = len(df)
    text_cols = ["station", "district", "tehsil", "river", "basin", "tributary", "local_river"]
    for col in text_cols:
        if col in df.columns:
            df[col] = (df[col].astype("string").str.strip()
                       .str.replace(r"\s+", " ", regex=True).str.title())
    _log(log, "T4 Standardize text", "Trim spaces and Title Case so the same name is never counted as two values", before, len(df))
    return df


def t5_handle_missing_values(df, log):
    before = len(df)
    for col in ["river", "basin", "tributary", "local_river"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
    _log(log, "T5 Handle missing values", "Fill missing river/basin details with 'Unknown' so no rows are lost", before, len(df))
    return df


def t6_convert_dates(df, log):
    before = len(df)
    cleaned = df["acquisition_time"].astype(str).str.split().str.join(" ")
    df["date_time"] = pd.to_datetime(cleaned, format="%d%m%Y %I:%M:%S %p", errors="coerce")
    df["date"] = df["date_time"].dt.normalize()
    df = df.drop(columns=["acquisition_time"])
    _log(log, "T6 Convert date format", "Text timestamps cannot be sorted or grouped by month; parsed to datetime", before, len(df))
    return df


def t7_change_data_types(df, log):
    before = len(df)
    df["state_lgd_code"] = df["state_lgd_code"].astype("int32")
    df["district_lgd_code"] = df["district_lgd_code"].astype("int32")
    df["latitude"] = df["latitude"].astype("float64")
    df["longitude"] = df["longitude"].astype("float64")
    df["rainfall_mm"] = pd.to_numeric(df["rainfall_mm"], errors="coerce")
    _log(log, "T7 Change data types", "Codes as integers, coordinates and rainfall as floats", before, len(df))
    return df


def t8_remove_invalid_values(df, log):
    before = len(df)
    valid = (
        df["date"].notna()
        & df["rainfall_mm"].notna()
        & (df["rainfall_mm"] >= 0)
        & (df["latitude"] >= KERALA_LAT[0]) & (df["latitude"] <= KERALA_LAT[1])
        & (df["longitude"] >= KERALA_LON[0]) & (df["longitude"] <= KERALA_LON[1])
    )
    df = df[valid]
    _log(log, "T8 Remove invalid values",
         "Dropped rows with unparseable dates, missing/negative rainfall or coordinates outside Kerala", before, len(df))
    return df


def t8b_remove_duplicate_readings(df, log):
    before = len(df)
    df = df.drop_duplicates(subset=["station", "date"], keep="first")
    _log(log, "T8b Remove duplicate station-days", "One reading per station per day; keeps the first", before, len(df))
    return df


# --------------------------------------------------------------------------
# STEP 6: TRANSFORM - Enrichment (Member 4)
# --------------------------------------------------------------------------
def t9_add_date_parts(df, log):
    before = len(df)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()
    df["day_of_week"] = df["date"].dt.day_name()
    _log(log, "T9 Split date into parts", "Year/month/weekday columns make monthly and trend analysis easy", before, len(df))
    return df


def t10_add_season(df, log):
    before = len(df)
    df["season"] = df["month"].map(SEASONS)
    _log(log, "T10 Create season column", "Kerala rainfall is driven by monsoon seasons, so season is a key category", before, len(df))
    return df


def t11_add_rainfall_category(df, log):
    before = len(df)
    df["rainfall_category"] = pd.cut(df["rainfall_mm"], bins=RAIN_BINS, labels=RAIN_LABELS, right=False).astype("string")
    _log(log, "T11 Create rainfall category", "IMD intensity classes (Very Light ... Extremely Heavy) for each reading", before, len(df))
    return df


def t12_add_station_totals_and_rank(df, log):
    before = len(df)
    df["station_total_rainfall_mm"] = df.groupby("station")["rainfall_mm"].transform("sum").round(2)
    station_totals = df.groupby("station")["rainfall_mm"].sum()
    rank = station_totals.rank(ascending=False, method="min").astype(int)
    df["station_rank"] = df["station"].map(rank)
    _log(log, "T12 Aggregation + ranking", "Station total rainfall and rank (1 = wettest) added to each row", before, len(df))
    return df


def t13_sort_records(df, log):
    before = len(df)
    df = df.sort_values(["station", "date"]).reset_index(drop=True)
    _log(log, "T13 Sort records", "Ordered by station then date for time-series use", before, len(df))
    return df


# --------------------------------------------------------------------------
# STEP 7: GENERATE REPORTS (Member 4)
# --------------------------------------------------------------------------
def generate_reports(df, log):
    """Build all analytical report tables and return as dictionary."""
    print("\n--- Generating Reports (Step 7) ---")
    reports = {}

    reports["cleaned_data.csv"] = df

    # 1. Summary Statistics
    summary = df["rainfall_mm"].describe().round(2).rename_axis("statistic").reset_index()
    summary.columns = ["statistic", "rainfall_mm"]
    extra_stats = pd.DataFrame({
        "statistic": ["stations", "districts", "first_date", "last_date"],
        "rainfall_mm": [
            df["station"].nunique(),
            df["district"].nunique(),
            df["date"].min().date(),
            df["date"].max().date()
        ],
    })
    reports["summary_statistics.csv"] = pd.concat([summary, extra_stats], ignore_index=True)

    # 2. District-Wise Report
    district = (df.groupby("district")
                .agg(stations=("station", "nunique"),
                     records=("rainfall_mm", "size"),
                     total_rainfall_mm=("rainfall_mm", "sum"),
                     avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                     max_daily_rainfall_mm=("rainfall_mm", "max"))
                .round(2).sort_values("avg_daily_rainfall_mm", ascending=False).reset_index())
    district["rank_by_avg_daily_rainfall"] = range(1, len(district) + 1)
    reports["district_wise_report.csv"] = district

    # 3. Monthly Report
    monthly = (df.groupby(["month", "month_name"])
               .agg(records=("rainfall_mm", "size"),
                    total_rainfall_mm=("rainfall_mm", "sum"),
                    avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                    max_daily_rainfall_mm=("rainfall_mm", "max"))
               .round(2).reset_index())
    reports["monthly_report.csv"] = monthly

    # 4. Seasonal Report
    seasonal = (df.groupby("season")
                .agg(records=("rainfall_mm", "size"),
                     avg_daily_rainfall_mm=("rainfall_mm", "mean"),
                     max_daily_rainfall_mm=("rainfall_mm", "max"))
                .round(2).sort_values("avg_daily_rainfall_mm", ascending=False).reset_index())
    reports["seasonal_report.csv"] = seasonal

    # 5. Rainfall Category Report
    category_counts = df["rainfall_category"].value_counts().reindex(RAIN_LABELS).fillna(0).astype(int)
    cat_df = category_counts.rename_axis("rainfall_category").reset_index(name="records")
    cat_df["percentage"] = (cat_df["records"] / cat_df["records"].sum() * 100).round(2)
    reports["rainfall_category_report.csv"] = cat_df

    # 6. Top 10 Rainiest Days
    cols = ["station", "district", "date", "rainfall_mm", "rainfall_category"]
    reports["top10_rainiest_days.csv"] = df.nlargest(10, "rainfall_mm")[cols].reset_index(drop=True)

    # 7. Top & Bottom 10 Stations
    station = (df.groupby(["station", "district"])
               .agg(records=("rainfall_mm", "size"),
                    total_rainfall_mm=("rainfall_mm", "sum"),
                    avg_daily_rainfall_mm=("rainfall_mm", "mean"))
               .round(2).reset_index())
    reports["top10_stations_by_avg_rainfall.csv"] = station.nlargest(10, "avg_daily_rainfall_mm").reset_index(drop=True)
    reports["bottom10_stations_by_avg_rainfall.csv"] = station.nsmallest(10, "avg_daily_rainfall_mm").reset_index(drop=True)

    # 8. Highest and Lowest Values
    hi = df.loc[df["rainfall_mm"].idxmax()]
    lo = df.loc[df["rainfall_mm"].idxmin()]
    reports["highest_lowest_values.csv"] = pd.DataFrame([
        {"type": "Highest", **{c: hi[c] for c in cols}},
        {"type": "Lowest", **{c: lo[c] for c in cols}},
    ])

    # 9. Transformation Log
    reports["transformation_log.csv"] = pd.DataFrame(log)

    for name, table in reports.items():
        print(f"  • {name}: {len(table)} rows")
    return reports


def transform(df):
    """Execute all cleaning and enrichment transformations, then generate reports."""
    print("\n=== STEP 6: TRANSFORM ===")
    validate_data(df)
    log = []
    print("\n--- Transformations ---")
    steps = (
        t1_rename_columns,
        t2_remove_duplicates,
        t3_drop_unwanted_columns,
        t4_standardize_text,
        t5_handle_missing_values,
        t6_convert_dates,
        t7_change_data_types,
        t8_remove_invalid_values,
        t8b_remove_duplicate_readings,
        t9_add_date_parts,
        t10_add_season,
        t11_add_rainfall_category,
        t12_add_station_totals_and_rank,
        t13_sort_records,
    )
    for step in steps:
        df = step(df, log)
    return generate_reports(df, log)


# --------------------------------------------------------------------------
# STEP 8: LOAD (Member 5)
# --------------------------------------------------------------------------
def load(datasets):
    """Save all reports to reports/ and the analysis-ready dataset to output/."""
    print("\n=== STEP 8: LOAD (Member 5) ===")

    for name, table in datasets.items():
        table.to_csv(f"reports/{name}", index=False)
        print(f"  Saved reports/{name}")

    datasets["cleaned_data.csv"].to_csv(OUTPUT_FILE, index=False)
    print(f"  Saved {OUTPUT_FILE}")


# --------------------------------------------------------------------------
# STEP 9: PIPELINE ORCHESTRATION (Member 5)
# --------------------------------------------------------------------------
def run_etl_pipeline():
    """Main function executing Extract -> Transform -> Load."""
    print("=====================================================")
    print(" KERALA RAINFALL ETL PIPELINE (5-MEMBER MINI PROJECT)")
    print("=====================================================")
    raw = extract()
    datasets = transform(raw)
    load(datasets)
    print("\n[SUCCESS] ETL pipeline finished successfully.")


# Execute the pipeline only when the program is run directly
if __name__ == "__main__":
    run_etl_pipeline()
