"""
Data Validation Pipeline for REVORA

Performs comprehensive validation checks on generated payment datasets,
verifying column completeness, data integrity, numerical constraints,
target consistency, and data leakage absence.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_id",
    "merchant_id",
    "amount",
    "currency",
    "payment_method",
    "payment_gateway",
    "card_type",
    "transaction_timestamp",
    "customer_payment_success_rate",
    "customer_previous_transactions",
    "customer_previous_failures",
    "days_since_last_successful_payment",
    "device_type",
    "device_id",
    "ip_risk_score",
    "customer_location",
    "merchant_category",
    "merchant_risk_score",
    "avs_result",
    "cvv_result",
    "authentication_result",
    "bank_response_code",
    "gateway_response_code",
    "payment_status",
    "failure_code",
    "failure_reason",
    "is_retryable",
    "recovery_probability_target",
    "recovered",
]

LEAKAGE_CANDIDATE_COLUMNS = [
    "final_recovery_timestamp",
    "post_recovery_transaction_status",
    "actual_recovery_action_result",
    "recovered_amount",
    "future_retry_outcome",
]

ALLOWED_CURRENCIES = {"INR", "USD", "EUR"}
ALLOWED_PAYMENT_STATUSES = {"SUCCESS", "FAILED"}
ALLOWED_FAILURE_CODES = {
    "NONE",
    "TEMPORARY_GATEWAY_FAILURE",
    "NETWORK_ERROR",
    "INSUFFICIENT_FUNDS",
    "BANK_DECLINED",
    "AUTHENTICATION_FAILURE",
    "FRAUD_RISK_BLOCK",
    "EXPIRED_CARD",
    "INVALID_PAYMENT_DETAILS",
    "UNKNOWN_FAILURE",
}


class DataValidator:
    """Validates payment transactions DataFrame against business and ML rules."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    def validate(self) -> Tuple[bool, str]:
        """
        Executes all validation rules and formats a summary report.

        Returns:
            Tuple of (is_valid: bool, summary_report: str)
        """
        self.errors.clear()
        self.warnings.clear()

        rows_count = len(self.df)
        cols_count = len(self.df.columns)

        # 1. Missing required columns
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in self.df.columns]
        if missing_cols:
            self.errors.append(f"Missing required columns: {missing_cols}")

        # 2. Check leakage candidate columns
        detected_leakage = [c for c in LEAKAGE_CANDIDATE_COLUMNS if c in self.df.columns]
        if detected_leakage:
            self.errors.append(f"Data leakage detected! Prohibited outcome columns present: {detected_leakage}")

        # If required columns are missing, abort further column-level checks safely
        if missing_cols:
            return False, self._format_summary(rows_count, cols_count, False)

        # 3. Duplicate transaction IDs
        duplicate_ids_count = int(self.df["transaction_id"].duplicated().sum())
        if duplicate_ids_count > 0:
            self.errors.append(f"Found {duplicate_ids_count} duplicate transaction_ids.")

        # 4. Feature Null Checks (predictive features must not contain NaN)
        feature_cols = [
            c for c in REQUIRED_COLUMNS
            if c not in ["recovery_probability_target", "recovered"]
        ]
        feature_nulls_count = int(self.df[feature_cols].isnull().sum().sum())
        if feature_nulls_count > 0:
            self.errors.append(f"Found {feature_nulls_count} missing values in feature columns.")

        # 5. Amount validation
        invalid_amounts_count = int((self.df["amount"] <= 0).sum())
        if invalid_amounts_count > 0:
            self.errors.append(f"Found {invalid_amounts_count} records with non-positive transaction amounts.")

        # 6. Currency validation
        invalid_currencies_count = int((~self.df["currency"].isin(ALLOWED_CURRENCIES)).sum())
        if invalid_currencies_count > 0:
            self.errors.append(f"Found {invalid_currencies_count} records with invalid currency codes.")

        # 7. Payment status and failure code validation
        invalid_status_count = int((~self.df["payment_status"].isin(ALLOWED_PAYMENT_STATUSES)).sum())
        if invalid_status_count > 0:
            self.errors.append(f"Found {invalid_status_count} records with invalid payment_status.")

        invalid_failure_code_count = int((~self.df["failure_code"].isin(ALLOWED_FAILURE_CODES)).sum())
        if invalid_failure_code_count > 0:
            self.errors.append(f"Found {invalid_failure_code_count} records with invalid failure_code.")

        # 8. Target validation (Separation of SUCCESS vs FAILED outcomes per Correction #1)
        failed_mask = self.df["payment_status"] == "FAILED"
        success_mask = self.df["payment_status"] == "SUCCESS"

        # For FAILED payments, recovered target must be 0 or 1
        failed_recovered = self.df.loc[failed_mask, "recovered"]
        invalid_failed_rec = int((~failed_recovered.isin([0.0, 1.0])).sum())
        if invalid_failed_rec > 0:
            self.errors.append(f"Found {invalid_failed_rec} failed transactions with invalid recovery target.")

        # For SUCCESS payments, recovered target must be NaN / null
        success_recovered = self.df.loc[success_mask, "recovered"]
        invalid_success_rec = int(success_recovered.notnull().sum())
        if invalid_success_rec > 0:
            self.errors.append(f"Found {invalid_success_rec} successful transactions with non-null recovery target.")

        # 9. Risk scores bounds check (0.0 to 100.0)
        invalid_ip_risk = int(((self.df["ip_risk_score"] < 0) | (self.df["ip_risk_score"] > 100)).sum())
        if invalid_ip_risk > 0:
            self.errors.append(f"Found {invalid_ip_risk} records with ip_risk_score outside [0, 100].")

        # 10. Timestamp parsing check
        try:
            pd.to_datetime(self.df["transaction_timestamp"])
            invalid_timestamps_count = 0
        except Exception:
            invalid_timestamps_count = rows_count
            self.errors.append("Failed to parse transaction_timestamp column into datetimes.")

        # Save stats
        self.stats = {
            "rows": rows_count,
            "columns": cols_count,
            "missing_feature_values": feature_nulls_count,
            "duplicate_ids": duplicate_ids_count,
            "invalid_amounts": invalid_amounts_count,
            "invalid_categories": invalid_status_count + invalid_failure_code_count + invalid_currencies_count,
            "potential_leakage_columns": len(detected_leakage),
        }

        is_valid = len(self.errors) == 0
        summary_report = self._format_summary(rows_count, cols_count, is_valid)
        return is_valid, summary_report

    def _format_summary(self, rows: int, cols: int, is_valid: bool) -> str:
        """Formats clean terminal summary string for validation output."""
        status_str = "PASS" if is_valid else "FAIL"
        summary = [
            "REVORA DATA VALIDATION",
            "----------------------",
            f"Rows: {rows:,}",
            f"Columns: {cols}",
            "",
            f"Missing values in features: {self.stats.get('missing_feature_values', 0)}",
            f"Duplicate transaction IDs: {self.stats.get('duplicate_ids', 0)}",
            f"Invalid amounts: {self.stats.get('invalid_amounts', 0)}",
            f"Invalid categories: {self.stats.get('invalid_categories', 0)}",
            f"Potential leakage columns: {self.stats.get('potential_leakage_columns', 0)}",
            "",
            f"Status: {status_str}",
        ]

        if self.errors:
            summary.append("")
            summary.append("Validation Errors:")
            for err in self.errors:
                summary.append(f" - {err}")

        return "\n".join(summary)
