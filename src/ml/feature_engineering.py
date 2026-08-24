"""
Leak-Free Feature Engineering Pipeline for REVORA Phase 2

Extracts, encodes, scales, and prepares pre-recovery features strictly for
FAILED payment transactions.
"""

from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

PREDICTIVE_NUMERICAL_FEATURES = [
    "amount",
    "customer_payment_success_rate",
    "customer_previous_transactions",
    "customer_previous_failures",
    "days_since_last_successful_payment",
    "ip_risk_score",
    "merchant_risk_score",
]

PREDICTIVE_CATEGORICAL_FEATURES = [
    "payment_method",
    "payment_gateway",
    "card_type",
    "merchant_category",
    "device_type",
    "failure_code",
    "avs_result",
    "cvv_result",
    "authentication_result",
    "bank_response_code",
    "gateway_response_code",
    "is_retryable",
]


class FeaturePipeline:
    """Preprocesses raw transaction DataFrames into ML feature matrices."""

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.is_fitted = False
        self.feature_names_: List[str] = []

    def _extract_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Derives safe pre-recovery features without leakage."""
        df_feat = df.copy()

        # Handle days_since_last_successful_payment missing/sentinel value -1
        days_clean = np.where(
            df_feat["days_since_last_successful_payment"] < 0,
            999.0,
            df_feat["days_since_last_successful_payment"]
        )
        df_feat["days_since_last_success_clean"] = days_clean

        # Pre-recovery failure ratio
        prev_txns = df_feat["customer_previous_transactions"].clip(lower=0)
        prev_fails = df_feat["customer_previous_failures"].clip(lower=0)
        df_feat["recent_failure_ratio"] = prev_fails / (prev_txns + 1.0)

        return df_feat

    def fit(self, df: pd.DataFrame) -> "FeaturePipeline":
        """
        Fits scaler and encoder exclusively on training data.

        Args:
            df: Training pandas DataFrame (will be filtered for payment_status == 'FAILED').

        Returns:
            self
        """
        failed_df = df[df["payment_status"] == "FAILED"].copy()
        if len(failed_df) == 0:
            raise ValueError("No FAILED transactions found in DataFrame to fit feature pipeline!")

        failed_df = self._extract_engineered_features(failed_df)

        num_cols = PREDICTIVE_NUMERICAL_FEATURES + ["days_since_last_success_clean", "recent_failure_ratio"]
        cat_cols = PREDICTIVE_CATEGORICAL_FEATURES

        # Fit scaler on numerical features
        self.scaler.fit(failed_df[num_cols].values)

        # Fit encoder on categorical features
        self.encoder.fit(failed_df[cat_cols].astype(str).values)

        # Build feature names
        cat_feature_names = list(self.encoder.get_feature_names_out(cat_cols))
        self.feature_names_ = num_cols + cat_feature_names

        self.is_fitted = True
        logger.info("FeaturePipeline fitted on %d FAILED training rows (%d features)", len(failed_df), len(self.feature_names_))
        return self

    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray], pd.DataFrame]:
        """
        Transforms input DataFrame into scaled feature matrix X and target y.

        Args:
            df: Input transactions DataFrame.

        Returns:
            Tuple of (X: np.ndarray, y: Optional[np.ndarray], filtered_df: pd.DataFrame)
        """
        if not self.is_fitted:
            raise RuntimeError("FeaturePipeline must be fitted before calling transform()!")

        failed_df = df[df["payment_status"] == "FAILED"].copy().reset_index(drop=True)
        if len(failed_df) == 0:
            logger.warning("No FAILED transactions found in DataFrame during transform!")
            return np.empty((0, len(self.feature_names_))), None, failed_df

        engineered_df = self._extract_engineered_features(failed_df)

        num_cols = PREDICTIVE_NUMERICAL_FEATURES + ["days_since_last_success_clean", "recent_failure_ratio"]
        cat_cols = PREDICTIVE_CATEGORICAL_FEATURES

        # Scale numerical features
        X_num = self.scaler.transform(engineered_df[num_cols].values)

        # Encode categorical features
        X_cat = self.encoder.transform(engineered_df[cat_cols].astype(str).values)

        # Combine features
        X = np.hstack([X_num, X_cat])

        # Extract ground-truth recovery target y if present
        y = None
        if "recovered" in failed_df.columns and not failed_df["recovered"].isnull().all():
            y = failed_df["recovered"].values.astype(float)

        return X, y, failed_df

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray], pd.DataFrame]:
        """Fits on training data and transforms in one step."""
        return self.fit(df).transform(df)
