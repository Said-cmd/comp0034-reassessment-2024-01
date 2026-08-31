"""Build the dashboard layout."""
import pandas as pd
from dash import dash_table, dcc, html

from summersports import processing


def build_layout(df: pd.DataFrame, suggestions: pd.DataFrame) -> html.Div:
    """Build the app's HTML layout.

    Args:
        df: The full dataset, used to populate the dropdown filters.
        suggestions: Pre-computed future-events trend table (see
            processing.suggested_sports_for_next_year), rendered as a
            static section independent of the dropdown filters.

    """
    options = processing.get_filter_options(df)
    return html.Div([
        html.H1("Summer Sports Events Dashboard"),
        html.Div([
            dcc.Dropdown(id="borough-filter",
                         options=[{"label": b, "value": b} for b in options["boroughs"]],
                         multi=True, placeholder="All boroughs"),
            dcc.Dropdown(id="year-filter",
                         options=[{"label": str(y), "value": y} for y in options["years"]],
                         multi=True, placeholder="All years"),
        ]),
        html.Div(id="summary-stats"),
        dcc.Graph(id="attendance-trend"),
        dcc.Graph(id="attendance-by-borough"),
        dcc.Graph(id="top-sports"),
        dash_table.DataTable(
            id="park-table",
            columns=[
                {"name": c, "id": c}
                for c in ["park", "total_attendance", "average_attendance", "sessions"]
            ],
            sort_action="native", page_size=13,
        ),

        html.H2("Suggested sports for future years"),
        html.P(
            "Ranked by attendance growth trend (a linear fit across all "
            "available years for each sport). This section is independent "
            "of the filters above, since a future-years suggestion needs "
            "the full multi-year picture rather than one filtered slice."
        ),
        dash_table.DataTable(
            id="suggestions-table",
            columns=[{"name": c, "id": c} for c in
                     ["sport", "trend_per_year", "latest_attendance"]],
            data=suggestions.to_dict("records"),
            sort_action="native",
        ),
    ])
