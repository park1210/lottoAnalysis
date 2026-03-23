from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.correlation_analysis import calculate_consecutive_overlap


ALL_NUMBERS = np.arange(1, 46)


def generate_random_draws(n_draws: int, rng: np.random.Generator) -> np.ndarray:
    return np.array(
        [rng.choice(ALL_NUMBERS, size=6, replace=False) for _ in range(n_draws)]
    )


def calculate_frequency_from_draws(draws: np.ndarray) -> pd.Series:
    return pd.Series(np.bincount(draws.ravel(), minlength=46)[1:], index=ALL_NUMBERS)


def simulate_random_frequency_baseline(
    n_draws: int,
    n_simulations: int = 2000,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    freq_matrix = np.zeros((n_simulations, 45), dtype=int)
    overlap_means = np.zeros(n_simulations)

    for i in range(n_simulations):
        draws = generate_random_draws(n_draws, rng)
        freq_matrix[i] = calculate_frequency_from_draws(draws).values
        overlap_means[i] = calculate_consecutive_overlap(draws).mean()

    return freq_matrix, overlap_means


def simulate_random_hit_baseline(
    actual_number_lists: list[list[int]],
    n_simulations: int = 2000,
    seed: int = 42,
) -> pd.Series:
    mean_hits = []

    for sim in range(n_simulations):
        rng = np.random.default_rng(seed + sim)
        predictions = [
            sorted(rng.choice(ALL_NUMBERS, size=6, replace=False).tolist())
            for _ in range(len(actual_number_lists))
        ]
        scores = [
            len(set(pred) & set(actual))
            for pred, actual in zip(predictions, actual_number_lists)
        ]
        mean_hits.append(np.mean(scores))

    return pd.Series(mean_hits, name="random_mean_hit")
