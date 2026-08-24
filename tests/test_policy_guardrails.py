"""
Unit tests for REVORA Phase 3 Deterministic Safety Guardrails.
"""

import pytest
from src.policy.guardrails import SafetyGuardrails
from src.schemas.decision_schemas import RiskLevel, InterventionAction


@pytest.fixture
def guardrails():
    config = {
        "constraints": {
            "max_retries_per_transaction": 2,
            "customer_rolling_24h_retry_cap": 3,
        }
    }
    return SafetyGuardrails(config)


def test_fraud_risk_always_blocks(guardrails):
    tx = {
        "transaction_id": "tx_fraud_1",
        "payment_status": "FAILED",
        "failure_code": "FRAUD_RISK_BLOCK",
        "amount": 5000.0,
    }
    results = guardrails.evaluate_hard_guardrails(tx, RiskLevel.CRITICAL, recovery_probability=0.99)
    failed_rules = [r for r in results if not r.passed]
    assert len(failed_rules) > 0
    assert failed_rules[0].forced_decision == InterventionAction.BLOCK.value
    assert "FRAUD_RISK_BLOCK" in failed_rules[0].reason


def test_success_payment_yields_no_action(guardrails):
    tx = {
        "transaction_id": "tx_success_1",
        "payment_status": "SUCCESS",
        "failure_code": "SUCCESS",
        "amount": 1000.0,
    }
    results = guardrails.evaluate_hard_guardrails(tx, RiskLevel.LOW, recovery_probability=0.0)
    failed_rules = [r for r in results if not r.passed]
    assert len(failed_rules) == 1
    assert failed_rules[0].forced_decision == InterventionAction.NO_ACTION.value


def test_non_retryable_codes_fail_guardrail(guardrails):
    for f_code in ["EXPIRED_CARD", "INVALID_PAYMENT_DETAILS", "AUTHENTICATION_FAILURE", "BANK_DECLINED"]:
        tx = {
            "transaction_id": f"tx_{f_code}",
            "payment_status": "FAILED",
            "failure_code": f_code,
            "amount": 1000.0,
        }
        results = guardrails.evaluate_hard_guardrails(tx, RiskLevel.MEDIUM, recovery_probability=0.80)
        non_retryable_rule = [r for r in results if r.rule_id == "RULE_NON_RETRYABLE_CODE"][0]
        assert not non_retryable_rule.passed


def test_customer_velocity_limit_exceeded(guardrails):
    tx = {
        "transaction_id": "tx_vel_1",
        "payment_status": "FAILED",
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "customer_previous_failures": 4,
        "amount": 1000.0,
    }
    results = guardrails.evaluate_hard_guardrails(tx, RiskLevel.LOW, recovery_probability=0.75)
    vel_rule = [r for r in results if r.rule_id == "RULE_CUSTOMER_VELOCITY_CAP"][0]
    assert not vel_rule.passed
