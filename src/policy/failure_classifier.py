"""
Failure Classifier Module for REVORA Phase 3.

Maps raw transaction failure codes, status, and attributes to standardized
failure situation categories.
"""

from typing import Dict, Any
from src.schemas.policy_schemas import FailureCategory


NON_RETRYABLE_FAILURE_CODES = {
    "FRAUD_RISK_BLOCK",
    "EXPIRED_CARD",
    "INVALID_PAYMENT_DETAILS",
    "BANK_DECLINED",
    "AUTHENTICATION_FAILURE",
}


class FailureClassifier:
    """Classifies transaction failures into policy-relevant situation categories."""

    @staticmethod
    def classify(transaction: Dict[str, Any]) -> FailureCategory:
        """
        Classifies transaction based on failure_code, payment_status, and retryability.

        Args:
            transaction: Dictionary of transaction key-value attributes.

        Returns:
            FailureCategory enum.
        """
        status = transaction.get("payment_status", "FAILED")
        if status == "SUCCESS":
            return FailureCategory.SUCCESS

        code = transaction.get("failure_code", "UNKNOWN_FAILURE")

        if code == "FRAUD_RISK_BLOCK":
            return FailureCategory.HARD_SECURITY_BLOCK

        if code in ("EXPIRED_CARD", "INVALID_PAYMENT_DETAILS"):
            return FailureCategory.INVALID_CREDENTIALS

        if code == "AUTHENTICATION_FAILURE":
            return FailureCategory.AUTHENTICATION_FAILURE

        if code == "INSUFFICIENT_FUNDS":
            return FailureCategory.INSUFFICIENT_FUNDS

        if code in ("TEMPORARY_GATEWAY_FAILURE", "NETWORK_ERROR"):
            return FailureCategory.TRANSIENT_INFRASTRUCTURE

        if code == "BANK_DECLINED":
            return FailureCategory.BANK_DECLINE_GENERIC

        return FailureCategory.UNKNOWN_FAILURE

    @staticmethod
    def is_retryable(failure_code: str, is_retryable_flag: bool = True) -> bool:
        """
        Determines whether a failure code is eligible for automated retries.

        Hard safety invariant: If failure_code is in NON_RETRYABLE_FAILURE_CODES,
        it returns False regardless of any external flag.
        """
        if failure_code in NON_RETRYABLE_FAILURE_CODES:
            return False
        return bool(is_retryable_flag)
