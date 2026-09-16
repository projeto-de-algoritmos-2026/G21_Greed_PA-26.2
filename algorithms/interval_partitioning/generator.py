import random


def generate(count=10, seed=42, max_time=24):
    rng = random.Random(seed)
    intervals = []
    for index in range(count):
        start = rng.randint(0, max_time - 2)
        end = rng.randint(start + 1, max_time)
        intervals.append({
            "id": f"L{index + 1}",
            "start": start,
            "end": end,
        })
    return intervals
