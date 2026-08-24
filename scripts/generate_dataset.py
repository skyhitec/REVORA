#!/usr/bin/env python3
"""
REVORA Dataset Generation CLI Script

Usage:
    python scripts/generate_dataset.py --rows 20000 --seed 42
    python scripts/generate_dataset.py --rows 1000 --seed 42 --output-dir data/sample
"""

import argparse
import os
import sys

# Ensure root workspace directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.generator import PaymentDataGenerator
from src.data.preprocessing import MinimalDataPreprocessor
from src.data.split import DatasetSplitter
from src.data.validation import DataValidator
from src.utils.logging_utils import get_logger, setup_logging

logger = get_logger("scripts.generate_dataset")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic payment dataset for REVORA Phase 1.")
    parser.add_argument("--rows", type=int, default=20000, help="Number of synthetic transaction rows (default: 20000).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible generation (default: 42).")
    parser.add_argument("--config", type=str, default="config/dataset_config.yaml", help="Path to config file.")
    parser.add_argument("--output-dir", type=str, default="data", help="Target base directory for datasets (default: data).")
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_args()

    logger.info("=== REVORA Dataset Generation Task ===")
    logger.info("Rows: %d | Seed: %d | Config: %s | Base Output: %s", args.rows, args.seed, args.config, args.output_dir)

    # 1. Instantiate and run generator
    generator = PaymentDataGenerator(config_path=args.config, seed=args.seed)
    raw_df = generator.generate(num_rows=args.rows)

    # 2. Minimal preprocessing / type cleaning
    preprocessor = MinimalDataPreprocessor()
    clean_df = preprocessor.clean_dataset(raw_df)

    # 3. Data Validation
    validator = DataValidator(clean_df)
    is_valid, summary_report = validator.validate()

    print("\n" + summary_report + "\n")

    if not is_valid:
        logger.error("Validation failed! Dataset generation aborted.")
        sys.exit(1)

    # 4. Save Raw / Clean Dataset
    if args.output_dir == "data/sample":
        raw_dir = os.path.join(args.output_dir)
        processed_dir = os.path.join(args.output_dir)
    else:
        raw_dir = os.path.join(args.output_dir, "raw")
        processed_dir = os.path.join(args.output_dir, "processed")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    raw_path = os.path.join(raw_dir, "transactions.csv")
    clean_df.to_csv(raw_path, index=False)
    logger.info("Saved full dataset to %s (%d rows)", raw_path, len(clean_df))

    # 5. Stratified Train / Val / Test Split
    splitter = DatasetSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=args.seed)
    splits = splitter.split(clean_df)

    train_path = os.path.join(processed_dir, "train.csv")
    val_path = os.path.join(processed_dir, "val.csv")
    test_path = os.path.join(processed_dir, "test.csv")

    splits["train"].to_csv(train_path, index=False)
    splits["validation"].to_csv(val_path, index=False)
    splits["test"].to_csv(test_path, index=False)

    logger.info("Saved splits to:")
    logger.info(" - Train:      %s (%d rows)", train_path, len(splits["train"]))
    logger.info(" - Validation: %s (%d rows)", val_path, len(splits["validation"]))
    logger.info(" - Test:       %s (%d rows)", test_path, len(splits["test"]))
    logger.info("=== Generation Task Completed Successfully ===")


if __name__ == "__main__":
    main()
