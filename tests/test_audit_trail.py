"""
Unit tests for REVORA Phase 3 Immutable Audit Trail & Hash Chain Verifier.
"""

import json
import pytest
from pathlib import Path
from src.schemas.decision_schemas import DecisionObject, InterventionAction, RiskLevel
from src.audit.logger import AuditLogger
from src.audit.verifier import AuditVerifier


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "test_audit.jsonl")


def test_audit_logging_and_hash_verification(audit_file):
    logger = AuditLogger(log_filepath=audit_file)

    d1 = DecisionObject(
        decision_id="dec_001",
        transaction_id="tx_1001",
        customer_id="cust_1",
        merchant_id="merch_1",
        timestamp="2026-08-24T20:00:00Z",
        amount=1500.0,
        failure_code="TEMPORARY_GATEWAY_FAILURE",
        retryability=True,
        recovery_probability=0.80,
        expected_recovery_value=1200.0,
        intervention_cost=10.0,
        net_expected_recovery_value=1190.0,
        risk_level=RiskLevel.LOW,
        decision=InterventionAction.RETRY,
        reason="Gateway retry approved.",
    )

    d2 = DecisionObject(
        decision_id="dec_002",
        transaction_id="tx_1002",
        customer_id="cust_2",
        merchant_id="merch_1",
        timestamp="2026-08-24T20:01:00Z",
        amount=5000.0,
        failure_code="FRAUD_RISK_BLOCK",
        retryability=False,
        recovery_probability=0.95,
        expected_recovery_value=4750.0,
        intervention_cost=0.0,
        net_expected_recovery_value=0.0,
        risk_level=RiskLevel.CRITICAL,
        decision=InterventionAction.BLOCK,
        reason="Fraud block guardrail.",
    )

    logger.log_decision(d1, {"amount": 1500.0})
    logger.log_decision(d2, {"amount": 5000.0})

    is_valid, errors = AuditVerifier.verify_audit_file(audit_file)
    assert is_valid
    assert len(errors) == 0


def test_audit_tamper_detection(audit_file):
    logger = AuditLogger(log_filepath=audit_file)

    d1 = DecisionObject(
        decision_id="dec_001",
        transaction_id="tx_1001",
        customer_id="cust_1",
        merchant_id="merch_1",
        timestamp="2026-08-24T20:00:00Z",
        amount=1500.0,
        failure_code="TEMPORARY_GATEWAY_FAILURE",
        retryability=True,
        recovery_probability=0.80,
        expected_recovery_value=1200.0,
        intervention_cost=10.0,
        net_expected_recovery_value=1190.0,
        risk_level=RiskLevel.LOW,
        decision=InterventionAction.RETRY,
        reason="Gateway retry approved.",
    )

    logger.log_decision(d1, {"amount": 1500.0})

    # Tamper with the audit log file
    with open(audit_file, "r", encoding="utf-8") as f:
        content = f.read()

    tampered_content = content.replace("1500.0", "9999.0")
    with open(audit_file, "w", encoding="utf-8") as f:
        f.write(tampered_content)

    is_valid, errors = AuditVerifier.verify_audit_file(audit_file)
    assert not is_valid
    assert len(errors) > 0
