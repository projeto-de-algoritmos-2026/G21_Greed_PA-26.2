import pytest

from algorithms.travel.distance import build_matrix
from algorithms.travel import heuristics


SAMPLE_LOCATIONS = [
    {"id": 1, "name": "A", "latitude": -15.7939, "longitude": -47.8828, "region": "R1", "score": 90},
    {"id": 2, "name": "B", "latitude": -23.5505, "longitude": -46.6333, "region": "R1", "score": 70},
    {"id": 3, "name": "C", "latitude": -22.9068, "longitude": -43.1729, "region": "R2", "score": 60},
    {"id": 4, "name": "D", "latitude": -19.9167, "longitude": -43.9345, "region": "R2", "score": 50},
    {"id": 5, "name": "E", "latitude": -25.4284, "longitude": -49.2733, "region": "R1", "score": 40},
]


@pytest.mark.parametrize("key", list(heuristics.ALGORITHMS.keys()))
def test_all_heuristics_visit_every_city_exactly_once(key):
    matrix = build_matrix(SAMPLE_LOCATIONS)
    result = heuristics.run_algorithm(key, SAMPLE_LOCATIONS, matrix)
    visited = result["order"][:-1] if result["order"][0] == result["order"][-1] else result["order"]
    assert sorted(visited) == sorted(range(len(SAMPLE_LOCATIONS)))
    assert result["total_distance_km"] >= 0


@pytest.mark.parametrize("key", list(heuristics.ALGORITHMS.keys()))
def test_all_heuristics_handle_two_cities(key):
    two_cities = SAMPLE_LOCATIONS[:2]
    matrix = build_matrix(two_cities)
    result = heuristics.run_algorithm(key, two_cities, matrix)
    assert len(set(result["order"][:2])) == 2


def test_unknown_algorithm_raises_error():
    matrix = build_matrix(SAMPLE_LOCATIONS)
    with pytest.raises(ValueError):
        heuristics.run_algorithm("does_not_exist", SAMPLE_LOCATIONS, matrix)


def test_cheapest_insertion_respects_max_size_limit():
    oversized = [
        {"id": i, "name": f"L{i}", "latitude": (i % 90) - 45, "longitude": (i % 180) - 90, "region": "R", "score": 50}
        for i in range(heuristics.MAX_SIZE_CHEAPEST_INSERTION + 5)
    ]
    matrix = build_matrix(oversized)
    with pytest.raises(ValueError):
        heuristics.cheapest_insertion(oversized, matrix)


def test_nearest_neighbor_is_deterministic_for_same_start():
    matrix = build_matrix(SAMPLE_LOCATIONS)
    first = heuristics.nearest_neighbor(SAMPLE_LOCATIONS, matrix, start=0)
    second = heuristics.nearest_neighbor(SAMPLE_LOCATIONS, matrix, start=0)
    assert first["order"] == second["order"]


def test_multi_start_result_is_at_least_as_good_as_single_start():
    matrix = build_matrix(SAMPLE_LOCATIONS)
    single = heuristics.nearest_neighbor(SAMPLE_LOCATIONS, matrix, start=0)
    multi = heuristics.multi_start_nearest_neighbor(SAMPLE_LOCATIONS, matrix)
    assert multi["total_distance_km"] <= single["total_distance_km"] + 1e-9
