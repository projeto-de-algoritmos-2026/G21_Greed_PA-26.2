import random


def generate(distance=1000, seed=42, station_count=12):
    rng = random.Random(seed)
    count = max(1, min(station_count, distance - 2))
    segment_size = distance / (count + 1)
    positions = []
    for index in range(count):
        segment_start = segment_size * index + segment_size * 0.1
        segment_end = segment_size * (index + 1) - segment_size * 0.1
        if segment_end <= segment_start:
            position = segment_size * (index + 1)
        else:
            position = rng.uniform(segment_start, segment_end)
        positions.append(max(1, min(distance - 1, round(position))))

    positions = sorted(set(positions))
    stations = [
        {"name": f"Posto {index + 1}", "position": position}
        for index, position in enumerate(positions)
    ]
    return stations
