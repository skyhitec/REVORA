"""
Cryptographic SHA-256 Hash Chaining Engine for REVORA Phase 3.

Ensures tamper-evident immutability for decision audit trail logs.
"""

import hashlib
import json
from typing import Dict, Any


GENESIS_HASH = hashlib.sha256("REVORA_PHASE3_GENESIS".encode("utf-8")).hexdigest()


class HashChainEngine:
    """Computes SHA-256 cryptographic hash chains for audit records."""

    @staticmethod
    def get_genesis_hash() -> str:
        """Returns the fixed genesis hash string."""
        return GENESIS_HASH

    @staticmethod
    def canonical_json(data: Dict[str, Any]) -> str:
        """
        Produces deterministic, key-sorted, compact JSON representation.
        Excludes existing 'current_hash' field if present.
        """
        payload = {k: v for k, v in data.items() if k != "current_hash"}
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @classmethod
    def compute_record_hash(cls, previous_hash: str, record_dict: Dict[str, Any]) -> str:
        """
        Computes current_hash = SHA256(previous_hash + canonical_json(record_dict)).

        Args:
            previous_hash: Hex string of previous audit record hash.
            record_dict: Record data dictionary.

        Returns:
            SHA-256 hex string digest.
        """
        canonical_str = cls.canonical_json(record_dict)
        composite = f"{previous_hash}{canonical_str}".encode("utf-8")
        return hashlib.sha256(composite).hexdigest()
