"""
Unit tests for Phase 2 FeaturePipeline.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import PaymentDataGenerator
from src.ml.feature_engineering import FeaturePipeline


def test_feature_pipeline_fit_transform():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=500)

    pipeline = FeaturePipeline()
    X, y, failed_df = pipeline.fit_transform(df)

    assert pipeline.is_fitted is True
    assert X.ndim == 2
    assert X.shape[0] == len(failed_df)
    assert len(pipeline.feature_names_) == X.shape[1]
    assert y is not None
    assert len(y) == len(failed_df)
    assert set(np.unique(y)).issubset({0.0, 1.0})


def test_feature_pipeline_transforms_validation_unfitted_raises():
    pipeline = FeaturePipeline()
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=100)

    with pytest.raises(RuntimeError):
        pipeline.transform(df)


def test_feature_pipeline_zero_leakage():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=200)

    pipeline = FeaturePipeline()
    pipeline.fit(df)

    leakage_cols = [
        "recovered",
        "recovery_probability_target",
        "final_recovery_timestamp",
        "actual_recovery_action_result",
    ]
    for feat_name in pipeline.feature_names_:
        for leak in leakage_cols:
            assert leak not in feat_name, f"Leakage column {leak} found in feature names!"
