# Models

This directory stores modeling outputs separately from raw and processed data.

- `artifacts/`
  Serialized trained estimators such as `logistic_regression.joblib`
- `results/`
  Saved summaries, draw-level outputs, and run metadata from the modeling notebook

Typical files created after rerunning `05_model_baseline.ipynb`:

- `results/holdout_summary.csv`
- `results/holdout_draw_results.csv`
- `results/backtest_results.csv`
- `results/backtest_summary.csv`
- `results/run_metadata.json`
- `artifacts/logistic_regression.joblib`
- `artifacts/random_forest.joblib`
- `artifacts/xgboost.joblib`
- `artifacts/classifier_chain.joblib`
