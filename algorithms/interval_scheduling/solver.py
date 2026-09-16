import time


def solve(intervals):
    start_time = time.perf_counter()
    comparisons = 0

    ordered = sorted(enumerate(intervals), key=lambda pair: pair[1]["end"])

    selected = []
    rejected = []
    last_end = float("-inf")

    for index, interval in ordered:
        comparisons += 1
        if interval["start"] >= last_end:
            selected.append(interval)
            last_end = interval["end"]
        else:
            rejected.append(interval)

    selected_sorted = sorted(selected, key=lambda item: item["start"])
    rejected_sorted = sorted(rejected, key=lambda item: item["start"])

    elapsed = time.perf_counter() - start_time

    return {
        "input": intervals,
        "selected": selected_sorted,
        "rejected": rejected_sorted,
        "selected_count": len(selected_sorted),
        "rejected_count": len(rejected_sorted),
        "total_count": len(intervals),
        "criterion": "menor horario de termino (earliest finish time)",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
