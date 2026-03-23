from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "row_id",
    "round",
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    "bonus",
]


def validate_processed_columns(df: pd.DataFrame, required_columns: list[str] = REQUIRED_COLUMNS) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_number_ranges(df: pd.DataFrame) -> None:
    number_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "bonus"]
    for col in number_cols:
        invalid = ~df[col].between(1, 45)
        if invalid.any():
            raise ValueError(f"Column {col} contains values outside the 1-45 range")


def validate_unique_main_numbers(df: pd.DataFrame) -> None:
    number_cols = ["n1", "n2", "n3", "n4", "n5", "n6"]
    duplicates = df[number_cols].apply(lambda row: len(set(row)) != 6, axis=1)
    if duplicates.any():
        raise ValueError("Some rows contain duplicated main numbers")
