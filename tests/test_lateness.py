from algorithms.scheduling_lateness.solver import solve, count_inversions
from algorithms.scheduling_lateness.generator import generate


def test_empty_input():
    result = solve([])
    assert result["greedy_order"]["max_lateness"] == 0
    assert result["greedy_order"]["total_lateness"] == 0


def test_single_task_has_no_lateness_if_deadline_is_met():
    result = solve([{"id": "T1", "processing_time": 3, "deadline": 10}])
    assert result["greedy_order"]["max_lateness"] == 0


def test_greedy_order_is_never_worse_than_arbitrary_order():
    tasks = generate(count=15, seed=5)
    result = solve(tasks)
    assert result["greedy_order"]["max_lateness"] <= result["arbitrary_order"]["max_lateness"]


def test_greedy_order_has_no_inversions():
    tasks = generate(count=15, seed=5)
    result = solve(tasks)
    assert result["greedy_order"]["inversions"] == 0


def test_count_inversions_detects_out_of_order_deadlines():
    tasks = [
        {"id": "T1", "processing_time": 1, "deadline": 5},
        {"id": "T2", "processing_time": 1, "deadline": 2},
    ]
    assert count_inversions(tasks) == 1


def test_duplicate_deadlines_are_handled():
    tasks = [
        {"id": "T1", "processing_time": 2, "deadline": 5},
        {"id": "T2", "processing_time": 3, "deadline": 5},
    ]
    result = solve(tasks)
    assert result["greedy_order"]["max_lateness"] >= 0
