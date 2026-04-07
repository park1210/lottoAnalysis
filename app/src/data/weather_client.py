from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout
from urllib3.util.retry import Retry


KMA_API_BASE_URL = "https://apihub.kma.go.kr/api/typ01/url"
ASOS_HOURLY_ENDPOINT = "/kma_sfctm2.php"
ASOS_DAILY_ENDPOINT = "/kma_sfcdd.php"
DEFAULT_TIMEOUT = 60
DEFAULT_HEADERS = {
    "User-Agent": "lotto-analysis-weather-sync/1.0",
    "Accept": "text/plain, */*",
}
REQUEST_SLEEP_SECONDS = 0.15


class WeatherAPIConfigurationError(RuntimeError):
    pass


HOURLY_COLUMNS = [
    "TM", "STN", "WD", "WS", "GST_WD", "GST_WS", "GST_TM", "PA", "PS", "PT", "PR",
    "TA", "TD", "HM", "PV", "RN", "RN_DAY", "RN_JUN", "RN_INT", "SD_HR3", "SD_DAY",
    "SD_TOT", "WC", "WP", "WW", "CA_TOT", "CA_MID", "CH_MIN", "CT", "CT_TOP", "CT_MID",
    "CT_LOW", "VS", "SS", "SI", "ST_GD", "TS", "TE_005", "TE_01", "TE_02", "TE_03",
    "ST_SEA", "WH", "BF", "IR", "IX",
]
DAILY_COLUMNS = [
    "TM", "STN", "RN_DAY", "CA_TOT", "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM",
    "TA_AVG", "TA_MAX", "TA_MAX_TM", "TA_MIN", "TA_MIN_TM", "TD_AVG", "HM_AVG", "PV_AVG",
    "EV_S", "SS_DAY", "SS_DUR", "SI_DAY", "ST_GD", "TS_AVG", "TE_005", "TE_01", "TE_02",
    "TE_03", "TMON", "TMAXS", "TMINS", "RN_JUN", "RN_INT", "RN_60M_MAX", "RN_60M_MAX_TM",
    "RN_10M_MAX", "RN_10M_MAX_TM",
]


def _build_session() -> requests.Session:
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(DEFAULT_HEADERS)
    return session


def get_kma_service_key(explicit_key: str | None = None) -> str:
    service_key = (
        explicit_key
        or os.getenv("KMA_AUTH_KEY")
        or os.getenv("KMA_SERVICE_KEY")
        or os.getenv("DATA_GO_KR_SERVICE_KEY")
    )
    if not service_key:
        raise WeatherAPIConfigurationError(
            "KMA auth key is not configured. Set KMA_AUTH_KEY (preferred) or KMA_SERVICE_KEY."
        )
    return service_key.strip()


def _request_weather_api(endpoint: str, params: dict[str, Any], service_key: str | None = None, session: requests.Session | None = None) -> str:
    key = get_kma_service_key(service_key)
    query = params | {"authKey": key, "help": "0"}
    url = f"{KMA_API_BASE_URL}{endpoint}"
    active_session = session or _build_session()
    response = active_session.get(url, params=query, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    text = response.text
    if '<html' in text.lower():
        raise RuntimeError(f"KMA API Hub returned HTML instead of weather data: {text[:300]}")
    return text


def _extract_data_lines(text: str) -> list[str]:
    data_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or line.startswith('START7777') or line.startswith('7777END'):
            continue
        data_lines.append(line)
    return data_lines


def _build_dataframe_from_lines(lines: list[str], columns: list[str]) -> pd.DataFrame:
    if not lines:
        return pd.DataFrame(columns=columns)
    rows = []
    for line in lines:
        parts = line.split()
        if len(parts) < len(columns):
            parts = parts + [pd.NA] * (len(columns) - len(parts))
        elif len(parts) > len(columns):
            parts = parts[: len(columns)]
        rows.append(parts)
    return pd.DataFrame(rows, columns=columns)


def _nearest_hour_marks(timestamps: list[datetime]) -> list[datetime]:
    rounded: set[pd.Timestamp] = set()
    for ts in pd.to_datetime(timestamps):
        current = pd.Timestamp(ts)
        floor = current.floor("h")
        ceil = floor if current == floor else floor + pd.Timedelta(hours=1)
        nearest = ceil if (ceil - current) <= (current - floor) else floor
        rounded.add(nearest)
    return [ts.to_pydatetime() for ts in sorted(rounded)]


def fetch_hourly_weather(stn_ids: list[int] | list[str], timestamps: list[datetime], service_key: str | None = None) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    unique_timestamps = _nearest_hour_marks(timestamps)
    session = _build_session()
    for target_dt in unique_timestamps:
        tm = pd.Timestamp(target_dt).strftime("%Y%m%d%H%M")
        for stn_id in stn_ids:
            params = {"tm": tm, "stn": str(stn_id)}
            try:
                text = _request_weather_api(ASOS_HOURLY_ENDPOINT, params=params, service_key=service_key, session=session)
            except (HTTPError, ReadTimeout, ConnectionError):
                time.sleep(REQUEST_SLEEP_SECONDS * 4)
                continue
            lines = _extract_data_lines(text)
            payload_df = _build_dataframe_from_lines(lines, HOURLY_COLUMNS)
            if not payload_df.empty:
                records.append(payload_df)
            time.sleep(REQUEST_SLEEP_SECONDS)
    raw_df = pd.concat(records, ignore_index=True) if records else pd.DataFrame(columns=HOURLY_COLUMNS)
    return normalize_hourly_weather(raw_df)


def fetch_daily_weather(stn_ids: list[int] | list[str], dates: list[datetime], service_key: str | None = None) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    unique_dates = sorted({pd.Timestamp(d).strftime("%Y%m%d") for d in dates})
    session = _build_session()
    for tm in unique_dates:
        for stn_id in stn_ids:
            params = {"tm": tm, "stn": str(stn_id), "disp": "0"}
            text = _request_weather_api(ASOS_DAILY_ENDPOINT, params=params, service_key=service_key, session=session)
            lines = _extract_data_lines(text)
            payload_df = _build_dataframe_from_lines(lines, DAILY_COLUMNS)
            if not payload_df.empty:
                records.append(payload_df)
            time.sleep(REQUEST_SLEEP_SECONDS)
    raw_df = pd.concat(records, ignore_index=True) if records else pd.DataFrame(columns=DAILY_COLUMNS)
    return normalize_daily_weather(raw_df)


def fetch_daily_weather_optional(stn_ids: list[int] | list[str], dates: list[datetime], service_key: str | None = None) -> pd.DataFrame:
    try:
        return fetch_daily_weather(stn_ids=stn_ids, dates=dates, service_key=service_key)
    except (requests.HTTPError, ReadTimeout, ConnectionError) as exc:
        response = getattr(exc, "response", None)
        if response is None or response.status_code in {403, 401, 429, 500, 502, 503, 504}:
            return pd.DataFrame(columns=["station_id", "station_name", "date", "daily_tavg", "daily_tmin", "daily_tmax", "daily_precip_mm"])
        raise


def normalize_hourly_weather(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["station_id", "station_name", "observed_at", "temp_c", "humidity_pct", "precip_mm", "precip_day_cumulative_mm", "wind_speed_ms", "pressure_hpa", "snow_cm"])

    normalized = df.rename(columns={
        "STN": "station_id",
        "TM": "observed_at",
        "TA": "temp_c",
        "HM": "humidity_pct",
        "RN": "precip_mm",
        "RN_DAY": "precip_day_cumulative_mm",
        "WS": "wind_speed_ms",
        "PA": "pressure_hpa",
        "SD_HR3": "snow_cm",
    }).copy()
    normalized["observed_at"] = pd.to_datetime(normalized["observed_at"], format="%Y%m%d%H%M", errors="coerce")
    for col in ["temp_c", "humidity_pct", "precip_mm", "precip_day_cumulative_mm", "wind_speed_ms", "pressure_hpa", "snow_cm"]:
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
    # KMA uses negative sentinel values for unavailable precipitation and snow fields.
    for col in ["precip_mm", "precip_day_cumulative_mm", "snow_cm"]:
        normalized.loc[normalized[col] < 0, col] = pd.NA
    normalized["station_id"] = normalized["station_id"].astype(str)
    normalized["station_name"] = pd.Series([pd.NA] * len(normalized), dtype="string")
    keep = ["station_id", "station_name", "observed_at", "temp_c", "humidity_pct", "precip_mm", "precip_day_cumulative_mm", "wind_speed_ms", "pressure_hpa", "snow_cm"]
    return normalized[keep].drop_duplicates(subset=["station_id", "observed_at"]).sort_values(["station_id", "observed_at"]).reset_index(drop=True)


def normalize_daily_weather(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["station_id", "station_name", "date", "daily_tavg", "daily_tmin", "daily_tmax", "daily_precip_mm"])

    normalized = df.rename(columns={
        "STN": "station_id",
        "TM": "date",
        "TA_AVG": "daily_tavg",
        "TA_MIN": "daily_tmin",
        "TA_MAX": "daily_tmax",
        "RN_DAY": "daily_precip_mm",
    }).copy()
    normalized["date"] = pd.to_datetime(normalized["date"], format="%Y%m%d", errors="coerce").dt.date
    for col in ["daily_tavg", "daily_tmin", "daily_tmax", "daily_precip_mm"]:
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
    normalized["station_id"] = normalized["station_id"].astype(str)
    normalized["station_name"] = pd.Series([pd.NA] * len(normalized), dtype="string")
    keep = ["station_id", "station_name", "date", "daily_tavg", "daily_tmin", "daily_tmax", "daily_precip_mm"]
    return normalized[keep].drop_duplicates(subset=["station_id", "date"]).sort_values(["station_id", "date"]).reset_index(drop=True)
