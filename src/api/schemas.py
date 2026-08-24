"""
Pydantic API Schemas for REVORA Phase 4.1 FastAPI Service.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check status model."""
    status: str = "ok"
    version: str = "1.0.0"
    phase: str = "Phase 4.1 — Production FastAPI API Layer"
    timestamp: str


class PredictRequest(BaseModel):
    """Request payload for transaction prediction endpoint."""
    transaction_id: str = "tx_sample_01"
    customer_id: str = "cust_001"
    merchant_id: str = "merch_001"
    amount: float = Field(..., gt=0)
    currency: str = "INR"
    payment_method: str = "UPI"
    payment_gateway: str = "RAZORPAY"
    card_type: Optional[str] = "CREDIT_CARD"
    failure_code: str = "TEMPORARY_GATEWAY_FAILURE"
    customer_payment_success_rate: float = Field(default=0.85, ge=0.0, le=1.0)
    customer_previous_transactions: int = Field(default=10, ge=0)
    customer_previous_failures: int = Field(default=1, ge=0)
    days_since_last_successful_payment: float = Field(default=2.5, ge=0.0)
    device_type: str = "MOBILE_ANDROID"
    ip_risk_score: float = Field(default=5.0, ge=0.0, le=100.0)
    merchant_category: str = "ECOMMERCE"
    merchant_risk_score: float = Field(default=5.0, ge=0.0, le=100.0)
    payment_status: str = "FAILED"
    is_retryable: bool = True
    avs_result: str = "MATCH"
    cvv_result: str = "MATCH"
    authentication_result: str = "SUCCESS"
    bank_response_code: str = "00"
    gateway_response_code: str = "GATEWAY_TIMEOUT"


class PredictResponse(BaseModel):
    """Response payload for prediction endpoint."""
    transaction_id: str
    payment_status: str
    failure_code: str
    predicted_recovery_probability: float
    optimal_threshold: float
    should_intervene: bool
    intervention_reason: str


class DecideRequest(BaseModel):
    """Request payload for policy decision endpoint."""
    transaction_id: str = "tx_decide_01"
    customer_id: str = "cust_001"
    merchant_id: str = "merch_001"
    amount: float = Field(..., gt=0)
    failure_code: str = "TEMPORARY_GATEWAY_FAILURE"
    payment_method: str = "UPI"
    payment_gateway: str = "RAZORPAY"
    card_type: Optional[str] = "CREDIT_CARD"
    merchant_category: str = "ECOMMERCE"
    device_type: str = "MOBILE_ANDROID"
    payment_status: str = "FAILED"
    is_retryable: bool = True
    customer_payment_success_rate: float = Field(default=0.85, ge=0.0, le=1.0)
    customer_previous_transactions: int = Field(default=10, ge=0)
    customer_previous_failures: int = Field(default=1, ge=0)
    days_since_last_successful_payment: float = Field(default=2.5, ge=0.0)
    ip_risk_score: float = Field(default=5.0, ge=0.0, le=100.0)
    merchant_risk_score: float = Field(default=5.0, ge=0.0, le=100.0)
    avs_result: str = "MATCH"
    cvv_result: str = "MATCH"
    authentication_result: str = "SUCCESS"
    bank_response_code: str = "00"
    gateway_response_code: str = "GATEWAY_TIMEOUT"
    predicted_recovery_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class PolicyCheckItem(BaseModel):
    """Item schema for guardrail policy checks."""
    rule_id: str
    rule_name: str
    passed: bool
    reason: str
    forced_decision: Optional[str] = None


class DecideResponse(BaseModel):
    """Response payload for policy decision endpoint."""
    decision_id: str
    transaction_id: str
    customer_id: str
    merchant_id: str
    timestamp: str
    amount: float
    failure_code: str
    retryability: bool
    recovery_probability: float
    expected_recovery_value: float
    intervention_cost: float
    net_expected_recovery_value: float
    risk_level: str
    decision: str
    reason: str
    policy_checks: List[PolicyCheckItem]
    policy_version: str


class SimulateRequest(BaseModel):
    """Request payload for API-level simulation endpoint."""
    amount: Optional[float] = Field(default=1500.0, gt=0)
    failure_code: Optional[str] = "TEMPORARY_GATEWAY_FAILURE"
    payment_method: Optional[str] = "UPI"
    recovery_probability: Optional[float] = Field(default=0.80, ge=0.0, le=1.0)


class AuditVerifyResponse(BaseModel):
    """Response model for audit trail SHA-256 verification."""
    is_valid: bool
    total_records: int
    log_filepath: str
    errors: List[str]


class MetricsResponse(BaseModel):
    """Response payload for system metrics endpoint."""
    total_failed_count: int
    optimal_threshold: float
    revenue_at_risk: float
    expected_recoverable_revenue: float
    gross_revenue_recovered: float
    retry_cost: float
    net_revenue_recovered: float
    intervention_rate: float
    intervention_recovery_rate: float
    overall_recovery_yield: float
