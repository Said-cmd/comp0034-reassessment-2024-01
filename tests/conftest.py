"""Fixture that runs the dash app for the browser tests."""
import pytest
from dash.testing.application_runners import ThreadedRunner
from summersports.main import create_app

@pytest.fixture(scope="session")
def dash_url():
    """Start the app once for the whole test run and give back its url."""
    runner = ThreadedRunner()
    runner.start(create_app())
    yield runner.url
    runner.stop()