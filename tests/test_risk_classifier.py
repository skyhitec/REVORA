"""
Unit tests for REVORA Phase 3 Deterministic Risk Classifier.
"""

import pytest
from src.decision.risk_classifier import RiskClassifier
from src.schemas.decision_schemas import RiskLevel


@pytest.fixture
def classifier():
    return RiskClassifier()


def test_fraud_risk_classified_as_critical(classifier):
    tx = {"failure_code": "FRAUD_RISK_BLOCK", "ip_risk_score": 0.1, "merchant_risk_score": 0.1}
    assert classifier.classify(tx) == RiskLevel.CRITICAL


def test_low_risk_gateway_failure(classifier):
    tx = {
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "ip_risk_score": 0.05,
        "merchant_risk_score": 0.05,
        "customer_previous_failures": 0,
    }
    score = classifier.calculate_risk_score(tx)
    assert score < 30.0
    assert classifier.classify(tx) == RiskLevel.LOW


def test_high_risk_signals(classifier):
    tx = {
        "failure_code": "BANK_DECLINED",
        "ip_risk_score": 0.90,
        "merchant_risk_score": 0.85,
        "customer_previous_failures": 3,
    }
    score = classifier.calculate_risk_score(tx)
    assert score >= 55.0
    assert classifier.classify(tx) in (RiskLevel.HIGH, RiskLevel.CRITICAL)
