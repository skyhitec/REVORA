"""
Unit tests for REVORA Phase 3 ERV Calculator.
"""

import pytest
from src.decision.erv_calculator import ERVCalculator
from src.schemas.decision_schemas import InterventionAction


@pytest.fixture
def calculator():
    return ERVCalculator()


def test_gross_erv_calculation(calculator):
    gross = calculator.calculate_gross_erv(amount=1000.0, recovery_probability=0.75)
    assert gross == 750.0


def test_intervention_costs(calculator):
    assert calculator.get_intervention_cost(InterventionAction.RETRY) == 10.0
    assert calculator.get_intervention_cost(InterventionAction.DELAY_AND_RETRY) == 12.0
    assert calculator.get_intervention_cost(InterventionAction.CUSTOMER_ACTION_REQUIRED) == 5.0
    assert calculator.get_intervention_cost(InterventionAction.ESCALATE) == 25.0
    assert calculator.get_intervention_cost(InterventionAction.BLOCK) == 0.0


def test_erv_breakdown_net_value(calculator):
    tx = {"amount": 2000.0, "customer_previous_failures": 1}
    # Gross ERV = 2000 * 0.80 = 1600.0
    # Cost = 10.0
    # Friction = min(2.0 * (1 + 1) * 1.5, 50.0) = 6.0
    # Net ERV = 1600.0 - 10.0 - 6.0 = 1584.0
    breakdown = calculator.calculate_erv_breakdown(tx, 0.80, InterventionAction.RETRY)
    assert breakdown.gross_expected_recovery_value == 1600.0
    assert breakdown.intervention_cost == 10.0
    assert breakdown.friction_penalty == 6.0
    assert breakdown.net_expected_recovery_value == 1584.0
