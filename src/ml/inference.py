"""
Inference Engine for REVORA Phase 2 Recovery Prediction

Provides high-level inference scoring API for payment transactions, enforcing
policy guardrails and optimal decision thresholds.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.ml.feature_engineering import FeaturePipeline
from src.ml.trainer import XGBoostRecoveryModel
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

NON_RETRYABLE_CODES = {
    "FRAUD_RISK_BLOCK",
    "EXPIRED_CARD",
    "INVALID_PAYMENT_DETAILS",
    "BANK_DECLINED",
    "AUTHENTICATION_FAILURE",
}


class RecoveryInferenceEngine:
    """Production inference engine scoring payment transactions."""

    def __init__(
        self,
        feature_pipeline: FeaturePipeline,
        model: XGBoostRecoveryModel,
        optimal_threshold: float = 0.50,
    ) -> None:
        self.pipeline = feature_pipeline
        self.model = model
        self.optimal_threshold = optimal_threshold

    def predict_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scores input transactions DataFrame, adding prediction and decision columns.

        Args:
            df: Input transactions DataFrame.

        Returns:
            pandas.DataFrame containing scored transactions.
        """
        df_out = df.copy()

        # Identify failed transactions
        failed_mask = df_out["payment_status"] == "FAILED"
        df_failed = df_out[failed_mask].copy()

        # Initialize prediction columns
        df_out["predicted_recovery_probability"] = np.nan
        df_out["should_intervene"] = False
        df_out["intervention_reason"] = "SUCCESS_TRANSACTION_NO_ACTION"

        if len(df_failed) == 0:
            return df_out

        # Transform features
        X_failed, _, _ = self.pipeline.transform(df_failed)

        # Get probabilities from XGBoost model
        probs = self.model.predict_proba(X_failed)

        df_out.loc[failed_mask, "predicted_recovery_probability"] = probs

        # Apply Safety Guardrail & Decision Rule
        should_intervene_flags = []
        reasons = []

        for i, row in df_failed.reset_index(drop=True).iterrows():
            prob = probs[i]
            f_code = row.get("failure_code", "UNKNOWN")
            is_retry = bool(row.get("is_retryable", False))

            if f_code in NON_RETRYABLE_CODES or not is_retry:
                should_intervene_flags.append(False)
                reasons.append(f"GUARDRAIL_BLOCK_NON_RETRYABLE_{f_code}")
            elif prob >= self.optimal_threshold:
                should_intervene_flags.append(True)
                reasons.append(f"RECOMMEND_RETRY_PROB_{prob:.2f}_ABOVE_TAU")
            else:
                should_intervene_flags.append(False)
                reasons.append(f"SKIP_LOW_PROB_{prob:.2f}_BELOW_TAU")

        df_out.loc[failed_mask, "should_intervene"] = should_intervene_flags
        df_out.loc[failed_mask, "intervention_reason"] = reasons

        logger.info(
            "Scored %d failed transactions: %d recommended for intervention (%.1f%%)",
            len(df_failed),
            sum(should_intervene_flags),
            sum(should_intervene_flags) / len(df_failed) * 100,
        )

        return df_out
