from algorithms.interval_scheduling.solver import solve
from algorithms.interval_scheduling.generator import generate


def test_empty_input():
    result = solve([])
    assert result["selected_count"] == 0
    assert result["rejected_count"] == 0


def test_single_interval_is_always_selected():
    result = solve([{"id": "A1", "start": 0, "end": 5}])
    assert result["selected_count"] == 1


def test_non_overlapping_intervals_all_selected():
    intervals = [
        {"id": "A1", "start": 0, "end": 2},
        {"id": "A2", "start": 2, "end": 4},
        {"id": "A3", "start": 4, "end": 6},
    ]
    result = solve(intervals)
    assert result["selected_count"] == 3


def test_classic_counterexample_for_longest_first_heuristic():
    intervals = [
        {"id": "long", "start": 0, "end": 10},
        {"id": "short1", "start": 0, "end": 3},
        {"id": "short2", "start": 3, "end": 6},
        {"id": "short3", "start": 6, "end": 10},
    ]
    result = solve(intervals)
    selected_ids = {item["id"] for item in result["selected"]}
    assert selected_ids == {"short1", "short2", "short3"}
    assert result["selected_count"] == 3


def test_duplicate_intervals_are_handled():
    intervals = [
        {"id": "A1", "start": 1, "end": 3},
        {"id": "A2", "start": 1, "end": 3},
    ]
    result = solve(intervals)
    assert result["selected_count"] == 1
    assert result["rejected_count"] == 1


def test_generator_produces_requested_count_and_is_reproducible():
    first = generate(count=30, seed=7)
    second = generate(count=30, seed=7)
    assert len(first) == 30
    assert first == second


def test_large_input_runs_and_selects_at_least_one():
    intervals = generate(count=2000, seed=1, max_time=2000)
    result = solve(intervals)
    assert result["selected_count"] >= 1
    assert result["selected_count"] + result["rejected_count"] == 2000
