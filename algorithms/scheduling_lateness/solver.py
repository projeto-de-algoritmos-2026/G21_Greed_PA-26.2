import time


def build_schedule(tasks):
    completion = 0
    schedule = []
    for task in tasks:
        completion += task["processing_time"]
        lateness = max(0, completion - task["deadline"])
        schedule.append({
            "id": task["id"],
            "processing_time": task["processing_time"],
            "deadline": task["deadline"],
            "completion": completion,
            "lateness": lateness,
        })
    return schedule


def count_inversions(tasks):
    inversions = 0
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            if tasks[i]["deadline"] > tasks[j]["deadline"]:
                inversions += 1
    return inversions


def summarize(schedule):
    max_lateness = max((item["lateness"] for item in schedule), default=0)
    total_lateness = sum(item["lateness"] for item in schedule)
    return max_lateness, total_lateness


def solve(tasks):
    start_time = time.perf_counter()
    comparisons = 0

    arbitrary_schedule = build_schedule(tasks)
    arbitrary_max, arbitrary_total = summarize(arbitrary_schedule)
    arbitrary_inversions = count_inversions(tasks)

    ordered_tasks = sorted(tasks, key=lambda task: task["deadline"])
    comparisons += len(tasks)
    greedy_schedule = build_schedule(ordered_tasks)
    greedy_max, greedy_total = summarize(greedy_schedule)
    greedy_inversions = count_inversions(ordered_tasks)

    elapsed = time.perf_counter() - start_time

    return {
        "input": tasks,
        "arbitrary_order": {
            "schedule": arbitrary_schedule,
            "max_lateness": arbitrary_max,
            "total_lateness": arbitrary_total,
            "inversions": arbitrary_inversions,
        },
        "greedy_order": {
            "schedule": greedy_schedule,
            "max_lateness": greedy_max,
            "total_lateness": greedy_total,
            "inversions": greedy_inversions,
        },
        "criterion": "ordenar por deadline crescente (earliest deadline first)",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
