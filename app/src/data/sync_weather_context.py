from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path

import pandas as pd

from src.analysis.contextual_analysis import FIRST_DRAW_DATE
from src.config import (
    DRAW_METADATA_FILE,
    PROCESSED_LOTTO_FILE,
    WEATHER_CONTEXT_FILE,
    WEATHER_OBSERVATION_FILE,
)
from src.data.weather_client import fetch_daily_weather_optional, fetch_hourly_weather


DEFAULT_DRAW_TIME = time(20, 35)
DEFAULT_DRAW_LOCATION = "MBC Studio"
DEFAULT_STATION_ID = "108"
DEFAULT_STATION_NAME = "Seoul ASOS"
DRAW_METADATA_COLUMNS = [
    "round",
    "draw_date",
    "scheduled_draw_datetime",
    "actual_draw_datetime",
    "draw_location_name",
    "weather_station_id",
    "weather_station_name",
    "is_time_exception",
    "is_location_exception",
    "metadata_quality",
    "notes",
]
HOURLY_FETCH_BATCH_SIZE = 50

WEATHER_CONTEXT_COLUMNS = [
    "round",
    "draw_date",
    "draw_datetime_used",
    "draw_location_name",
    "station_id",
    "station_name",
    "temp_at_draw",
    "humidity_at_draw",
    "wind_at_draw",
    "pressure_at_draw",
    "snow_at_draw",
    "precip_1h",
    "precip_6h",
    "precip_24h",
    "daily_tavg",
    "daily_tmin",
    "daily_tmax",
    "daily_precip_mm",
    "is_raining",
    "is_snowing",
    "temp_bin",
    "humidity_bin",
]


@dataclass
class WeatherSyncBundle:
    metadata_df: pd.DataFrame
    hourly_df: pd.DataFrame
    daily_df: pd.DataFrame
    context_df: pd.DataFrame


def _load_round_index() -> list[int]:
    df = pd.read_csv(PROCESSED_LOTTO_FILE)
    rounds = pd.to_numeric(df["round"], errors="coerce").dropna().astype(int).sort_values().unique().tolist()
    return rounds


def build_draw_metadata(rounds: list[int] | None = None) -> pd.DataFrame:
    rounds = rounds or _load_round_index()
    rows: list[dict[str, object]] = []

    for round_no in rounds:
        draw_date = (FIRST_DRAW_DATE + pd.to_timedelta(round_no - 1, unit="W")).date()
        scheduled_dt = datetime.combine(draw_date, DEFAULT_DRAW_TIME)
        rows.append(
            {
                "round": round_no,
                "draw_date": draw_date,
                "scheduled_draw_datetime": scheduled_dt,
                "actual_draw_datetime": pd.NaT,
                "draw_location_name": DEFAULT_DRAW_LOCATION,
                "weather_station_id": DEFAULT_STATION_ID,
                "weather_station_name": DEFAULT_STATION_NAME,
                "is_time_exception": False,
                "is_location_exception": False,
                "metadata_quality": "default_rule",
                "notes": "",
            }
        )

    metadata_df = pd.DataFrame(rows, columns=DRAW_METADATA_COLUMNS)
    return metadata_df


def load_draw_metadata(path: Path = DRAW_METADATA_FILE) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path, parse_dates=["draw_date", "scheduled_draw_datetime", "actual_draw_datetime"])
        return df.reindex(columns=DRAW_METADATA_COLUMNS)

    df = build_draw_metadata()
    save_draw_metadata(df, path=path)
    return df


def save_draw_metadata(df: pd.DataFrame, path: Path = DRAW_METADATA_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def _resolve_draw_datetime_used(row: pd.Series) -> pd.Timestamp:
    actual_dt = pd.to_datetime(row.get("actual_draw_datetime"), errors="coerce")
    if pd.notna(actual_dt):
        return actual_dt
    return pd.to_datetime(row["scheduled_draw_datetime"])


def _nearest_hour_timestamp(value: pd.Timestamp | datetime) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    floor = ts.floor("h")
    ceil = floor if ts == floor else floor + pd.Timedelta(hours=1)
    return ceil if (ceil - ts) <= (ts - floor) else floor


def collect_weather_observations(
    draw_meta_df: pd.DataFrame,
    existing_hourly_df: pd.DataFrame | None = None,
    existing_daily_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    working = draw_meta_df.copy()
    working["draw_datetime_used"] = working.apply(_resolve_draw_datetime_used, axis=1)
    station_ids = sorted(working["weather_station_id"].dropna().astype(str).unique().tolist())

    draw_datetimes = pd.to_datetime(working["draw_datetime_used"].dropna()).tolist()
    draw_dates = pd.to_datetime(working["draw_datetime_used"].dropna()).dt.date.tolist()

    existing_hourly_df = existing_hourly_df.copy() if existing_hourly_df is not None and not existing_hourly_df.empty else pd.DataFrame()
    existing_daily_df = existing_daily_df.copy() if existing_daily_df is not None and not existing_daily_df.empty else pd.DataFrame()

    if not existing_hourly_df.empty:
        existing_hourly_df["observed_at"] = pd.to_datetime(existing_hourly_df["observed_at"], errors="coerce")
        existing_hourly_keys = set(
            zip(existing_hourly_df["station_id"].astype(str), existing_hourly_df["observed_at"].dt.strftime("%Y%m%d%H%M"))
        )
    else:
        existing_hourly_keys = set()

    if not existing_daily_df.empty and "date" in existing_daily_df.columns:
        existing_daily_df["date"] = pd.to_datetime(existing_daily_df["date"], errors="coerce").dt.date
        existing_daily_keys = set(
            zip(existing_daily_df["station_id"].astype(str), pd.Series(existing_daily_df["date"]).astype(str))
        )
    else:
        existing_daily_keys = set()

    needed_hourly = []
    for dt in draw_datetimes:
        query_dt = _nearest_hour_timestamp(dt)
        dt_key = query_dt.strftime("%Y%m%d%H%M")
        if any((station_id, dt_key) not in existing_hourly_keys for station_id in station_ids):
            needed_hourly.append(query_dt)

    needed_daily = []
    for d in draw_dates:
        d_key = str(d)
        if any((station_id, d_key) not in existing_daily_keys for station_id in station_ids):
            needed_daily.append(d)

    hourly_df = existing_hourly_df.copy()
    daily_df = existing_daily_df.copy()

    if needed_hourly:
        for start in range(0, len(needed_hourly), HOURLY_FETCH_BATCH_SIZE):
            batch = needed_hourly[start:start + HOURLY_FETCH_BATCH_SIZE]
            batch_hourly_df = fetch_hourly_weather(station_ids, timestamps=batch)
            hourly_df = pd.concat([hourly_df, batch_hourly_df], ignore_index=True, sort=False)
            if not hourly_df.empty:
                hourly_df["observed_at"] = pd.to_datetime(hourly_df["observed_at"], errors="coerce")
                hourly_df = hourly_df.drop_duplicates(subset=["station_id", "observed_at"]).sort_values(["station_id", "observed_at"]).reset_index(drop=True)
            save_weather_observations(hourly_df, daily_df)

    # Save hourly progress first so long-running collection is not lost if daily access is unavailable.
    save_weather_observations(hourly_df, daily_df)

    new_daily_df = fetch_daily_weather_optional(station_ids, dates=needed_daily) if needed_daily else pd.DataFrame()
    daily_df = pd.concat([existing_daily_df, new_daily_df], ignore_index=True, sort=False)

    if not hourly_df.empty:
        hourly_df["observed_at"] = pd.to_datetime(hourly_df["observed_at"], errors="coerce")
        hourly_df = hourly_df.drop_duplicates(subset=["station_id", "observed_at"]).sort_values(["station_id", "observed_at"]).reset_index(drop=True)
    if not daily_df.empty and "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce").dt.date
        daily_df = daily_df.drop_duplicates(subset=["station_id", "date"]).sort_values(["station_id", "date"]).reset_index(drop=True)

    return hourly_df, daily_df


def save_weather_observations(hourly_df: pd.DataFrame, daily_df: pd.DataFrame, path: Path = WEATHER_OBSERVATION_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    hourly_export = hourly_df.copy()
    hourly_export["source_type"] = "hourly"
    daily_export = daily_df.copy()
    daily_export["source_type"] = "daily"
    merged = pd.concat([hourly_export, daily_export], ignore_index=True, sort=False)
    merged.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def load_or_fetch_weather_observations(draw_meta_df: pd.DataFrame, force: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    existing_hourly_df = pd.DataFrame()
    existing_daily_df = pd.DataFrame()

    if WEATHER_OBSERVATION_FILE.exists() and not force:
        merged = pd.read_csv(WEATHER_OBSERVATION_FILE, parse_dates=["observed_at"], low_memory=False)
        existing_hourly_df = merged[merged["source_type"] == "hourly"].copy() if "source_type" in merged.columns else merged.copy()
        existing_daily_df = merged[merged["source_type"] == "daily"].copy() if "source_type" in merged.columns else pd.DataFrame()
        if "date" in existing_daily_df.columns:
            existing_daily_df["date"] = pd.to_datetime(existing_daily_df["date"], errors="coerce").dt.date

    hourly_df, daily_df = collect_weather_observations(
        draw_meta_df,
        existing_hourly_df=existing_hourly_df if not force else pd.DataFrame(),
        existing_daily_df=existing_daily_df if not force else pd.DataFrame(),
    )
    save_weather_observations(hourly_df, daily_df)
    return hourly_df, daily_df


def _nearest_observation(hourly_station_df: pd.DataFrame, draw_dt: pd.Timestamp) -> pd.Series:
    station_df = hourly_station_df.copy()
    station_df["distance_seconds"] = (station_df["observed_at"] - draw_dt).abs().dt.total_seconds()
    return station_df.sort_values("distance_seconds").iloc[0]


def _sum_precip_in_window(hourly_station_df: pd.DataFrame, draw_dt: pd.Timestamp, hours: int) -> float:
    window_df = hourly_station_df[
        (hourly_station_df["observed_at"] > draw_dt - timedelta(hours=hours))
        & (hourly_station_df["observed_at"] <= draw_dt)
    ]
    return float(window_df["precip_mm"].fillna(0).sum())


def _categorize_temperature(value: float | int | None) -> str | None:
    if pd.isna(value):
        return None
    if value < 0:
        return "freezing"
    if value < 10:
        return "cold"
    if value < 20:
        return "mild"
    if value < 30:
        return "warm"
    return "hot"


def _categorize_humidity(value: float | int | None) -> str | None:
    if pd.isna(value):
        return None
    if value < 30:
        return "dry"
    if value < 60:
        return "moderate"
    if value < 80:
        return "humid"
    return "very_humid"


def merge_weather_with_draws(draw_meta_df: pd.DataFrame, hourly_df: pd.DataFrame, daily_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    working = draw_meta_df.copy()
    working["draw_datetime_used"] = working.apply(_resolve_draw_datetime_used, axis=1)
    hourly_df = hourly_df.copy()
    hourly_df["observed_at"] = pd.to_datetime(hourly_df["observed_at"], errors="coerce")

    for row in working.itertuples(index=False):
        draw_dt = pd.to_datetime(row.draw_datetime_used)
        station_id = str(row.weather_station_id)
        hourly_station = hourly_df[hourly_df["station_id"].astype(str) == station_id].dropna(subset=["observed_at"])
        if hourly_station.empty:
            continue

        nearest = _nearest_observation(hourly_station, draw_dt)
        daily_station = daily_df[daily_df["station_id"].astype(str) == station_id].copy()
        daily_station["date"] = pd.to_datetime(daily_station["date"], errors="coerce").dt.date
        daily_row = daily_station[daily_station["date"] == draw_dt.date()]
        daily_row = daily_row.iloc[0] if not daily_row.empty else pd.Series(dtype=object)

        precip_1h = _sum_precip_in_window(hourly_station, draw_dt, 1)
        precip_6h = _sum_precip_in_window(hourly_station, draw_dt, 6)
        precip_24h = _sum_precip_in_window(hourly_station, draw_dt, 24)
        snow_at_draw = nearest.get("snow_cm")
        humidity_at_draw = nearest.get("humidity_pct")
        temp_at_draw = nearest.get("temp_c")

        rows.append(
            {
                "round": row.round,
                "draw_date": row.draw_date,
                "draw_datetime_used": draw_dt,
                "draw_location_name": row.draw_location_name,
                "station_id": station_id,
                "station_name": row.weather_station_name,
                "temp_at_draw": temp_at_draw,
                "humidity_at_draw": humidity_at_draw,
                "wind_at_draw": nearest.get("wind_speed_ms"),
                "pressure_at_draw": nearest.get("pressure_hpa"),
                "snow_at_draw": snow_at_draw,
                "precip_1h": precip_1h,
                "precip_6h": precip_6h,
                "precip_24h": precip_24h,
                "daily_tavg": daily_row.get("daily_tavg"),
                "daily_tmin": daily_row.get("daily_tmin"),
                "daily_tmax": daily_row.get("daily_tmax"),
                "daily_precip_mm": daily_row.get("daily_precip_mm"),
                "is_raining": precip_1h > 0,
                "is_snowing": bool(pd.notna(snow_at_draw) and float(snow_at_draw) > 0),
                "temp_bin": _categorize_temperature(temp_at_draw),
                "humidity_bin": _categorize_humidity(humidity_at_draw),
            }
        )

    return pd.DataFrame(rows, columns=WEATHER_CONTEXT_COLUMNS)


def save_weather_context(df: pd.DataFrame, path: Path = WEATHER_CONTEXT_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path




def load_cached_weather_observations() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not WEATHER_OBSERVATION_FILE.exists():
        return pd.DataFrame(), pd.DataFrame()
    merged = pd.read_csv(WEATHER_OBSERVATION_FILE, parse_dates=["observed_at"], low_memory=False)
    hourly_df = merged[merged["source_type"] == "hourly"].copy() if "source_type" in merged.columns else merged.copy()
    daily_df = merged[merged["source_type"] == "daily"].copy() if "source_type" in merged.columns else pd.DataFrame()
    if "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce").dt.date
    return hourly_df, daily_df


def fetch_weather_observations(force: bool = False) -> WeatherSyncBundle:
    draw_meta_df = load_draw_metadata()
    hourly_df, daily_df = load_or_fetch_weather_observations(draw_meta_df, force=force)
    return WeatherSyncBundle(
        metadata_df=draw_meta_df,
        hourly_df=hourly_df,
        daily_df=daily_df,
        context_df=pd.DataFrame(columns=WEATHER_CONTEXT_COLUMNS),
    )


def build_weather_context_from_cache() -> WeatherSyncBundle:
    draw_meta_df = load_draw_metadata()
    hourly_df, daily_df = load_cached_weather_observations()
    context_df = merge_weather_with_draws(draw_meta_df, hourly_df, daily_df)
    save_weather_context(context_df)
    return WeatherSyncBundle(
        metadata_df=draw_meta_df,
        hourly_df=hourly_df,
        daily_df=daily_df,
        context_df=context_df,
    )

def sync_weather_context(force: bool = False) -> WeatherSyncBundle:
    draw_meta_df = load_draw_metadata()
    try:
        hourly_df, daily_df = load_or_fetch_weather_observations(draw_meta_df, force=force)
    except Exception:
        # Fall back to any cached observations collected so far so we can still build a partial context file.
        if WEATHER_OBSERVATION_FILE.exists():
            hourly_df, daily_df = load_cached_weather_observations()
        else:
            raise
    context_df = merge_weather_with_draws(draw_meta_df, hourly_df, daily_df)
    save_weather_context(context_df)
    return WeatherSyncBundle(
        metadata_df=draw_meta_df,
        hourly_df=hourly_df,
        daily_df=daily_df,
        context_df=context_df,
    )
