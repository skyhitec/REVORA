"""
Unit tests for BaselineLogisticRegression and XGBoostRecoveryModel.
"""

import numpy as np
import pytest

from src.data.generator import PaymentDataGenerator
from src.ml.baseline import BaselineLogisticRegression
from src.ml.feature_engineering import FeaturePipeline
from src.ml.trainer import XGBoostRecoveryModel


def test_baseline_logistic_regression():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=500)

    pipeline = FeaturePipeline()
    X, y, _ = pipeline.fit_transform(df)

    baseline = BaselineLogisticRegression(random_state=42)
    baseline.fit(X, y)

    probs = baseline.predict_proba(X)
    assert len(probs) == len(y)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    preds = baseline.predict(X, threshold=0.5)
    assert set(np.unique(preds)).issubset({0, 1})


def test_xgboost_model_training_and_importances():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=500)

    pipeline = FeaturePipeline()
    X, y, _ = pipeline.fit_transform(df)

    model = XGBoostRecoveryModel(n_estimators=50, max_depth=3, random_state=42)
    model.fit(X, y)

    probs = model.predict_proba(X)
    assert len(probs) == len(y)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    fi_df = model.get_feature_importances(pipeline.feature_names_)
    assert len(fi_df) == len(pipeline.feature_names_)
    assert "feature" in fi_df.columns and "importance" in fi_df.columns
    assert fi_df["importance"].sum() > 0.0
