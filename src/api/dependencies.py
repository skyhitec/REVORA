"""
FastAPI Shared Dependency Providers for REVORA Phase 4.1.

Instantiates and reuses frozen Phase 2 and Phase 3 singletons cleanly.
"""

import os
import pickle
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from src.ml.inference import RecoveryInferenceEngine
from src.decision.engine import RecoveryPolicyEngine
from src.audit.logger import AuditLogger
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Singletons cache
_POLICY_CONFIG: Optional[Dict[str, Any]] = None
_INFERENCE_ENGINE: Optional[RecoveryInferenceEngine] = None
_POLICY_ENGINE: Optional[RecoveryPolicyEngine] = None
_AUDIT_LOGGER: Optional[AuditLogger] = None


def get_policy_config(config_path: str = "config/policy_config.yaml") -> Dict[str, Any]:
    """Loads and caches policy configuration."""
    global _POLICY_CONFIG
    if _POLICY_CONFIG is None:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                _POLICY_CONFIG = yaml.safe_load(f) or {}
        else:
            _POLICY_CONFIG = {}
    return _POLICY_CONFIG


def get_inference_engine(model_dir: str = "models") -> Optional[RecoveryInferenceEngine]:
    """Loads and caches Phase 2 RecoveryInferenceEngine."""
    global _INFERENCE_ENGINE
    if _INFERENCE_ENGINE is None:
        p_path = Path(model_dir) / "feature_pipeline.pkl"
        m_path = Path(model_dir) / "recovery_model.pkl"

        if p_path.exists() and m_path.exists():
            try:
                with open(p_path, "rb") as f:
                    pipeline = pickle.load(f)
                with open(m_path, "rb") as f:
                    model = pickle.load(f)
                _INFERENCE_ENGINE = RecoveryInferenceEngine(pipeline, model, optimal_threshold=0.1600)
                logger.info("Successfully initialized RecoveryInferenceEngine singleton.")
            except Exception as e:
                logger.error(f"Error loading Phase 2 inference artifacts: {e}")
        else:
            logger.warning(f"Phase 2 model files not found in {model_dir}/.")

    return _INFERENCE_ENGINE


def get_policy_engine() -> RecoveryPolicyEngine:
    """Provides Phase 3 RecoveryPolicyEngine singleton."""
    global _POLICY_ENGINE
    if _POLICY_ENGINE is None:
        config = get_policy_config()
        _POLICY_ENGINE = RecoveryPolicyEngine(config=config)
        logger.info("Successfully initialized RecoveryPolicyEngine singleton.")
    return _POLICY_ENGINE


def get_audit_logger(log_filepath: str = "data/audit/audit_trail.jsonl") -> AuditLogger:
    """Provides AuditLogger singleton."""
    global _AUDIT_LOGGER
    if _AUDIT_LOGGER is None:
        _AUDIT_LOGGER = AuditLogger(log_filepath=log_filepath)
    return _AUDIT_LOGGER
