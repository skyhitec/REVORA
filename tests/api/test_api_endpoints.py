"""
Integration Test Suite for REVORA Phase 4.1 FastAPI REST API.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /health returns 200 OK and valid health schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "Phase 4.1" in data["phase"]
    assert "timestamp" in data


def test_valid_predict_request():
    """Test POST /api/v1/predict with valid transaction payload."""
    payload = {
        "transaction_id": "tx_test_predict_01",
        "amount": 2500.0,
        "payment_method": "UPI",
        "payment_gateway": "RAZORPAY",
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "customer_payment_success_rate": 0.90,
        "customer_previous_transactions": 15,
        "customer_previous_failures": 1,
        "days_since_last_successful_payment": 1.0,
        "ip_risk_score": 5.0,
        "merchant_risk_score": 5.0,
        "payment_status": "FAILED",
        "is_retryable": True,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_test_predict_01"
    assert 0.0 <= data["predicted_recovery_probability"] <= 1.0
    assert data["optimal_threshold"] == 0.1600
    assert isinstance(data["should_intervene"], bool)


def test_invalid_predict_request():
    """Test POST /api/v1/predict with invalid amount (<= 0) returns 422 error."""
    payload = {
        "amount": -500.0,
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data or "detail" in data


def test_valid_decide_request():
    """Test POST /api/v1/decide returns valid Phase 3 policy decision."""
    payload = {
        "transaction_id": "tx_test_decide_01",
        "amount": 5000.0,
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "payment_method": "UPI",
        "predicted_recovery_probability": 0.85,
    }
    response = client.post("/api/v1/decide", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_test_decide_01"
    assert data["decision"] in [
        "RETRY", "DELAY_AND_RETRY", "RETRY_WITH_CAUTION",
        "CUSTOMER_ACTION_REQUIRED", "ESCALATE", "BLOCK", "NO_ACTION"
    ]
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert data["expected_recovery_value"] == round(5000.0 * 0.85, 2)
    assert len(data["policy_checks"]) > 0


def test_guardrail_behavior_through_decide():
    """Test hard fraud risk guardrail forces BLOCK decision through POST /api/v1/decide."""
    payload = {
        "transaction_id": "tx_fraud_test",
        "amount": 25000.0,
        "failure_code": "FRAUD_RISK_BLOCK",
        "payment_method": "CREDIT_CARD",
        "predicted_recovery_probability": 0.95,
    }
    response = client.post("/api/v1/decide", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "BLOCK"
    assert data["risk_level"] == "CRITICAL"
    assert "FRAUD_RISK_BLOCK" in data["reason"]


def test_simulate_endpoint():
    """Test POST /api/v1/simulate returns valid simulated decision response."""
    payload = {
        "amount": 1800.0,
        "failure_code": "TEMPORARY_GATEWAY_FAILURE",
        "payment_method": "UPI",
        "recovery_probability": 0.75,
    }
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"].startswith("sim_")
    assert data["decision"] in [
        "RETRY", "DELAY_AND_RETRY", "RETRY_WITH_CAUTION",
        "CUSTOMER_ACTION_REQUIRED", "ESCALATE", "BLOCK", "NO_ACTION"
    ]


def test_audit_verify_endpoint():
    """Test POST /api/v1/audit/verify verifies validation audit trail JSONL."""
    response = client.post("/api/v1/audit/verify?filepath=data/audit/val_audit.jsonl")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["total_records"] > 0
    assert len(data["errors"]) == 0


def test_metrics_endpoint():
    """Test GET /api/v1/metrics returns system revenue recovery metrics."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_failed_count"] > 0
    assert data["optimal_threshold"] == 0.1600
    assert data["revenue_at_risk"] > 0
    assert data["intervention_rate"] > 0


def test_demo_scenarios_endpoint():
    """Test GET /api/v1/demo/scenarios returns list of 5 buildathon demo scenarios."""
    response = client.get("/api/v1/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["id"] == "gateway_retry"


def test_demo_run_endpoint():
    """Test POST /api/v1/demo/run/fraud_block executes fraud block scenario."""
    response = client.post("/api/v1/demo/run/fraud_block")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "BLOCK"
    assert data["risk_level"] == "CRITICAL"


def test_malformed_request_handling():
    """Test handling of malformed JSON payload returns 422 validation error."""
    response = client.post(
        "/api/v1/predict",
        headers={"Content-Type": "application/json"},
        content="{invalid_json_body",
    )
    assert response.status_code == 422
