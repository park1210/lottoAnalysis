import pytest

from app.src.data.preprocess import preprocess_lotto_data
from app.src.data.validate_data import (
    validate_number_ranges,
    validate_processed_columns,
    validate_unique_main_numbers,
)


def test_preprocess_lotto_data_renames_columns_and_sorts_by_round(raw_df):
    processed = preprocess_lotto_data(raw_df)

    assert list(processed.columns[:12]) == [
        "row_id",
        "round",
        "n1",
        "n2",
        "n3",
        "n4",
        "n5",
        "n6",
        "bonus",
        "rank_text",
        "winner_count",
        "prize_amount",
    ]
    assert processed["round"].tolist() == [101, 102]


def test_preprocess_lotto_data_creates_expected_derived_columns(raw_df):
    processed = preprocess_lotto_data(raw_df)
    first_row = processed.iloc[0]

    assert first_row["numbers"] == "10,11,12,13,14,15"
    assert first_row["sum_main"] == 75
    assert first_row["odd_count"] == 3
    assert first_row["even_count"] == 3
    assert first_row["low_count"] == 6
    assert first_row["high_count"] == 0


def test_preprocess_lotto_data_cleans_numeric_text_fields(raw_df):
    processed = preprocess_lotto_data(raw_df)
    first_row = processed.iloc[0]

    assert first_row["rank_text"] == "1등"
    assert first_row["winner_count"] == 3
    assert first_row["prize_amount"] == 2500


def test_validate_processed_columns_passes_for_valid_frame(raw_df):
    processed = preprocess_lotto_data(raw_df)
    validate_processed_columns(processed)


def test_validate_processed_columns_raises_for_missing_column(raw_df):
    processed = preprocess_lotto_data(raw_df).drop(columns=["bonus"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_processed_columns(processed)


def test_validate_number_ranges_raises_for_invalid_number(raw_df):
    processed = preprocess_lotto_data(raw_df)
    processed.loc[0, "bonus"] = 99

    with pytest.raises(ValueError, match="outside the 1-45 range"):
        validate_number_ranges(processed)


def test_validate_unique_main_numbers_raises_for_duplicates(raw_df):
    processed = preprocess_lotto_data(raw_df)
    processed.loc[0, ["n1", "n2", "n3", "n4", "n5", "n6"]] = [1, 1, 2, 3, 4, 5]

    with pytest.raises(ValueError, match="duplicated main numbers"):
        validate_unique_main_numbers(processed)
