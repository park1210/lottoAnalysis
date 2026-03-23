from __future__ import annotations

import pandas as pd

from src.config import AUTO_RAW_LOTTO_FILE, RAW_LOTTO_FILE
from src.data.collect_lotto import fetch_lotto_history, save_auto_collected_history


def load_lotto_excel(file_path=RAW_LOTTO_FILE) -> pd.DataFrame:
    """
    Load lotto history from the existing local Excel file.
    """
    return pd.read_excel(file_path)


def load_lotto_source(
    source: str = "excel",
    file_path=RAW_LOTTO_FILE,
    auto_save_path=AUTO_RAW_LOTTO_FILE,
    start_round: int = 1,
    end_round: int | None = None,
) -> pd.DataFrame:
    """
    Load lotto history either from the local Excel file or from the official
    round-based web endpoint.
    """
    if source == "excel":
        return load_lotto_excel(file_path=file_path)

    if source == "auto":
        df = fetch_lotto_history(start_round=start_round, end_round=end_round)
        save_auto_collected_history(df, auto_save_path)
        return df

    raise ValueError("source must be either 'excel' or 'auto'")
