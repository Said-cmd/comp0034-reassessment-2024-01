"""Create and set up the app."""
from dash import Dash
from summersports import processing
from summersports.callbacks import register_callbacks
from summersports.layout import build_layout

def create_app():
    df = processing.load_data()
    app = Dash(__name__)
    app.title = "Summer Sports Dashboard"
    app.layout = build_layout(df)
    register_callbacks(app, df)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)