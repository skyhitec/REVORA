"""
Real-Time Transaction Stream Processor for REVORA Phase 4.2.

Orchestrates live event generation, Phase 2 ML scoring, Phase 3 policy decisioning,
and audit trail logging.
"""

import time
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Generator, Optional

from src.simulator.event_generator import TransactionEventGenerator
from src.ml.inference import RecoveryInferenceEngine
from src.decision.engine import RecoveryPolicyEngine
from src.schemas.decision_schemas import DecisionObject
from src.audit.logger import AuditLogger
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class SimulationEventResult:
    """Structured output object for a single simulated transaction event."""
    event_index: int
    transaction_id: str
    amount: float
    failure_code: str
    payment_method: str
    recovery_probability: float
    decision: str
    risk_level: str
    expected_recovery_value: float
    net_expected_recovery_value: float
    intervention_cost: float
    reason: str
    processed_at: str
    decision_object: DecisionObject

    def to_dict(self) -> Dict[str, Any]:
        """Converts result object to a serializable dictionary."""
        d = asdict(self)
        d["decision_object"] = self.decision_object.to_dict()
        return d


class TransactionStreamSimulator:
    """Processes simulated transaction streams through Phase 2 & 3 core engines."""

    def __init__(
        self,
        generator: Optional[TransactionEventGenerator] = None,
        inference_engine: Optional[RecoveryInferenceEngine] = None,
        policy_engine: Optional[RecoveryPolicyEngine] = None,
        audit_logger: Optional[AuditLogger] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.generator = generator or TransactionEventGenerator(seed=seed)
        self.policy_engine = policy_engine or RecoveryPolicyEngine()
        self.inference_engine = inference_engine
        self.audit_logger = audit_logger or AuditLogger()

        # Initialize Phase 2 inference engine if not provided
        if self.inference_engine is None:
            from src.api.dependencies import get_inference_engine
            self.inference_engine = get_inference_engine()

    def process_single_event(
        self,
        tx: Dict[str, Any],
        event_index: int = 1,
    ) -> SimulationEventResult:
        """
        Processes a single transaction dict through Phase 2 ML scoring & Phase 3 policy.

        Args:
            tx: Raw transaction event dictionary.
            event_index: Index sequence number in the simulation stream.

        Returns:
            SimulationEventResult containing complete prediction, decision, ERV, and audit trace.
        """
        # Step 1: Phase 2 Prediction Engine Scoring
        if self.inference_engine is not None and tx.get("payment_status") == "FAILED":
            try:
                df = pd.DataFrame([tx])
                scored_df = self.inference_engine.predict_transactions(df)
                prob = float(scored_df.iloc[0].get("predicted_recovery_probability", 0.0))
                prob = 0.0 if pd.isna(prob) else round(prob, 4)
            except Exception as e:
                logger.warning(f"Inference engine scoring fallback (0.0) due to error: {e}")
                prob = 0.0
        else:
            prob = 0.0

        # Step 2: Phase 3 Policy & Decision Engine Evaluation
        decision_obj = self.policy_engine.evaluate_transaction(
            transaction=tx,
            recovery_probability=prob,
        )

        # Step 3: Log decision to Immutable Audit Trail
        input_summary = {
            "amount": tx.get("amount", 0.0),
            "failure_code": tx.get("failure_code", ""),
            "payment_method": tx.get("payment_method", ""),
            "ip_risk_score": tx.get("ip_risk_score", 0.0),
            "merchant_risk_score": tx.get("merchant_risk_score", 0.0),
            "customer_previous_failures": tx.get("customer_previous_failures", 0),
        }
        self.audit_logger.log_decision(decision_obj, input_summary)

        processed_at = datetime.now(timezone.utc).isoformat()

        decision_str = decision_obj.decision.value if hasattr(decision_obj.decision, "value") else str(decision_obj.decision)
        risk_str = decision_obj.risk_level.value if hasattr(decision_obj.risk_level, "value") else str(decision_obj.risk_level)

        return SimulationEventResult(
            event_index=event_index,
            transaction_id=decision_obj.transaction_id,
            amount=decision_obj.amount,
            failure_code=decision_obj.failure_code,
            payment_method=str(tx.get("payment_method", "")),
            recovery_probability=decision_obj.recovery_probability,
            decision=decision_str,
            risk_level=risk_str,
            expected_recovery_value=decision_obj.expected_recovery_value,
            net_expected_recovery_value=decision_obj.net_expected_recovery_value,
            intervention_cost=decision_obj.intervention_cost,
            reason=decision_obj.reason,
            processed_at=processed_at,
            decision_object=decision_obj,
        )

    def run_simulation_batch(
        self,
        total_events: int = 50,
        seed: Optional[int] = None,
    ) -> List[SimulationEventResult]:
        """Runs a synchronous batch of N simulated transaction events."""
        if seed is not None:
            self.generator.set_seed(seed)

        results: List[SimulationEventResult] = []
        for i in range(1, total_events + 1):
            tx = self.generator.generate_event()
            result = self.process_single_event(tx, event_index=i)
            results.append(result)

        logger.info("Successfully processed batch simulation of %d events.", total_events)
        return results

    def stream_events(
        self,
        total_events: int = 100,
        rate_per_sec: float = 10.0,
        seed: Optional[int] = None,
    ) -> Generator[SimulationEventResult, None, None]:
        """
        Yields simulated events in real-time with configurable rate pacing.

        Args:
            total_events: Max events to generate (0 for unlimited).
            rate_per_sec: Target event frequency per second.
            seed: RNG seed for reproducible streaming.
        """
        if seed is not None:
            self.generator.set_seed(seed)

        delay = 1.0 / rate_per_sec if rate_per_sec > 0 else 0.0
        count = 0

        while total_events == 0 or count < total_events:
            count += 1
            tx = self.generator.generate_event()
            result = self.process_single_event(tx, event_index=count)
            yield result

            if delay > 0 and (total_events == 0 or count < total_events):
                time.sleep(delay)
