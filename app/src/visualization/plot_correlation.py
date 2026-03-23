from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_sum_distribution(sum_series):
    sum_mean = sum_series.mean()
    plt.figure(figsize=(12, 6))
    sns.histplot(sum_series, bins=25, kde=True, color="slateblue")
    plt.axvline(sum_mean, color="crimson", linestyle="--", label=f"Mean ({sum_mean:.1f})")
    plt.title("Distribution of Main-Number Sum")
    plt.xlabel("Sum of six main numbers")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_sum_over_time(rounds, sum_values, rolling_mean):
    plt.figure(figsize=(14, 6))
    plt.plot(rounds, sum_values, alpha=0.35, label="Round sum")
    plt.plot(rounds, rolling_mean, color="crimson", linewidth=2, label="20-round rolling mean")
    plt.title("Main-Number Sum Over Time")
    plt.xlabel("Round")
    plt.ylabel("Sum")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(corr, mask=None):
    plt.figure(figsize=(13, 11))
    sns.heatmap(
        corr,
        cmap="coolwarm",
        center=0,
        vmin=-0.2,
        vmax=0.2,
        mask=mask,
        square=True,
        cbar_kws={"shrink": 0.8},
    )
    plt.title("Pairwise Correlation Heatmap for Main Numbers")
    plt.tight_layout()
    plt.show()
