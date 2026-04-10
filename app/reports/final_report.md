# Lotto Analysis Final Report

## Project Goal

This project analyzes historical Korean Lotto 6/45 data to answer three main questions:

1. Does the historical number distribution look materially different from a random process?
2. Can forecasting-oriented features be built from past draws without leakage?
3. Do any model and feature combinations outperform random-style baselines in a meaningful and repeatable way?

## Data Pipeline

The project uses a notebook-first workflow with canonical saved files.

- raw workbook: `app/data/raw/lotto_history_latest.xlsx`
- processed lotto file: `app/data/processed/lotto_cleaned.csv`
- weather metadata: `app/data/external/draw_metadata.csv`
- weather cache: `app/data/external/weather_observations.csv`
- draw-level weather context: `app/data/external/weather_draw_context.csv`

The current collection workflow is:

- `python main.py sync` for lotto updates
- `python main.py weather-fetch` for weather cache collection
- `python main.py weather-build` for draw-level weather context construction

## Exploratory Analysis

The exploratory stage focuses on:

- main-number frequency vs uniform expectation
- bonus-number frequency vs uniform expectation
- odd-even balance
- low-high balance
- total-sum distribution
- time-trend inspection
- pairwise number correlation

Saved EDA assets:

- `fig_01_main_number_frequency.png`
- `fig_02_bonus_number_frequency.png`
- `fig_03_odd_even_pattern.png`
- `fig_04_low_high_split.png`
- `fig_05_sum_distribution.png`

## Randomness Tests

The statistical testing stage compares real outcomes against Monte Carlo baselines.

Key checks:

- frequency comparison against simulated random draws
- chi-square test for uniformity
- KL divergence against simulated distributions
- consecutive-draw overlap comparison

Saved outputs:

- `fig_06_real_vs_random_frequency.png`
- `fig_06b_consecutive_draw_overlap.png`
- `table_04_randomness_test_summary.csv`

Interpretation: the project continues to support a conservative view that the historical data does not show strong evidence of large structural bias away from a random process.

## Feature Engineering

The baseline feature set is forecasting-oriented and currently includes:

- rolling recent-frequency features
- gap features measuring time since each number last appeared

These are aligned so each row uses only information available before the target draw.

## Calendar Context Extension

The calendar-context notebook derives:

- month
- season
- year
- day of month

It then compares:

- number-frequency distributions across context groups
- draw-pattern distributions such as `sum_main`, `odd_count`, and `low_count`

Saved outputs:

- `fig_11` to `fig_17`
- `table_10` to `table_14`

Interpretation: calendar context is useful as a descriptive analysis layer, but it has not yet produced strong evidence of a stable predictive advantage.

## Weather Extension

The weather pipeline builds draw-level weather context from KMA API Hub observations.

Saved analysis outputs:

- `fig_18` to `fig_25`
- `table_15` to `table_19`

Current measured weather status:

- `temp_at_draw`, `humidity_at_draw`, `wind_at_draw`, and `pressure_at_draw` are available for all `1217` draws
- `rain_flag` is now non-zero after revising the rain proxy
- `rain_flag = 94` draws, about `7.72%`
- `snow_flag = 6` draws, about `0.49%`
- daily weather aggregates are still unavailable in the saved run

Current statistical interpretation from `table_17_weather_pattern_test_summary.csv`:

- rain vs non-rain group tests do not show small p-values for `sum_main`, `odd_count`, or `low_count`
- snow vs non-snow tests also do not show small p-values
- temperature-bin and humidity-bin Kruskal tests do not show strong distribution shifts

Interpretation: weather context is currently more useful as exploratory context than as a strong direct explanatory driver of lotto outcomes.

## Weather-Aware Feature Modeling

`09_weather_feature_modeling.ipynb` compares whether calendar and weather variables improve the temporal baseline.

Saved outputs:

- `fig_26_weather_feature_holdout_comparison.png`
- `fig_27_weather_feature_backtest_comparison.png`
- `fig_28_weather_feature_backtest_trend.png`
- `table_20_weather_feature_holdout_summary.csv`
- `table_21_weather_feature_backtest_summary.csv`
- `table_22_weather_feature_backtest_results.csv`

Measured results:

- holdout `avg_hit`
  - `base = 0.8708`
  - `base_plus_calendar = 0.8583`
  - `base_plus_calendar_weather = 0.8458`
  - `calendar_weather_only = 0.8292`
- rolling backtest `mean_avg_hit`
  - `base = 0.8389`
  - `base_plus_calendar_weather = 0.8139`
  - `base_plus_calendar = 0.7944`
  - `calendar_weather_only = 0.7722`

Interpretation: the existing temporal baseline remains strongest. Calendar and weather context are better interpreted as explanatory covariates than as direct performance-improving predictors in the current setup.

## Baseline Modeling

The baseline modeling suite includes:

- `freq_heuristic`
- `gap_heuristic`
- `random_baseline`
- `logistic_regression`
- `random_forest`
- `xgboost`
- `classifier_chain`

Saved outputs:

- `table_05_holdout_summary.csv`
- `table_06_backtest_summary.csv`
- `table_07_draw_level_results.csv`
- `table_08_run_metadata.csv`
- `table_09_model_output_paths.csv`
- model artifacts under `app/models/artifacts`

Measured baseline results:

- best holdout `avg_hit`: `classifier_chain = 0.9000`
- next best holdout `avg_hit`: `logistic_regression = 0.8708`
- best rolling backtest `mean_avg_hit`: `random_baseline = 0.8719`
- `logistic_regression` remains close in rolling backtest: `0.8684`
- all major runs still have `subset_accuracy = 0.0`

Interpretation: no model yet demonstrates a robust and large advantage over random-style baselines.

## Model-Family Comparison

`10_model_family_comparison.ipynb` compares four feature sets across multiple model families.

Feature sets:

- `base`
- `base_plus_pattern`
- `base_plus_context`
- `full_feature_set`

Model families:

- heuristic baselines
- linear model
- tree-based models
- classifier chain
- shallow neural network

Saved outputs:

- `fig_29_model_family_holdout_heatmap.png`
- `fig_30_model_family_backtest_heatmap.png`
- `fig_31_model_family_top_comparison.png`
- `fig_32_model_family_backtest_trend.png`
- `table_23_model_family_holdout_summary.csv`
- `table_24_model_family_backtest_summary.csv`
- `table_25_model_family_full_results.csv`

Measured results:

- best holdout combination: `base_plus_pattern + classifier_chain = 0.9042`
- second-best holdout combination: `base + classifier_chain = 0.9000`
- strong context-heavy combinations did not displace internal-pattern feature sets at the top of holdout ranking
- best backtest mean includes `random_baseline = 0.8567`
- `base_plus_context + mlp` matched that backtest mean by average score, but fold-level paths differ and the result should be interpreted cautiously

Interpretation:

- richer internal draw-pattern features appear more promising than weather/calendar context for prediction
- holdout improvements do not automatically transfer to robust rolling-backtest advantages
- model-family diversity is useful for comparison, but the evidence for a stable predictive edge remains limited

## Current Interpretation

At this stage, the project is best interpreted as a structured investigation into predictive limits rather than a claim that lotto outcomes can be strongly forecast.

The current evidence supports four conclusions:

- the historical distribution remains broadly compatible with random-style behavior
- temporal baseline features are still the most stable predictive foundation
- weather and calendar context help more as explanatory context than as direct predictive signal
- richer internal pattern features may help some models, but robust superiority over random-style baselines remains small

## Next Steps

Recommended follow-up work:

- rerun `10_model_family_comparison.ipynb` with scaled MLP inputs to reduce neural-model instability
- test recent-round-only modeling windows such as the most recent `200`, `300`, or `500` draws
- add lagged weather-regime features such as dry/wet streaks and short-term humidity or temperature trends
- compare extreme-weather subsets against matched non-extreme draws
- add feature-importance or coefficient summaries so the strongest feature groups can be interpreted more directly
- refresh legacy figure exports from `02_eda.ipynb` and `06_model_evaluation.ipynb` if those sections are needed in the final presentation
