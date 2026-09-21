import json

from algorithms import locations_store


def setup_isolated_store(tmp_path, monkeypatch):
    seed_file = tmp_path / "locations.json"
    seed_data = [
        {"id": 1, "name": "Cidade A", "country": "Brasil", "region": "DF", "latitude": -15.0, "longitude": -47.0, "capital": True, "score": 80},
        {"id": 2, "name": "Cidade B", "country": "Brasil", "region": "SP", "latitude": -23.0, "longitude": -46.0, "capital": False, "score": 60},
    ]
    seed_file.write_text(json.dumps(seed_data), encoding="utf-8")
    monkeypatch.setattr(locations_store, "MAIN_FILE", str(seed_file))
    monkeypatch.setattr(locations_store, "_cache", None)
    return seed_file


def test_create_assigns_incremental_id(tmp_path, monkeypatch):
    setup_isolated_store(tmp_path, monkeypatch)
    created = locations_store.create({
        "name": "Cidade C", "country": "Brasil", "region": "RJ",
        "latitude": -22.0, "longitude": -43.0, "capital": False, "score": 50,
    })
    assert created["id"] == 3
    assert len(locations_store.get_all()) == 3


def test_update_changes_fields_and_keeps_id(tmp_path, monkeypatch):
    setup_isolated_store(tmp_path, monkeypatch)
    updated = locations_store.update(1, {"name": "Cidade A Renomeada"})
    assert updated["id"] == 1
    assert updated["name"] == "Cidade A Renomeada"


def test_update_missing_id_returns_none(tmp_path, monkeypatch):
    setup_isolated_store(tmp_path, monkeypatch)
    assert locations_store.update(999, {"name": "X"}) is None


def test_delete_removes_location(tmp_path, monkeypatch):
    setup_isolated_store(tmp_path, monkeypatch)
    assert locations_store.delete(2) is True
    assert len(locations_store.get_all()) == 1


def test_delete_missing_id_returns_false(tmp_path, monkeypatch):
    setup_isolated_store(tmp_path, monkeypatch)
    assert locations_store.delete(999) is False


def test_persisted_changes_survive_cache_reload(tmp_path, monkeypatch):
    seed_file = setup_isolated_store(tmp_path, monkeypatch)
    locations_store.create({
        "name": "Cidade D", "country": "Brasil", "region": "MG",
        "latitude": -19.0, "longitude": -43.0, "capital": False, "score": 40,
    })
    monkeypatch.setattr(locations_store, "_cache", None)
    reloaded = json.loads(seed_file.read_text(encoding="utf-8"))
    assert len(reloaded) == 3
