"""Unit tests for processing.py's data loading and filtering."""
import pytest

from summersports import processing


def test_load_data_raises_for_missing_file(tmp_path):
    # ARRANGE
    missing_path = tmp_path / "does_not_exist.csv"

    # ACT / ASSERT
    with pytest.raises(FileNotFoundError):
        processing.load_data(missing_path)


def test_load_data_raises_for_wrong_column_count(tmp_path):
    # ARRANGE: a file with only 3 columns, not the expected 8
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("1,2,3\n4,5,6\n")

    # ACT / ASSERT
    with pytest.raises(ValueError):
        processing.load_data(bad_csv)


@pytest.mark.parametrize("boroughs", [
    ["Queens"],
    ["Queens", "Brooklyn"],
    ["Staten Island"],
])
def test_filter_data_by_borough_returns_fewer_rows(boroughs):
    # ARRANGE
    df = processing.load_data()

    # ACT
    filtered = processing.filter_data(df, boroughs, None)

    # ASSERT: filtering to specific boroughs never returns more rows than
    # the full dataset, and every remaining row is one of the requested boroughs
    assert len(filtered) < len(df)
    assert set(filtered["borough"].unique()).issubset(set(boroughs))


def test_filter_data_with_no_filters_returns_all_rows():
    # ARRANGE
    df = processing.load_data()

    # ACT
    filtered = processing.filter_data(df, None, None)

    # ASSERT
    assert len(filtered) == len(df)
