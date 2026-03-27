import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.src.data.load_data import load_lotto_excel, load_lotto_source
from app.src.data.sync_lotto_html import normalize_history_columns


def test_load_lotto_excel_reads_existing_workbook(tmp_path: Path):
    source_file = tmp_path / "lotto.xlsx"
    expected_df = pd.DataFrame(
        [[1, 1, 1, 2, 3, 4, 5, 6, 7, "1등", 10, 1000000000]],
        columns=[
            "No",
            "Round",
            "Number1",
            "Number2",
            "Number3",
            "Number4",
            "Number5",
            "Number6",
            "Bonus",
            "Rank",
            "WinnerCount",
            "PrizeAmount",
        ],
    )
    expected_df.to_excel(source_file, index=False)

    result = load_lotto_excel(file_path=source_file, sync=False)

    assert result.equals(expected_df)


def test_load_lotto_source_supports_excel_only(tmp_path: Path):
    source_file = tmp_path / "lotto.xlsx"
    pd.DataFrame([[1]], columns=["Round"]).to_excel(source_file, index=False)

    result = load_lotto_source(source="excel", file_path=source_file, sync=False)

    assert list(result.columns) == ["Round"]


def test_load_lotto_source_rejects_non_excel_sources():
    with pytest.raises(ValueError, match="source must be 'excel'"):
        load_lotto_source(source="auto")


def test_normalize_history_columns_supports_legacy_korean_headers():
    legacy_df = pd.DataFrame(
        [
            [1, 1214, 10, 15, 19, 27, 30, 33, 14, "1등", "12 명", "2,431,577,188 원"],
        ],
        columns=[
            "No",
            "회차",
            "당첨번호",
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 7",
            "보너스",
            "순위",
            "당첨게임수",
            "1게임당 당첨금액",
        ],
    )

    normalized = normalize_history_columns(legacy_df)

    assert list(normalized.columns) == [
        "No",
        "Round",
        "Number1",
        "Number2",
        "Number3",
        "Number4",
        "Number5",
        "Number6",
        "Bonus",
        "Rank",
        "WinnerCount",
        "PrizeAmount",
    ]
    assert normalized.loc[0, "Round"] == 1214
