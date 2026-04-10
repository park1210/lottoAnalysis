# Models

This directory stores modeling outputs separately from raw and processed data.

## Directories

- `artifacts/`
  serialized trained estimators such as `logistic_regression.joblib`
- `results/`
  saved summaries, draw-level outputs, and run metadata from modeling notebooks

## Typical Outputs from `05_model_baseline.ipynb`

- `results/holdout_summary.csv`
- `results/holdout_draw_results.csv`
- `results/backtest_results.csv`
- `results/backtest_summary.csv`
- `results/run_metadata.json`
- `artifacts/logistic_regression.joblib`
- `artifacts/random_forest.joblib`
- `artifacts/xgboost.joblib`
- `artifacts/classifier_chain.joblib`

## Related Report Exports

The report-facing summaries for baseline, weather-aware, and model-family comparison experiments are stored under `app/reports/tables`.

Key examples:

- `table_05_holdout_summary.csv`
- `table_06_backtest_summary.csv`
- `table_20_weather_feature_holdout_summary.csv`
- `table_21_weather_feature_backtest_summary.csv`
- `table_23_model_family_holdout_summary.csv`
- `table_24_model_family_backtest_summary.csv`

The current project structure keeps reusable model artifacts here while keeping report-ready views in `app/reports`.
