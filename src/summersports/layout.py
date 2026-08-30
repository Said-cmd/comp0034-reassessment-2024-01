"""Build the dashboard layout."""
from dash import dash_table, dcc, html
from summersports import processing

def build_layout(df):
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
        dash_table.DataTable(id="park-table",
                              columns=[{"name": c, "id": c} for c in
                                       ["park", "total_attendance", "average_attendance", "sessions"]],
                              sort_action="native", page_size=13),
    ])