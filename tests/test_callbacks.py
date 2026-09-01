"""Unit tests for the callback logic - no browser, much faster than the Playwright tests."""
import pytest

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
    assert list(suggestions.columns) == [
        "sport", "trend_per_year", "latest_attendance", "years_of_data"
    ]
    assert len(suggestions) <= 5


def test_suggested_sports_excludes_sparse_data():
    # ARRANGE
    df = processing.load_data()

    # ACT
    suggestions = processing.suggested_sports_for_next_year(df, n=60, min_years=3)

    # ASSERT: every returned sport has at least 3 years of data, not just 2
    assert (suggestions["years_of_data"] >= 3).all()


def test_suggested_sports_min_years_is_configurable():
    # ARRANGE
    df = processing.load_data()

    # ACT
    lenient = processing.suggested_sports_for_next_year(df, n=60, min_years=1)
    strict = processing.suggested_sports_for_next_year(df, n=60, min_years=3)

    # ASSERT: a lower bar includes at least as many sports as a stricter one
    assert len(lenient) >= len(strict)


def test_suggested_sports_growing_returns_only_positive_trends():
    # ARRANGE
    df = processing.load_data()

    # ACT
    growing = processing.suggested_sports_for_next_year(df, n=60, direction="growing")

    # ASSERT
    assert (growing["trend_per_year"] > 0).all()


def test_suggested_sports_declining_returns_only_negative_trends():
    # ARRANGE
    df = processing.load_data()

    # ACT
    declining = processing.suggested_sports_for_next_year(df, n=60, direction="declining")

    # ASSERT
    assert (declining["trend_per_year"] < 0).all()


def test_suggested_sports_invalid_direction_raises_value_error():
    # ARRANGE
    df = processing.load_data()

    # ACT / ASSERT
    with pytest.raises(ValueError):
        processing.suggested_sports_for_next_year(df, direction="sideways")
