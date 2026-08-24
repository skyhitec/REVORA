"""
Comprehensive Unit & Integration Test Suite for REVORA Phase 4.2 Real-Time Transaction Simulator.
"""

import pytest
import os
from pathlib import Path

from src.simulator.event_generator import TransactionEventGenerator
from src.simulator.stream_processor import TransactionStreamSimulator, SimulationEventResult
from src.schemas.decision_schemas import DecisionObject


def test_event_generator_schema_validity():
    """Verify generated transaction event contains all required fields and valid types."""
    generator = TransactionEventGenerator(seed=123)
    event = generator.generate_event()

    required_keys = [
        "transaction_id", "customer_id", "merchant_id", "amount", "currency",
        "payment_method", "payment_gateway", "failure_code", "payment_status",
        "is_retryable", "customer_payment_success_rate", "customer_previous_transactions",
        "customer_previous_failures", "days_since_last_successful_payment",
        "device_type", "merchant_category", "ip_risk_score", "merchant_risk_score",
        "avs_result", "cvv_result", "authentication_result", "bank_response_code",
        "gateway_response_code", "timestamp"
    ]

    for key in required_keys:
        assert key in event, f"Missing key '{key}' in generated event."

    assert event["amount"] > 0
    assert event["currency"] == "INR"
    assert event["payment_status"] == "FAILED"
    assert 0.0 <= event["customer_payment_success_rate"] <= 1.0
    assert 0.0 <= event["ip_risk_score"] <= 1.0


def test_event_generator_seed_reproducibility():
    """Verify fixed RNG seed produces identical deterministic events."""
    gen1 = TransactionEventGenerator(seed=42)
    gen2 = TransactionEventGenerator(seed=42)

    ev1 = gen1.generate_event()
    ev2 = gen2.generate_event()

    # Compare key fields excluding timestamp
    assert ev1["amount"] == ev2["amount"]
    assert ev1["failure_code"] == ev2["failure_code"]
    assert ev1["payment_method"] == ev2["payment_method"]
    assert ev1["customer_previous_transactions"] == ev2["customer_previous_transactions"]


def test_event_generation_count_and_batch():
    """Verify batch generator produces exact count of events."""
    generator = TransactionEventGenerator(seed=99)
    batch = generator.generate_batch(15)

    assert len(batch) == 15
    assert len(set(e["transaction_id"] for e in batch)) == 15  # Unique transaction IDs


def test_simulator_stream_processor_integration():
    """Verify stream processor correctly integrates with Phase 2 ML scoring & Phase 3 policy engine."""
    simulator = TransactionStreamSimulator(seed=101)
    results = simulator.run_simulation_batch(total_events=5, seed=101)

    assert len(results) == 5
    for res in results:
        assert isinstance(res, SimulationEventResult)
        assert isinstance(res.decision_object, DecisionObject)
        assert 0.0 <= res.recovery_probability <= 1.0
        assert res.decision in [
            "RETRY", "DELAY_AND_RETRY", "RETRY_WITH_CAUTION",
            "CUSTOMER_ACTION_REQUIRED", "ESCALATE", "BLOCK", "NO_ACTION"
        ]
        assert res.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_simulator_guardrail_enforcement_fraud_block():
    """Verify FRAUD_RISK_BLOCK event strictly forces BLOCK decision and CRITICAL risk level."""
    generator = TransactionEventGenerator()
    fraud_tx = generator.generate_event(
        override_amount=50000.0,
        override_failure_code="FRAUD_RISK_BLOCK",
        override_payment_method="CREDIT_CARD",
    )

    simulator = TransactionStreamSimulator()
    res = simulator.process_single_event(fraud_tx, event_index=1)

    assert res.decision == "BLOCK"
    assert res.risk_level == "CRITICAL"
    assert "FRAUD_RISK_BLOCK" in res.reason
    assert res.net_expected_recovery_value == 0.0


def test_simulator_non_retryable_failures():
    """Verify non-retryable credential failures (EXPIRED_CARD) result in CUSTOMER_ACTION_REQUIRED."""
    generator = TransactionEventGenerator()
    expired_tx = generator.generate_event(
        override_amount=2000.0,
        override_failure_code="EXPIRED_CARD",
        override_payment_method="CREDIT_CARD",
    )

    simulator = TransactionStreamSimulator()
    res = simulator.process_single_event(expired_tx, event_index=1)

    assert res.decision == "CUSTOMER_ACTION_REQUIRED"
    assert "EXPIRED_CARD" in res.reason


def test_simulator_streaming_generator():
    """Verify stream_events generator yields requested event count and rate pacing."""
    simulator = TransactionStreamSimulator()
    streamed_events = list(simulator.stream_events(total_events=10, rate_per_sec=100.0, seed=55))

    assert len(streamed_events) == 10
    assert streamed_events[0].event_index == 1
    assert streamed_events[-1].event_index == 10


def test_simulator_audit_trail_logging(tmp_path):
    """Verify every simulated transaction writes a valid audit record to JSONL."""
    log_file = tmp_path / "sim_audit.jsonl"

    from src.audit.logger import AuditLogger
    from src.audit.verifier import AuditVerifier

    audit_logger = AuditLogger(log_filepath=str(log_file))
    simulator = TransactionStreamSimulator(audit_logger=audit_logger, seed=200)

    results = simulator.run_simulation_batch(total_events=10, seed=200)
    assert len(results) == 10
    assert log_file.exists()

    is_valid, errors = AuditVerifier.verify_audit_file(str(log_file))
    assert is_valid is True
    assert len(errors) == 0
