from __future__ import annotations

import pandas as pd


NUMBER_COLS = ["n1", "n2", "n3", "n4", "n5", "n6"]


def flatten_main_numbers(df: pd.DataFrame, number_cols: list[str] = NUMBER_COLS) -> pd.Series:
    return pd.Series(df[number_cols].to_numpy().ravel())


def calculate_number_frequency(df: pd.DataFrame, number_cols: list[str] = NUMBER_COLS) -> pd.Series:
    numbers = flatten_main_numbers(df, number_cols=number_cols)
    return numbers.value_counts().sort_index()


def calculate_bonus_frequency(df: pd.DataFrame, bonus_col: str = "bonus") -> pd.Series:
    return df[bonus_col].value_counts().sort_index()


def calculate_expected_main_frequency(df: pd.DataFrame) -> float:
    return len(df) * 6 / 45


def calculate_expected_bonus_frequency(df: pd.DataFrame) -> float:
    return len(df) / 45


def calculate_odd_even_distribution(df: pd.DataFrame, odd_col: str = "odd_count") -> pd.Series:
    return df[odd_col].value_counts().sort_index()


def calculate_low_high_distribution(df: pd.DataFrame, low_col: str = "low_count") -> pd.Series:
    return df[low_col].value_counts().sort_index()


def calculate_sum_distribution(df: pd.DataFrame, sum_col: str = "sum_main") -> pd.Series:
    return df[sum_col]


def calculate_round_sum_trend(df: pd.DataFrame, round_col: str = "round", sum_col: str = "sum_main") -> pd.DataFrame:
    return df[[round_col, sum_col]].copy()


def categorize_number_ranges(df: pd.DataFrame, number_cols: list[str] = NUMBER_COLS) -> pd.Series:
    numbers = flatten_main_numbers(df, number_cols=number_cols)
    return pd.cut(
        numbers,
        bins=[0, 10, 20, 30, 40, 45],
        labels=["1-10", "11-20", "21-30", "31-40", "41-45"],
        include_lowest=True,
    )


def build_frequency_comparison_frame(real_freq: pd.Series, random_freq: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame({"real": real_freq, "random_mean": random_freq})
    frame["deviation_from_random_mean"] = frame["real"] - frame["random_mean"]
    return frame
