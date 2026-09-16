import time


def solve(items, capacity):
    start_time = time.perf_counter()
    comparisons = 0

    enriched = []
    for item in items:
        ratio = item["value"] / item["weight"] if item["weight"] > 0 else float("inf")
        enriched.append({**item, "ratio": ratio})

    ordered = sorted(enriched, key=lambda item: item["ratio"], reverse=True)

    remaining = capacity
    total_value = 0.0
    selection = []

    for item in ordered:
        comparisons += 1
        if remaining <= 0:
            fraction = 0.0
        elif item["weight"] <= remaining:
            fraction = 1.0
        else:
            fraction = remaining / item["weight"]

        taken_weight = item["weight"] * fraction
        taken_value = item["value"] * fraction
        remaining -= taken_weight
        total_value += taken_value

        selection.append({
            "name": item["name"],
            "weight": item["weight"],
            "value": item["value"],
            "ratio": item["ratio"],
            "fraction": fraction,
            "taken_weight": taken_weight,
            "taken_value": taken_value,
        })

    used_weight = capacity - remaining
    elapsed = time.perf_counter() - start_time

    return {
        "input": items,
        "capacity": capacity,
        "selection": selection,
        "used_weight": used_weight,
        "remaining_capacity": remaining,
        "total_value": total_value,
        "criterion": "ordenar por valor especifico (valor/peso) decrescente",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
