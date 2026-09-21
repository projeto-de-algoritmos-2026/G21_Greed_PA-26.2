import math

from algorithms.travel.distance import haversine, distance_between, build_matrix, route_distance


def test_haversine_same_point_is_zero():
    assert haversine(-15.7939, -47.8828, -15.7939, -47.8828) == 0.0


def test_haversine_known_distance_brasilia_sao_paulo():
    distance = haversine(-15.7939, -47.8828, -23.5505, -46.6333)
    assert 850 < distance < 900


def test_distance_between_locations():
    a = {"latitude": -15.7939, "longitude": -47.8828}
    b = {"latitude": -23.5505, "longitude": -46.6333}
    assert math.isclose(distance_between(a, b), haversine(-15.7939, -47.8828, -23.5505, -46.6333))


def test_build_matrix_is_symmetric():
    locations = [
        {"latitude": -15.7939, "longitude": -47.8828},
        {"latitude": -23.5505, "longitude": -46.6333},
        {"latitude": -22.9068, "longitude": -43.1729},
    ]
    matrix = build_matrix(locations)
    for i in range(len(locations)):
        for j in range(len(locations)):
            assert math.isclose(matrix[i][j], matrix[j][i])
    for i in range(len(locations)):
        assert matrix[i][i] == 0.0


def test_route_distance_sums_consecutive_edges():
    locations = [
        {"latitude": -15.7939, "longitude": -47.8828},
        {"latitude": -23.5505, "longitude": -46.6333},
        {"latitude": -22.9068, "longitude": -43.1729},
    ]
    matrix = build_matrix(locations)
    total = route_distance([0, 1, 2], matrix)
    assert math.isclose(total, matrix[0][1] + matrix[1][2])
