"""
Decision Schemas for REVORA Phase 3 Recovery Decision & Policy Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class InterventionAction(str, Enum):
    """Supported bounded recovery intervention actions."""
    RETRY = "RETRY"
    DELAY_AND_RETRY = "DELAY_AND_RETRY"
    RETRY_WITH_CAUTION = "RETRY_WITH_CAUTION"
    CUSTOMER_ACTION_REQUIRED = "CUSTOMER_ACTION_REQUIRED"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"
    NO_ACTION = "NO_ACTION"


class RiskLevel(str, Enum):
    """Deterministic transaction risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ERVBreakdown:
    """Breakdown of Expected Recovery Value calculation."""
    gross_expected_recovery_value: float
    intervention_cost: float
    friction_penalty: float
    net_expected_recovery_value: float


@dataclass
class DecisionObject:
    """
    Explainable Decision Object produced for every evaluated transaction.
    """
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
    risk_level: RiskLevel
    decision: InterventionAction
    reason: str
    policy_checks: List[Dict[str, Any]] = field(default_factory=list)
    policy_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert decision object to a dictionary."""
        return {
            "decision_id": self.decision_id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "merchant_id": self.merchant_id,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "failure_code": self.failure_code,
            "retryability": self.retryability,
            "recovery_probability": self.recovery_probability,
            "expected_recovery_value": self.expected_recovery_value,
            "intervention_cost": self.intervention_cost,
            "net_expected_recovery_value": self.net_expected_recovery_value,
            "risk_level": self.risk_level.value if isinstance(self.risk_level, Enum) else str(self.risk_level),
            "decision": self.decision.value if isinstance(self.decision, Enum) else str(self.decision),
            "reason": self.reason,
            "policy_checks": self.policy_checks,
            "policy_version": self.policy_version,
        }
