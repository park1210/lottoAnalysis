from __future__ import annotations

import numpy as np
import pandas as pd


NUMBER_COLS = ["n1", "n2", "n3", "n4", "n5", "n6"]


def build_one_hot_matrix(df: pd.DataFrame, number_cols: list[str] = NUMBER_COLS) -> pd.DataFrame:
    one_hot = pd.DataFrame(0, index=df.index, columns=range(1, 46))

    for col in number_cols:
        for i, num in enumerate(df[col]):
            one_hot.loc[i, int(num)] = 1

    return one_hot


def calculate_correlation_matrix(one_hot: pd.DataFrame) -> pd.DataFrame:
    return one_hot.corr()


def build_upper_triangle_mask(corr: pd.DataFrame) -> np.ndarray:
    return np.triu(np.ones_like(corr, dtype=bool))


def calculate_consecutive_overlap(draws: np.ndarray) -> pd.Series:
    return pd.Series(
        [len(set(draws[i - 1]) & set(draws[i])) for i in range(1, len(draws))]
    )
