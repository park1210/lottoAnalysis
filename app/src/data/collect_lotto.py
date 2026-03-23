from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests
from requests import Response


LOTTO_API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}
RAW_AUTO_COLUMNS = [
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


def fetch_lotto_round(round_no: int, timeout: int = 10) -> dict:
    response = requests.get(
        LOTTO_API_URL,
        params={"drwNo": round_no},
        headers=DEFAULT_HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()

    payload = _decode_lotto_payload(response, round_no)
    if payload.get("returnValue") != "success":
        raise ValueError(f"Round {round_no} is not available")

    return payload


def _decode_lotto_payload(response: Response, round_no: int) -> dict:
    try:
        return response.json()
    except ValueError as exc:
        snippet = response.text[:120].replace("\n", " ")
        raise RuntimeError(
            "The official lotto endpoint did not return JSON. "
            "This usually means the site blocked the request or returned an "
            "HTML page instead. Try the manual Excel mode if auto mode is "
            "not available in the current network environment. "
            f"(round={round_no}, status={response.status_code}, snippet={snippet!r})"
        ) from exc


def get_latest_lotto_round(start_round: int = 1) -> int:
    def is_available(round_no: int) -> bool:
        try:
            fetch_lotto_round(round_no)
            return True
        except ValueError:
            return False

    if not is_available(start_round):
        raise RuntimeError("Could not find any available lotto rounds")

    low = start_round
    high = start_round

    while is_available(high):
        low = high
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2
        if is_available(mid):
            low = mid
        else:
            high = mid

    return low


def build_round_record(payload: dict) -> list[int | str]:
    return [
        payload["drwNo"],
        payload["drwNo"],
        payload["drwtNo1"],
        payload["drwtNo2"],
        payload["drwtNo3"],
        payload["drwtNo4"],
        payload["drwtNo5"],
        payload["drwtNo6"],
        payload["bnusNo"],
        "1등",
        payload["firstPrzwnerCo"],
        payload["firstWinamnt"],
    ]


def fetch_lotto_history(start_round: int = 1, end_round: int | None = None) -> pd.DataFrame:
    if start_round < 1:
        raise ValueError("start_round must be at least 1")

    if end_round is None:
        end_round = get_latest_lotto_round(start_round=start_round)

    if end_round < start_round:
        raise ValueError("end_round must be greater than or equal to start_round")

    records = []
    for round_no in range(start_round, end_round + 1):
        payload = fetch_lotto_round(round_no)
        records.append(build_round_record(payload))

    return pd.DataFrame(records, columns=RAW_AUTO_COLUMNS)


def save_auto_collected_history(df: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path
