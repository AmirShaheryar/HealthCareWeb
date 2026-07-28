
from unittest.mock import patch

import pytest

from services import nutrition_service as ns


def test_get_conditions_contains_known_keys():
    keys = ns.get_conditions()
    assert "Iron Deficiency / Anaemia" in keys
    assert "Diabetes / Blood Sugar Control" in keys


def test_get_data_unknown_condition():
    assert ns.get_data("Unknown condition") == {}


def test_filter_by_budget_sets_affordable_flag():
    expensive, budget = ns.filter_by_budget("Iron Deficiency / Anaemia", 30_000)
    assert budget  # non-empty budget list
    assert len(expensive) >= 1
    assert all("affordable" in item and isinstance(item["affordable"], bool) for item in expensive)


def test_compute_value_score_zero_price_or_missing_focus():
    assert ns.compute_value_score({"price": 0, "iron": 5}, "iron") == 0
    assert ns.compute_value_score({"price": 100, "protein": 10}, "iron") == 0


def test_rank_budget_foods_sorted_desc():
    ranked = ns.rank_budget_foods("Iron Deficiency / Anaemia")
    scores = [ns.compute_value_score(item, "iron") for item in ranked]
    assert scores == sorted(scores, reverse=True)


def test_calculate_savings_non_negative():
    assert ns.calculate_savings("Iron Deficiency / Anaemia") >= 0


@patch("services.nutrition_service.random.choice", side_effect=lambda seq: seq[0])
def test_generate_meal_plan_uses_budget_foods(mock_choice):
    plan = ns.generate_meal_plan("Iron Deficiency / Anaemia")
    assert len(plan) == 4
    assert plan[0][0] == "Breakfast"
    names = {p[1] for p in plan}
    assert len(names) == 1  # all same because side_effect always first item


@pytest.mark.parametrize("budget, phrase", [(4000, "lentils"), (8000, "Mix local"), (15000, "balanced")])
def test_generate_recommendation_tiers(budget, phrase):
    text = ns.generate_recommendation("Iron Deficiency / Anaemia", budget)
    assert phrase.lower() in text.lower()


def test_best_swap_returns_top_ranked_name():
    name = ns.best_swap("Iron Deficiency / Anaemia")
    assert isinstance(name, str)
    assert name != "No suggestion"
