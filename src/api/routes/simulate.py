"""
Simulation Endpoint Route for REVORA Phase 4.1 FastAPI Service.
"""

import uuid
from fastapi import APIRouter, Depends, status

from src.api.schemas import SimulateRequest, DecideResponse, PolicyCheckItem
from src.api.dependencies import get_policy_engine, get_audit_logger
from src.decision.engine import RecoveryPolicyEngine
from src.audit.logger import AuditLogger

router = APIRouter(prefix="/api/v1", tags=["Simulation"])


@router.post(
    "/simulate",
    response_model=DecideResponse,
    status_code=status.HTTP_200_OK,
    summary="API-level Transaction Simulation",
    description="Simulates a single payment failure transaction through frozen Phase 2 recovery probability and Phase 3 policy decision engine.",
)
def simulate_transaction(
    request: SimulateRequest,
    policy_engine: RecoveryPolicyEngine = Depends(get_policy_engine),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> DecideResponse:
    tx_id = f"sim_{uuid.uuid4().hex[:8]}"
    cust_id = f"cust_{uuid.uuid4().hex[:6]}"
    merch_id = "merch_sim_01"

    tx_dict = {
        "transaction_id": tx_id,
        "customer_id": cust_id,
        "merchant_id": merch_id,
        "amount": request.amount or 1500.0,
        "failure_code": request.failure_code or "TEMPORARY_GATEWAY_FAILURE",
        "payment_method": request.payment_method or "UPI",
        "payment_status": "FAILED",
        "is_retryable": True,
        "ip_risk_score": 5.0,
        "merchant_risk_score": 5.0,
        "customer_previous_failures": 1,
    }

    prob = request.recovery_probability if request.recovery_probability is not None else 0.80

    decision_obj = policy_engine.evaluate_transaction(
        transaction=tx_dict,
        recovery_probability=prob,
    )

    input_summary = {
        "amount": tx_dict["amount"],
        "failure_code": tx_dict["failure_code"],
        "payment_method": tx_dict["payment_method"],
        "ip_risk_score": tx_dict["ip_risk_score"],
        "merchant_risk_score": tx_dict["merchant_risk_score"],
        "customer_previous_failures": tx_dict["customer_previous_failures"],
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
