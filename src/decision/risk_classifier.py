"""
Deterministic Risk Classification Engine for REVORA Phase 3.

Calculates transaction risk score and maps to LOW, MEDIUM, HIGH, or CRITICAL.
"""

from typing import Dict, Any, Optional
from src.schemas.decision_schemas import RiskLevel


BASE_FAILURE_RISK_SCORES: Dict[str, float] = {
    "FRAUD_RISK_BLOCK": 100.0,
    "BANK_DECLINED": 60.0,
    "EXPIRED_CARD": 50.0,
    "INVALID_PAYMENT_DETAILS": 50.0,
    "AUTHENTICATION_FAILURE": 40.0,
    "UNKNOWN_FAILURE": 35.0,
    "INSUFFICIENT_FUNDS": 30.0,
    "NETWORK_ERROR": 15.0,
    "TEMPORARY_GATEWAY_FAILURE": 10.0,
    "SUCCESS": 0.0,
}


class RiskClassifier:
    """Classifies transaction risk levels using multi-signal risk synthesis."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        risk_cfg = self.config.get("risk", {})
        self.low_thresh = risk_cfg.get("low_threshold", 30.0)
        self.med_thresh = risk_cfg.get("medium_threshold", 55.0)
        self.high_thresh = risk_cfg.get("high_threshold", 80.0)

    def calculate_risk_score(self, transaction: Dict[str, Any]) -> float:
        """
        Calculates composite risk score between 0.0 and 100.0.

        Args:
            transaction: Dictionary of transaction features.

        Returns:
            Risk score float in [0, 100].
        """
        f_code = transaction.get("failure_code", "UNKNOWN_FAILURE")
        if f_code == "FRAUD_RISK_BLOCK":
            return 100.0

        base_risk = BASE_FAILURE_RISK_SCORES.get(f_code, 35.0)

        ip_risk = float(transaction.get("ip_risk_score", 0.0)) * 25.0
        merchant_risk = float(transaction.get("merchant_risk_score", 0.0)) * 20.0

        prev_failures = float(transaction.get("customer_previous_failures", 0))
        cust_failure_contrib = min(prev_failures * 5.0, 20.0)

        composite_score = (0.40 * base_risk) + ip_risk + merchant_risk + cust_failure_contrib
        return min(max(composite_score, 0.0), 100.0)

    def classify(self, transaction: Dict[str, Any]) -> RiskLevel:
        """
        Maps transaction risk score to RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL).

        Args:
            transaction: Dictionary of transaction features.

        Returns:
            RiskLevel enum.
        """
        f_code = transaction.get("failure_code", "UNKNOWN_FAILURE")
        if f_code == "FRAUD_RISK_BLOCK":
            return RiskLevel.CRITICAL

        score = self.calculate_risk_score(transaction)

        if score >= self.high_thresh:
            return RiskLevel.CRITICAL
        elif score >= self.med_thresh:
            return RiskLevel.HIGH
        elif score >= self.low_thresh:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
