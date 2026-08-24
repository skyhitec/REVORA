"""
Audit Verification Endpoint Route for REVORA Phase 4.1 FastAPI Service.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, status

from src.api.schemas import AuditVerifyResponse
from src.audit.verifier import AuditVerifier

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Trail"])


@router.post(
    "/verify",
    response_model=AuditVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Audit Trail SHA-256 Hash Chain Integrity",
    description="Invokes frozen AuditVerifier to check cryptographic hash chain integrity and tamper detection of JSONL log file.",
)
def verify_audit_trail(
    filepath: str = Query(default="data/audit/val_audit.jsonl", description="Path to JSONL audit file to verify"),
) -> AuditVerifyResponse:
    path = Path(filepath)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit trail file '{filepath}' does not exist.",
        )

    try:
        is_valid, errors = AuditVerifier.verify_audit_file(str(path))
        record_count = 0
        with open(path, "r", encoding="utf-8") as f:
            record_count = sum(1 for line in f if line.strip())

        return AuditVerifyResponse(
            is_valid=is_valid,
            total_records=record_count,
            log_filepath=str(path),
            errors=errors,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit verification failed: {str(e)}",
        )
