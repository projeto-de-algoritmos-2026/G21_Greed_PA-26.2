from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_KM = 6371.0


def haversine(lat1, lon1, lat2, lon2):
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def distance_between(location_a, location_b):
    return haversine(location_a["latitude"], location_a["longitude"], location_b["latitude"], location_b["longitude"])


def build_matrix(locations):
    size = len(locations)
    matrix = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            value = distance_between(locations[i], locations[j])
            matrix[i][j] = value
            matrix[j][i] = value
    return matrix


def route_distance(order, matrix):
    total = 0.0
    for i in range(len(order) - 1):
        total += matrix[order[i]][order[i + 1]]
    return total
