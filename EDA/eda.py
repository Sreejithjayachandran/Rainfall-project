"""
Kerala Rainfall Meteorological Data - Exploratory Data Analysis (EDA) Module
=============================================================================
Provides data loading, styling, and plotting routines powered by Matplotlib
and Seaborn, matching the project template.

Usage in Notebook:
    import sys
    sys.path.insert(0, ".")
    sys.path.insert(0, "..")
    import matplotlib.pyplot as plt
    import seaborn as sns
    from IPython.display import Image, display
    import eda

    eda._style()
    df = eda.load_data()
    eda.OUT = eda.Path("output/eda")
    display(Image(eda.plot_overview(df)))
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Export Path so `eda.Path(...)` works directly in notebook
Path = Path

# Default output directory
OUT = Path("output/eda")


def _style():
    """Configure publication-grade visualization aesthetics with Seaborn & Matplotlib."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.facecolor"] = "#ffffff"
    plt.rcParams["axes.facecolor"] = "#fafafa"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#e5e5e5"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.7
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["axes.labelweight"] = "bold"


def load_data(path=None):
    """
    Load analysis-ready rainfall dataset with smart path fallback across
    local environments, Colab (/content/), and parent folders.
    """
    if path is not None:
        p = Path(path)
        if p.exists():
            return pd.read_csv(p, parse_dates=["date_time", "date"])

    candidates = [
        Path("output/analysis_ready_rainfall.csv"),
        Path("analysis_ready_rainfall.csv"),
        Path("../ETL/Rainfall-project/output/analysis_ready_rainfall.csv"),
        Path("ETL/Rainfall-project/output/analysis_ready_rainfall.csv"),
        Path("../output/analysis_ready_rainfall.csv"),
        Path("/content/analysis_ready_rainfall.csv"),
    ]

    for c in candidates:
        if c.exists():
            return pd.read_csv(c, parse_dates=["date_time", "date"])

    raise FileNotFoundError(
        "Could not locate analysis_ready_rainfall.csv. Please verify file path or run ETL pipeline."
    )


# -----------------------------------------------------------------------------
# 1. Overview: Intensity Distribution & Rainy Days
# -----------------------------------------------------------------------------
def plot_overview(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    imd_order = ["Very Light", "Light", "Moderate", "Heavy", "Very Heavy", "Extremely Heavy"]
    cat_counts = df["rainfall_category"].value_counts().reindex(imd_order).fillna(0).reset_index()
    cat_counts.columns = ["rainfall_category", "count"]
    cat_counts["pct"] = (cat_counts["count"] / cat_counts["count"].sum() * 100).round(1)

    palette = ["#ccece6", "#66c2a4", "#2ca25f", "#fe9929", "#d95f0e", "#990000"]
    sns.barplot(
        data=cat_counts,
        x="rainfall_category",
        y="count",
        palette=palette,
        edgecolor="#333333",
        linewidth=0.7,
        ax=axes[0]
    )
    axes[0].set_title("1. Distribution by IMD Rainfall Intensity Categories")
    axes[0].set_xlabel("IMD Category")
    axes[0].set_ylabel("Observation Count")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].grid(axis="y")

    for idx, row in cat_counts.iterrows():
        axes[0].annotate(
            f"{int(row['count']):,}\n({row['pct']}%)",
            xy=(idx, row["count"]),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold"
        )

    rainy_counts = (df["rainfall_mm"] >= 2.5).value_counts()
    labels = ["Rainy Day (>= 2.5 mm)", "Trace / Very Light (< 2.5 mm)"]
    vals = [rainy_counts.get(True, 0), rainy_counts.get(False, 0)]
    axes[1].pie(
        vals,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=["#1f78b4", "#a6cee3"],
        explode=(0.04, 0),
        wedgeprops={"edgecolor": "#333333", "linewidth": 0.8},
        textprops={"fontsize": 10, "fontweight": "bold"}
    )
    axes[1].set_title("Precipitation Day Share (IMD 2.5 mm Threshold)")

    plt.tight_layout()
    out_file = OUT / "1_overview.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# -----------------------------------------------------------------------------
# 2. Monthly Rainfall Progression Over Time
# -----------------------------------------------------------------------------
def plot_monthly_rainfall(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = df.groupby(["month", "month_name"]).agg(
        total_mm=("rainfall_mm", "sum"),
        avg_mm=("rainfall_mm", "mean")
    ).reset_index().sort_values("month")
    monthly["total_k_mm"] = monthly["total_mm"] / 1000

    fig, ax1 = plt.subplots(figsize=(13, 6))

    sns.barplot(
        data=monthly,
        x="month_name",
        y="total_k_mm",
        color="#2b8cbe",
        edgecolor="#333333",
        linewidth=0.7,
        ax=ax1,
        label="Total Rainfall (x1,000 mm)"
    )
    ax1.set_title("2. Monthly Rainfall Volume and Daily Precipitation Rate (2021)")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Cumulative Recorded Rainfall (Thousand mm)", color="#2b8cbe")
    ax1.tick_params(axis="y", labelcolor="#2b8cbe")
    ax1.tick_params(axis="x", rotation=30)
    ax1.grid(axis="y")

    ax2 = ax1.twinx()
    sns.lineplot(
        data=monthly,
        x="month_name",
        y="avg_mm",
        color="#e41a1c",
        marker="o",
        linewidth=2.5,
        markersize=8,
        ax=ax2,
        label="Mean Daily Rainfall (mm/day)"
    )
    ax2.set_ylabel("Mean Daily Rainfall (mm/day)", color="#e41a1c")
    ax2.tick_params(axis="y", labelcolor="#e41a1c")
    ax2.grid(False)

    for idx, row in monthly.iterrows():
        ax1.annotate(
            f"{row['total_k_mm']:.1f}k",
            xy=(idx, row["total_k_mm"]),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5
        )

    plt.tight_layout()
    out_file = OUT / "2_monthly_rainfall.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_monthly_bookings = plot_monthly_rainfall


# -----------------------------------------------------------------------------
# 3. Monsoon Seasonality
# -----------------------------------------------------------------------------
def plot_seasonality(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    season_order = ["Winter", "Pre-Monsoon", "Southwest Monsoon", "Post-Monsoon"]
    season_agg = df.groupby("season").agg(
        total_mm=("rainfall_mm", "sum"),
        avg_mm=("rainfall_mm", "mean")
    ).reindex(season_order).reset_index()
    season_agg["total_k_mm"] = season_agg["total_mm"] / 1000

    palette = ["#a6bddb", "#74c476", "#08519c", "#fe9929"]
    sns.barplot(
        data=season_agg,
        x="season",
        y="total_k_mm",
        palette=palette,
        edgecolor="#333333",
        linewidth=0.8,
        ax=axes[0]
    )
    axes[0].set_title("3. Cumulative Rainfall by Meteorological Season")
    axes[0].set_xlabel("Season")
    axes[0].set_ylabel("Total Recorded Rainfall (Thousand mm)")
    axes[0].tick_params(axis="x", rotation=15)
    axes[0].grid(axis="y")

    total_sum = season_agg["total_mm"].sum()
    for idx, row in season_agg.iterrows():
        pct = (row["total_mm"] / total_sum) * 100
        axes[0].annotate(
            f"{row['total_k_mm']:.1f}k mm\n({pct:.1f}%)",
            xy=(idx, row["total_k_mm"]),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )

    sns.barplot(
        data=season_agg,
        y="season",
        x="avg_mm",
        palette=palette,
        edgecolor="#333333",
        linewidth=0.8,
        ax=axes[1]
    )
    axes[1].set_title("Mean Daily Precipitation Rate by Season")
    axes[1].set_xlabel("Mean Daily Rainfall (mm/day)")
    axes[1].set_ylabel("Season")
    axes[1].grid(axis="x")

    for idx, row in season_agg.iterrows():
        axes[1].annotate(
            f"{row['avg_mm']:.1f} mm/day",
            xy=(row["avg_mm"] + 0.3, idx),
            va="center",
            fontsize=9,
            fontweight="bold"
        )

    plt.tight_layout()
    out_file = OUT / "3_seasonality.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_price_seasonality = plot_seasonality


# -----------------------------------------------------------------------------
# 4. Numerical Distributions
# -----------------------------------------------------------------------------
def plot_distributions(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    clipped = df[df["rainfall_mm"] <= 100]["rainfall_mm"]
    sns.histplot(
        clipped,
        bins=50,
        kde=True,
        color="#41b6c4",
        edgecolor="#225ea8",
        linewidth=0.7,
        ax=axes[0],
        line_kws={"linewidth": 2, "color": "#081d58"}
    )
    axes[0].set_title("4. Daily Rainfall Distribution with KDE (0–100 mm Range)")
    axes[0].set_xlabel("Daily Rainfall (mm)")
    axes[0].set_ylabel("Frequency")
    axes[0].axvline(
        df["rainfall_mm"].median(),
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Median: {df['rainfall_mm'].median():.1f} mm"
    )
    axes[0].axvline(
        df["rainfall_mm"].mean(),
        color="black",
        linestyle="-",
        linewidth=1.5,
        label=f"Mean: {df['rainfall_mm'].mean():.1f} mm"
    )
    axes[0].legend(loc="upper right")
    axes[0].grid(True)

    sns.boxplot(
        x=df["rainfall_mm"],
        ax=axes[1],
        color="#c7e9b4",
        flierprops=dict(marker="o", markerfacecolor="#e31a1c", markersize=3, alpha=0.5)
    )
    axes[1].set_xscale("log")
    axes[1].set_title("Rainfall Spread & Outlier Extreme Deluges (Log Scale)")
    axes[1].set_xlabel("Rainfall (mm) [Log Scale]")
    axes[1].grid(True, which="both")

    plt.tight_layout()
    out_file = OUT / "4_distributions.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# -----------------------------------------------------------------------------
# 5. District-Wise Rainfall Spread
# -----------------------------------------------------------------------------
def plot_rainfall_by_district(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    dist_agg = df.groupby("district").agg(
        total_mm=("rainfall_mm", "sum"),
        avg_mm=("rainfall_mm", "mean")
    ).reset_index()
    dist_agg["total_k_mm"] = dist_agg["total_mm"] / 1000

    dist_total = dist_agg.sort_values("total_k_mm", ascending=True)
    sns.barplot(
        data=dist_total,
        x="total_k_mm",
        y="district",
        palette="Blues_r",
        edgecolor="#081d58",
        linewidth=0.7,
        ax=axes[0]
    )
    axes[0].set_title("5. Cumulative Recorded Rainfall by District")
    axes[0].set_xlabel("Total Rainfall (Thousand mm)")
    axes[0].set_ylabel("District")
    axes[0].grid(axis="x")

    for idx, row in dist_total.reset_index(drop=True).iterrows():
        axes[0].annotate(f"{row['total_k_mm']:.1f}k", xy=(row["total_k_mm"] + 2, idx), va="center", fontsize=8.5)

    dist_avg = dist_agg.sort_values("avg_mm", ascending=True)
    sns.barplot(
        data=dist_avg,
        x="avg_mm",
        y="district",
        palette="Greens_r",
        edgecolor="#005824",
        linewidth=0.7,
        ax=axes[1]
    )
    axes[1].set_title("Mean Daily Precipitation Rate by District")
    axes[1].set_xlabel("Mean Daily Rainfall (mm/day)")
    axes[1].set_ylabel("")
    axes[1].grid(axis="x")

    for idx, row in dist_avg.reset_index(drop=True).iterrows():
        axes[1].annotate(f"{row['avg_mm']:.1f} mm", xy=(row["avg_mm"] + 0.3, idx), va="center", fontsize=8.5)

    plt.tight_layout()
    out_file = OUT / "5_district_spread.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_price_by_hotel = plot_rainfall_by_district


# -----------------------------------------------------------------------------
# 6. Extreme Rainfall Events & Deluges
# -----------------------------------------------------------------------------
def plot_extreme_events(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    top15 = df.nlargest(15, "rainfall_mm")[
        ["station", "district", "date", "rainfall_mm", "rainfall_category", "season"]
    ].copy().reset_index(drop=True)

    top15["event_label"] = [
        f"{row['station']} ({row['district'])}\n{row['date'].strftime('%d %b %Y')}"
        if hasattr(row['date'], 'strftime') else f"{row['station']} ({row['district']})\n{row['date']}"
        for _, row in top15.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(13, 7))
    sns.barplot(
        data=top15,
        x="rainfall_mm",
        y="event_label",
        palette="Reds_r",
        edgecolor="#67001f",
        linewidth=0.8,
        ax=ax
    )
    ax.set_title("6. Top 15 Heaviest Single-Day Deluges Recorded in Kerala (Extreme Weather)")
    ax.set_xlabel("Single-Day Rainfall (mm)")
    ax.set_ylabel("Rainfall Station & Date")
    ax.grid(axis="x")

    for idx, row in top15.iterrows():
        w = row["rainfall_mm"]
        ax.annotate(
            f"{w:.1f} mm",
            xy=(w + 3, idx),
            va="center",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_xlim(0, max(top15["rainfall_mm"]) * 1.15)
    plt.tight_layout()
    out_file = OUT / "6_extreme_deluges.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_cancel_lead_time = plot_extreme_events


# -----------------------------------------------------------------------------
# 7. Spatial Patterns
# -----------------------------------------------------------------------------
def plot_spatial_patterns(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    station_geo = df.groupby(["station", "district"]).agg(
        lat=("latitude", "mean"),
        lon=("longitude", "mean"),
        avg_rain=("rainfall_mm", "mean"),
        total_rain=("rainfall_mm", "sum")
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.scatterplot(
        data=station_geo,
        x="lon",
        y="lat",
        hue="avg_rain",
        size="total_rain",
        palette="viridis",
        sizes=(40, 300),
        edgecolor="#333333",
        linewidth=0.8,
        alpha=0.85,
        ax=ax
    )

    ax.set_title("7. Spatial Distribution of Rain-Gauge Stations Across Kerala\n(Seaborn Scatter: Hue = Daily Rate, Size = Total Volume)")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(True)

    wettest = station_geo.loc[station_geo["avg_rain"].idxmax()]
    ax.annotate(
        f"Wettest: {wettest['station']} ({wettest['avg_rain']:.1f} mm/d)",
        xy=(wettest["lon"], wettest["lat"]),
        xytext=(wettest["lon"] + 0.15, wettest["lat"] + 0.15),
        arrowprops=dict(facecolor="red", shrink=0.05, width=1, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="darkred"
    )

    plt.tight_layout()
    out_file = OUT / "7_spatial_patterns.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_cancel_segments = plot_spatial_patterns


# -----------------------------------------------------------------------------
# 8. River Basin & Catchment Distribution
# -----------------------------------------------------------------------------
def plot_river_basins(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    basin_agg = df[df["basin"] != "Unknown"].groupby("basin").agg(
        total_mm=("rainfall_mm", "sum"),
        records=("rainfall_mm", "count")
    ).reset_index().sort_values("total_mm", ascending=False)
    basin_agg["total_k_mm"] = basin_agg["total_mm"] / 1000

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=basin_agg,
        x="total_k_mm",
        y="basin",
        palette="mako",
        edgecolor="#08519c",
        linewidth=0.7,
        ax=ax
    )
    ax.set_title("8. Precipitation Capture Across Major River Catchments")
    ax.set_xlabel("Total Monitored Rainfall (Thousand mm)")
    ax.set_ylabel("River Basin")
    ax.grid(axis="x")

    for idx, row in basin_agg.reset_index(drop=True).iterrows():
        ax.annotate(
            f"{row['total_k_mm']:.1f}k mm",
            xy=(row["total_k_mm"] + 2, idx),
            va="center",
            fontsize=9
        )

    plt.tight_layout()
    out_file = OUT / "8_river_basins.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_cancel_signals = plot_river_basins


# -----------------------------------------------------------------------------
# 9. Station-Level Variations
# -----------------------------------------------------------------------------
def plot_station_performance(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    station_stats = df.groupby(["station", "district"]).agg(
        avg_mm=("rainfall_mm", "mean"),
        total_mm=("rainfall_mm", "sum")
    ).reset_index()

    top10 = station_stats.nlargest(10, "avg_mm").sort_values("avg_mm", ascending=False).reset_index(drop=True)
    bottom10 = station_stats.nsmallest(10, "avg_mm").sort_values("avg_mm", ascending=True).reset_index(drop=True)

    top10["label"] = [f"{s} ({d})" for s, d in zip(top10["station"], top10["district"])]
    bottom10["label"] = [f"{s} ({d})" for s, d in zip(bottom10["station"], bottom10["district"])]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    sns.barplot(
        data=top10,
        x="avg_mm",
        y="label",
        palette="Blues_r",
        edgecolor="#08589e",
        ax=axes[0]
    )
    axes[0].set_title("9. Top 10 Wettest Stations (by Daily Average)")
    axes[0].set_xlabel("Mean Daily Rainfall (mm/day)")
    axes[0].set_ylabel("")
    axes[0].grid(axis="x")
    for idx, row in top10.iterrows():
        axes[0].annotate(f"{row['avg_mm']:.1f} mm", xy=(row["avg_mm"] + 0.3, idx), va="center", fontsize=8.5)

    sns.barplot(
        data=bottom10,
        x="avg_mm",
        y="label",
        palette="Oranges_r",
        edgecolor="#b30000",
        ax=axes[1]
    )
    axes[1].set_title("Top 10 Driest Stations (by Daily Average)")
    axes[1].set_xlabel("Mean Daily Rainfall (mm/day)")
    axes[1].set_ylabel("")
    axes[1].grid(axis="x")
    for idx, row in bottom10.iterrows():
        axes[1].annotate(f"{row['avg_mm']:.1f} mm", xy=(row["avg_mm"] + 0.2, idx), va="center", fontsize=8.5)

    plt.tight_layout()
    out_file = OUT / "9_station_performance.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)


# Template alias
plot_revenue = plot_station_performance


# -----------------------------------------------------------------------------
# 10. Correlation Matrix
# -----------------------------------------------------------------------------
def plot_correlation(df):
    _style()
    OUT.mkdir(parents=True, exist_ok=True)
    numeric_cols = ["rainfall_mm", "latitude", "longitude", "month", "station_rank", "station_total_rainfall_mm"]
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(8.5, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.8,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )
    ax.set_title("10. Feature Correlation Matrix (Pearson)", pad=15)
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    out_file = OUT / "10_correlation.png"
    plt.savefig(out_file, dpi=200, bbox_inches="tight")
    plt.close()
    return str(out_file)
