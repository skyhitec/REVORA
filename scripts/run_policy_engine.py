"""
CLI script to evaluate REVORA Phase 3 Recovery Decision & Policy Engine.

Usage:
    python scripts/run_policy_engine.py --input data/processed/val.csv --output data/processed/val_decisions.csv --audit-log data/audit/val_audit.jsonl
"""

import argparse
import sys
import yaml
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import pandas as pd

from src.ml.feature_engineering import FeaturePipeline
from src.ml.trainer import XGBoostRecoveryModel
from src.ml.inference import RecoveryInferenceEngine
from src.decision.engine import RecoveryPolicyEngine
from src.audit.logger import AuditLogger
from src.audit.verifier import AuditVerifier
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="REVORA Phase 3 Policy & Decision Engine CLI")
    parser.add_argument("--input", type=str, default="data/processed/val.csv", help="Input dataset path")
    parser.add_argument("--model-dir", type=str, default="models", help="Phase 2 model directory")
    parser.add_argument("--config", type=str, default="config/policy_config.yaml", help="Policy config path")
    parser.add_argument("--output", type=str, default="data/processed/val_decisions.csv", help="Output decisions CSV path")
    parser.add_argument("--audit-log", type=str, default="data/audit/val_audit.jsonl", help="Audit log output JSONL path")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # Load policy configuration
    config_path = Path(args.config)
    policy_config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            policy_config = yaml.safe_load(f) or {}

    logger.info(f"Loading input transactions from {input_path}...")
    df = pd.read_csv(input_path)

    # If predicted_recovery_probability column is missing, run Phase 2 inference engine
    if "predicted_recovery_probability" not in df.columns:
        logger.info("Scoring recovery probabilities using frozen Phase 2 inference model...")
        model_dir = Path(args.model_dir)
        pipeline_file = model_dir / "feature_pipeline.pkl"
        model_file = model_dir / "recovery_model.pkl"

        import pickle
        with open(pipeline_file, "rb") as f:
            pipeline = pickle.load(f)
        with open(model_file, "rb") as f:
            xgb_model = pickle.load(f)

        inf_engine = RecoveryInferenceEngine(pipeline, xgb_model, optimal_threshold=0.1600)
        df = inf_engine.predict_transactions(df)

    # Initialize Policy Engine and Audit Logger
    policy_engine = RecoveryPolicyEngine(config=policy_config)
    audit_logger = AuditLogger(log_filepath=args.audit_log)

    decisions = []
    reasons = []
    risk_levels = []
    erv_gross = []
    erv_net = []
    intervention_costs = []

    logger.info("Evaluating Phase 3 Policy Engine on transactions...")
    for idx, row in df.iterrows():
        tx_dict = row.to_dict()
        prob = float(tx_dict.get("predicted_recovery_probability", 0.0))
        if pd.isna(prob):
            prob = 0.0

        decision_obj = policy_engine.evaluate_transaction(
            transaction=tx_dict,
            recovery_probability=prob,
        )

        # Log decision to audit trail
        input_summary = {
            "amount": float(tx_dict.get("amount", 0.0)),
            "failure_code": str(tx_dict.get("failure_code", "")),
            "payment_method": str(tx_dict.get("payment_method", "")),
            "ip_risk_score": float(tx_dict.get("ip_risk_score", 0.0)),
            "merchant_risk_score": float(tx_dict.get("merchant_risk_score", 0.0)),
            "customer_previous_failures": int(tx_dict.get("customer_previous_failures", 0)),
        }
        audit_logger.log_decision(decision_obj, input_summary)

        decisions.append(decision_obj.decision.value if hasattr(decision_obj.decision, "value") else str(decision_obj.decision))
        reasons.append(decision_obj.reason)
        risk_levels.append(decision_obj.risk_level.value if hasattr(decision_obj.risk_level, "value") else str(decision_obj.risk_level))
        erv_gross.append(decision_obj.expected_recovery_value)
        erv_net.append(decision_obj.net_expected_recovery_value)
        intervention_costs.append(decision_obj.intervention_cost)

    df["policy_decision"] = decisions
    df["policy_reason"] = reasons
    df["risk_level"] = risk_levels
    df["expected_recovery_value"] = erv_gross
    df["net_expected_recovery_value"] = erv_net
    df["intervention_cost"] = intervention_costs

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved decisions output to {output_path}")

    # Verify audit log integrity
    is_valid, errors = AuditVerifier.verify_audit_file(args.audit_log)
    if is_valid:
        logger.info(f"Audit log {args.audit_log} verified 100% valid with SHA-256 hash chaining.")
    else:
        logger.error(f"Audit log verification failed with errors: {errors}")


if __name__ == "__main__":
    main()
