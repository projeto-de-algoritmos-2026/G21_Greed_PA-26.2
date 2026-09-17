import json
import os
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MAIN_FILE = os.path.join(DATA_DIR, "locations.json")

_lock = threading.Lock()
_cache = None


def _load():
    global _cache
    if _cache is None:
        with open(MAIN_FILE, "r", encoding="utf-8") as handle:
            _cache = json.load(handle)
    return _cache


def get_all():
    with _lock:
        return list(_load())


def get_by_id(location_id):
    for location in get_all():
        if location["id"] == location_id:
            return location
    return None


def get_by_ids(ids):
    id_set = set(ids)
    return [location for location in get_all() if location["id"] in id_set]


def search(query="", country=None, region=None, limit=200):
    query_lower = query.strip().lower()
    results = []
    for location in get_all():
        if query_lower and query_lower not in location["name"].lower():
            continue
        if country and location["country"] != country:
            continue
        if region and location["region"] != region:
            continue
        results.append(location)
        if len(results) >= limit:
            break
    return results


def list_countries():
    return sorted({location["country"] for location in get_all()})


def list_regions(country=None):
    locations = get_all()
    if country:
        locations = [item for item in locations if item["country"] == country]
    return sorted({location["region"] for location in locations})


def load_test_set(size):
    path = os.path.join(DATA_DIR, f"test_{size}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def create(location):
    with _lock:
        locations = _load()
        new_id = max((item["id"] for item in locations), default=0) + 1
        location = dict(location)
        location["id"] = new_id
        locations.append(location)
        _persist(locations)
        return location


def update(location_id, changes):
    with _lock:
        locations = _load()
        for location in locations:
            if location["id"] == location_id:
                location.update(changes)
                location["id"] = location_id
                _persist(locations)
                return location
        return None


def delete(location_id):
    with _lock:
        locations = _load()
        remaining = [item for item in locations if item["id"] != location_id]
        if len(remaining) == len(locations):
            return False
        _persist(remaining)
        return True


def _persist(locations):
    global _cache
    _cache = locations
    with open(MAIN_FILE, "w", encoding="utf-8") as handle:
        json.dump(locations, handle, ensure_ascii=False, indent=2)
