import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def label_cols():
    return [f"y_{i}" for i in range(1, 46)]


@pytest.fixture
def raw_df():
    return pd.DataFrame(
        [
            [2, 102, 1, 2, 3, 4, 5, 6, 7, " 1등 ", "10명", "1,000원"],
            [1, 101, 10, 11, 12, 13, 14, 15, 16, " 1등 ", "3명", "2,500원"],
        ],
        columns=[f"raw_{i}" for i in range(12)],
    )


@pytest.fixture
def clean_df():
    return pd.DataFrame(
        {
            "n1": [1, 1, 2],
            "n2": [2, 3, 4],
            "n3": [3, 4, 5],
            "n4": [4, 5, 6],
            "n5": [5, 6, 7],
            "n6": [6, 7, 8],
        }
    )


@pytest.fixture
def simple_feature_df():
    return pd.DataFrame({"f1": [10, 20, 30]})


@pytest.fixture
def simple_label_df():
    return pd.DataFrame({"y_1": [0, 1, 0, 1, 0]})


@pytest.fixture
def time_split_feature_df():
    return pd.DataFrame({"f1": [1, 2, 3, 4, 5]})


@pytest.fixture
def probability_matrix():
    row1 = np.linspace(0.01, 0.45, 45)
    row2 = np.linspace(0.45, 0.01, 45)
    return np.vstack([row1, row2])


@pytest.fixture
def y_true_two_rows(label_cols):
    y_true = pd.DataFrame(0, index=range(2), columns=label_cols)
    for num in [40, 41, 42, 43, 44, 45]:
        y_true.loc[0, f"y_{num}"] = 1
    for num in [1, 2, 3, 4, 5, 6]:
        y_true.loc[1, f"y_{num}"] = 1
    return y_true
