"""
Unit tests for REVORA Phase 3 Explainability Synthesizer.
"""

import pytest
from src.decision.explainer import DecisionExplainer
from src.schemas.decision_schemas import InterventionAction, RiskLevel, ERVBreakdown
from src.schemas.policy_schemas import GuardrailCheckResult


def test_explainability_content():
    tx = {"amount": 2500.0, "failure_code": "TEMPORARY_GATEWAY_FAILURE"}
    erv = ERVBreakdown(
        gross_expected_recovery_value=2125.0,
        intervention_cost=10.0,
        friction_penalty=3.0,
        net_expected_recovery_value=2112.0,
    )
    guardrails = [
        GuardrailCheckResult("RULE_SUCCESS_NO_ACTION", "Success Check", True, "Passed"),
        GuardrailCheckResult("RULE_FRAUD_HARD_BLOCK", "Fraud Check", True, "Passed"),
    ]

    reason = DecisionExplainer.synthesize_explanation(
        transaction=tx,
        decision=InterventionAction.RETRY,
        raw_reason="Transient gateway downtime detected.",
        risk_level=RiskLevel.LOW,
        recovery_probability=0.85,
        erv_breakdown=erv,
        guardrail_results=guardrails,
    )

    assert "RETRY" in reason
    assert "TEMPORARY_GATEWAY_FAILURE" in reason
    assert "2,500.00" in reason
    assert "85.00%" in reason
    assert "2,112.00" in reason
