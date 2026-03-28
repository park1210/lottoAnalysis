from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_main_number_frequency(number_freq, expected_freq: float):
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(x=number_freq.index, y=number_freq.values, color="steelblue", ax=ax)
    ax.axhline(
        expected_freq,
        color="crimson",
        linestyle="--",
        label=f"Uniform expectation ({expected_freq:.1f})",
    )
    ax.set_title("Main Number Frequency vs Uniform Expectation")
    ax.set_xlabel("Number")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return fig


def plot_bonus_number_frequency(bonus_freq, expected_bonus_freq: float):
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(x=bonus_freq.index, y=bonus_freq.values, color="darkorange", ax=ax)
    ax.axhline(
        expected_bonus_freq,
        color="crimson",
        linestyle="--",
        label=f"Uniform expectation ({expected_bonus_freq:.1f})",
    )
    ax.set_title("Bonus Number Frequency vs Uniform Expectation")
    ax.set_xlabel("Bonus number")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return fig


def plot_count_distribution(series, title: str, xlabel: str, ylabel: str = "Count"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x=series, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    plt.show()
    return fig
