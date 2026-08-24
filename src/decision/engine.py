"""
Recovery Policy & Decision Engine Main Orchestrator for REVORA Phase 3.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.schemas.decision_schemas import DecisionObject, InterventionAction, RiskLevel
from src.policy.failure_classifier import FailureClassifier
from src.policy.guardrails import SafetyGuardrails
from src.policy.policy_rules import PolicyRulesManager
from src.decision.risk_classifier import RiskClassifier
from src.decision.erv_calculator import ERVCalculator
from src.decision.intervention_selector import InterventionSelector
from src.decision.explainer import DecisionExplainer


class RecoveryPolicyEngine:
    """
    Production-grade Policy & Decision Engine orchestrator.

    Consumes transaction features and Phase 2 recovery probability,
    evaluates safety guardrails, classifies risk, calculates ERV,
    selects bounded intervention actions, and outputs an explainable DecisionObject.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        policy_cfg = self.config.get("policy", {})
        self.policy_version = policy_cfg.get("version", "1.0.0")

        self.classifier = FailureClassifier()
        self.guardrails = SafetyGuardrails(self.config)
        self.risk_engine = RiskClassifier(self.config)
        self.erv_calculator = ERVCalculator(self.config)
        self.selector = InterventionSelector(self.config)
        self.explainer = DecisionExplainer()

    def evaluate_transaction(
        self,
        transaction: Dict[str, Any],
        recovery_probability: float,
        timestamp: Optional[str] = None,
    ) -> DecisionObject:
        """
        Evaluates a single transaction and returns an explainable DecisionObject.

        Args:
            transaction: Dictionary of pre-recovery transaction attributes.
            recovery_probability: Predicted recovery probability P(recovered=1) from Phase 2.
            timestamp: Optional ISO timestamp string.

        Returns:
            DecisionObject instance.
        """
        tx_id = str(transaction.get("transaction_id", f"tx_{uuid.uuid4().hex[:8]}"))
        cust_id = str(transaction.get("customer_id", "cust_unknown"))
        merch_id = str(transaction.get("merchant_id", "merch_unknown"))
        amount = float(transaction.get("amount", 0.0))
        f_code = str(transaction.get("failure_code", "UNKNOWN_FAILURE"))
        is_retry = self.classifier.is_retryable(f_code, transaction.get("is_retryable", True))

        ts = timestamp or datetime.now(timezone.utc).isoformat()
        decision_id = f"dec_{uuid.uuid4().hex[:12]}"

        # Step 1: Risk Classification
        risk_level = self.risk_engine.classify(transaction)

        # Step 2: Guardrail Evaluation
        guardrail_results = self.guardrails.evaluate_hard_guardrails(
            transaction=transaction,
            risk_level=risk_level,
            recovery_probability=recovery_probability,
        )

        # Step 3: Select Bounded Intervention Action
        decision_action, raw_reason = self.selector.select_intervention(
            transaction=transaction,
            risk_level=risk_level,
            recovery_probability=recovery_probability,
            guardrail_results=guardrail_results,
        )

        # Step 4: Calculate ERV Breakdown
        erv_breakdown = self.erv_calculator.calculate_erv_breakdown(
            transaction=transaction,
            recovery_probability=recovery_probability,
            intervention=decision_action,
        )

        # Step 5: Synthesize Human-Readable Explanation
        explanation = self.explainer.synthesize_explanation(
            transaction=transaction,
            decision=decision_action,
            raw_reason=raw_reason,
            risk_level=risk_level,
            recovery_probability=recovery_probability,
            erv_breakdown=erv_breakdown,
            guardrail_results=guardrail_results,
        )

        # Format policy checks for audit
        policy_checks_formatted = PolicyRulesManager.format_rule_evaluations(guardrail_results)

        return DecisionObject(
            decision_id=decision_id,
            transaction_id=tx_id,
            customer_id=cust_id,
            merchant_id=merch_id,
            timestamp=ts,
            amount=amount,
            failure_code=f_code,
            retryability=is_retry,
            recovery_probability=round(float(recovery_probability), 4),
            expected_recovery_value=erv_breakdown.gross_expected_recovery_value,
            intervention_cost=erv_breakdown.intervention_cost,
            net_expected_recovery_value=erv_breakdown.net_expected_recovery_value,
            risk_level=risk_level,
            decision=decision_action,
            reason=explanation,
            policy_checks=policy_checks_formatted,
            policy_version=self.policy_version,
        )
