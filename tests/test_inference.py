"""
Unit tests for RecoveryInferenceEngine and Policy Guardrails.
"""

import numpy as np
import pandas as pd
import pytest

from src.data.generator import PaymentDataGenerator
from src.ml.evaluator import ModelEvaluator
from src.ml.feature_engineering import FeaturePipeline
from src.ml.inference import NON_RETRYABLE_CODES, RecoveryInferenceEngine
from src.ml.trainer import XGBoostRecoveryModel


def test_inference_engine_guardrail_enforcement():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=500)

    pipeline = FeaturePipeline()
    X, y, _ = pipeline.fit_transform(df)

    model = XGBoostRecoveryModel(n_estimators=30, random_state=42)
    model.fit(X, y)

    engine = RecoveryInferenceEngine(feature_pipeline=pipeline, model=model, optimal_threshold=0.30)
    scored_df = engine.predict_transactions(df)

    assert "predicted_recovery_probability" in scored_df.columns
    assert "should_intervene" in scored_df.columns
    assert "intervention_reason" in scored_df.columns

    # Verify non-retryable categories are NEVER recommended for intervention
    non_retry_mask = scored_df["failure_code"].isin(NON_RETRYABLE_CODES)
    non_retry_interventions = scored_df.loc[non_retry_mask, "should_intervene"]
    assert (non_retry_interventions == False).all(), "Guardrail violation! Non-retryable category recommended for intervention."

    # Verify SUCCESS transactions are unaffected
    success_mask = scored_df["payment_status"] == "SUCCESS"
    assert (scored_df.loc[success_mask, "should_intervene"] == False).all()
    assert scored_df.loc[success_mask, "predicted_recovery_probability"].isnull().all()


def test_intervention_rate_does_not_exceed_max_constraint():
    generator = PaymentDataGenerator(seed=42)
    df = generator.generate(num_rows=1000)

    pipeline = FeaturePipeline()
    X, y, df_failed = pipeline.fit_transform(df)

    model = XGBoostRecoveryModel(n_estimators=50, random_state=42)
    model.fit(X, y)

    probs = model.predict_proba(X)
    evaluator = ModelEvaluator(cost_per_retry=10.0)

    max_limit = 0.80
    opt_tau, _ = evaluator.optimize_threshold(df_failed, probs, max_intervention_rate=max_limit)

    biz_metrics = evaluator.evaluate_business_metrics(df_failed, probs, threshold=opt_tau)
    assert biz_metrics["intervention_rate"] <= max_limit, f"Intervention rate {biz_metrics['intervention_rate']} exceeded max limit {max_limit}"
