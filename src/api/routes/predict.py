"""
Prediction Endpoint Route for REVORA Phase 4.1 FastAPI Service.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import pandas as pd

from src.api.schemas import PredictRequest, PredictResponse
from src.api.dependencies import get_inference_engine
from src.ml.inference import RecoveryInferenceEngine

router = APIRouter(prefix="/api/v1", tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Recovery Probability",
    description="Scores failed transaction using frozen Phase 2 XGBoost model to predict P(recovered=1).",
)
def predict_transaction(
    request: PredictRequest,
    inf_engine: RecoveryInferenceEngine = Depends(get_inference_engine),
) -> PredictResponse:
    if inf_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Phase 2 Prediction Model is not loaded or unavailable.",
        )

    tx_dict = request.model_dump()
    df = pd.DataFrame([tx_dict])

    try:
        scored_df = inf_engine.predict_transactions(df)
        row = scored_df.iloc[0]

        prob = float(row.get("predicted_recovery_probability", 0.0))
        if pd.isna(prob):
            prob = 0.0

        return PredictResponse(
            transaction_id=str(row.get("transaction_id", request.transaction_id)),
            payment_status=str(row.get("payment_status", "FAILED")),
            failure_code=str(row.get("failure_code", request.failure_code)),
            predicted_recovery_probability=round(prob, 4),
            optimal_threshold=inf_engine.optimal_threshold,
            should_intervene=bool(row.get("should_intervene", False)),
            intervention_reason=str(row.get("intervention_reason", "")),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction scoring failed: {str(e)}",
        )
