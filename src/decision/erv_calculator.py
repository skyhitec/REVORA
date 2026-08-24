"""
Expected Recovery Value (ERV) & Financial Optimization Engine for REVORA Phase 3.
"""

from typing import Dict, Any, Optional
from src.schemas.decision_schemas import InterventionAction, ERVBreakdown


DEFAULT_INTERVENTION_COSTS: Dict[str, float] = {
    InterventionAction.RETRY.value: 10.0,
    InterventionAction.DELAY_AND_RETRY.value: 12.0,
    InterventionAction.RETRY_WITH_CAUTION.value: 15.0,
    InterventionAction.CUSTOMER_ACTION_REQUIRED.value: 5.0,
    InterventionAction.ESCALATE.value: 25.0,
    InterventionAction.BLOCK.value: 0.0,
    InterventionAction.NO_ACTION.value: 0.0,
}


class ERVCalculator:
    """Calculates Gross and Net Expected Recovery Values and financial costs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        costs = self.config.get("intervention_costs", {})
        self.costs = {**DEFAULT_INTERVENTION_COSTS, **costs}

        f_penalties = self.config.get("friction_penalties", {})
        self.base_friction = f_penalties.get("base_friction", 2.0)
        self.failure_mult = f_penalties.get("failure_multiplier", 1.5)
        self.max_friction = f_penalties.get("max_friction_penalty", 50.0)

    def calculate_gross_erv(self, amount: float, recovery_probability: float) -> float:
        """
        Calculates Gross Expected Recovery Value = amount * recovery_probability.
        """
        return round(float(amount) * float(recovery_probability), 2)

    def get_intervention_cost(self, intervention: InterventionAction) -> float:
        """Returns execution cost for a given intervention action."""
        key = intervention.value if isinstance(intervention, InterventionAction) else str(intervention)
        return float(self.costs.get(key, 0.0))

    def calculate_friction_penalty(self, transaction: Dict[str, Any]) -> float:
        """
        Calculates customer dissatisfaction / friction penalty.
        """
        prev_failures = float(transaction.get("customer_previous_failures", 0))
        penalty = self.base_friction * (1.0 + prev_failures) * self.failure_mult
        return round(min(penalty, self.max_friction), 2)

    def calculate_erv_breakdown(
        self,
        transaction: Dict[str, Any],
        recovery_probability: float,
        intervention: InterventionAction,
    ) -> ERVBreakdown:
        """
        Calculates complete ERV Breakdown object for a transaction and target intervention.
        """
        amount = float(transaction.get("amount", 0.0))
        gross_erv = self.calculate_gross_erv(amount, recovery_probability)
        cost = self.get_intervention_cost(intervention)

        if intervention in (InterventionAction.BLOCK, InterventionAction.NO_ACTION):
            friction = 0.0
            net_erv = 0.0
        else:
            friction = self.calculate_friction_penalty(transaction)
            net_erv = round(gross_erv - cost - friction, 2)

        return ERVBreakdown(
            gross_expected_recovery_value=gross_erv,
            intervention_cost=cost,
            friction_penalty=friction,
            net_expected_recovery_value=net_erv,
        )
