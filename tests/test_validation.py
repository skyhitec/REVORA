"""
Unit tests for DataValidator.
"""

import pandas as pd
import pytest

from src.data.generator import PaymentDataGenerator
from src.data.validation import DataValidator


def test_valid_dataset_passes():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    validator = DataValidator(df)
    is_valid, report = validator.validate()

    assert is_valid is True, f"Valid dataset failed validation report:\n{report}"
    assert "Status: PASS" in report


def test_duplicate_transaction_ids_detected():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    # Duplicate first row
    df.loc[1, "transaction_id"] = df.loc[0, "transaction_id"]

    validator = DataValidator(df)
    is_valid, report = validator.validate()

    assert is_valid is False
    assert "duplicate transaction_ids" in report


def test_invalid_amounts_detected():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    # Set negative amount
    df.loc[5, "amount"] = -100.0

    validator = DataValidator(df)
    is_valid, report = validator.validate()

    assert is_valid is False
    assert "non-positive transaction amounts" in report


def test_missing_required_column_detected():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    df_dropped = df.drop(columns=["payment_method"])

    validator = DataValidator(df_dropped)
    is_valid, report = validator.validate()

    assert is_valid is False
    assert "Missing required columns" in report


def test_data_leakage_detected():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    # Add leakage column
    df["actual_recovery_action_result"] = "RETRY_SUCCESS"

    validator = DataValidator(df)
    is_valid, report = validator.validate()

    assert is_valid is False
    assert "Data leakage detected" in report
