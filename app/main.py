from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_LOTTO_FILE
from src.data.load_data import load_lotto_source
from src.data.preprocess import preprocess_lotto_data, save_processed_lotto
from src.data.validate_data import (
    validate_number_ranges,
    validate_processed_columns,
    validate_unique_main_numbers,
)
from src.features.build_features import build_feature_dataset
from src.models.model_suite import run_full_model_suite


def run_data_pipeline(
    source: str = "excel",
    start_round: int = 1,
    end_round: int | None = None,
) -> Path:
    raw_df = load_lotto_source(source=source, start_round=start_round, end_round=end_round)
    clean_df = preprocess_lotto_data(raw_df)
    validate_processed_columns(clean_df)
    validate_number_ranges(clean_df)
    validate_unique_main_numbers(clean_df)
    save_processed_lotto(clean_df, PROCESSED_LOTTO_FILE)
    return PROCESSED_LOTTO_FILE


def run_feature_pipeline(window: int = 20):
    return build_feature_dataset(window=window)


def run_model_pipeline(
    window: int = 20,
    test_ratio: float = 0.2,
    random_seed: int = 42,
    backtest_initial_train_size: int = 600,
    backtest_test_size: int = 30,
    backtest_step_size: int = 30,
):
    return run_full_model_suite(
        window=window,
        test_ratio=test_ratio,
        random_seed=random_seed,
        backtest_initial_train_size=backtest_initial_train_size,
        backtest_test_size=backtest_test_size,
        backtest_step_size=backtest_step_size,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the lotto-analysis pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    data_parser = subparsers.add_parser("data", help="Collect/load and preprocess lotto data.")
    # 'auto' and 'auto_browser' are exposed for ongoing development, but
    # 'excel' remains the recommended stable source today.
    data_parser.add_argument("--source", choices=["excel", "auto", "auto_browser"], default="excel")
    data_parser.add_argument("--start-round", type=int, default=1)
    data_parser.add_argument("--end-round", type=int, default=None)

    feature_parser = subparsers.add_parser("features", help="Build model features.")
    feature_parser.add_argument("--window", type=int, default=20)

    model_parser = subparsers.add_parser("model", help="Run the full modeling suite.")
    model_parser.add_argument("--window", type=int, default=20)
    model_parser.add_argument("--test-ratio", type=float, default=0.2)
    model_parser.add_argument("--random-seed", type=int, default=42)
    model_parser.add_argument("--backtest-initial-train-size", type=int, default=600)
    model_parser.add_argument("--backtest-test-size", type=int, default=30)
    model_parser.add_argument("--backtest-step-size", type=int, default=30)

    all_parser = subparsers.add_parser("all", help="Run data, features, and model pipeline end-to-end.")
    all_parser.add_argument("--source", choices=["excel", "auto", "auto_browser"], default="excel")
    all_parser.add_argument("--start-round", type=int, default=1)
    all_parser.add_argument("--end-round", type=int, default=None)
    all_parser.add_argument("--window", type=int, default=20)
    all_parser.add_argument("--test-ratio", type=float, default=0.2)
    all_parser.add_argument("--random-seed", type=int, default=42)
    all_parser.add_argument("--backtest-initial-train-size", type=int, default=600)
    all_parser.add_argument("--backtest-test-size", type=int, default=30)
    all_parser.add_argument("--backtest-step-size", type=int, default=30)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "data":
        output_path = run_data_pipeline(
            source=args.source,
            start_round=args.start_round,
            end_round=args.end_round,
        )
        print(f"Processed data saved to: {output_path}")
        return

    if args.command == "features":
        feature_df = run_feature_pipeline(window=args.window)
        print(f"Feature dataset shape: {feature_df.shape}")
        return

    if args.command == "model":
        results = run_model_pipeline(
            window=args.window,
            test_ratio=args.test_ratio,
            random_seed=args.random_seed,
            backtest_initial_train_size=args.backtest_initial_train_size,
            backtest_test_size=args.backtest_test_size,
            backtest_step_size=args.backtest_step_size,
        )
        print("Holdout summary:")
        print(results["holdout_summary"])
        print("\nBacktest summary:")
        print(results["backtest_summary"])
        return

    if args.command == "all":
        run_data_pipeline(
            source=args.source,
            start_round=args.start_round,
            end_round=args.end_round,
        )
        run_feature_pipeline(window=args.window)
        results = run_model_pipeline(
            window=args.window,
            test_ratio=args.test_ratio,
            random_seed=args.random_seed,
            backtest_initial_train_size=args.backtest_initial_train_size,
            backtest_test_size=args.backtest_test_size,
            backtest_step_size=args.backtest_step_size,
        )
        print("Pipeline completed.")
        print("Holdout summary:")
        print(results["holdout_summary"])
        return


if __name__ == "__main__":
    main()
