"""Build the dashboard layout."""
import pandas as pd
from dash import dash_table, dcc, html

from summersports import processing


def build_layout(df: pd.DataFrame, growing: pd.DataFrame, declining: pd.DataFrame) -> html.Div:
    """Build the app's HTML layout.

    Args:
        df: The full dataset, used to populate the dropdown filters.
        growing: Sports with a positive attendance trend (see
            processing.suggested_sports_for_next_year), rendered as a
            static section independent of the dropdown filters.
        declining: Sports with a negative attendance trend, same source
            function called with direction="declining".

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

        html.H2("Sports trending upward"),
        html.P(
            "Ranked by attendance growth trend (a linear fit across all "
            "available years for each sport with at least 3 years of "
            "data). Independent of the filters above, since a trend "
            "needs the full multi-year picture. Only sports with a "
            "genuinely positive trend appear here."
        ),
        dash_table.DataTable(
            id="suggestions-table",
            columns=[{"name": c, "id": c} for c in
                     ["sport", "trend_per_year", "latest_attendance", "years_of_data"]],
            data=growing.to_dict("records"),
            sort_action="native",
        ),

        html.H2("Sports trending downward"),
        html.P(
            "The same method applied in the opposite direction. Two of "
            "the largest programmes by attendance appear at the top of "
            "this list, which is worth the manager's attention even "
            "though it isn't a 'suggestion' in the usual sense."
        ),
        dash_table.DataTable(
            id="declining-table",
            columns=[{"name": c, "id": c} for c in
                     ["sport", "trend_per_year", "latest_attendance", "years_of_data"]],
            data=declining.to_dict("records"),
            sort_action="native",
        ),
    ])
