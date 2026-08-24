#!/usr/bin/env python3
"""
REVORA Phase 2 Evaluation CLI Script

Evaluates final persisted model on locked test set data/processed/test.csv.
Performs ONE-TIME final evaluation report without tuning model parameters.

Usage:
    python scripts/evaluate_model.py
"""

import json
import os
import sys
import pickle
import pandas as pd

# Ensure root workspace directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ml.evaluator import ModelEvaluator
from src.ml.inference import RecoveryInferenceEngine
from src.utils.logging_utils import get_logger, setup_logging

logger = get_logger("scripts.evaluate_model")


def main():
    setup_logging()
    logger.info("=== REVORA Phase 2: Final Test Set Evaluation Task ===")

    test_path = "data/processed/test.csv"
    models_dir = "models"

    pipeline_file = os.path.join(models_dir, "feature_pipeline.pkl")
    model_file = os.path.join(models_dir, "recovery_model.pkl")
    meta_file = os.path.join(models_dir, "model_metadata.json")

    if not os.path.exists(test_path):
        logger.error("Test set file %s not found!", test_path)
        sys.exit(1)

    if not os.path.exists(model_file) or not os.path.exists(pipeline_file) or not os.path.exists(meta_file):
        logger.error("Model artifacts not found in %s/! Please run python scripts/train_model.py first.", models_dir)
        sys.exit(1)

    # 1. Load Artifacts
    with open(pipeline_file, "rb") as f:
        pipeline = pickle.load(f)

    with open(model_file, "rb") as f:
        model = pickle.load(f)

    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    optimal_tau = metadata.get("optimal_threshold", 0.50)

    # 2. Load Locked Test Set
    test_df = pd.read_csv(test_path)
    logger.info("Loaded locked Test set (%d total rows)", len(test_df))

    # Transform Test set
    X_test, y_test, test_failed = pipeline.transform(test_df)

    if len(test_failed) == 0:
        logger.error("No FAILED transactions in test set!")
        sys.exit(1)

    # 3. Score Test set
    test_probs = model.predict_proba(X_test)

    # 4. Evaluate Test Set Metrics
    evaluator = ModelEvaluator(cost_per_retry=10.0)
    stat_metrics = evaluator.evaluate_statistical_metrics(y_test, test_probs, threshold=optimal_tau)
    biz_metrics = evaluator.evaluate_business_metrics(test_failed, test_probs, threshold=optimal_tau)

    # 5. Format Final Report with Metric Reconciliation
    report = [
        "==========================================================",
        "REVORA PHASE 2 — FINAL HELD-OUT TEST SET EVALUATION REPORT",
        "==========================================================",
        f"Evaluated Transactions (FAILED): {len(test_failed):,}",
        f"Optimal Decision Threshold (tau*): {optimal_tau:.4f}",
        "",
        "--- METRIC RECONCILIATION AUDIT ---",
        f"Total Failed Transactions:         {biz_metrics['total_failed_count']}",
        f"Model-Positive Count (raw prob >= tau*): {biz_metrics['model_positive_count']} ({biz_metrics['model_positive_count']/biz_metrics['total_failed_count']*100:.2f}%)",
        f"Non-Retryable Filtered Count:      {biz_metrics['non_retryable_filtered_count']} (Blocked by Guardrail)",
        f"Actual Intervention Count:         {biz_metrics['actual_intervention_count']} (Selected for Retry)",
        f"Actual Recovered in Interventions: {biz_metrics['actual_recovered_among_interventions']} (Ground Truth Recovered)",
        f"Intervention Rate:                 {biz_metrics['intervention_rate']*100:.2f}% ({biz_metrics['actual_intervention_count']} / {biz_metrics['total_failed_count']})",
        f"Intervention Recovery Rate:        {biz_metrics['intervention_recovery_rate']*100:.2f}% ({biz_metrics['actual_recovered_among_interventions']} / {biz_metrics['actual_intervention_count']})",
        f"Overall Recovery Yield:            {biz_metrics['overall_recovery_yield']*100:.2f}% ({biz_metrics['actual_recovered_among_interventions']} / {biz_metrics['total_failed_count']})",
        "",
        "--- BUSINESS REVENUE & MONETARY METRICS ---",
        f"Revenue at Risk:                  INR {biz_metrics['revenue_at_risk']:,.2f}",
        f"Actual Recoverable Revenue:       INR {biz_metrics['actual_recoverable_revenue']:,.2f}",
        f"Expected Recoverable Revenue:     INR {biz_metrics['expected_recoverable_revenue']:,.2f}",
        f"Gross Revenue Recovered:          INR {biz_metrics['gross_revenue_recovered']:,.2f}",
        f"Retry / Intervention Cost:        INR {biz_metrics['retry_cost']:,.2f}",
        f"Net Revenue Recovered:            INR {biz_metrics['net_revenue_recovered']:,.2f}",
        "",
        "--- STATISTICAL CLASSIFICATION METRICS (RAW MODEL PROBABILITIES) ---",
        f"Precision:         {stat_metrics['precision']:.4f}",
        f"Recall:            {stat_metrics['recall']:.4f}",
        f"F1-Score:          {stat_metrics['f1']:.4f}",
        f"ROC-AUC:           {stat_metrics['roc_auc']:.4f}",
        f"PR-AUC:            {stat_metrics['pr_auc']:.4f}",
        f"Confusion Matrix:  TN={stat_metrics['confusion_matrix']['TN']}, FP={stat_metrics['confusion_matrix']['FP']}, FN={stat_metrics['confusion_matrix']['FN']}, TP={stat_metrics['confusion_matrix']['TP']}",
        "==========================================================",
    ]

    print("\n" + "\n".join(report) + "\n")
    logger.info("=== Final Test Set Evaluation Completed Successfully ===")


if __name__ == "__main__":
    main()
