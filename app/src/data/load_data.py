from __future__ import annotations

import pandas as pd

from src.config import AUTO_RAW_LOTTO_FILE, RAW_LOTTO_FILE
from src.data.collect_lotto import fetch_lotto_history, save_auto_collected_history
from src.data.collect_lotto_browser import (
    fetch_lotto_history_browser,
    save_auto_browser_collected_history,
)


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

    Note:
    The automated sources ('auto', 'auto_browser') are still under
    implementation and environment-specific verification.
    """
    if source == "excel":
        return load_lotto_excel(file_path=file_path)

    if source == "auto":
        # Experimental path: kept in the project while access stability is
        # still being validated against the official site.
        df = fetch_lotto_history(start_round=start_round, end_round=end_round)
        save_auto_collected_history(df, auto_save_path)
        return df

    if source == "auto_browser":
        # Experimental path: browser-driven fetch is implemented, but the
        # official site may still block some environments.
        df = fetch_lotto_history_browser(start_round=start_round, end_round=end_round)
        save_auto_browser_collected_history(df, auto_save_path)
        return df

    raise ValueError("source must be one of 'excel', 'auto', or 'auto_browser'")
