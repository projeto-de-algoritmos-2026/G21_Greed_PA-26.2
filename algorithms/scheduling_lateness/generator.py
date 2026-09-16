import random


def generate(count=8, seed=42, max_processing=10, max_deadline=60):
    rng = random.Random(seed)
    tasks = []
    for index in range(count):
        processing_time = rng.randint(1, max_processing)
        deadline = rng.randint(processing_time, max_deadline)
        tasks.append({
            "id": f"T{index + 1}",
            "processing_time": processing_time,
            "deadline": deadline,
        })
    rng.shuffle(tasks)
    return tasks
