from algorithms.interval_partitioning.solver import solve, compute_depth
from algorithms.interval_partitioning.generator import generate


def test_empty_input():
    result = solve([])
    assert result["resources_used"] == 0
    assert result["depth"] == 0


def test_single_interval_uses_one_resource():
    result = solve([{"id": "L1", "start": 0, "end": 5}])
    assert result["resources_used"] == 1


def test_non_overlapping_intervals_use_one_resource():
    intervals = [
        {"id": "L1", "start": 0, "end": 2},
        {"id": "L2", "start": 2, "end": 4},
        {"id": "L3", "start": 4, "end": 6},
    ]
    result = solve(intervals)
    assert result["resources_used"] == 1


def test_resources_used_matches_depth():
    intervals = [
        {"id": "L1", "start": 0, "end": 6},
        {"id": "L2", "start": 1, "end": 4},
        {"id": "L3", "start": 2, "end": 5},
        {"id": "L4", "start": 3, "end": 7},
    ]
    result = solve(intervals)
    assert result["resources_used"] == compute_depth(intervals)


def test_no_resource_has_overlapping_intervals():
    intervals = generate(count=25, seed=3)
    result = solve(intervals)
    for resource in result["resources"]:
        sorted_intervals = sorted(resource["intervals"], key=lambda item: item["start"])
        for i in range(len(sorted_intervals) - 1):
            assert sorted_intervals[i]["end"] <= sorted_intervals[i + 1]["start"]


def test_duplicate_intervals_require_multiple_resources():
    intervals = [
        {"id": "L1", "start": 0, "end": 5},
        {"id": "L2", "start": 0, "end": 5},
        {"id": "L3", "start": 0, "end": 5},
    ]
    result = solve(intervals)
    assert result["resources_used"] == 3
