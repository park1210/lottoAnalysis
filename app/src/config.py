from pathlib import Path


# Resolve the project/app directory from this file so local runs and
# container runs both use the same relative data layout.
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_LOTTO_FILE = RAW_DIR / "lotto_history_1214.xlsx"
AUTO_RAW_LOTTO_FILE = RAW_DIR / "lotto_history_auto.csv"
PROCESSED_LOTTO_FILE = PROCESSED_DIR / "lotto_cleaned.csv"
FEATURE_LOTTO_FILE = PROCESSED_DIR / "lotto_features.csv"
MODEL_OUTPUT_DIR = PROCESSED_DIR / "model_outputs"
HOLDOUT_SUMMARY_FILE = MODEL_OUTPUT_DIR / "holdout_summary.csv"
HOLDOUT_DRAW_RESULTS_FILE = MODEL_OUTPUT_DIR / "holdout_draw_results.csv"
BACKTEST_RESULTS_FILE = MODEL_OUTPUT_DIR / "backtest_results.csv"
BACKTEST_SUMMARY_FILE = MODEL_OUTPUT_DIR / "backtest_summary.csv"
MODEL_RUN_METADATA_FILE = MODEL_OUTPUT_DIR / "run_metadata.json"
