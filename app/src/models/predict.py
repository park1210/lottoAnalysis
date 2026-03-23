from __future__ import annotations

import numpy as np
import pandas as pd


def select_top6(values: np.ndarray) -> list[int]:
    top6_idx = np.argsort(values)[-6:]
    return sorted([i + 1 for i in top6_idx])


def probability_matrix_to_number_lists(probability_matrix: np.ndarray) -> list[list[int]]:
    return [select_top6(row) for row in probability_matrix]


def number_lists_to_binary_df(number_lists: list[list[int]], label_cols: list[str]) -> pd.DataFrame:
    binary = pd.DataFrame(0, index=range(len(number_lists)), columns=label_cols)
    for idx, nums in enumerate(number_lists):
        for num in nums:
            binary.loc[idx, f"y_{num}"] = 1
    return binary
