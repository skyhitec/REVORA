"""
Minimal Data Preprocessing for REVORA (Phase 1)

Focuses strictly on basic data hygiene, standardizing data types, and ensuring
clean DataFrames for EDA and dataset storage.

Note per Phase 1 scope: No model-specific feature engineering, scaling,
or transformations are included in this module yet.
"""

import pandas as pd
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class MinimalDataPreprocessor:
    """Minimal preprocessor for Phase 1 data cleaning and formatting."""

    def __init__(self) -> None:
        pass

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies basic data cleaning and standardizes data types.

        Args:
            df: Raw synthesized DataFrame.

        Returns:
            Cleaned pandas DataFrame.
        """
        df_clean = df.copy()

        # 1. Standardize string columns (strip trailing whitespace)
        str_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in str_cols:
            df_clean[col] = df_clean[col].astype(str).str.strip()

        # 2. Ensure datetime parsing for transaction_timestamp
        if "transaction_timestamp" in df_clean.columns:
            df_clean["transaction_timestamp"] = pd.to_datetime(df_clean["transaction_timestamp"])

        # 3. Ensure proper numeric dtypes
        float_cols = [
            "amount",
            "customer_payment_success_rate",
            "days_since_last_successful_payment",
            "ip_risk_score",
            "merchant_risk_score",
            "recovery_probability_target",
        ]
        for col in float_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        int_cols = ["customer_previous_transactions", "customer_previous_failures"]
        for col in int_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(int)

        logger.info("Minimal preprocessing complete. Clean dataset shape: %s", df_clean.shape)
        return df_clean
