import heapq
import time


def compute_depth(intervals):
    events = []
    for interval in intervals:
        events.append((interval["start"], 1))
        events.append((interval["end"], -1))
    events.sort(key=lambda event: (event[0], event[1]))

    depth = 0
    max_depth = 0
    for _, delta in events:
        depth += delta
        max_depth = max(max_depth, depth)
    return max_depth


def solve(intervals):
    start_time = time.perf_counter()
    comparisons = 0

    ordered = sorted(intervals, key=lambda item: item["start"])

    heap = []
    resources = {}
    next_resource_id = 0
    assignment = []

    for interval in ordered:
        comparisons += 1
        if heap and heap[0][0] <= interval["start"]:
            end_time, resource_id = heapq.heappop(heap)
            resources[resource_id].append(interval)
            heapq.heappush(heap, (interval["end"], resource_id))
        else:
            resource_id = next_resource_id
            next_resource_id += 1
            resources[resource_id] = [interval]
            heapq.heappush(heap, (interval["end"], resource_id))
        assignment.append({"interval": interval, "resource": resource_id})

    depth = compute_depth(intervals)
    elapsed = time.perf_counter() - start_time

    resource_list = [
        {"resource": resource_id, "intervals": items}
        for resource_id, items in sorted(resources.items())
    ]

    return {
        "input": intervals,
        "assignment": assignment,
        "resources": resource_list,
        "resources_used": next_resource_id,
        "depth": depth,
        "criterion": "ordenar por horario de inicio e reutilizar o recurso disponivel mais cedo (heap de termino)",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
