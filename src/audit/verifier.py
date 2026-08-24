"""
Audit Trail Verifier Engine for REVORA Phase 3.

Validates sequence continuity and cryptographic SHA-256 hash chaining integrity
across audit logs to detect tampering or corruption.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

from src.audit.hash_chain import HashChainEngine
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class AuditVerifier:
    """Verifies SHA-256 hash chain continuity and audit log integrity."""

    @staticmethod
    def verify_audit_file(log_filepath: str) -> Tuple[bool, List[str]]:
        """
        Verifies line-by-line hash integrity of an audit JSONL file.

        Args:
            log_filepath: Path to audit_trail.jsonl.

        Returns:
            Tuple of (is_valid: bool, error_messages: List[str]).
        """
        path = Path(log_filepath)
        if not path.exists() or path.stat().st_size == 0:
            return True, []

        errors: List[str] = []
        expected_prev_hash = HashChainEngine.get_genesis_hash()
        expected_seq = 1

        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        for i, line in enumerate(lines, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: JSON decode error - {e}")
                continue

            seq_id = record.get("sequence_id")
            prev_hash = record.get("previous_hash")
            curr_hash = record.get("current_hash")

            if seq_id != expected_seq:
                errors.append(f"Line {i}: Sequence mismatch. Expected {expected_seq}, got {seq_id}.")

            if prev_hash != expected_prev_hash:
                errors.append(
                    f"Line {i} (Seq {seq_id}): Previous hash mismatch. "
                    f"Expected {expected_prev_hash}, got {prev_hash}."
                )

            # Re-compute current hash
            recomputed_hash = HashChainEngine.compute_record_hash(prev_hash, record)
            if recomputed_hash != curr_hash:
                errors.append(
                    f"Line {i} (Seq {seq_id}): Current hash mismatch (Tampering detected!). "
                    f"Expected {recomputed_hash}, got {curr_hash}."
                )

            expected_prev_hash = curr_hash
            expected_seq += 1

        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"Audit log {log_filepath} verified successfully ({len(lines)} records).")
        else:
            logger.error(f"Audit log verification failed with {len(errors)} error(s).")

        return is_valid, errors
