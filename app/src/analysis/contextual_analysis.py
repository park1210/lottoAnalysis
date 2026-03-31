from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chisquare, entropy, f_oneway, kruskal

try:
    import holidays
except ImportError:  # pragma: no cover - optional dependency
    holidays = None


MAIN_NUMBER_COLS = ["n1", "n2", "n3", "n4", "n5", "n6"]
DEFAULT_METRIC_COLS = ["sum_main", "odd_count", "low_count", "winner_count", "prize_amount"]
FIRST_DRAW_DATE = pd.Timestamp("2002-12-07")

SEASON_MAP = {
    12: "winter",
    1: "winter",
    2: "winter",
    3: "spring",
    4: "spring",
    5: "spring",
    6: "summer",
    7: "summer",
    8: "summer",
    9: "autumn",
    10: "autumn",
    11: "autumn",
}


def attach_draw_date(
    df: pd.DataFrame,
    round_col: str = "round",
    first_draw_date: str | pd.Timestamp = FIRST_DRAW_DATE,
) -> pd.DataFrame:
    enriched = df.copy()
    base_date = pd.Timestamp(first_draw_date)
    enriched["draw_date"] = base_date + pd.to_timedelta(enriched[round_col] - 1, unit="W")
    return enriched


def _compute_nearest_holiday_distance(date_series: pd.Series, holiday_dates: pd.DatetimeIndex) -> pd.Series:
    if holiday_dates.empty:
        return pd.Series(np.nan, index=date_series.index, dtype="float64")

    holiday_ordinals = holiday_dates.view("int64") // 86_400_000_000_000
    draw_ordinals = date_series.view("int64") // 86_400_000_000_000

    distances = []
    for ordinal in draw_ordinals:
        distances.append(int(np.min(np.abs(holiday_ordinals - ordinal))))
    return pd.Series(distances, index=date_series.index, dtype="int64")


def add_calendar_context_features(
    df: pd.DataFrame,
    date_col: str = "draw_date",
    holiday_window_days: int = 3,
) -> pd.DataFrame:
    enriched = df.copy()
    date_series = pd.to_datetime(enriched[date_col])

    enriched["year"] = date_series.dt.year
    enriched["month"] = date_series.dt.month
    enriched["month_name"] = date_series.dt.month_name().str.slice(0, 3)
    enriched["quarter"] = "Q" + date_series.dt.quarter.astype(str)
    enriched["season"] = enriched["month"].map(SEASON_MAP)
    enriched["day_of_month"] = date_series.dt.day
    enriched["week_of_month"] = ((date_series.dt.day - 1) // 7) + 1
    enriched["weekday_name"] = date_series.dt.day_name().str.slice(0, 3)
    enriched["is_month_start_window"] = date_series.dt.day <= 7
    enriched["is_month_end_window"] = (date_series.dt.days_in_month - date_series.dt.day) < 7
    enriched["is_quarter_start_month"] = enriched["month"].isin([1, 4, 7, 10])
    enriched["is_quarter_end_month"] = enriched["month"].isin([3, 6, 9, 12])
    enriched["is_year_start_window"] = date_series.dt.month.eq(1) & (date_series.dt.day <= 14)
    enriched["is_year_end_window"] = date_series.dt.month.eq(12) & (date_series.dt.day >= 18)

    if holidays is None:
        enriched["is_near_korean_holiday"] = False
        enriched["days_to_nearest_korean_holiday"] = np.nan
        return enriched

    years = sorted(enriched["year"].dropna().unique().tolist())
    kr_holidays = holidays.country_holidays("KR", years=years)
    holiday_dates = pd.DatetimeIndex(pd.to_datetime(list(kr_holidays.keys()))).sort_values()
    nearest_distance = _compute_nearest_holiday_distance(date_series, holiday_dates)
    enriched["days_to_nearest_korean_holiday"] = nearest_distance
    enriched["is_near_korean_holiday"] = nearest_distance.le(holiday_window_days).fillna(False)
    return enriched


def build_context_profile(
    df: pd.DataFrame,
    group_col: str,
    metric_cols: list[str] | None = None,
) -> pd.DataFrame:
    metric_cols = metric_cols or DEFAULT_METRIC_COLS
    existing_metrics = [col for col in metric_cols if col in df.columns]

    profile = (
        df.groupby(group_col, dropna=False)
        .agg(
            draws=("round", "count"),
            first_round=("round", "min"),
            last_round=("round", "max"),
            **{f"avg_{col}": (col, "mean") for col in existing_metrics},
        )
        .reset_index()
        .sort_values("draws", ascending=False)
    )
    return profile


def build_context_number_frequency(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    number_frame = df[[group_col] + MAIN_NUMBER_COLS].melt(
        id_vars=group_col,
        value_vars=MAIN_NUMBER_COLS,
        var_name="position",
        value_name="number",
    )
    frequency = (
        number_frame.groupby([group_col, "number"])
        .size()
        .reset_index(name="count")
        .sort_values([group_col, "number"])
    )
    frequency["share_within_group"] = frequency.groupby(group_col)["count"].transform(lambda s: s / s.sum())
    return frequency


def run_context_frequency_tests(
    df: pd.DataFrame,
    group_col: str,
    min_draws: int = 20,
) -> pd.DataFrame:
    number_frame = df[[group_col] + MAIN_NUMBER_COLS].melt(
        id_vars=group_col,
        value_vars=MAIN_NUMBER_COLS,
        var_name="position",
        value_name="number",
    )

    group_draw_counts = df.groupby(group_col).size()
    valid_groups = group_draw_counts[group_draw_counts >= min_draws].index.tolist()
    number_frame = number_frame[number_frame[group_col].isin(valid_groups)].copy()

    overall_counts = (
        number_frame.groupby("number")
        .size()
        .reindex(range(1, 46), fill_value=0)
        .astype(float)
    )
    overall_probs = overall_counts / overall_counts.sum()

    rows: list[dict[str, float | str | int]] = []
    for group_value, group_df in number_frame.groupby(group_col):
        observed = (
            group_df.groupby("number")
            .size()
            .reindex(range(1, 46), fill_value=0)
            .astype(float)
        )
        total_count = float(observed.sum())
        expected = overall_probs * total_count
        chi_stat, chi_p = chisquare(observed.values, expected.values)

        observed_prob = observed / total_count
        kl_divergence = float(entropy(observed_prob, overall_probs))

        rows.append(
            {
                "group_col": group_col,
                "group_value": group_value,
                "draws": int(group_draw_counts[group_value]),
                "total_number_count": int(total_count),
                "chi_square_stat": float(chi_stat),
                "chi_square_p_value": float(chi_p),
                "kl_divergence_vs_overall": kl_divergence,
            }
        )

    return pd.DataFrame(rows).sort_values("chi_square_p_value")


def run_context_mean_tests(
    df: pd.DataFrame,
    group_col: str,
    metric_cols: list[str] | None = None,
    min_group_size: int = 10,
) -> pd.DataFrame:
    metric_cols = metric_cols or DEFAULT_METRIC_COLS
    existing_metrics = [col for col in metric_cols if col in df.columns]

    rows: list[dict[str, float | str | int]] = []
    group_sizes = df.groupby(group_col).size()
    valid_groups = group_sizes[group_sizes >= min_group_size].index.tolist()
    filtered = df[df[group_col].isin(valid_groups)].copy()

    for metric_col in existing_metrics:
        grouped_values = [
            grp[metric_col].dropna().to_numpy()
            for _, grp in filtered.groupby(group_col)
            if len(grp[metric_col].dropna()) >= min_group_size
        ]
        if len(grouped_values) < 2:
            continue

        anova_stat, anova_p = f_oneway(*grouped_values)
        kruskal_stat, kruskal_p = kruskal(*grouped_values)
        rows.append(
            {
                "group_col": group_col,
                "metric": metric_col,
                "n_groups_tested": len(grouped_values),
                "anova_stat": float(anova_stat),
                "anova_p_value": float(anova_p),
                "kruskal_stat": float(kruskal_stat),
                "kruskal_p_value": float(kruskal_p),
            }
        )

    return pd.DataFrame(rows)


def merge_external_context(
    df: pd.DataFrame,
    external_csv_path: str | Path,
    on: str = "draw_date",
    date_cols: list[str] | None = None,
) -> pd.DataFrame:
    date_cols = date_cols or [on]
    external_path = Path(external_csv_path)
    external_df = pd.read_csv(external_path, parse_dates=date_cols)
    merged = df.merge(external_df, on=on, how="left")
    return merged
