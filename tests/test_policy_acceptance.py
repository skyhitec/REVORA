"""
End-to-end Acceptance Test Suite for REVORA Phase 3 Recovery Policy Engine.
"""

import pandas as pd
import pytest
from pathlib import Path

from src.decision.engine import RecoveryPolicyEngine
from src.schemas.decision_schemas import InterventionAction
from src.policy.failure_classifier import NON_RETRYABLE_FAILURE_CODES


def test_validation_set_policy_acceptance():
    val_path = Path("data/processed/val.csv")
    if not val_path.exists():
        pytest.skip("Validation set data/processed/val.csv not available.")

    df_val = pd.read_csv(val_path)
    engine = RecoveryPolicyEngine()

    automating_actions = {
        InterventionAction.RETRY,
        InterventionAction.DELAY_AND_RETRY,
        InterventionAction.RETRY_WITH_CAUTION,
    }

    violations = 0
    fraud_blocks = 0
    total_evaluated = 0

    for idx, row in df_val.iterrows():
        tx_dict = row.to_dict()
        # Use synthetic target or baseline probability for evaluation test
        prob = float(tx_dict.get("recovery_probability_target", 0.50))
        if pd.isna(prob):
            prob = 0.50

        decision_obj = engine.evaluate_transaction(tx_dict, recovery_probability=prob)
        total_evaluated += 1

        f_code = tx_dict.get("failure_code", "UNKNOWN_FAILURE")

        # AC-02: Zero automated retry of non-retryable failures
        if f_code in NON_RETRYABLE_FAILURE_CODES:
            if decision_obj.decision in automating_actions:
                violations += 1

        # AC-03: Fraud Protection
        if f_code == "FRAUD_RISK_BLOCK":
            assert decision_obj.decision == InterventionAction.BLOCK
            fraud_blocks += 1

        # AC-04: Explainability
        assert decision_obj.reason is not None and len(decision_obj.reason) > 0

    assert violations == 0, f"Found {violations} non-retryable safety policy violations!"
    assert total_evaluated > 0
