import time

from . import locations_store
from .travel.distance import build_matrix
from .travel.heuristics import run_algorithm as run_travel_algorithm
from .interval_scheduling.solver import solve as solve_interval_scheduling
from .interval_scheduling.generator import generate as generate_interval_scheduling
from .interval_partitioning.solver import solve as solve_interval_partitioning
from .interval_partitioning.generator import generate as generate_interval_partitioning
from .scheduling_lateness.solver import solve as solve_lateness
from .scheduling_lateness.generator import generate as generate_lateness
from .knapsack.solver import solve as solve_knapsack
from .knapsack.generator import generate as generate_knapsack

TRAVEL_SIZES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
CLASSIC_SIZES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000]


def _pick_locations(size):
    exact = locations_store.load_test_set(size)
    if exact is not None:
        return exact
    all_locations = locations_store.get_all()
    return all_locations[:size]


def run_travel_benchmark(algorithm_keys, sizes=None):
    sizes = sizes or TRAVEL_SIZES
    results = []
    for size in sizes:
        locations = _pick_locations(size)
        if len(locations) < 2:
            continue
        matrix = build_matrix(locations)
        for key in algorithm_keys:
            entry = {"algorithm": key, "size": len(locations)}
            try:
                start = time.perf_counter()
                outcome = run_travel_algorithm(key, locations, matrix)
                elapsed = time.perf_counter() - start
                entry.update({
                    "success": True,
                    "elapsed_seconds": elapsed,
                    "total_distance_km": outcome["total_distance_km"],
                    "comparisons": outcome["metrics"]["comparisons"],
                })
            except ValueError as error:
                entry.update({"success": False, "reason": str(error)})
            results.append(entry)
    return results


def run_classic_benchmark(kind, sizes=None, seed=42):
    sizes = sizes or CLASSIC_SIZES
    results = []
    for size in sizes:
        entry = {"size": size}
        start = time.perf_counter()
        if kind == "interval_scheduling":
            data = generate_interval_scheduling(count=size, seed=seed, max_time=max(size, 24))
            outcome = solve_interval_scheduling(data)
            entry["comparisons"] = outcome["metrics"]["comparisons"]
        elif kind == "interval_partitioning":
            data = generate_interval_partitioning(count=size, seed=seed, max_time=max(size, 24))
            outcome = solve_interval_partitioning(data)
            entry["comparisons"] = outcome["metrics"]["comparisons"]
        elif kind == "lateness":
            data = generate_lateness(count=size, seed=seed, max_deadline=max(size * 2, 60))
            outcome = solve_lateness(data)
            entry["comparisons"] = outcome["metrics"]["comparisons"]
        elif kind == "knapsack":
            data = generate_knapsack(count=size, seed=seed)
            outcome = solve_knapsack(data, capacity=size * 10)
            entry["comparisons"] = outcome["metrics"]["comparisons"]
        else:
            raise ValueError(f"Tipo de benchmark desconhecido: {kind}")
        elapsed = time.perf_counter() - start
        entry["elapsed_seconds"] = elapsed
        results.append(entry)
    return results
