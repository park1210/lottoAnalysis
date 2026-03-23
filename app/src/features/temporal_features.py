from __future__ import annotations

import pandas as pd


def align_features_and_labels(
    feature_df: pd.DataFrame,
    label_df: pd.DataFrame,
    window: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    label_aligned = label_df.iloc[window:].reset_index(drop=True)
    X = feature_df.reset_index(drop=True)
    y = label_aligned.reset_index(drop=True)
    return X, y


def time_based_train_test_split(
    X: pd.DataFrame,
    y: pd.DataFrame,
    test_ratio: float = 0.2,
) -> dict[str, pd.DataFrame]:
    split_idx = int(len(X) * (1 - test_ratio))
    return {
        "split_idx": split_idx,
        "X_train": X.iloc[:split_idx].reset_index(drop=True),
        "X_test": X.iloc[split_idx:].reset_index(drop=True),
        "y_train": y.iloc[:split_idx].reset_index(drop=True),
        "y_test": y.iloc[split_idx:].reset_index(drop=True),
    }
