from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_sum_distribution(sum_series):
    sum_mean = sum_series.mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(sum_series, bins=25, kde=True, color="slateblue", ax=ax)
    ax.axvline(sum_mean, color="crimson", linestyle="--", label=f"Mean ({sum_mean:.1f})")
    ax.set_title("Distribution of Main-Number Sum")
    ax.set_xlabel("Sum of six main numbers")
    ax.set_ylabel("Count")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return fig


def plot_sum_over_time(rounds, sum_values, rolling_mean):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rounds, sum_values, alpha=0.35, label="Round sum")
    ax.plot(rounds, rolling_mean, color="crimson", linewidth=2, label="20-round rolling mean")
    ax.set_title("Main-Number Sum Over Time")
    ax.set_xlabel("Round")
    ax.set_ylabel("Sum")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return fig


def plot_correlation_heatmap(corr, mask=None):
    fig, ax = plt.subplots(figsize=(13, 11))
    sns.heatmap(
        corr,
        cmap="coolwarm",
        center=0,
        vmin=-0.2,
        vmax=0.2,
        mask=mask,
        square=True,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title("Pairwise Correlation Heatmap for Main Numbers")
    plt.tight_layout()
    plt.show()
    return fig
