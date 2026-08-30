"""Register the callback that updates the charts and table."""
import plotly.express as px
from dash import Input, Output
from summersports import processing

def register_callbacks(app, df):
    @app.callback(
        Output("attendance-trend", "figure"),
        Output("attendance-by-borough", "figure"),
        Output("top-sports", "figure"),
        Output("park-table", "data"),
        Output("summary-stats", "children"),
        Input("borough-filter", "value"),
        Input("year-filter", "value"),
    )
    def update(boroughs, years):
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