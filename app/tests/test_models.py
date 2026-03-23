import numpy as np
import pandas as pd

from app.src.models.evaluate import evaluate_number_predictions, hits_per_draw, row_to_numbers
from app.src.models.predict import (
    number_lists_to_binary_df,
    probability_matrix_to_number_lists,
    select_top6,
)


def test_select_top6_returns_sorted_six_numbers():
    values = np.array([0.1, 0.9, 0.8, 0.2, 0.7, 0.6, 0.5])
    selected = select_top6(values)

    assert selected == [2, 3, 4, 5, 6, 7]


def test_probability_matrix_to_number_lists_converts_each_row(probability_matrix):
    number_lists = probability_matrix_to_number_lists(probability_matrix)

    assert number_lists[0] == [40, 41, 42, 43, 44, 45]
    assert number_lists[1] == [1, 2, 3, 4, 5, 6]


def test_number_lists_to_binary_df_creates_expected_one_hot_rows(label_cols):
    number_lists = [[1, 2, 3, 4, 5, 6], [40, 41, 42, 43, 44, 45]]
    binary = number_lists_to_binary_df(number_lists, label_cols)

    assert binary.shape == (2, 45)
    assert int(binary.loc[0].sum()) == 6
    assert binary.loc[0, "y_1"] == 1
    assert binary.loc[1, "y_45"] == 1
    assert binary.loc[1, "y_1"] == 0


def test_row_to_numbers_extracts_active_labels():
    row = pd.Series({"y_1": 1, "y_2": 0, "y_3": 1, "y_4": 0})
    assert row_to_numbers(row) == [1, 3]


def test_hits_per_draw_counts_overlap_correctly():
    predicted = [[1, 2, 3, 4, 5, 6], [10, 11, 12, 13, 14, 15]]
    label_cols = [f"y_{i}" for i in range(1, 46)]
    y_true = pd.DataFrame(0, index=range(2), columns=label_cols)
    for num in [1, 2, 7, 8, 9, 10]:
        y_true.loc[0, f"y_{num}"] = 1
    for num in [10, 11, 20, 21, 22, 23]:
        y_true.loc[1, f"y_{num}"] = 1

    assert hits_per_draw(predicted, y_true) == [2, 2]


def test_evaluate_number_predictions_returns_expected_metrics(y_true_two_rows, label_cols):
    predicted_lists = [[40, 41, 42, 43, 44, 45], [1, 2, 3, 7, 8, 9]]

    result = evaluate_number_predictions(
        "test_model",
        predicted_lists,
        y_true_two_rows,
        label_cols=label_cols,
    )

    assert result["model"] == "test_model"
    assert result["subset_accuracy"] == 0.5
    assert result["number_level_accuracy"] == 42 / 45
    assert result["avg_hit"] == 4.5
    assert set(result["draw_results"].columns) == {
        "model",
        "draw_index",
        "predicted_numbers",
        "actual_numbers",
        "hit_count",
        "exact_match",
    }
