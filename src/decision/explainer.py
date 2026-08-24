"""
Explainability Synthesizer for REVORA Phase 3.

Generates human-readable decision explanations detailing decision rationale,
recovery metrics, financial ERV, risk factors, and active guardrails.
"""

from typing import Dict, Any, List
from src.schemas.decision_schemas import InterventionAction, RiskLevel, ERVBreakdown
from src.schemas.policy_schemas import GuardrailCheckResult


class DecisionExplainer:
    """Synthesizes structured human-readable explanations for decision objects."""

    @staticmethod
    def synthesize_explanation(
        transaction: Dict[str, Any],
        decision: InterventionAction,
        raw_reason: str,
        risk_level: RiskLevel,
        recovery_probability: float,
        erv_breakdown: ERVBreakdown,
        guardrail_results: List[GuardrailCheckResult],
    ) -> str:
        """
        Synthesizes concise, explainable text paragraph.

        Args:
            transaction: Transaction dictionary.
            decision: Selected InterventionAction.
            raw_reason: Raw policy matrix reason string.
            risk_level: RiskLevel enum.
            recovery_probability: P(recovered=1).
            erv_breakdown: ERVBreakdown object.
            guardrail_results: Evaluated guardrails list.

        Returns:
            Human-readable explanation string.
        """
        amount = float(transaction.get("amount", 0.0))
        f_code = transaction.get("failure_code", "UNKNOWN_FAILURE")

        failed_rules = [r.rule_name for r in guardrail_results if not r.passed]
        passed_rules_count = sum(1 for r in guardrail_results if r.passed)

        if decision == InterventionAction.BLOCK:
            if failed_rules:
                rule_str = ", ".join(failed_rules)
                return (
                    f"Decision: BLOCK. Reason: Transaction of ₹{amount:,.2f} with failure code '{f_code}' is BLOCKED. "
                    f"Violated safety policy rule(s): {rule_str}. "
                    f"Model probability ({recovery_probability:.2%}) cannot override hard security and safety guardrails."
                )
            return f"Decision: BLOCK. Reason: {raw_reason}"

        if decision == InterventionAction.NO_ACTION:
            return (
                f"Decision: NO_ACTION. Reason: {raw_reason} "
                f"Recovery probability is {recovery_probability:.2%}, producing Net ERV of ₹{erv_breakdown.net_expected_recovery_value:,.2f} "
                f"against intervention cost ₹{erv_breakdown.intervention_cost:.2f}."
            )

        return (
            f"Decision: {decision.value}. Reason: Failure category '{f_code}' evaluated under {risk_level.value} risk. "
            f"{raw_reason} "
            f"Gross ERV: ₹{erv_breakdown.gross_expected_recovery_value:,.2f} (Amount: ₹{amount:,.2f} x P: {recovery_probability:.2%}). "
            f"Net ERV: ₹{erv_breakdown.net_expected_recovery_value:,.2f} after deducting intervention cost ₹{erv_breakdown.intervention_cost:.2f} "
            f"and customer friction penalty ₹{erv_breakdown.friction_penalty:.2f}. "
            f"Passed {passed_rules_count} safety guardrail check(s)."
        )
