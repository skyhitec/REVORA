"""
Intervention Selector Module for REVORA Phase 3.

Matches transactions against the Decision-Policy Matrix to select bounded
recovery actions.
"""

from typing import Dict, Any, List, Optional, Tuple
from src.schemas.decision_schemas import InterventionAction, RiskLevel
from src.schemas.policy_schemas import GuardrailCheckResult, FailureCategory
from src.policy.failure_classifier import NON_RETRYABLE_FAILURE_CODES
from src.decision.erv_calculator import ERVCalculator


class InterventionSelector:
    """Selects bounded intervention action using deterministic decision policy rules."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        policy_cfg = self.config.get("policy", {})
        self.min_net_ev = float(policy_cfg.get("min_expected_recovery_value", 5.0))
        self.tau = float(policy_cfg.get("optimal_threshold_tau", 0.1600))

        constraints = self.config.get("constraints", {})
        self.escalation_thresh = float(constraints.get("high_value_escalation_threshold", 10000.0))
        self.bank_inquiry_thresh = float(constraints.get("high_value_bank_inquiry_threshold", 5000.0))
        self.erv_calc = ERVCalculator(self.config)

    def select_intervention(
        self,
        transaction: Dict[str, Any],
        risk_level: RiskLevel,
        recovery_probability: float,
        guardrail_results: List[GuardrailCheckResult],
    ) -> Tuple[InterventionAction, str]:
        """
        Selects intervention action and returns (InterventionAction, decision_reason).

        Args:
            transaction: Transaction attribute dictionary.
            risk_level: RiskLevel enum.
            recovery_probability: P(recovered=1) from Phase 2 score.
            guardrail_results: List of evaluated GuardrailCheckResult objects.

        Returns:
            Tuple of (InterventionAction, reason_string).
        """
        f_code = transaction.get("failure_code", "UNKNOWN_FAILURE")
        amount = float(transaction.get("amount", 0.0))

        # Check for hard guardrail overrides
        for res in guardrail_results:
            if not res.passed and res.forced_decision:
                action = InterventionAction(res.forced_decision)
                return action, f"HARD_GUARDRAIL_OVERRIDE_{res.rule_id}: {res.reason}"

        # Hard Security Block & Critical Risk
        if f_code == "FRAUD_RISK_BLOCK" or risk_level == RiskLevel.CRITICAL:
            return InterventionAction.BLOCK, (
                f"Transaction classified as {f_code} with {risk_level.value} risk. "
                f"Hard safety guardrail enforces BLOCK."
            )

        # Handle Non-Retryable Failure Categories
        if f_code in NON_RETRYABLE_FAILURE_CODES:
            if f_code in ("EXPIRED_CARD", "INVALID_PAYMENT_DETAILS"):
                return InterventionAction.CUSTOMER_ACTION_REQUIRED, (
                    f"Failure code {f_code} is non-retryable. "
                    f"Customer notification required to update payment credentials."
                )

            if f_code == "AUTHENTICATION_FAILURE":
                if amount >= self.escalation_thresh:
                    return InterventionAction.ESCALATE, (
                        f"High-value transaction (₹{amount:,.2f}) failed 3DS authentication. "
                        f"Escalating to VIP customer support."
                    )
                return InterventionAction.CUSTOMER_ACTION_REQUIRED, (
                    f"Authentication failed. Customer nudge required to retry 3DS / OTP verification."
                )

            if f_code == "BANK_DECLINED":
                if recovery_probability >= self.tau and amount >= self.bank_inquiry_thresh:
                    return InterventionAction.ESCALATE, (
                        f"Bank decline on high-value transaction (₹{amount:,.2f}) with recovery prob {recovery_probability:.2f} >= tau ({self.tau}). "
                        f"Escalating to merchant desk for manual bank inquiry."
                    )
                return InterventionAction.NO_ACTION, (
                    f"Generic bank decline with non-retryable classification. No automated retry permitted under safety policy."
                )

        # Handle Retryable Categories
        # First calculate Net ERV for standard RETRY action
        breakdown_retry = self.erv_calc.calculate_erv_breakdown(
            transaction, recovery_probability, InterventionAction.RETRY
        )

        if recovery_probability < self.tau:
            return InterventionAction.NO_ACTION, (
                f"Predicted recovery probability ({recovery_probability:.4f}) is below optimal decision threshold tau ({self.tau}). "
                f"Skipping recovery intervention."
            )

        if breakdown_retry.net_expected_recovery_value <= 0.0 or breakdown_retry.net_expected_recovery_value < self.min_net_ev:
            return InterventionAction.NO_ACTION, (
                f"Net Expected Recovery Value (₹{breakdown_retry.net_expected_recovery_value:.2f}) does not exceed "
                f"minimum required threshold (₹{self.min_net_ev:.2f}). Skipping intervention."
            )

        if f_code == "INSUFFICIENT_FUNDS":
            if recovery_probability >= self.tau:
                return InterventionAction.DELAY_AND_RETRY, (
                    f"Insufficient funds failure has high recovery potential ({recovery_probability:.2f}). "
                    f"Scheduling delayed retry after pay-day / off-peak window."
                )
            return InterventionAction.CUSTOMER_ACTION_REQUIRED, (
                f"Insufficient funds failure with low recovery score ({recovery_probability:.2f}). "
                f"Nudging customer to add funds."
            )

        if f_code == "TEMPORARY_GATEWAY_FAILURE":
            return InterventionAction.RETRY, (
                f"Transient gateway downtime detected. Recovery probability ({recovery_probability:.2f}) >= tau ({self.tau}) "
                f"and Net ERV (₹{breakdown_retry.net_expected_recovery_value:.2f}) exceeds minimum threshold. Executing immediate retry."
            )

        if f_code == "NETWORK_ERROR":
            if recovery_probability >= 0.50 and risk_level == RiskLevel.LOW:
                return InterventionAction.RETRY, (
                    f"Network error with high probability ({recovery_probability:.2f}) and LOW risk. Executing immediate retry."
                )
            return InterventionAction.RETRY_WITH_CAUTION, (
                f"Network error with moderate probability ({recovery_probability:.2f}) and {risk_level.value} risk. "
                f"Executing retry with caution."
            )

        if f_code == "UNKNOWN_FAILURE":
            if risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM):
                return InterventionAction.RETRY_WITH_CAUTION, (
                    f"Unclassified failure with acceptable risk ({risk_level.value}) and positive Net ERV (₹{breakdown_retry.net_expected_recovery_value:.2f}). "
                    f"Executing retry with caution."
                )
            return InterventionAction.NO_ACTION, (
                f"Unclassified failure with high risk ({risk_level.value}). Skipping automated retry."
            )

        return InterventionAction.NO_ACTION, "No intervention policy matched. Defaulting to NO_ACTION."
