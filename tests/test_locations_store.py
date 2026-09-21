from algorithms import locations_store


def test_dataset_has_at_least_5000_locations():
    assert len(locations_store.get_all()) >= 5000


def test_all_locations_have_valid_coordinates():
    for location in locations_store.get_all():
        assert -90 <= location["latitude"] <= 90
        assert -180 <= location["longitude"] <= 180


def test_all_locations_have_unique_ids():
    ids = [location["id"] for location in locations_store.get_all()]
    assert len(ids) == len(set(ids))


def test_search_by_name_is_case_insensitive():
    results = locations_store.search(query="brasilia")
    assert any(item["name"] == "Brasilia" for item in results)


def test_load_test_sets_exist_and_are_subsets():
    for size in [10, 50, 100, 500, 1000]:
        subset = locations_store.load_test_set(size)
        assert subset is not None
        assert len(subset) == size
