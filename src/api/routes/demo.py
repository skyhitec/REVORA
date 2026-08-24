"""
Buildathon Demo Scenarios Route for REVORA Phase 4.1/4.3 API Service.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from src.api.schemas import DecideResponse, PolicyCheckItem
from src.api.dependencies import get_policy_engine, get_audit_logger
from src.decision.engine import RecoveryPolicyEngine
from src.audit.logger import AuditLogger

router = APIRouter(prefix="/api/v1/demo", tags=["Demo Studio"])


class DemoScenario(BaseModel):
    id: str
    title: str
    badge: str
    color: str
    description: str
    expected_action: str
    payload: Dict[str, Any]


DEMO_SCENARIOS = [
    {
        "id": "gateway_retry",
        "title": "Transient Gateway Failure",
        "badge": "High Yield Retry",
        "color": "emerald",
        "description": "INR 12,500 payment failed due to TEMPORARY_GATEWAY_FAILURE. ML P_rec = 85%.",
        "expected_action": "RETRY",
        "payload": {
            "transaction_id": "demo_gateway_01",
            "amount": 12500.0,
            "failure_code": "TEMPORARY_GATEWAY_FAILURE",
            "payment_method": "UPI",
            "predicted_recovery_probability": 0.85,
        }
    },
    {
        "id": "high_value_escalate",
        "title": "High-Value Auth Failure",
        "badge": "VIP Escalation",
        "color": "violet",
        "description": "INR 45,000 corporate payment failed due to AUTHENTICATION_FAILURE. Requires VIP escalation.",
        "expected_action": "ESCALATE",
        "payload": {
            "transaction_id": "demo_escalate_01",
            "amount": 45000.0,
            "failure_code": "AUTHENTICATION_FAILURE",
            "payment_method": "CREDIT_CARD",
            "predicted_recovery_probability": 0.75,
        }
    },
    {
        "id": "fraud_block",
        "title": "Fraud Risk Flag",
        "badge": "Hard Guardrail",
        "color": "rose",
        "description": "High ML probability (92%) overridden by mandatory FRAUD_RISK_BLOCK safety guardrail.",
        "expected_action": "BLOCK",
        "payload": {
            "transaction_id": "demo_fraud_01",
            "amount": 25000.0,
            "failure_code": "FRAUD_RISK_BLOCK",
            "payment_method": "CREDIT_CARD",
            "predicted_recovery_probability": 0.92,
        }
    },
    {
        "id": "expired_card",
        "title": "Expired Card Credential",
        "badge": "Customer Nudge",
        "color": "gold",
        "description": "Non-retryable EXPIRED_CARD failure. Automatically triggers customer update nudge.",
        "expected_action": "CUSTOMER_ACTION_REQUIRED",
        "payload": {
            "transaction_id": "demo_expired_01",
            "amount": 3200.0,
            "failure_code": "EXPIRED_CARD",
            "payment_method": "CREDIT_CARD",
            "predicted_recovery_probability": 0.40,
        }
    },
    {
        "id": "negative_erv_skip",
        "title": "Negative Net ERV Skip",
        "badge": "Cost Optimizer",
        "color": "blue",
        "description": "Low P_rec (12%) where retry cost exceeds expected recovery. Engine suppresses retry.",
        "expected_action": "NO_ACTION",
        "payload": {
            "transaction_id": "demo_skip_01",
            "amount": 80.0,
            "failure_code": "TEMPORARY_GATEWAY_FAILURE",
            "payment_method": "WALLET",
            "predicted_recovery_probability": 0.12,
        }
    }
]


@router.get(
    "/scenarios",
    response_model=List[DemoScenario],
    status_code=status.HTTP_200_OK,
    summary="Get Buildathon Demo Scenarios",
    description="Returns pre-configured one-click demo scenarios for buildathon presentation.",
)
def get_demo_scenarios() -> List[DemoScenario]:
    return [DemoScenario(**s) for s in DEMO_SCENARIOS]


@router.post(
    "/run/{scenario_id}",
    response_model=DecideResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Specific Buildathon Demo Scenario",
    description="Executes a named demo scenario through frozen Phase 3 policy engine and records decision to audit log.",
)
def run_demo_scenario(
    scenario_id: str,
    policy_engine: RecoveryPolicyEngine = Depends(get_policy_engine),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> DecideResponse:
    scenario = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo scenario '{scenario_id}' not found.",
        )

    payload = scenario["payload"]
    prob = payload.get("predicted_recovery_probability", 0.5)

    decision_obj = policy_engine.evaluate_transaction(
        transaction=payload,
        recovery_probability=prob,
    )

    input_summary = {
        "amount": payload.get("amount", 0.0),
        "failure_code": payload.get("failure_code", ""),
        "payment_method": payload.get("payment_method", ""),
    }
    audit_logger.log_decision(decision_obj, input_summary)

    policy_checks = [
        PolicyCheckItem(
            rule_id=c.get("rule_id", ""),
            rule_name=c.get("rule_name", ""),
            passed=bool(c.get("passed", False)),
            reason=str(c.get("reason", "")),
            forced_decision=c.get("forced_decision"),
        )
        for c in decision_obj.policy_checks
    ]

    return DecideResponse(
        decision_id=decision_obj.decision_id,
        transaction_id=decision_obj.transaction_id,
        customer_id=decision_obj.customer_id,
        merchant_id=decision_obj.merchant_id,
        timestamp=decision_obj.timestamp,
        amount=decision_obj.amount,
        failure_code=decision_obj.failure_code,
        retryability=decision_obj.retryability,
        recovery_probability=decision_obj.recovery_probability,
        expected_recovery_value=decision_obj.expected_recovery_value,
        intervention_cost=decision_obj.intervention_cost,
        net_expected_recovery_value=decision_obj.net_expected_recovery_value,
        risk_level=decision_obj.risk_level.value if hasattr(decision_obj.risk_level, "value") else str(decision_obj.risk_level),
        decision=decision_obj.decision.value if hasattr(decision_obj.decision, "value") else str(decision_obj.decision),
        reason=decision_obj.reason,
        policy_checks=policy_checks,
        policy_version=decision_obj.policy_version,
    )
