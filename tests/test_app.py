import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client


def login(client):
    return client.post("/login", data={"username": "tester", "password": "x"}, follow_redirects=True)


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_protected_route_redirects_when_not_logged_in(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302


def test_login_grants_access_to_dashboard(client):
    login(client)
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/planejador",
        "/localidades",
        "/algoritmos",
        "/comparacao",
        "/benchmarks",
        "/huffman",
        "/teoria",
        "/contraexemplos",
        "/sobre",
    ],
)
def test_all_pages_load_after_login(client, path):
    login(client)
    response = client.get(path)
    assert response.status_code == 200


def test_api_locations_search(client):
    login(client)
    response = client.get("/api/locations?q=Brasilia")
    assert response.status_code == 200
    data = response.get_json()
    assert any(item["name"] == "Brasilia" for item in data)


def test_api_travel_demo_and_run(client):
    login(client)
    demo = client.get("/api/travel/demo").get_json()
    assert len(demo) == 10
    ids = [item["id"] for item in demo]
    result = client.post("/api/travel/run", json={"algorithm": "nearest_neighbor", "location_ids": ids})
    assert result.status_code == 200
    assert result.get_json()["total_distance_km"] > 0


def test_api_huffman_solve(client):
    login(client)
    response = client.post("/api/huffman/solve", json={"text": "teste"})
    assert response.status_code == 200
    assert response.get_json()["decoding_matches_original"] is True


def test_api_requires_login(client):
    response = client.get("/api/locations")
    assert response.status_code == 302
