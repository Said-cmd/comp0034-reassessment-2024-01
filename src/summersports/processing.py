"""Load and clean the summer sports dataset."""
from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "summersports.csv"
COLUMNS = ["event_id", "date", "year", "month", "borough", "park", "sport", "attendance"]

def load_data():
    """Load the CSV and parse the date column."""
    df = pd.read_csv(CSV_PATH, header=None, names=COLUMNS)
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_filter_options(df):
    """Get the boroughs/years for the dropdowns."""
    return {
        "boroughs": sorted(df["borough"].unique()),
        "years": sorted(df["year"].unique()),
    }

def filter_data(df, boroughs, years):
    """Filter by borough and year, empty = no filter."""
    if boroughs:
        df = df[df["borough"].isin(boroughs)]
    if years:
        df = df[df["year"].isin(years)]
    return df

def attendance_by_month(df):
    """Group attendance by month, for the trend chart."""
    g = df.groupby(df["date"].dt.to_period("M"))["attendance"].sum().reset_index()
    g["date"] = g["date"].dt.to_timestamp()
    return g.sort_values("date")

def attendance_by_borough(df):
    """Group attendance by borough."""
    return df.groupby("borough")["attendance"].sum().reset_index().sort_values("attendance", ascending=False)

def top_sports(df, n=10):
    """Top n sports by attendance."""
    return df.groupby("sport")["attendance"].sum().reset_index().sort_values("attendance", ascending=False).head(n)

def park_summary(df):
    """Summary stats per park."""
    s = df.groupby("park").agg(total_attendance=("attendance", "sum"),
                                average_attendance=("attendance", "mean"),
                                sessions=("attendance", "count")).reset_index()
    s["average_attendance"] = s["average_attendance"].round(0).astype(int)
    return s.sort_values("total_attendance", ascending=False)