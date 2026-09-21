import pytest

from algorithms.caminhoneiro.solver import solve
from algorithms.caminhoneiro.generator import generate


def test_no_stops_needed_when_autonomy_covers_distance():
    result = solve(distance=100, tank_capacity=15, consumption=10, stations=[])
    assert result["feasible"] is True
    assert result["stops_count"] == 0


def test_infeasible_when_no_station_reachable():
    result = solve(distance=1000, tank_capacity=5, consumption=10, stations=[])
    assert result["feasible"] is False
    assert result["reason"] is not None


def test_uses_farthest_reachable_station_not_nearest():
    stations = [
        {"name": "P1", "position": 10},
        {"name": "P2", "position": 90},
    ]
    result = solve(distance=180, tank_capacity=10, consumption=10, stations=stations)
    assert result["feasible"] is True
    assert result["stops"][0]["station"] == "P2"


def test_single_station_exact_distance():
    stations = [{"name": "P1", "position": 50}]
    result = solve(distance=100, tank_capacity=10, consumption=10, stations=stations)
    assert result["feasible"] is True


def test_station_beyond_distance_raises_error():
    stations = [{"name": "P1", "position": 500}]
    with pytest.raises(ValueError):
        solve(distance=100, tank_capacity=10, consumption=10, stations=stations)


def test_generator_produces_sorted_reproducible_stations():
    first = generate(distance=1000, seed=2, station_count=10)
    second = generate(distance=1000, seed=2, station_count=10)
    assert first == second
    positions = [station["position"] for station in first]
    assert positions == sorted(positions)


def test_large_route_is_feasible_with_enough_stations():
    stations = generate(distance=5000, seed=1, station_count=200)
    result = solve(distance=5000, tank_capacity=15, consumption=10, stations=stations)
    assert result["feasible"] is True


def test_generator_never_produces_a_gap_larger_than_twice_the_segment_size():
    for distance in [200, 500, 1000, 2000, 5000]:
        for station_count in [3, 8, 12, 20, 50]:
            for seed in range(10):
                stations = generate(distance=distance, seed=seed, station_count=station_count)
                positions = [0] + [station["position"] for station in stations] + [distance]
                max_gap = max(positions[i + 1] - positions[i] for i in range(len(positions) - 1))
                segment_size = distance / (station_count + 1)
                assert max_gap <= 2 * segment_size + 1


def test_default_demo_parameters_are_feasible():
    stations = generate(distance=1000, seed=42, station_count=12)
    result = solve(distance=1000, tank_capacity=15, consumption=10, stations=stations)
    assert result["feasible"] is True
