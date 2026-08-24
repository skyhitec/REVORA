"""
Integration tests for REVORA Phase 3 Recovery Policy & Decision Engine.
"""

import pytest
from src.decision.engine import RecoveryPolicyEngine
from src.schemas.decision_schemas import InterventionAction, RiskLevel


@pytest.fixture
def engine():
    return RecoveryPolicyEngine()


def test_retry_action_selection(engine):
    tx = {
        "transaction_id": "tx_gw_1",
        "amount": 2500.0,
        "payment_status": "FAILED",
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "is_retryable": True,
        "ip_risk_score": 0.1,
        "merchant_risk_score": 0.1,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.85)
    assert decision_obj.decision == InterventionAction.RETRY
    assert decision_obj.net_expected_recovery_value > 0


def test_delay_and_retry_action_selection(engine):
    tx = {
        "transaction_id": "tx_funds_1",
        "amount": 1500.0,
        "payment_status": "FAILED",
        "failure_code": "INSUFFICIENT_FUNDS",
        "is_retryable": True,
        "ip_risk_score": 0.1,
        "merchant_risk_score": 0.1,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.65)
    assert decision_obj.decision == InterventionAction.DELAY_AND_RETRY


def test_retry_with_caution_action_selection(engine):
    tx = {
        "transaction_id": "tx_net_1",
        "amount": 1200.0,
        "payment_status": "FAILED",
        "failure_code": "NETWORK_ERROR",
        "is_retryable": True,
        "ip_risk_score": 0.4,
        "merchant_risk_score": 0.3,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.30)
    assert decision_obj.decision == InterventionAction.RETRY_WITH_CAUTION


def test_customer_action_required_action_selection(engine):
    tx = {
        "transaction_id": "tx_exp_1",
        "amount": 800.0,
        "payment_status": "FAILED",
        "failure_code": "EXPIRED_CARD",
        "is_retryable": False,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.90)
    assert decision_obj.decision == InterventionAction.CUSTOMER_ACTION_REQUIRED


def test_escalate_action_selection(engine):
    tx = {
        "transaction_id": "tx_escalate_1",
        "amount": 15000.0,
        "payment_status": "FAILED",
        "failure_code": "AUTHENTICATION_FAILURE",
        "is_retryable": False,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.80)
    assert decision_obj.decision == InterventionAction.ESCALATE


def test_block_action_selection(engine):
    tx = {
        "transaction_id": "tx_fraud_1",
        "amount": 50000.0,
        "payment_status": "FAILED",
        "failure_code": "FRAUD_RISK_BLOCK",
        "is_retryable": False,
        "ip_risk_score": 0.95,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.99)
    assert decision_obj.decision == InterventionAction.BLOCK


def test_no_action_for_low_probability(engine):
    tx = {
        "transaction_id": "tx_low_prob_1",
        "amount": 500.0,
        "payment_status": "FAILED",
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "is_retryable": True,
    }
    decision_obj = engine.evaluate_transaction(tx, recovery_probability=0.05)
    assert decision_obj.decision == InterventionAction.NO_ACTION
