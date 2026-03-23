from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_main_number_frequency(number_freq, expected_freq: float):
    plt.figure(figsize=(14, 6))
    sns.barplot(x=number_freq.index, y=number_freq.values, color="steelblue")
    plt.axhline(
        expected_freq,
        color="crimson",
        linestyle="--",
        label=f"Uniform expectation ({expected_freq:.1f})",
    )
    plt.title("Main Number Frequency vs Uniform Expectation")
    plt.xlabel("Number")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_bonus_number_frequency(bonus_freq, expected_bonus_freq: float):
    plt.figure(figsize=(14, 6))
    sns.barplot(x=bonus_freq.index, y=bonus_freq.values, color="darkorange")
    plt.axhline(
        expected_bonus_freq,
        color="crimson",
        linestyle="--",
        label=f"Uniform expectation ({expected_bonus_freq:.1f})",
    )
    plt.title("Bonus Number Frequency vs Uniform Expectation")
    plt.xlabel("Bonus number")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_count_distribution(series, title: str, xlabel: str, ylabel: str = "Count"):
    plt.figure(figsize=(10, 6))
    sns.countplot(x=series)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()
