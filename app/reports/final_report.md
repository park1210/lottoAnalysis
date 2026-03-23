# Lotto Analysis Final Report

## Project Goal

This project analyzes historical Korean lotto data to answer three main questions:

1. Does the historical number distribution look materially different from a random process?
2. Can we build forecasting-oriented features from past draws without leakage?
3. Do simple or more complex models outperform random guessing in a meaningful way?

## Data Pipeline

The project supports two input workflows:

- Manual Excel-based loading
- Automated round-based collection through the official lotto endpoint when available

The raw data is standardized through preprocessing, validated, and saved as a clean tabular dataset for downstream notebooks and modules.

## Exploratory Analysis

The exploratory analysis focuses on:

- Main-number frequency vs. uniform expectation
- Bonus-number frequency vs. uniform expectation
- Odd-even and low-high balance
- Distribution of the total sum of the six main numbers
- Time-trend inspection
- Pairwise correlation between numbers

The purpose of this stage is to look for visible structural bias before applying formal tests.

## Randomness Tests

The statistical testing stage compares real lotto outcomes against Monte Carlo baselines instead of relying on a single random sample.

The main checks include:

- Frequency comparison against a simulated random interval
- Chi-square test for uniformity
- KL divergence between real and simulated distributions
- Consecutive-draw overlap comparison

If these diagnostics remain broadly close to simulated random behavior, the data does not provide strong evidence that the drawing process is non-independent.

## Feature Engineering

The feature set is forecasting-oriented rather than descriptive.

It currently includes:

- Rolling frequency features over recent draws
- Gap features measuring how long it has been since each number last appeared

These features are aligned so that each row uses only information available before the target draw.

## Modeling

The modeling stage includes:

- Frequency heuristic baseline
- Gap heuristic baseline
- Random baseline
- Logistic regression
- Random forest
- XGBoost
- Classifier chain

Model outputs are saved so that evaluation can be run separately from model construction.

## Evaluation

The evaluation stage reports:

- Holdout subset accuracy
- Holdout number-level accuracy
- Holdout average hit count
- Rolling backtest averages across folds
- Draw-level hit distributions

This split makes it easier to compare model families and judge whether added complexity produces a meaningful advantage over heuristics and random guessing.

## Current Interpretation

At this stage, the project is designed less as a claim that lotto outcomes are predictable and more as a structured analysis of whether historical patterns provide usable predictive signal.

The key interpretation is:

- If the real data remains statistically close to simulated random baselines
- And if learned models remain close to heuristic or random performance

then the evidence for strong predictive structure in historical lotto data remains limited.

## Next Steps

Recommended follow-up work:

- Run the full notebook pipeline and refresh saved outputs
- Execute the pytest suite regularly during refactoring
- Add CLI-level automation around the notebook workflow
- Expand the final report with actual measured results from the latest run
