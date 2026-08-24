"""
Unit tests for PaymentDataGenerator.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import PaymentDataGenerator
from src.data.validation import REQUIRED_COLUMNS


def test_generator_row_count_and_columns():
    generator = PaymentDataGenerator(seed=42)
    rows = 500
    df = generator.generate(num_rows=rows)

    assert len(df) == rows
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing expected column: {col}"


def test_generator_id_uniqueness():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=1000)

    assert df["transaction_id"].nunique() == 1000, "Transaction IDs must be unique"


def test_generator_deterministic_seed():
    gen1 = PaymentDataGenerator(seed=123)
    df1 = gen1.generate(num_rows=300)

    gen2 = PaymentDataGenerator(seed=123)
    df2 = gen2.generate(num_rows=300)

    pd.testing.assert_frame_equal(df1, df2)


def test_generator_target_separation():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=1000)

    # SUCCESS transactions should have NaN target
    success_df = df[df["payment_status"] == "SUCCESS"]
    assert len(success_df) > 0
    assert success_df["recovered"].isnull().all()
    assert success_df["recovery_probability_target"].isnull().all()

    # FAILED transactions should have valid non-null target
    failed_df = df[df["payment_status"] == "FAILED"]
    assert len(failed_df) > 0
    assert failed_df["recovered"].isin([0.0, 1.0]).all()
    assert (failed_df["recovery_probability_target"] >= 0.0).all()
    assert (failed_df["recovery_probability_target"] <= 1.0).all()
