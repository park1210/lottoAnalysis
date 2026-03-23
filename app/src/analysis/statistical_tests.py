from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chisquare, entropy


def run_chi_square_uniform_test(real_freq: pd.Series, total_count: int) -> tuple[float, float]:
    expected = np.full(len(real_freq), total_count / len(real_freq))
    chi_stat, p_value = chisquare(real_freq.values, expected)
    return float(chi_stat), float(p_value)


def calculate_kl_divergence(real_freq: pd.Series, random_freq: pd.Series) -> float:
    real_prob = real_freq / real_freq.sum()
    random_prob = random_freq / random_freq.sum()
    return float(entropy(real_prob, random_prob))


def build_random_frequency_interval_frame(
    real_freq: pd.Series,
    freq_matrix: np.ndarray,
    all_numbers: np.ndarray | list[int],
) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "real": real_freq,
            "random_mean": freq_matrix.mean(axis=0),
            "random_lower": np.percentile(freq_matrix, 2.5, axis=0),
            "random_upper": np.percentile(freq_matrix, 97.5, axis=0),
        },
        index=all_numbers,
    )
    frame["deviation_from_random_mean"] = frame["real"] - frame["random_mean"]
    return frame


def summarize_randomness_results(
    comparison: pd.DataFrame,
    chi_square_p_value: float,
    kl_divergence: float,
    actual_overlap_mean: float,
    simulated_overlap_means: np.ndarray,
) -> pd.Series:
    within_random_band_ratio = (
        (comparison["real"] >= comparison["random_lower"])
        & (comparison["real"] <= comparison["random_upper"])
    ).mean()
    overlap_empirical_p = float(np.mean(simulated_overlap_means >= actual_overlap_mean))

    return pd.Series(
        {
            "chi_square_p_value": chi_square_p_value,
            "kl_divergence_real_vs_random_mean": kl_divergence,
            "share_of_numbers_within_random_95pct_band": within_random_band_ratio,
            "actual_consecutive_overlap_mean": actual_overlap_mean,
            "random_overlap_mean": float(np.mean(simulated_overlap_means)),
            "empirical_p_value_for_overlap": overlap_empirical_p,
        }
    )
