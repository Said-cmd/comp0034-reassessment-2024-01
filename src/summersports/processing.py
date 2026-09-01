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


def suggested_sports_for_next_year(
    df: pd.DataFrame, n: int = 5, min_years: int = 3, direction: str = "growing"
) -> pd.DataFrame:
    """Rank sports by attendance growth trend (linear fit per sport, across years).

    Excludes sports with fewer than min_years of data, since a line
    through only 2 points always fits perfectly. direction filters to
    only positive ("growing") or only negative ("declining") trends,
    rather than mixing both in one ranked list.

    Args:
        df: The full, unfiltered dataset.
        n: How many sports to return.
        min_years: Minimum distinct years of data required for a sport
            to be included. Defaults to 3.
        direction: "growing" returns only sports with a positive trend,
            highest first. "declining" returns only sports with a
            negative trend, steepest decline first.

    Returns:
        DataFrame with sport, trend_per_year, latest_attendance,
        years_of_data. May have fewer than n rows.

    Raises:
        ValueError: If direction is not "growing" or "declining".

    """
    if direction not in ("growing", "declining"):
        raise ValueError(f"direction must be 'growing' or 'declining', got {direction!r}")

    yearly = df.groupby(["sport", "year"])["attendance"].sum().reset_index()

    trends = []
    for sport, group in yearly.groupby("sport"):
        # a line can't be fit through fewer than 2 points, regardless of
        # what min_years the caller asks for
        if len(group) < max(min_years, 2):
            continue
        slope, _intercept = np.polyfit(group["year"], group["attendance"], 1)
        latest = group.sort_values("year").iloc[-1]["attendance"]
        trends.append({
            "sport": sport,
            "trend_per_year": round(float(slope), 1),
            "latest_attendance": int(latest),
            "years_of_data": len(group),
        })

    if not trends:
        return pd.DataFrame(
            columns=["sport", "trend_per_year", "latest_attendance", "years_of_data"]
        )

    trend_df = pd.DataFrame(trends)
    if direction == "growing":
        trend_df = trend_df[trend_df["trend_per_year"] > 0]
        trend_df = trend_df.sort_values("trend_per_year", ascending=False)
    else:
        trend_df = trend_df[trend_df["trend_per_year"] < 0]
        trend_df = trend_df.sort_values("trend_per_year", ascending=True)

    return trend_df.head(n)
