import math

from algorithms.knapsack.solver import solve
from algorithms.knapsack.generator import generate


def test_empty_items():
    result = solve([], 10)
    assert result["total_value"] == 0
    assert result["used_weight"] == 0


def test_single_item_fits_entirely():
    items = [{"name": "A", "weight": 5, "value": 50}]
    result = solve(items, 10)
    assert result["selection"][0]["fraction"] == 1.0
    assert result["total_value"] == 50


def test_single_item_partially_fits():
    items = [{"name": "A", "weight": 10, "value": 100}]
    result = solve(items, 4)
    assert math.isclose(result["selection"][0]["fraction"], 0.4)
    assert math.isclose(result["total_value"], 40)


def test_zero_capacity_selects_nothing():
    items = [{"name": "A", "weight": 5, "value": 50}]
    result = solve(items, 0)
    assert result["total_value"] == 0


def test_greedy_by_ratio_is_optimal_for_fractional_knapsack():
    items = [
        {"name": "A", "weight": 10, "value": 60},
        {"name": "B", "weight": 20, "value": 100},
        {"name": "C", "weight": 30, "value": 120},
    ]
    result = solve(items, 50)
    expected_value = 60 + 100 + (20 / 30) * 120
    assert math.isclose(result["total_value"], expected_value)


def test_duplicate_items_are_handled():
    items = [
        {"name": "A", "weight": 5, "value": 50},
        {"name": "A", "weight": 5, "value": 50},
    ]
    result = solve(items, 10)
    assert math.isclose(result["total_value"], 100)


def test_large_input_uses_full_capacity_or_less():
    items = generate(count=500, seed=9)
    result = solve(items, 1000)
    assert result["used_weight"] <= 1000 + 1e-9
