from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_LOTTO_FILE


RENAMED_COLUMNS = [
    "row_id",
    "round",
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    "bonus",
    "rank_text",
    "winner_count",
    "prize_amount",
]


def preprocess_lotto_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw lotto data into a consistent analysis-ready schema.
    """
    df = df.copy()
    df.columns = RENAMED_COLUMNS

    numeric_cols = ["row_id", "round", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["rank_text"] = df["rank_text"].astype(str).str.strip()

    df["winner_count"] = (
        df["winner_count"]
        .astype(str)
        .str.replace("명", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    df["winner_count"] = pd.to_numeric(df["winner_count"], errors="coerce").astype("Int64")

    df["prize_amount"] = (
        df["prize_amount"]
        .astype(str)
        .str.replace("원", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    df["prize_amount"] = pd.to_numeric(df["prize_amount"], errors="coerce").astype("Int64")

    number_cols = ["n1", "n2", "n3", "n4", "n5", "n6"]
    df = df.sort_values("round").reset_index(drop=True)

    df["numbers"] = df[number_cols].astype(str).agg(",".join, axis=1)
    df["sum_main"] = df[number_cols].sum(axis=1)
    df["odd_count"] = df[number_cols].apply(lambda row: sum(x % 2 == 1 for x in row), axis=1)
    df["even_count"] = 6 - df["odd_count"]
    df["low_count"] = df[number_cols].apply(lambda row: sum(x <= 22 for x in row), axis=1)
    df["high_count"] = 6 - df["low_count"]

    return df


def save_processed_lotto(df: pd.DataFrame, output_path=PROCESSED_LOTTO_FILE) -> None:
    """
    Save processed lotto data to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
