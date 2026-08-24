"""
Policy Decision Endpoint Route for REVORA Phase 4.1 FastAPI Service.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import pandas as pd

from src.api.schemas import DecideRequest, DecideResponse, PolicyCheckItem
from src.api.dependencies import get_policy_engine, get_inference_engine, get_audit_logger
from src.decision.engine import RecoveryPolicyEngine
from src.ml.inference import RecoveryInferenceEngine
from src.audit.logger import AuditLogger

router = APIRouter(prefix="/api/v1", tags=["Policy Decision"])


@router.post(
    "/decide",
    response_model=DecideResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Recovery Policy Decision",
    description="Evaluates transaction against frozen Phase 3 Policy Engine to produce deterministic, explainable recovery intervention.",
)
def decide_transaction(
    request: DecideRequest,
    policy_engine: RecoveryPolicyEngine = Depends(get_policy_engine),
    inf_engine: RecoveryInferenceEngine = Depends(get_inference_engine),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> DecideResponse:
    tx_dict = request.model_dump()
    prob = request.predicted_recovery_probability

    # If probability is missing, score it via Phase 2 inference engine if available
    if prob is None:
        if inf_engine is not None:
            try:
                df = pd.DataFrame([tx_dict])
                scored = inf_engine.predict_transactions(df)
                p_val = float(scored.iloc[0].get("predicted_recovery_probability", 0.0))
                prob = 0.0 if pd.isna(p_val) else p_val
            except Exception:
                prob = 0.0
        else:
            prob = 0.0

    try:
        decision_obj = policy_engine.evaluate_transaction(
            transaction=tx_dict,
            recovery_probability=prob,
        )

        # Log decision to audit trail
        input_summary = {
            "amount": request.amount,
            "failure_code": request.failure_code,
            "payment_method": request.payment_method,
            "ip_risk_score": request.ip_risk_score,
            "merchant_risk_score": request.merchant_risk_score,
            "customer_previous_failures": request.customer_previous_failures,
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy decision evaluation failed: {str(e)}",
        )
