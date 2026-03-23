import pandas as pd

from app.src.features.build_features import create_one_hot
from app.src.features.gap_features import create_gap_feature
from app.src.features.rolling_features import create_recent_frequency
from app.src.features.temporal_features import (
    align_features_and_labels,
    time_based_train_test_split,
)


def test_create_one_hot_marks_drawn_numbers_correctly(clean_df):
    one_hot = create_one_hot(clean_df)

    assert one_hot.shape == (3, 45)
    assert one_hot.loc[0, 1] == 1
    assert one_hot.loc[0, 6] == 1
    assert one_hot.loc[0, 7] == 0
    assert int(one_hot.loc[1].sum()) == 6


def test_create_recent_frequency_uses_only_prior_draws(clean_df):
    one_hot = create_one_hot(clean_df)
    recent_freq = create_recent_frequency(one_hot, window=2)

    assert recent_freq.iloc[0].isna().all()
    assert recent_freq.iloc[1].isna().all()
    assert recent_freq.loc[2, 1] == 2
    assert recent_freq.loc[2, 7] == 1
    assert recent_freq.loc[2, 8] == 0


def test_create_gap_feature_tracks_distance_since_last_seen(clean_df):
    one_hot = create_one_hot(clean_df)
    gap = create_gap_feature(one_hot)

    assert pd.isna(gap.loc[0, 1])
    assert gap.loc[1, 1] == 1
    assert gap.loc[2, 1] == 1
    assert gap.loc[2, 8] == 1
    assert pd.isna(gap.loc[0, 8])


def test_align_features_and_labels_keeps_lengths_consistent(simple_feature_df, simple_label_df):
    X, y = align_features_and_labels(simple_feature_df, simple_label_df, window=2)

    assert len(X) == 3
    assert len(y) == 3
    assert y["y_1"].tolist() == [0, 1, 0]


def test_time_based_train_test_split_preserves_order(time_split_feature_df):
    y = pd.DataFrame({"y_1": [0, 1, 0, 1, 0]})
    split = time_based_train_test_split(X=time_split_feature_df, y=y, test_ratio=0.4)

    assert split["split_idx"] == 3
    assert split["X_train"]["f1"].tolist() == [1, 2, 3]
    assert split["X_test"]["f1"].tolist() == [4, 5]
    assert split["y_train"]["y_1"].tolist() == [0, 1, 0]
    assert split["y_test"]["y_1"].tolist() == [1, 0]
