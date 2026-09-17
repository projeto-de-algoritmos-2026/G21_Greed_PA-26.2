import time


def solve(distance, tank_capacity, consumption, stations):
    start_time = time.perf_counter()
    comparisons = 0

    autonomy = tank_capacity * consumption
    ordered_stations = sorted(stations, key=lambda station: station["position"])

    for station in ordered_stations:
        if station["position"] > distance:
            raise ValueError("Posto alem da distancia total da viagem")

    current_position = 0.0
    remaining_range = autonomy
    stops = []
    used_index = 0
    total_fuel_used = 0.0
    feasible = True
    reason = None

    while current_position + remaining_range < distance:
        farthest = None
        farthest_index = None
        for index in range(used_index, len(ordered_stations)):
            station = ordered_stations[index]
            comparisons += 1
            if station["position"] <= current_position:
                continue
            if station["position"] > current_position + remaining_range:
                break
            farthest = station
            farthest_index = index

        if farthest is None:
            feasible = False
            reason = "Nao existe posto alcancavel dentro da autonomia do veiculo"
            break

        traveled = farthest["position"] - current_position
        remaining_range -= traveled
        refill = autonomy - remaining_range
        total_fuel_used += refill / consumption

        stops.append({
            "station": farthest["name"],
            "position": farthest["position"],
            "fuel_added_liters": refill / consumption,
            "range_after_refuel_km": autonomy,
        })

        current_position = farthest["position"]
        remaining_range = autonomy
        used_index = farthest_index + 1

    if feasible:
        total_fuel_used += (distance - current_position) / consumption

    elapsed = time.perf_counter() - start_time

    return {
        "distance": distance,
        "tank_capacity": tank_capacity,
        "consumption": consumption,
        "autonomy": autonomy,
        "stations": ordered_stations,
        "stops": stops,
        "stops_count": len(stops),
        "feasible": feasible,
        "reason": reason,
        "total_fuel_liters": total_fuel_used if feasible else None,
        "criterion": "avancar o maximo possivel e abastecer sempre no posto mais distante ainda alcancavel",
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
        },
    }
