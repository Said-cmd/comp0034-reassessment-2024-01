"""Register the callback that updates the charts and table."""
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output

from summersports import processing


def compute_outputs(
    df: pd.DataFrame, boroughs: list[str] | None, years: list[int] | None
) -> tuple[go.Figure, go.Figure, go.Figure, list[dict[str, Any]], str]:
    """Filter the data and build every chart/table/summary for the selection.

    Split out from the callback so it can be unit tested without a
    running app or browser (see tests/test_callbacks.py).

    Args:
        df: The full, unfiltered dataset.
        boroughs: Selected boroughs from the dropdown, or None/empty for all.
        years: Selected years from the dropdown, or None/empty for all.

    Returns:
        A tuple of (trend_fig, borough_fig, sports_fig, table_data, summary_text).

    """
    filtered = processing.filter_data(df, boroughs, years)
    if filtered.empty:
        # no rows match the current filters
        empty = px.scatter(title="No data for this selection")
        return empty, empty, empty, [], "No sessions match these filters."

    trend_fig = px.line(processing.attendance_by_month(filtered), x="date", y="attendance",
                         title="Monthly attendance trend", markers=True)
    borough_fig = px.bar(processing.attendance_by_borough(filtered), x="borough", y="attendance",
                          title="Total attendance by borough")
    sports_fig = px.bar(processing.top_sports(filtered), x="attendance", y="sport",
                         orientation="h", title="Top 10 sports by attendance")

    table_data = processing.park_summary(filtered).to_dict("records")
    summary = f"{len(filtered):,} sessions | {int(filtered['attendance'].sum()):,} total attendance"

    return trend_fig, borough_fig, sports_fig, table_data, summary


def register_callbacks(app: Dash, df: pd.DataFrame) -> None:
    """Wire the filters to the charts and table."""

    @app.callback(
        Output("attendance-trend", "figure"),
        Output("attendance-by-borough", "figure"),
        Output("top-sports", "figure"),
        Output("park-table", "data"),
        Output("summary-stats", "children"),
        Input("borough-filter", "value"),
        Input("year-filter", "value"),
    )
    def update(boroughs: list[str] | None, years: list[int] | None):
        return compute_outputs(df, boroughs, years)
