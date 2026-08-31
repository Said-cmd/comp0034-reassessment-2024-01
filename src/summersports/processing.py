"""Load, validate, and aggregate the summer sports dataset."""
from pathlib import Path

import numpy as np
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "summersports.csv"
COLUMNS = ["event_id", "date", "year", "month", "borough", "park", "sport", "attendance"]


def load_data(path: Path = CSV_PATH) -> pd.DataFrame:
    """Load the CSV, validate its shape, and parse the date column.

    Args:
        path: Location of the dataset. Defaults to the packaged CSV.

    Returns:
        A DataFrame with parsed dates and the expected columns.

    Raises:
        FileNotFoundError: If no file exists at ``path``.
        ValueError: If the file can't be parsed, or is missing an
            expected column, or the date column can't be converted.

    """
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Check the src/data folder.")

    try:
        df = pd.read_csv(path, header=None)
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse dataset at {path}: {exc}") from exc

    if df.shape[1] != len(COLUMNS):
        raise ValueError(
            f"Expected {len(COLUMNS)} columns but found {df.shape[1]} in {path}. "
            "Check the file hasn't been truncated or re-formatted."
        )
    df.columns = COLUMNS

    try:
        df["date"] = pd.to_datetime(df["date"])
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Could not parse the date column: {exc}") from exc

    # drop any rows where attendance itself failed to load, rather than
    # letting a NaN silently break later sums/averages
    df = df.dropna(subset=["attendance"])

    return df


def get_filter_options(df: pd.DataFrame) -> dict[str, list]:
    """Get the boroughs/years for the dropdowns."""
    return {
        "boroughs": sorted(df["borough"].unique()),
        "years": sorted(df["year"].unique()),
    }


def filter_data(
    df: pd.DataFrame, boroughs: list[str] | None, years: list[int] | None
) -> pd.DataFrame:
    """Filter by borough and year, empty = no filter."""
    if boroughs:
        df = df[df["borough"].isin(boroughs)]
    if years:
        df = df[df["year"].isin(years)]
    return df


def attendance_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Group attendance by month, for the trend chart."""
    g = df.groupby(df["date"].dt.to_period("M"))["attendance"].sum().reset_index()
    g["date"] = g["date"].dt.to_timestamp()
    return g.sort_values("date")


def attendance_by_borough(df: pd.DataFrame) -> pd.DataFrame:
    """Group attendance by borough."""
    return (
        df.groupby("borough")["attendance"]
        .sum()
        .reset_index()
        .sort_values("attendance", ascending=False)
    )


def top_sports(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top n sports by attendance."""
    return (
        df.groupby("sport")["attendance"]
        .sum()
        .reset_index()
        .sort_values("attendance", ascending=False)
        .head(n)
    )


def park_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summary stats per park."""
    s = df.groupby("park").agg(
        total_attendance=("attendance", "sum"),
        average_attendance=("attendance", "mean"),
        sessions=("attendance", "count"),
    ).reset_index()
    s["average_attendance"] = s["average_attendance"].round(0).astype(int)
    return s.sort_values("total_attendance", ascending=False)


def suggested_sports_for_next_year(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Rank sports by attendance growth trend (linear fit per sport, across years).

    Uses the full dataset rather than the borough/year filters, since a
    multi-year trend needs more than one filtered slice. Sports with
    only one year of data are skipped.

    Args:
        df: The full, unfiltered dataset.
        n: How many top-trending sports to return.

    Returns:
        DataFrame with sport, trend_per_year, latest_attendance, sorted
        by trend_per_year descending.

    """
    yearly = df.groupby(["sport", "year"])["attendance"].sum().reset_index()

    trends = []
    for sport, group in yearly.groupby("sport"):
        if len(group) < 2:
            continue
        slope, _intercept = np.polyfit(group["year"], group["attendance"], 1)
        latest = group.sort_values("year").iloc[-1]["attendance"]
        trends.append({
            "sport": sport,
            "trend_per_year": round(float(slope), 1),
            "latest_attendance": int(latest),
        })

    if not trends:
        return pd.DataFrame(columns=["sport", "trend_per_year", "latest_attendance"])

    trend_df = pd.DataFrame(trends).sort_values("trend_per_year", ascending=False)
    return trend_df.head(n)
