"""
Deterministic Safety Guardrails Engine for REVORA Phase 3.

Enforces non-overridable safety rules, hard blocks, and policy constraints.
"""

from typing import Dict, Any, List, Optional
from src.schemas.policy_schemas import GuardrailCheckResult, FailureCategory
from src.schemas.decision_schemas import InterventionAction, RiskLevel
from src.policy.failure_classifier import NON_RETRYABLE_FAILURE_CODES


class SafetyGuardrails:
    """Evaluates safety rules and enforces hard decision overrides."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        constraints = self.config.get("constraints", {})
        self.max_retries_per_transaction = constraints.get("max_retries_per_transaction", 2)
        self.customer_rolling_24h_retry_cap = constraints.get("customer_rolling_24h_retry_cap", 3)

    def evaluate_hard_guardrails(
        self,
        transaction: Dict[str, Any],
        risk_level: RiskLevel,
        recovery_probability: float,
    ) -> List[GuardrailCheckResult]:
        """
        Evaluates hard guardrails on a transaction.

        Returns:
            List of GuardrailCheckResult objects.
        """
        results: List[GuardrailCheckResult] = []

        status = transaction.get("payment_status", "FAILED")
        f_code = transaction.get("failure_code", "UNKNOWN_FAILURE")
        attempt_count = transaction.get("attempt_count", 1)
        cust_prev_failures = transaction.get("customer_previous_failures", 0)

        # Rule 1: Success Status
        if status == "SUCCESS":
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_SUCCESS_NO_ACTION",
                    rule_name="Success Payment No Action Guardrail",
                    passed=False,
                    reason="Transaction is already in SUCCESS state.",
                    forced_decision=InterventionAction.NO_ACTION.value,
                )
            )
            return results
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_SUCCESS_NO_ACTION",
                    rule_name="Success Payment No Action Guardrail",
                    passed=True,
                    reason="Transaction is in FAILED state.",
                )
            )

        # Rule 2: Fraud Risk Hard Block
        if f_code == "FRAUD_RISK_BLOCK":
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_FRAUD_HARD_BLOCK",
                    rule_name="Fraud Risk Hard Block Guardrail",
                    passed=False,
                    reason="Transaction classified as FRAUD_RISK_BLOCK. Non-retryable under security policy.",
                    forced_decision=InterventionAction.BLOCK.value,
                )
            )
            return results
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_FRAUD_HARD_BLOCK",
                    rule_name="Fraud Risk Hard Block Guardrail",
                    passed=True,
                    reason="No fraud flag present.",
                )
            )

        # Rule 3: Critical Risk Block
        if risk_level == RiskLevel.CRITICAL:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_CRITICAL_RISK_BLOCK",
                    rule_name="Critical Risk Block Guardrail",
                    passed=False,
                    reason="Transaction risk level is CRITICAL. Automated retries strictly blocked.",
                    forced_decision=InterventionAction.BLOCK.value,
                )
            )
            return results
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_CRITICAL_RISK_BLOCK",
                    rule_name="Critical Risk Block Guardrail",
                    passed=True,
                    reason=f"Risk level is {risk_level.value}.",
                )
            )

        # Rule 4: Non-Retryable Failure Category Check
        if f_code in NON_RETRYABLE_FAILURE_CODES:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_NON_RETRYABLE_CODE",
                    rule_name="Non-Retryable Category Guardrail",
                    passed=False,
                    reason=f"Failure code {f_code} is classified as non-retryable. Automated retry prohibited.",
                )
            )
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_NON_RETRYABLE_CODE",
                    rule_name="Non-Retryable Category Guardrail",
                    passed=True,
                    reason=f"Failure code {f_code} is retryable.",
                )
            )

        # Rule 5: Transaction Max Retries Check
        if attempt_count > self.max_retries_per_transaction:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_MAX_RETRIES_EXCEEDED",
                    rule_name="Max Retries Guardrail",
                    passed=False,
                    reason=f"Attempt count {attempt_count} exceeds maximum limit of {self.max_retries_per_transaction}.",
                )
            )
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_MAX_RETRIES_EXCEEDED",
                    rule_name="Max Retries Guardrail",
                    passed=True,
                    reason=f"Attempt count {attempt_count} is within limit.",
                )
            )

        # Rule 6: Customer Velocity Cap Check
        if cust_prev_failures >= self.customer_rolling_24h_retry_cap:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_CUSTOMER_VELOCITY_CAP",
                    rule_name="Customer Velocity Guardrail",
                    passed=False,
                    reason=f"Customer previous failures ({cust_prev_failures}) reaches/exceeds 24h rolling cap ({self.customer_rolling_24h_retry_cap}).",
                )
            )
        else:
            results.append(
                GuardrailCheckResult(
                    rule_id="RULE_CUSTOMER_VELOCITY_CAP",
                    rule_name="Customer Velocity Guardrail",
                    passed=True,
                    reason=f"Customer previous failures ({cust_prev_failures}) within velocity limit.",
                )
            )

        return results
