from __future__ import annotations

import pandas as pd


def create_recent_frequency(one_hot: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Use only prior draws so each feature row predicts the current draw
    without leaking the target numbers into the rolling window.
    """
    return one_hot.rolling(window).sum().shift(1)
