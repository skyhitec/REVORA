"""
Unit tests for DatasetSplitter.
"""

import pytest

from src.data.generator import PaymentDataGenerator
from src.data.split import DatasetSplitter


def test_split_proportions_and_no_overlap():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=2000)

    splitter = DatasetSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42)
    splits = splitter.split(df)

    train_df = splits["train"]
    val_df = splits["validation"]
    test_df = splits["test"]

    total = len(df)
    assert len(train_df) == int(total * 0.70)
    assert len(val_df) == int(total * 0.15)
    assert len(test_df) == total - len(train_df) - len(val_df)

    # Zero overlap check
    train_ids = set(train_df["transaction_id"])
    val_ids = set(val_df["transaction_id"])
    test_ids = set(test_df["transaction_id"])

    assert len(train_ids.intersection(val_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(val_ids.intersection(test_ids)) == 0


def test_stratification_preserves_target_distribution():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=2000)

    splitter = DatasetSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42)
    splits = splitter.split(df)

    failed_total = df[df["payment_status"] == "FAILED"]
    overall_recovery_rate = (failed_total["recovered"] == 1.0).mean()

    for name, split_df in splits.items():
        failed_split = split_df[split_df["payment_status"] == "FAILED"]
        split_rec_rate = (failed_split["recovered"] == 1.0).mean()
        # Recovery rate in each split should be within +/- 3% of overall recovery rate
        assert pytest.approx(split_rec_rate, abs=0.03) == overall_recovery_rate
