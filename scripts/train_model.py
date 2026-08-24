#!/usr/bin/env python3
"""
REVORA Phase 2 Model Training CLI Script

Trains Baseline Logistic Regression and Primary Advanced XGBoost models on train.csv,
evaluates performance and optimizes threshold on val.csv, and saves artifacts to models/.

Usage:
    python scripts/train_model.py
"""

import json
import os
import sys
import pickle
import pandas as pd

# Ensure root workspace directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ml.feature_engineering import FeaturePipeline
from src.ml.baseline import BaselineLogisticRegression
from src.ml.trainer import XGBoostRecoveryModel
from src.ml.evaluator import ModelEvaluator
from src.utils.logging_utils import get_logger, setup_logging

logger = get_logger("scripts.train_model")


def main():
    setup_logging()
    logger.info("=== REVORA Phase 2: Model Training Task ===")

    train_path = "data/processed/train.csv"
    val_path = "data/processed/val.csv"
    models_dir = "models"

    if not os.path.exists(train_path) or not os.path.exists(val_path):
        logger.error("Phase 1 splits not found! Please run python scripts/generate_dataset.py --rows 20000 --seed 42 first.")
        sys.exit(1)

    # 1. Load Training and Validation Sets (Test set remains LOCKED)
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    logger.info("Loaded Training split (%d rows) and Validation split (%d rows)", len(train_df), len(val_df))

    # 2. Fit Feature Pipeline ONLY on Training set
    pipeline = FeaturePipeline()
    X_train, y_train, train_failed = pipeline.fit_transform(train_df)

    # Transform Validation set
    X_val, y_val, val_failed = pipeline.transform(val_df)

    # 3. Train Baseline Logistic Regression Model
    baseline = BaselineLogisticRegression(random_state=42)
    baseline.fit(X_train, y_train)
    val_baseline_probs = baseline.predict_proba(X_val)

    # 4. Train Primary Advanced XGBoost Model
    xgb_model = XGBoostRecoveryModel(n_estimators=150, max_depth=4, learning_rate=0.05, random_state=42)
    xgb_model.fit(X_train, y_train)
    val_xgb_probs = xgb_model.predict_proba(X_val)

    # 5. Model Evaluation and Business Metric Comparison on Validation Set
    evaluator = ModelEvaluator(cost_per_retry=10.0)

    baseline_stat = evaluator.evaluate_statistical_metrics(y_val, val_baseline_probs, threshold=0.5)
    xgb_stat = evaluator.evaluate_statistical_metrics(y_val, val_xgb_probs, threshold=0.5)

    baseline_biz = evaluator.evaluate_business_metrics(val_failed, val_baseline_probs, threshold=0.5)
    xgb_biz = evaluator.evaluate_business_metrics(val_failed, val_xgb_probs, threshold=0.5)

    logger.info("=== Validation Set Baseline vs XGBoost Comparison (Default Threshold 0.50) ===")
    logger.info("Baseline Logistic Regression — ROC-AUC: %.4f | PR-AUC: %.4f | F1: %.4f | Net Recovery: INR %.2f",
                baseline_stat["roc_auc"], baseline_stat["pr_auc"], baseline_stat["f1"], baseline_biz["net_revenue_recovered"])
    logger.info("XGBoost Advanced Model     — ROC-AUC: %.4f | PR-AUC: %.4f | F1: %.4f | Net Recovery: INR %.2f",
                xgb_stat["roc_auc"], xgb_stat["pr_auc"], xgb_stat["f1"], xgb_biz["net_revenue_recovered"])

    # 6. Optimize Intervention Threshold tau* on Validation Set
    optimal_tau, grid_df = evaluator.optimize_threshold(val_failed, val_xgb_probs, max_intervention_rate=0.80)
    opt_stat = evaluator.evaluate_statistical_metrics(y_val, val_xgb_probs, threshold=optimal_tau)
    opt_biz = evaluator.evaluate_business_metrics(val_failed, val_xgb_probs, threshold=optimal_tau)

    logger.info("=== Optimal Threshold Evaluation (tau* = %.4f) ===", optimal_tau)
    logger.info("Net Recovery Value:          INR %.2f", opt_biz["net_revenue_recovered"])
    logger.info("Gross Revenue Recovered:     INR %.2f", opt_biz["gross_revenue_recovered"])
    logger.info("Retry / Intervention Cost:   INR %.2f", opt_biz["retry_cost"])
    logger.info("Intervention Recovery Rate:  %.2f%%", opt_biz["intervention_recovery_rate"] * 100)
    logger.info("Intervention Rate:           %.2f%%", opt_biz["intervention_rate"] * 100)
    logger.info("Overall Recovery Yield:      %.2f%%", opt_biz["overall_recovery_yield"] * 100)

    # 7. Persist Models and Metadata to models/
    os.makedirs(models_dir, exist_ok=True)

    pipeline_file = os.path.join(models_dir, "feature_pipeline.pkl")
    model_file = os.path.join(models_dir, "recovery_model.pkl")
    meta_file = os.path.join(models_dir, "model_metadata.json")

    with open(pipeline_file, "wb") as f:
        pickle.dump(pipeline, f)

    with open(model_file, "wb") as f:
        pickle.dump(xgb_model, f)

    metadata = {
        "model_type": "XGBoostClassifier",
        "optimal_threshold": optimal_tau,
        "validation_baseline_metrics": {**baseline_stat, **baseline_biz},
        "validation_xgb_default_metrics": {**xgb_stat, **xgb_biz},
        "validation_xgb_optimal_metrics": {**opt_stat, **opt_biz},
        "feature_list": pipeline.feature_names_,
        "num_features": len(pipeline.feature_names_),
    }

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Saved model artifacts to %s/", models_dir)
    logger.info("=== Model Training Task Completed Successfully ===")


if __name__ == "__main__":
    main()
