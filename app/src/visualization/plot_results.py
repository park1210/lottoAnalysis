from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def plot_holdout_metric_bars(summary_df):
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    plot_frame = summary_df.sort_values("avg_hit", ascending=False)

    sns.barplot(data=plot_frame, x="avg_hit", y="model", ax=axes[0], color="steelblue")
    axes[0].set_title("Holdout Average Hit Count")
    axes[0].set_xlabel("Average hit count")
    axes[0].set_ylabel("")

    sns.barplot(
        data=plot_frame,
        x="number_level_accuracy",
        y="model",
        ax=axes[1],
        color="darkorange",
    )
    axes[1].set_title("Holdout Number-Level Accuracy")
    axes[1].set_xlabel("Accuracy")
    axes[1].set_ylabel("")

    sns.barplot(data=plot_frame, x="subset_accuracy", y="model", ax=axes[2], color="seagreen")
    axes[2].set_title("Holdout Subset Accuracy")
    axes[2].set_xlabel("Accuracy")
    axes[2].set_ylabel("")

    plt.tight_layout()
    plt.show()


def plot_hit_distribution(hit_distribution):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=hit_distribution, x="hit_count", y="share", hue="model")
    plt.title("Holdout Hit Distribution by Model")
    plt.xlabel("Hit count")
    plt.ylabel("Share of draws")
    plt.tight_layout()
    plt.show()


def plot_backtest_metric_bars(summary_df):
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    plot_frame = summary_df.sort_values("mean_avg_hit", ascending=False)

    sns.barplot(data=plot_frame, x="mean_avg_hit", y="model", ax=axes[0], color="mediumpurple")
    axes[0].set_title("Backtest Mean Average Hit")
    axes[0].set_xlabel("Average hit")
    axes[0].set_ylabel("")

    sns.barplot(
        data=plot_frame,
        x="mean_number_level_accuracy",
        y="model",
        ax=axes[1],
        color="goldenrod",
    )
    axes[1].set_title("Backtest Number-Level Accuracy")
    axes[1].set_xlabel("Accuracy")
    axes[1].set_ylabel("")

    sns.barplot(
        data=plot_frame,
        x="mean_subset_accuracy",
        y="model",
        ax=axes[2],
        color="cadetblue",
    )
    axes[2].set_title("Backtest Subset Accuracy")
    axes[2].set_xlabel("Accuracy")
    axes[2].set_ylabel("")

    plt.tight_layout()
    plt.show()


def plot_backtest_stability(backtest_results):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=backtest_results, x="fold", y="avg_hit", hue="model", marker="o")
    plt.title("Rolling Backtest Average Hit by Fold")
    plt.xlabel("Backtest fold")
    plt.ylabel("Average hit")
    plt.tight_layout()
    plt.show()
