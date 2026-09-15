import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from core_cities import BRAZIL_CAPITALS, BRAZIL_OTHER_CITIES, INTERNATIONAL_CITIES

SEED = 42
TARGET_TOTAL = 5200
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

DISTRICT_LABELS = [
    "Centro", "Zona Norte", "Zona Sul", "Zona Leste", "Zona Oeste", "Setor Industrial",
    "Bairro Alto", "Bairro Novo", "Distrito Comercial", "Distrito Historico", "Vila Verde",
    "Jardim das Flores", "Parque das Nacoes", "Setor Universitario", "Porto", "Estacao",
    "Mirante", "Colina", "Vale", "Litoral", "Planalto", "Bosque", "Praia", "Serra",
]


def build_core_locations():
    locations = []
    for name, region, lat, lon in BRAZIL_CAPITALS:
        locations.append({
            "name": name,
            "country": "Brasil",
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "capital": True,
        })
    for name, region, lat, lon in BRAZIL_OTHER_CITIES:
        locations.append({
            "name": name,
            "country": "Brasil",
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "capital": False,
        })
    for name, country, lat, lon in INTERNATIONAL_CITIES:
        locations.append({
            "name": name,
            "country": country,
            "region": country,
            "latitude": lat,
            "longitude": lon,
            "capital": True,
        })
    return locations


def generate_satellites(core_locations, rng, target_total):
    satellites = []
    needed = max(0, target_total - len(core_locations))
    core_count = len(core_locations)

    for index in range(needed):
        base = core_locations[index % core_count]
        label = DISTRICT_LABELS[(index // core_count) % len(DISTRICT_LABELS)]
        suffix = (index // core_count) + 1
        district_name = f"{base['name']} - {label} {suffix}" if suffix > 1 else f"{base['name']} - {label}"

        lat_jitter = rng.uniform(-0.18, 0.18)
        lon_jitter = rng.uniform(-0.18, 0.18)

        satellites.append({
            "name": district_name,
            "country": base["country"],
            "region": base["region"],
            "latitude": round(base["latitude"] + lat_jitter, 6),
            "longitude": round(base["longitude"] + lon_jitter, 6),
            "capital": False,
        })

    return satellites


def assign_ids_and_scores(locations, rng):
    for index, location in enumerate(locations):
        location["id"] = index + 1
        location["score"] = rng.randint(10, 100) if not location["capital"] else rng.randint(60, 100)
    return locations


def main():
    rng = random.Random(SEED)
    core_locations = build_core_locations()
    satellites = generate_satellites(core_locations, rng, TARGET_TOTAL)
    all_locations = core_locations + satellites
    all_locations = assign_ids_and_scores(all_locations, rng)

    os.makedirs(DATA_DIR, exist_ok=True)
    locations_path = os.path.join(DATA_DIR, "locations.json")
    with open(locations_path, "w", encoding="utf-8") as handle:
        json.dump(all_locations, handle, ensure_ascii=False, indent=2)

    shuffled = all_locations[:]
    random.Random(SEED).shuffle(shuffled)

    for size in [10, 50, 100, 500, 1000, 2500, 5000]:
        subset = shuffled[:min(size, len(shuffled))]
        subset_path = os.path.join(DATA_DIR, f"test_{size}.json")
        with open(subset_path, "w", encoding="utf-8") as handle:
            json.dump(subset, handle, ensure_ascii=False, indent=2)

    print(f"Total de localidades geradas: {len(all_locations)}")
    print(f"Arquivo principal: {locations_path}")


if __name__ == "__main__":
    main()
