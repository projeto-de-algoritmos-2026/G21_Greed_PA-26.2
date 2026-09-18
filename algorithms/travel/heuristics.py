import time

from .distance import route_distance

MAX_SIZE_CHEAPEST_INSERTION = 400
MAX_SIZE_ALL_PAIRS_SORT = 1200


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        self.parent[root_a] = root_b
        return True


def _finish(name, criterion, locations, order, matrix, steps, comparisons, start_time):
    total_distance = route_distance(order, matrix)
    elapsed = time.perf_counter() - start_time
    return {
        "algorithm": name,
        "criterion": criterion,
        "order": order,
        "route": [locations[index]["name"] for index in order],
        "total_distance_km": total_distance,
        "steps": steps,
        "metrics": {
            "elapsed_seconds": elapsed,
            "comparisons": comparisons,
            "cities": len(locations),
        },
    }


def nearest_neighbor(locations, matrix, start=0):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    visited = [False] * size
    order = [start]
    visited[start] = True
    steps = []

    current = start
    for _ in range(size - 1):
        best_index = -1
        best_distance = float("inf")
        for candidate in range(size):
            if visited[candidate]:
                continue
            comparisons += 1
            distance = matrix[current][candidate]
            if distance < best_distance:
                best_distance = distance
                best_index = candidate
        order.append(best_index)
        visited[best_index] = True
        steps.append({
            "from": locations[current]["name"],
            "to": locations[best_index]["name"],
            "distance_km": best_distance,
        })
        current = best_index

    return _finish(
        "Nearest Neighbor",
        "escolher sempre a localidade nao visitada mais proxima da atual",
        locations, order, matrix, steps, comparisons, start_time,
    )


def multi_start_nearest_neighbor(locations, matrix, max_starts=20):
    start_time = time.perf_counter()
    size = len(locations)
    candidate_starts = list(range(size)) if size <= max_starts else [
        round(i * (size - 1) / (max_starts - 1)) for i in range(max_starts)
    ]

    best_result = None
    all_results = []
    total_comparisons = 0
    for start in sorted(set(candidate_starts)):
        result = nearest_neighbor(locations, matrix, start=start)
        total_comparisons += result["metrics"]["comparisons"]
        all_results.append({
            "start": locations[start]["name"],
            "total_distance_km": result["total_distance_km"],
        })
        if best_result is None or result["total_distance_km"] < best_result["total_distance_km"]:
            best_result = result

    elapsed = time.perf_counter() - start_time
    best_result = dict(best_result)
    best_result["algorithm"] = "Multi-Start Nearest Neighbor"
    best_result["criterion"] = "executar Nearest Neighbor a partir de varios pontos de partida e manter a melhor rota"
    best_result["starts_tested"] = all_results
    best_result["metrics"] = {
        "elapsed_seconds": elapsed,
        "comparisons": total_comparisons,
        "cities": size,
        "starts_evaluated": len(all_results),
    }
    return best_result


def farthest_neighbor(locations, matrix, start=0):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    visited = [False] * size
    order = [start]
    visited[start] = True
    steps = []

    current = start
    for _ in range(size - 1):
        best_index = -1
        best_distance = -1.0
        for candidate in range(size):
            if visited[candidate]:
                continue
            comparisons += 1
            distance = matrix[current][candidate]
            if distance > best_distance:
                best_distance = distance
                best_index = candidate
        order.append(best_index)
        visited[best_index] = True
        steps.append({
            "from": locations[current]["name"],
            "to": locations[best_index]["name"],
            "distance_km": best_distance,
        })
        current = best_index

    return _finish(
        "Farthest Neighbor",
        "escolher sempre a localidade nao visitada mais distante da atual",
        locations, order, matrix, steps, comparisons, start_time,
    )


def _cheapest_position(route, node, matrix):
    best_position = 1
    best_extra = float("inf")
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        extra = matrix[a][node] + matrix[node][b] - matrix[a][b]
        if extra < best_extra:
            best_extra = extra
            best_position = i + 1
    return best_position, best_extra


def nearest_insertion(locations, matrix):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    if size < 2:
        return _finish("Nearest Insertion", "insercao pelo vizinho mais proximo da rota", locations, list(range(size)), matrix, [], 0, start_time)

    route = [0, 1, 0]
    unrouted = set(range(2, size))
    steps = []

    while unrouted:
        best_city = None
        best_distance = float("inf")
        for city in unrouted:
            for node in route[:-1]:
                comparisons += 1
                distance = matrix[city][node]
                if distance < best_distance:
                    best_distance = distance
                    best_city = city

        position, extra = _cheapest_position(route, best_city, matrix)
        route.insert(position, best_city)
        unrouted.remove(best_city)
        steps.append({"inserted": locations[best_city]["name"], "position": position, "added_km": extra})

    return _finish(
        "Nearest Insertion",
        "inserir a localidade mais proxima da rota atual na melhor posicao",
        locations, route, matrix, steps, comparisons, start_time,
    )


def farthest_insertion(locations, matrix):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    if size < 2:
        return _finish("Farthest Insertion", "insercao pela localidade mais distante da rota", locations, list(range(size)), matrix, [], 0, start_time)

    route = [0, 1, 0]
    unrouted = set(range(2, size))
    steps = []

    while unrouted:
        best_city = None
        best_distance = -1.0
        for city in unrouted:
            nearest_to_route = min(matrix[city][node] for node in route[:-1])
            comparisons += len(route) - 1
            if nearest_to_route > best_distance:
                best_distance = nearest_to_route
                best_city = city

        position, extra = _cheapest_position(route, best_city, matrix)
        route.insert(position, best_city)
        unrouted.remove(best_city)
        steps.append({"inserted": locations[best_city]["name"], "position": position, "added_km": extra})

    return _finish(
        "Farthest Insertion",
        "inserir a localidade mais distante da rota atual na posicao de menor aumento de custo",
        locations, route, matrix, steps, comparisons, start_time,
    )


def cheapest_insertion(locations, matrix):
    start_time = time.perf_counter()
    size = len(locations)
    if size > MAX_SIZE_CHEAPEST_INSERTION:
        raise ValueError(
            f"Cheapest Insertion tem complexidade cubica; limite pratico de {MAX_SIZE_CHEAPEST_INSERTION} localidades nesta demonstracao"
        )

    comparisons = 0
    if size < 2:
        return _finish("Cheapest Insertion", "insercao de menor custo adicional", locations, list(range(size)), matrix, [], 0, start_time)

    route = [0, 1, 0]
    unrouted = set(range(2, size))
    steps = []

    while unrouted:
        best_city = None
        best_position = None
        best_extra = float("inf")
        for city in unrouted:
            for i in range(len(route) - 1):
                a, b = route[i], route[i + 1]
                comparisons += 1
                extra = matrix[a][city] + matrix[city][b] - matrix[a][b]
                if extra < best_extra:
                    best_extra = extra
                    best_position = i + 1
                    best_city = city

        route.insert(best_position, best_city)
        unrouted.remove(best_city)
        steps.append({"inserted": locations[best_city]["name"], "position": best_position, "added_km": best_extra})

    return _finish(
        "Cheapest Insertion",
        "inserir a cada passo a localidade e posicao que geram o menor aumento de custo na rota",
        locations, route, matrix, steps, comparisons, start_time,
    )


def greedy_edge_selection(locations, matrix):
    start_time = time.perf_counter()
    size = len(locations)
    if size > MAX_SIZE_ALL_PAIRS_SORT:
        raise ValueError(
            f"Greedy Edge Selection ordena todas as arestas O(n^2 log n); limite pratico de {MAX_SIZE_ALL_PAIRS_SORT} localidades"
        )

    edges = []
    for i in range(size):
        for j in range(i + 1, size):
            edges.append((matrix[i][j], i, j))
    edges.sort(key=lambda edge: edge[0])
    comparisons = len(edges)

    degree = [0] * size
    union_find = UnionFind(size)
    chosen_edges = []
    steps = []

    for distance, i, j in edges:
        if degree[i] >= 2 or degree[j] >= 2:
            continue
        if union_find.find(i) == union_find.find(j) and len(chosen_edges) < size - 1:
            continue
        if len(chosen_edges) == size:
            break
        union_find.union(i, j)
        degree[i] += 1
        degree[j] += 1
        chosen_edges.append((i, j))
        steps.append({"from": locations[i]["name"], "to": locations[j]["name"], "distance_km": distance})
        if len(chosen_edges) == size:
            break

    adjacency = {index: [] for index in range(size)}
    for i, j in chosen_edges:
        adjacency[i].append(j)
        adjacency[j].append(i)

    endpoints = [node for node, neighbors in adjacency.items() if len(neighbors) < 2]
    start_node = endpoints[0] if endpoints else 0

    order = [start_node]
    previous = None
    current = start_node
    while len(order) < size:
        neighbors = [node for node in adjacency[current] if node != previous]
        if not neighbors:
            remaining = [node for node in range(size) if node not in order]
            if not remaining:
                break
            neighbors = [remaining[0]]
        next_node = neighbors[0]
        order.append(next_node)
        previous = current
        current = next_node

    order.append(start_node)

    return _finish(
        "Greedy Edge Selection",
        "ordenar todas as arestas por distancia e adiciona-las evitando graus invalidos e ciclos prematuros",
        locations, order, matrix, steps, comparisons, start_time,
    )


def clarke_wright_savings(locations, matrix, depot=0):
    start_time = time.perf_counter()
    size = len(locations)
    if size > MAX_SIZE_ALL_PAIRS_SORT:
        raise ValueError(
            f"Clarke-Wright Savings depende de pares O(n^2); limite pratico de {MAX_SIZE_ALL_PAIRS_SORT} localidades"
        )

    customers = [index for index in range(size) if index != depot]
    routes = {customer: [depot, customer, depot] for customer in customers}
    route_of = {customer: customer for customer in customers}

    savings = []
    for i in range(len(customers)):
        for j in range(i + 1, len(customers)):
            a, b = customers[i], customers[j]
            saving = matrix[depot][a] + matrix[depot][b] - matrix[a][b]
            savings.append((saving, a, b))
    savings.sort(key=lambda item: item[0], reverse=True)
    comparisons = len(savings)

    steps = []
    for saving, a, b in savings:
        route_a_key = route_of.get(a)
        route_b_key = route_of.get(b)
        if route_a_key is None or route_b_key is None or route_a_key == route_b_key:
            continue

        route_a = routes[route_a_key]
        route_b = routes[route_b_key]

        a_is_end = route_a[-2] == a
        b_is_start = route_b[1] == b
        if not (a_is_end and b_is_start):
            continue

        merged = route_a[:-1] + route_b[1:]
        for node in merged[1:-1]:
            route_of[node] = route_a_key
        routes[route_a_key] = merged
        del routes[route_b_key]
        steps.append({"merge": f"{locations[a]['name']} - {locations[b]['name']}", "saving_km": saving})

    final_route = next(iter(routes.values()))
    missing = [node for node in range(size) if node not in final_route]
    for node in missing:
        final_route.insert(-1, node)

    return _finish(
        "Clarke-Wright Savings",
        "unir rotas priorizando o maior ganho de economia savings(i,j) = d(deposito,i) + d(deposito,j) - d(i,j)",
        locations, final_route, matrix, steps, comparisons, start_time,
    )


def greedy_by_region(locations, matrix):
    start_time = time.perf_counter()
    comparisons = 0
    regions = {}
    for index, location in enumerate(locations):
        regions.setdefault(location.get("region", "Sem regiao"), []).append(index)

    region_names = list(regions.keys())
    region_centroid = {}
    for name, indices in regions.items():
        avg_lat = sum(locations[i]["latitude"] for i in indices) / len(indices)
        avg_lon = sum(locations[i]["longitude"] for i in indices) / len(indices)
        region_centroid[name] = (avg_lat, avg_lon)

    visited_regions = set()
    current_region = region_names[0]
    region_order = [current_region]
    visited_regions.add(current_region)

    from .distance import haversine

    while len(region_order) < len(region_names):
        current_lat, current_lon = region_centroid[current_region]
        best_region = None
        best_distance = float("inf")
        for name in region_names:
            if name in visited_regions:
                continue
            comparisons += 1
            lat, lon = region_centroid[name]
            distance = haversine(current_lat, current_lon, lat, lon)
            if distance < best_distance:
                best_distance = distance
                best_region = name
        region_order.append(best_region)
        visited_regions.add(best_region)
        current_region = best_region

    order = []
    for region_name in region_order:
        indices = regions[region_name]
        visited = {indices[0]}
        local_order = [indices[0]]
        current = indices[0]
        remaining = set(indices[1:])
        while remaining:
            best_index = min(remaining, key=lambda candidate: matrix[current][candidate])
            comparisons += len(remaining)
            local_order.append(best_index)
            remaining.discard(best_index)
            current = best_index
        order.extend(local_order)

    steps = [{"region": name} for name in region_order]

    return _finish(
        "Estrategia Greedy por Regiao",
        "agrupar localidades por regiao e visitar a regiao mais proxima ainda nao visitada, com Nearest Neighbor dentro de cada regiao",
        locations, order, matrix, steps, comparisons, start_time,
    )


def greedy_by_cluster(locations, matrix, num_clusters=None):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    if num_clusters is None:
        num_clusters = max(2, min(8, size // 10 or 1))

    seed_step = max(1, size // num_clusters)
    seeds = [i * seed_step for i in range(num_clusters) if i * seed_step < size]

    from .distance import haversine

    assignment = []
    for index, location in enumerate(locations):
        best_seed = 0
        best_distance = float("inf")
        for seed_index, seed in enumerate(seeds):
            comparisons += 1
            distance = haversine(location["latitude"], location["longitude"], locations[seed]["latitude"], locations[seed]["longitude"])
            if distance < best_distance:
                best_distance = distance
                best_seed = seed_index
        assignment.append(best_seed)

    clusters = {i: [] for i in range(len(seeds))}
    for index, cluster_id in enumerate(assignment):
        clusters[cluster_id].append(index)

    cluster_centroid = {}
    for cluster_id, indices in clusters.items():
        if not indices:
            continue
        avg_lat = sum(locations[i]["latitude"] for i in indices) / len(indices)
        avg_lon = sum(locations[i]["longitude"] for i in indices) / len(indices)
        cluster_centroid[cluster_id] = (avg_lat, avg_lon)

    remaining_clusters = set(cluster_centroid.keys())
    current_cluster = next(iter(remaining_clusters))
    cluster_order = [current_cluster]
    remaining_clusters.discard(current_cluster)

    while remaining_clusters:
        current_lat, current_lon = cluster_centroid[current_cluster]
        best_cluster = min(
            remaining_clusters,
            key=lambda cid: haversine(current_lat, current_lon, cluster_centroid[cid][0], cluster_centroid[cid][1]),
        )
        comparisons += len(remaining_clusters)
        cluster_order.append(best_cluster)
        remaining_clusters.discard(best_cluster)
        current_cluster = best_cluster

    order = []
    for cluster_id in cluster_order:
        indices = clusters[cluster_id]
        if not indices:
            continue
        current = indices[0]
        local_order = [current]
        remaining = set(indices[1:])
        while remaining:
            best_index = min(remaining, key=lambda candidate: matrix[current][candidate])
            comparisons += len(remaining)
            local_order.append(best_index)
            remaining.discard(best_index)
            current = best_index
        order.extend(local_order)

    steps = [{"cluster": cluster_id, "size": len(clusters[cluster_id])} for cluster_id in cluster_order]

    return _finish(
        "Estrategia Greedy por Cluster",
        "agrupar localidades em clusters proximos e construir a rota entre os centroides dos clusters",
        locations, order, matrix, steps, comparisons, start_time,
    )


def greedy_benefit_distance(locations, matrix, start=0):
    start_time = time.perf_counter()
    comparisons = 0
    size = len(locations)
    visited = [False] * size
    order = [start]
    visited[start] = True
    steps = []

    current = start
    for _ in range(size - 1):
        best_index = -1
        best_score = float("-inf")
        for candidate in range(size):
            if visited[candidate]:
                continue
            comparisons += 1
            distance = matrix[current][candidate]
            benefit = locations[candidate].get("score", 1)
            score = benefit / distance if distance > 0 else float("inf")
            if score > best_score:
                best_score = score
                best_index = candidate
        order.append(best_index)
        visited[best_index] = True
        steps.append({
            "from": locations[current]["name"],
            "to": locations[best_index]["name"],
            "score": best_score,
        })
        current = best_index

    return _finish(
        "Greedy por Beneficio/Distancia",
        "escolher a proxima localidade que maximiza o criterio beneficio/distancia a partir da localidade atual",
        locations, order, matrix, steps, comparisons, start_time,
    )


ALGORITHMS = {
    "nearest_neighbor": nearest_neighbor,
    "multi_start_nearest_neighbor": multi_start_nearest_neighbor,
    "farthest_neighbor": farthest_neighbor,
    "cheapest_insertion": cheapest_insertion,
    "nearest_insertion": nearest_insertion,
    "farthest_insertion": farthest_insertion,
    "greedy_edge_selection": greedy_edge_selection,
    "clarke_wright_savings": clarke_wright_savings,
    "greedy_by_region": greedy_by_region,
    "greedy_by_cluster": greedy_by_cluster,
    "greedy_benefit_distance": greedy_benefit_distance,
}


def run_algorithm(key, locations, matrix):
    if key not in ALGORITHMS:
        raise ValueError(f"Algoritmo desconhecido: {key}")
    return ALGORITHMS[key](locations, matrix)
