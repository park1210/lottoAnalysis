from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from src.models.predict import number_lists_to_binary_df


def row_to_numbers(row: pd.Series) -> list[int]:
    return sorted([int(col.split("_")[1]) for col, val in row.items() if val == 1])


def hits_per_draw(predicted_number_lists: list[list[int]], y_true: pd.DataFrame) -> list[int]:
    actual_numbers = y_true.apply(row_to_numbers, axis=1).reset_index(drop=True)
    return [
        len(set(pred) & set(actual))
        for pred, actual in zip(predicted_number_lists, actual_numbers)
    ]


def evaluate_number_predictions(
    model_name: str,
    predicted_number_lists: list[list[int]],
    y_true: pd.DataFrame,
    label_cols: list[str],
) -> dict:
    y_pred_binary = number_lists_to_binary_df(predicted_number_lists, label_cols=label_cols)
    actual_numbers = y_true.apply(row_to_numbers, axis=1).reset_index(drop=True)
    hit_scores = hits_per_draw(predicted_number_lists, y_true)

    draw_results = pd.DataFrame(
        {
            "model": model_name,
            "draw_index": np.arange(len(predicted_number_lists)),
            "predicted_numbers": [",".join(map(str, nums)) for nums in predicted_number_lists],
            "actual_numbers": [",".join(map(str, nums)) for nums in actual_numbers],
            "hit_count": hit_scores,
            "exact_match": (y_true.values == y_pred_binary.values).all(axis=1).astype(int),
        }
    )

    return {
        "model": model_name,
        "subset_accuracy": accuracy_score(y_true.values, y_pred_binary.values),
        "number_level_accuracy": (y_true.values == y_pred_binary.values).mean(),
        "avg_hit": float(np.mean(hit_scores)),
        "hit_std": float(np.std(hit_scores)),
        "draw_results": draw_results,
    }
