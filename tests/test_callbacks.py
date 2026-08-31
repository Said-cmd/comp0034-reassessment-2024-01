"""Unit tests for the callback logic - no browser, much faster than the Playwright tests."""
from summersports import processing
from summersports.callbacks import compute_outputs


def test_compute_outputs_with_no_filters_returns_all_sessions():
    # ARRANGE
    df = processing.load_data()

    # ACT
    _, _, _, table_data, summary = compute_outputs(df, None, None)

    # ASSERT
    assert "4,748 sessions" in summary
    assert len(table_data) > 0


def test_compute_outputs_filters_by_borough():
    # ARRANGE
    df = processing.load_data()

    # ACT
    _, _, _, _, summary = compute_outputs(df, ["Queens"], None)

    # ASSERT
    assert "4,748 sessions" not in summary


def test_compute_outputs_with_no_matching_data_returns_empty_state():
    # ARRANGE
    df = processing.load_data()

    # ACT
    _, _, _, table_data, summary = compute_outputs(df, ["Nonexistent Borough"], None)

    # ASSERT
    assert table_data == []
    assert "No sessions match" in summary


def test_suggested_sports_returns_expected_columns():
    # ARRANGE
    df = processing.load_data()

    # ACT
    suggestions = processing.suggested_sports_for_next_year(df, n=5)

    # ASSERT
    assert list(suggestions.columns) == ["sport", "trend_per_year", "latest_attendance"]
    assert len(suggestions) <= 5
