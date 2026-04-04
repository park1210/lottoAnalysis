from pathlib import Path


# Resolve the project/app directory from this file so local runs and
# container runs both use the same relative data layout.
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
MODEL_DIR = BASE_DIR / "models"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

RAW_LOTTO_FILE = RAW_DIR / "lotto_history_latest.xlsx"
PROCESSED_LOTTO_FILE = PROCESSED_DIR / "lotto_cleaned.csv"
FEATURE_LOTTO_FILE = PROCESSED_DIR / "lotto_features.csv"
MODEL_OUTPUT_DIR = MODEL_DIR / "results"
MODEL_ARTIFACT_DIR = MODEL_DIR / "artifacts"
HOLDOUT_SUMMARY_FILE = MODEL_OUTPUT_DIR / "holdout_summary.csv"
HOLDOUT_DRAW_RESULTS_FILE = MODEL_OUTPUT_DIR / "holdout_draw_results.csv"
BACKTEST_RESULTS_FILE = MODEL_OUTPUT_DIR / "backtest_results.csv"
BACKTEST_SUMMARY_FILE = MODEL_OUTPUT_DIR / "backtest_summary.csv"
MODEL_RUN_METADATA_FILE = MODEL_OUTPUT_DIR / "run_metadata.json"

DRAW_METADATA_FILE = EXTERNAL_DIR / "draw_metadata.csv"
WEATHER_OBSERVATION_FILE = EXTERNAL_DIR / "weather_observations.csv"
WEATHER_CONTEXT_FILE = EXTERNAL_DIR / "weather_draw_context.csv"
