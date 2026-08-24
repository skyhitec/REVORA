"""
Policy Schemas for REVORA Phase 3 Recovery Decision & Policy Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class FailureCategory(str, Enum):
    """Standard failure situation categories."""
    HARD_SECURITY_BLOCK = "HARD_SECURITY_BLOCK"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    TRANSIENT_INFRASTRUCTURE = "TRANSIENT_INFRASTRUCTURE"
    BANK_DECLINE_GENERIC = "BANK_DECLINE_GENERIC"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"
    SUCCESS = "SUCCESS"


@dataclass
class PolicyRule:
    """Definition of a deterministic policy guardrail rule."""
    rule_id: str
    rule_name: str
    description: str
    is_hard_guardrail: bool = True


@dataclass
class GuardrailCheckResult:
    """Result of evaluating a policy guardrail."""
    rule_id: str
    rule_name: str
    passed: bool
    reason: str
    forced_decision: Optional[str] = None
