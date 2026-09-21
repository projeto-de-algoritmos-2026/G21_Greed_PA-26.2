import itertools
import math
import random

from algorithms.interval_scheduling.solver import solve as solve_interval_scheduling
from algorithms.interval_scheduling.generator import generate as generate_interval_scheduling
from algorithms.interval_partitioning.solver import solve as solve_interval_partitioning
from algorithms.scheduling_lateness.solver import solve as solve_lateness
from algorithms.scheduling_lateness.generator import generate as generate_lateness
from algorithms.knapsack.solver import solve as solve_knapsack
from algorithms.trocador.solver import solve as solve_trocador
from algorithms.huffman.solver import solve as solve_huffman
from algorithms.travel.distance import build_matrix, route_distance
from algorithms.travel import heuristics


def brute_force_interval_scheduling(intervals):
    best = 0
    for size in range(len(intervals), -1, -1):
        for combo in itertools.combinations(intervals, size):
            ordered = sorted(combo, key=lambda item: item["start"])
            valid = all(ordered[i]["end"] <= ordered[i + 1]["start"] for i in range(len(ordered) - 1))
            if valid:
                return len(combo)
    return best


def test_interval_scheduling_matches_brute_force_optimal_count():
    rng = random.Random(11)
    for _ in range(15):
        count = rng.randint(1, 7)
        intervals = generate_interval_scheduling(count=count, seed=rng.randint(0, 10_000), max_time=12)
        result = solve_interval_scheduling(intervals)
        optimal = brute_force_interval_scheduling(intervals)
        assert result["selected_count"] == optimal


def brute_force_min_resources(intervals):
    events = []
    for interval in intervals:
        events.append((interval["start"], 1))
        events.append((interval["end"], -1))
    events.sort(key=lambda event: (event[0], event[1]))
    depth = 0
    peak = 0
    for _, delta in events:
        depth += delta
        peak = max(peak, depth)
    return peak


def test_interval_partitioning_matches_theoretical_minimum_across_random_cases():
    rng = random.Random(21)
    for _ in range(20):
        count = rng.randint(0, 20)
        intervals = [
            {"id": f"L{i}", "start": (s := rng.randint(0, 30)), "end": s + rng.randint(1, 10)}
            for i in range(count)
        ]
        result = solve_interval_partitioning(intervals)
        assert result["resources_used"] == brute_force_min_resources(intervals)


def test_lateness_greedy_never_worse_than_any_random_permutation():
    rng = random.Random(31)
    for _ in range(10):
        tasks = generate_lateness(count=6, seed=rng.randint(0, 10_000))
        result = solve_lateness(tasks)
        greedy_max = result["greedy_order"]["max_lateness"]
        for _ in range(30):
            shuffled = tasks[:]
            rng.shuffle(shuffled)
            from algorithms.scheduling_lateness.solver import build_schedule, summarize
            random_max, _ = summarize(build_schedule(shuffled))
            assert greedy_max <= random_max


def brute_force_fractional_knapsack_value(items, capacity):
    ratios = sorted(items, key=lambda item: item["value"] / item["weight"], reverse=True)
    remaining = capacity
    total = 0.0
    for item in ratios:
        take = min(item["weight"], remaining)
        total += (take / item["weight"]) * item["value"]
        remaining -= take
        if remaining <= 0:
            break
    return total


def test_knapsack_matches_independent_reference_implementation():
    rng = random.Random(41)
    for _ in range(15):
        items = [
            {"name": f"I{i}", "weight": rng.randint(1, 50), "value": rng.randint(1, 500)}
            for i in range(rng.randint(1, 10))
        ]
        capacity = rng.randint(1, 200)
        result = solve_knapsack(items, capacity)
        expected = brute_force_fractional_knapsack_value(items, capacity)
        assert math.isclose(result["total_value"], expected, rel_tol=1e-9)


def dp_optimal_coin_count(amount, denominations):
    infinity = float("inf")
    best = [0] + [infinity] * amount
    for value in range(1, amount + 1):
        for coin in denominations:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
    return best[amount] if best[amount] != infinity else None


def test_trocador_canonical_real_system_always_matches_optimal():
    rng = random.Random(51)
    denominations = [100, 50, 20, 10, 5, 2, 1]
    for _ in range(40):
        amount = rng.randint(0, 500)
        result = solve_trocador(amount, denominations)
        assert result["is_greedy_optimal"] is True
        assert result["greedy"]["total_coins"] == dp_optimal_coin_count(amount, denominations)


def test_trocador_greedy_coin_count_never_beats_optimal():
    rng = random.Random(61)
    for _ in range(25):
        denominations = sorted(set(rng.sample(range(1, 30), rng.randint(2, 5))))
        if 1 not in denominations:
            denominations.append(1)
        amount = rng.randint(1, 100)
        result = solve_trocador(amount, denominations)
        if result["optimal"]["total_coins"] is not None:
            assert result["greedy"]["total_coins"] >= result["optimal"]["total_coins"]


def shannon_entropy_bits(text):
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in frequencies.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


def test_huffman_average_code_length_is_close_to_entropy_bound():
    text = "the quick brown fox jumps over the lazy dog the fox runs away quickly" * 3
    result = solve_huffman(text)
    entropy = shannon_entropy_bits(text)
    assert result["average_code_length"] >= entropy - 1e-9
    assert result["average_code_length"] < entropy + 1.0


def test_huffman_more_skewed_text_compresses_better_than_uniform_text():
    skewed = "a" * 90 + "b" * 5 + "c" * 5
    uniform = "abc" * 33 + "a"
    skewed_result = solve_huffman(skewed)
    uniform_result = solve_huffman(uniform)
    assert skewed_result["compression_ratio"] > uniform_result["compression_ratio"]


def brute_force_tsp_optimal(locations, matrix):
    indices = list(range(len(locations)))
    start = indices[0]
    rest = indices[1:]
    best = None
    for perm in itertools.permutations(rest):
        order = [start] + list(perm)
        length = route_distance(order, matrix)
        if best is None or length < best:
            best = length
    return best


def test_heuristics_never_beat_brute_force_optimal():
    rng = random.Random(71)
    algorithms_to_check = [
        "nearest_neighbor",
        "farthest_neighbor",
        "nearest_insertion",
        "farthest_insertion",
        "cheapest_insertion",
        "greedy_benefit_distance",
    ]
    for _ in range(6):
        count = rng.randint(4, 7)
        locations = [
            {
                "id": i,
                "name": f"C{i}",
                "latitude": rng.uniform(-30, 10),
                "longitude": rng.uniform(-70, -35),
                "region": "R",
                "score": rng.randint(1, 100),
            }
            for i in range(count)
        ]
        matrix = build_matrix(locations)
        optimal = brute_force_tsp_optimal(locations, matrix)
        for key in algorithms_to_check:
            result = heuristics.run_algorithm(key, locations, matrix)
            assert result["total_distance_km"] >= optimal - 1e-6


def test_multi_start_nearest_neighbor_is_always_at_least_as_good_as_worst_single_start():
    rng = random.Random(81)
    locations = [
        {
            "id": i,
            "name": f"C{i}",
            "latitude": rng.uniform(-30, 10),
            "longitude": rng.uniform(-70, -35),
            "region": "R",
            "score": 50,
        }
        for i in range(8)
    ]
    matrix = build_matrix(locations)
    multi = heuristics.multi_start_nearest_neighbor(locations, matrix)
    all_single_starts = [heuristics.nearest_neighbor(locations, matrix, start=i)["total_distance_km"] for i in range(len(locations))]
    assert multi["total_distance_km"] <= max(all_single_starts) + 1e-9
    assert multi["total_distance_km"] == min(all_single_starts)
