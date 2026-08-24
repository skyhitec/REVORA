"""
Model Evaluator and Business Revenue Optimizer for REVORA Phase 2

Computes statistical classification metrics, revenue metrics, and performs
safety-aware threshold selection maximizing Net Recovery Value.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
)

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """Evaluates ML models using statistical metrics and monetized revenue formulas."""

    def __init__(self, cost_per_retry: float = 10.0) -> None:
        """
        Initializes evaluator.

        Args:
            cost_per_retry: Retry/intervention cost per attempt (default INR 10.0).
        """
        self.cost_per_retry = cost_per_retry

    def evaluate_statistical_metrics(
        self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Calculates standard classification metrics on raw model probabilities."""
        y_pred = (y_prob >= threshold).astype(int)

        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5

        p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(r_curve, p_curve))

        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        return {
            "threshold": threshold,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
        }

    def evaluate_business_metrics(
        self,
        df_failed: pd.DataFrame,
        y_prob: np.ndarray,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Computes business revenue metrics and detailed metric reconciliation.

        Args:
            df_failed: DataFrame of FAILED transactions (must contain 'amount', 'recovered', 'is_retryable').
            y_prob: Predicted recovery probabilities.
            threshold: Probability decision threshold.

        Returns:
            Dict containing detailed revenue, count reconciliation, and rate metrics.
        """
        total_failed_count = len(df_failed)
        amounts = df_failed["amount"].values
        y_true = df_failed["recovered"].values
        is_retryable = df_failed["is_retryable"].values.astype(bool)

        # 1. Raw Model Positives (prob >= threshold) before guardrail filter
        raw_model_positive_mask = y_prob >= threshold
        model_positive_count = int(np.sum(raw_model_positive_mask))

        # 2. Selected Interventions after non-retryable guardrail filter (prob >= threshold AND is_retryable)
        selected_mask = raw_model_positive_mask & is_retryable
        actual_intervention_count = int(np.sum(selected_mask))

        # 3. Non-retryable Filtered Count (model predicted positive but blocked by guardrail)
        non_retryable_filtered_count = int(model_positive_count - actual_intervention_count)

        # 4. Actual Recovered Count & Amounts among selected interventions
        actual_recovered_amounts = np.where(y_true[selected_mask] == 1.0, amounts[selected_mask], 0.0)
        actual_recovered_among_interventions = int(np.sum(y_true[selected_mask] == 1.0))
        gross_revenue_recovered = float(np.sum(actual_recovered_amounts))

        # 5. Monetary Revenue Calculations
        revenue_at_risk = float(np.sum(amounts))
        actual_recoverable_revenue = float(np.sum(np.where(y_true == 1.0, amounts, 0.0)))
        expected_recoverable_revenue = float(np.sum(amounts * y_prob))
        retry_cost = float(actual_intervention_count * self.cost_per_retry)
        net_revenue_recovered = gross_revenue_recovered - retry_cost

        # 6. Distinct Rate Reconciliation (per user specifications):
        # - Intervention Recovery Rate = actual_recovered_among_interventions / actual_intervention_count
        intervention_recovery_rate = (
            float(actual_recovered_among_interventions / actual_intervention_count)
            if actual_intervention_count > 0
            else 0.0
        )

        # - Intervention Rate = actual_intervention_count / total_failed_count
        intervention_rate = (
            float(actual_intervention_count / total_failed_count)
            if total_failed_count > 0
            else 0.0
        )

        # - Overall Recovery Yield = actual_recovered_among_interventions / total_failed_count
        overall_recovery_yield = (
            float(actual_recovered_among_interventions / total_failed_count)
            if total_failed_count > 0
            else 0.0
        )

        return {
            "threshold": threshold,
            "total_failed_count": total_failed_count,
            "model_positive_count": model_positive_count,
            "non_retryable_filtered_count": non_retryable_filtered_count,
            "actual_intervention_count": actual_intervention_count,
            "actual_recovered_among_interventions": actual_recovered_among_interventions,
            "revenue_at_risk": round(revenue_at_risk, 2),
            "actual_recoverable_revenue": round(actual_recoverable_revenue, 2),
            "expected_recoverable_revenue": round(expected_recoverable_revenue, 2),
            "gross_revenue_recovered": round(gross_revenue_recovered, 2),
            "retry_cost": round(retry_cost, 2),
            "net_revenue_recovered": round(net_revenue_recovered, 2),
            "intervention_recovery_rate": round(intervention_recovery_rate, 4),
            "intervention_rate": round(intervention_rate, 4),
            "overall_recovery_yield": round(overall_recovery_yield, 4),
        }

    def optimize_threshold(
        self,
        df_failed: pd.DataFrame,
        y_prob: np.ndarray,
        max_intervention_rate: float = 0.80,
        max_retry_cost: Optional[float] = None,
        threshold_step: float = 0.01,
    ) -> Tuple[float, pd.DataFrame]:
        """
        Scans thresholds on validation set to find tau* maximizing Net Recovery Value subject to constraints.

        Args:
            df_failed: Validation set FAILED transactions DataFrame.
            y_prob: Validation set predicted recovery probabilities.
            max_intervention_rate: Maximum allowed intervention rate safety constraint (default 0.80).
            max_retry_cost: Maximum allowed total retry cost constraint.
            threshold_step: Step size for threshold grid scan.

        Returns:
            Tuple of (optimal_threshold: float, grid_df: pd.DataFrame)
        """
        thresholds = np.arange(0.05, 0.95 + threshold_step, threshold_step)
        grid_results = []

        best_net_value = -float("inf")
        best_threshold = 0.50

        y_true = df_failed["recovered"].values

        for tau in thresholds:
            tau_round = float(np.round(tau, 4))
            stat_res = self.evaluate_statistical_metrics(y_true, y_prob, threshold=tau_round)
            biz_res = self.evaluate_business_metrics(df_failed, y_prob, threshold=tau_round)

            row = {**stat_res, **biz_res}
            grid_results.append(row)

            # Check safety constraints
            passes_rate_constraint = biz_res["intervention_rate"] <= max_intervention_rate
            passes_cost_constraint = (
                max_retry_cost is None or biz_res["retry_cost"] <= max_retry_cost
            )

            if passes_rate_constraint and passes_cost_constraint:
                if biz_res["net_revenue_recovered"] > best_net_value:
                    best_net_value = biz_res["net_revenue_recovered"]
                    best_threshold = tau_round

        grid_df = pd.DataFrame(grid_results)
        logger.info(
            "Threshold optimization complete. Optimal threshold tau* = %.4f (Max Rate Constraint: %.2f, Net Recovery: INR %.2f)",
            best_threshold,
            max_intervention_rate,
            best_net_value,
        )
        return best_threshold, grid_df
