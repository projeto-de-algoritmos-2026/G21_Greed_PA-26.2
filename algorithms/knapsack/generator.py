import random


def generate(count=6, seed=42, max_weight=50, max_value=500):
    rng = random.Random(seed)
    items = []
    for index in range(count):
        weight = rng.randint(1, max_weight)
        value = rng.randint(1, max_value)
        items.append({
            "name": f"Item {chr(65 + index % 26)}{index // 26 or ''}",
            "weight": weight,
            "value": value,
        })
    return items
