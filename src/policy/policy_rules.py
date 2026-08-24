"""
Policy Rules Manager for REVORA Phase 3.
"""

from typing import List, Dict, Any
from src.schemas.policy_schemas import GuardrailCheckResult, PolicyRule


class PolicyRulesManager:
    """Manages policy rules registry and formats rule evaluations for audit objects."""

    @staticmethod
    def format_rule_evaluations(
        guardrail_results: List[GuardrailCheckResult]
    ) -> List[Dict[str, Any]]:
        """Formats guardrail results into serializable list of dicts."""
        formatted = []
        for res in guardrail_results:
            formatted.append({
                "rule_id": res.rule_id,
                "rule_name": res.rule_name,
                "passed": res.passed,
                "reason": res.reason,
                "forced_decision": res.forced_decision,
            })
        return formatted

    @staticmethod
    def extract_rule_names(
        guardrail_results: List[GuardrailCheckResult]
    ) -> Dict[str, List[str]]:
        """Categorizes evaluated rules into evaluated, passed, and failed lists."""
        evaluated = []
        passed = []
        failed = []

        for res in guardrail_results:
            evaluated.append(res.rule_id)
            if res.passed:
                passed.append(res.rule_id)
            else:
                failed.append(res.rule_id)

        return {
            "rules_evaluated": evaluated,
            "rules_passed": passed,
            "rules_failed": failed,
        }
