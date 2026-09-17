import time


def greedy_change(amount, denominations):
    remaining = amount
    used = []
    comparisons = 0
    for coin in sorted(denominations, reverse=True):
        comparisons += 1
        if remaining <= 0:
            break
        count = remaining // coin
        if count > 0:
            used.append({"denomination": coin, "quantity": count})
            remaining -= coin * count
    return used, remaining, comparisons


def optimal_change(amount, denominations, limit=100000):
    if amount > limit:
        return None
    infinity = float("inf")
    best = [0] + [infinity] * amount
    choice = [0] * (amount + 1)
    for value in range(1, amount + 1):
        for coin in denominations:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
                choice[value] = coin
    if best[amount] == infinity:
        return None
    counts = {}
    value = amount
    while value > 0:
        coin = choice[value]
        counts[coin] = counts.get(coin, 0) + 1
        value -= coin
    used = [{"denomination": coin, "quantity": qty} for coin, qty in sorted(counts.items(), reverse=True)]
    return used


def solve(amount, denominations):
    start_time = time.perf_counter()

    greedy_used, remainder, comparisons = greedy_change(amount, denominations)
    greedy_total_coins = sum(entry["quantity"] for entry in greedy_used)
    greedy_value = amount - remainder

    optimal_used = optimal_change(amount, denominations)
    optimal_total_coins = sum(entry["quantity"] for entry in optimal_used) if optimal_used is not None else None

    is_optimal = (
        remainder == 0
        and optimal_total_coins is not None
        and greedy_total_coins == optimal_total_coins
    )

    elapsed = time.perf_counter() - start_time

    return {
        "amount": amount,
        "denominations": sorted(denominations, reverse=True),
        "greedy": {
            "used": greedy_used,
            "total_coins": greedy_total_coins,
            "value_reached": greedy_value,
            "remainder": remainder,
            "exact": remainder == 0,
        },
        "optimal": {
            "used": optimal_used,
            "total_coins": optimal_total_coins,
            "computed": optimal_used is not None,
        },
        "is_greedy_optimal": is_optimal,
        "criterion": "sempre escolher a maior moeda/nota menor ou igual ao valor restante",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
