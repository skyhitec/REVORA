"""
Structured Audit Logger for REVORA Phase 3.

Appends DecisionObject records to an immutable JSONL file with sequence locking
and SHA-256 cryptographic hash chaining.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.schemas.decision_schemas import DecisionObject
from src.schemas.audit_schemas import AuditRecord
from src.audit.hash_chain import HashChainEngine
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """Appends decision records to JSONL with cryptographic hash chaining."""

    def __init__(self, log_filepath: str = "data/audit/audit_trail.jsonl") -> None:
        self.log_filepath = Path(log_filepath)
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = HashChainEngine.get_genesis_hash()
        self.sequence_id = 0
        self._initialize_chain_state()

    def _initialize_chain_state(self) -> None:
        """Reads existing log file to restore sequence count and last hash state."""
        if not self.log_filepath.exists() or os.path.getsize(self.log_filepath) == 0:
            return

        try:
            with open(self.log_filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    last_line = json.loads(lines[-1])
                    self.sequence_id = int(last_line.get("sequence_id", 0))
                    self.last_hash = str(last_line.get("current_hash", HashChainEngine.get_genesis_hash()))
        except Exception as e:
            logger.warning(f"Could not restore audit chain state from {self.log_filepath}: {e}")

    def log_decision(
        self,
        decision_obj: DecisionObject,
        input_summary: Dict[str, Any],
    ) -> AuditRecord:
        """
        Logs a decision object to the JSONL audit file.

        Args:
            decision_obj: Evaluated DecisionObject.
            input_summary: Dictionary of essential raw input features.

        Returns:
            Constructed AuditRecord instance.
        """
        self.sequence_id += 1
        prev_hash = self.last_hash

        rules_eval = [c.get("rule_id", "UNKNOWN") for c in decision_obj.policy_checks]
        rules_pass = [c.get("rule_id", "UNKNOWN") for c in decision_obj.policy_checks if c.get("passed")]
        rules_fail = [c.get("rule_id", "UNKNOWN") for c in decision_obj.policy_checks if not c.get("passed")]

        record_dict: Dict[str, Any] = {
            "sequence_id": self.sequence_id,
            "decision_id": decision_obj.decision_id,
            "transaction_id": decision_obj.transaction_id,
            "timestamp": decision_obj.timestamp,
            "policy_version": decision_obj.policy_version,
            "input_summary": input_summary,
            "model_probability": decision_obj.recovery_probability,
            "risk_level": decision_obj.risk_level.value if hasattr(decision_obj.risk_level, "value") else str(decision_obj.risk_level),
            "expected_recovery_value": decision_obj.expected_recovery_value,
            "intervention_cost": decision_obj.intervention_cost,
            "rules_evaluated": rules_eval,
            "rules_passed": rules_pass,
            "rules_failed": rules_fail,
            "selected_decision": decision_obj.decision.value if hasattr(decision_obj.decision, "value") else str(decision_obj.decision),
            "reason": decision_obj.reason,
            "previous_hash": prev_hash,
        }

        # Compute SHA-256 digest
        curr_hash = HashChainEngine.compute_record_hash(prev_hash, record_dict)
        record_dict["current_hash"] = curr_hash

        # Append to JSONL log file
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict, ensure_ascii=True) + "\n")

        self.last_hash = curr_hash

        return AuditRecord(**record_dict)
