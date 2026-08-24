"""
Audit Schemas for REVORA Phase 3 Immutable Audit Trail System.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AuditRecord:
    """Immutable audit log entry schema."""
    sequence_id: int
    decision_id: str
    transaction_id: str
    timestamp: str
    policy_version: str
    input_summary: Dict[str, Any]
    model_probability: float
    risk_level: str
    expected_recovery_value: float
    intervention_cost: float
    rules_evaluated: List[str]
    rules_passed: List[str]
    rules_failed: List[str]
    selected_decision: str
    reason: str
    previous_hash: str
    current_hash: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit record to a dictionary."""
        return {
            "sequence_id": self.sequence_id,
            "decision_id": self.decision_id,
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp,
            "policy_version": self.policy_version,
            "input_summary": self.input_summary,
            "model_probability": self.model_probability,
            "risk_level": self.risk_level,
            "expected_recovery_value": self.expected_recovery_value,
            "intervention_cost": self.intervention_cost,
            "rules_evaluated": self.rules_evaluated,
            "rules_passed": self.rules_passed,
            "rules_failed": self.rules_failed,
            "selected_decision": self.selected_decision,
            "reason": self.reason,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
        }
