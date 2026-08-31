"""Create and set up the app.

Run with: python src/summersports/main.py
"""
from dash import Dash

from summersports import processing
from summersports.callbacks import register_callbacks
from summersports.layout import build_layout


def create_app() -> Dash:
    """Build and configure the Dash app."""
    df = processing.load_data()
    suggestions = processing.suggested_sports_for_next_year(df)

    app = Dash(__name__)
    app.title = "Summer Sports Dashboard"
    app.layout = build_layout(df, suggestions)
    register_callbacks(app, df)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
