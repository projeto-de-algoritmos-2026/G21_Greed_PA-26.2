from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from algorithms import locations_store, benchmark
from algorithms.travel.distance import build_matrix, distance_between, route_distance
from algorithms.travel.heuristics import ALGORITHMS as TRAVEL_ALGORITHMS, run_algorithm as run_travel_algorithm
from algorithms.interval_scheduling.solver import solve as solve_interval_scheduling
from algorithms.interval_scheduling.generator import generate as generate_interval_scheduling
from algorithms.interval_partitioning.solver import solve as solve_interval_partitioning
from algorithms.interval_partitioning.generator import generate as generate_interval_partitioning
from algorithms.scheduling_lateness.solver import solve as solve_lateness
from algorithms.scheduling_lateness.generator import generate as generate_lateness
from algorithms.knapsack.solver import solve as solve_knapsack
from algorithms.knapsack.generator import generate as generate_knapsack
from algorithms.trocador.solver import solve as solve_trocador
from algorithms.trocador.cases import CASES as TROCADOR_CASES
from algorithms.caminhoneiro.solver import solve as solve_caminhoneiro
from algorithms.caminhoneiro.generator import generate as generate_caminhoneiro
from algorithms.huffman.solver import solve as solve_huffman

app = Flask(__name__)
app.secret_key = "greedy-travel-lab-academic-demo-key"

DEMO_TRIP_NAMES = [
    "Brasilia", "Goiania", "Belo Horizonte", "Rio de Janeiro", "Sao Paulo",
    "Curitiba", "Porto Alegre", "Salvador", "Recife", "Fortaleza",
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        session["logged_in"] = True
        session["username"] = username or "Convidado"
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    all_locations = locations_store.get_all()
    countries = locations_store.list_countries()
    stats = {
        "total_locations": len(all_locations),
        "total_countries": len(countries),
        "total_algorithms": len(TRAVEL_ALGORITHMS) + 7,
    }
    return render_template("dashboard.html", stats=stats, username=session.get("username"))


@app.route("/planejador")
@login_required
def planejador():
    return render_template("planejador.html", demo_names=DEMO_TRIP_NAMES, algorithms=list(TRAVEL_ALGORITHMS.keys()))


@app.route("/localidades")
@login_required
def localidades():
    return render_template("localidades.html")


@app.route("/algoritmos")
@login_required
def algoritmos():
    return render_template("algoritmos.html")


@app.route("/comparacao")
@login_required
def comparacao():
    return render_template("comparacao.html", algorithms=list(TRAVEL_ALGORITHMS.keys()))


@app.route("/benchmarks")
@login_required
def benchmarks():
    return render_template("benchmarks.html", algorithms=list(TRAVEL_ALGORITHMS.keys()))


@app.route("/huffman")
@login_required
def huffman_page():
    return render_template("huffman.html")


@app.route("/teoria")
@login_required
def teoria():
    return render_template("teoria.html")


@app.route("/contraexemplos")
@login_required
def contraexemplos():
    return render_template("contraexemplos.html", trocador_cases=TROCADOR_CASES)


@app.route("/sobre")
@login_required
def sobre():
    return render_template("sobre.html")


@app.route("/api/locations")
@login_required
def api_locations():
    query = request.args.get("q", "")
    country = request.args.get("country") or None
    region = request.args.get("region") or None
    limit = int(request.args.get("limit", 200))
    results = locations_store.search(query=query, country=country, region=region, limit=limit)
    return jsonify(results)


@app.route("/api/locations/meta")
@login_required
def api_locations_meta():
    return jsonify({
        "countries": locations_store.list_countries(),
        "regions": locations_store.list_regions(request.args.get("country")),
        "total": len(locations_store.get_all()),
    })


@app.route("/api/locations", methods=["POST"])
@login_required
def api_locations_create():
    payload = request.get_json(force=True)
    required = ["name", "country", "region", "latitude", "longitude"]
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify({"error": f"Campos obrigatorios ausentes: {', '.join(missing)}"}), 400
    location = locations_store.create({
        "name": payload["name"],
        "country": payload["country"],
        "region": payload["region"],
        "latitude": float(payload["latitude"]),
        "longitude": float(payload["longitude"]),
        "capital": bool(payload.get("capital", False)),
        "score": int(payload.get("score", 50)),
    })
    return jsonify(location), 201


@app.route("/api/locations/<int:location_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def api_location_detail(location_id):
    if request.method == "GET":
        location = locations_store.get_by_id(location_id)
        if location is None:
            return jsonify({"error": "Localidade nao encontrada"}), 404
        return jsonify(location)

    if request.method == "PUT":
        payload = request.get_json(force=True)
        changes = {}
        for field in ["name", "country", "region", "capital", "score"]:
            if field in payload:
                changes[field] = payload[field]
        for field in ["latitude", "longitude"]:
            if field in payload:
                changes[field] = float(payload[field])
        location = locations_store.update(location_id, changes)
        if location is None:
            return jsonify({"error": "Localidade nao encontrada"}), 404
        return jsonify(location)

    deleted = locations_store.delete(location_id)
    if not deleted:
        return jsonify({"error": "Localidade nao encontrada"}), 404
    return jsonify({"deleted": True})


@app.route("/api/distance", methods=["POST"])
@login_required
def api_distance():
    payload = request.get_json(force=True)
    origin = locations_store.get_by_id(int(payload["from_id"]))
    destination = locations_store.get_by_id(int(payload["to_id"]))
    if origin is None or destination is None:
        return jsonify({"error": "Localidade nao encontrada"}), 404
    distance_km = distance_between(origin, destination)
    return jsonify({"from": origin, "to": destination, "distance_km": distance_km})


@app.route("/api/distance/matrix", methods=["POST"])
@login_required
def api_distance_matrix():
    payload = request.get_json(force=True)
    ids = [int(value) for value in payload["ids"]]
    locations = locations_store.get_by_ids(ids)
    ordered = sorted(locations, key=lambda item: ids.index(item["id"]))
    matrix = build_matrix(ordered)
    return jsonify({"locations": ordered, "matrix": matrix})


@app.route("/api/travel/demo")
@login_required
def api_travel_demo():
    demo_locations = []
    for name in DEMO_TRIP_NAMES:
        matches = locations_store.search(query=name, limit=5)
        exact = next((item for item in matches if item["name"] == name and item["country"] == "Brasil"), None)
        if exact:
            demo_locations.append(exact)
    return jsonify(demo_locations)


@app.route("/api/travel/run", methods=["POST"])
@login_required
def api_travel_run():
    payload = request.get_json(force=True)
    algorithm_key = payload["algorithm"]
    ids = [int(value) for value in payload["location_ids"]]
    locations = locations_store.get_by_ids(ids)
    ordered = sorted(locations, key=lambda item: ids.index(item["id"]))
    if len(ordered) < 2:
        return jsonify({"error": "Selecione pelo menos duas localidades"}), 400
    matrix = build_matrix(ordered)
    try:
        result = run_travel_algorithm(algorithm_key, ordered, matrix)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@app.route("/api/travel/compare", methods=["POST"])
@login_required
def api_travel_compare():
    payload = request.get_json(force=True)
    algorithm_keys = payload["algorithms"]
    ids = [int(value) for value in payload["location_ids"]]
    locations = locations_store.get_by_ids(ids)
    ordered = sorted(locations, key=lambda item: ids.index(item["id"]))
    if len(ordered) < 2:
        return jsonify({"error": "Selecione pelo menos duas localidades"}), 400
    matrix = build_matrix(ordered)

    results = []
    for key in algorithm_keys:
        try:
            outcome = run_travel_algorithm(key, ordered, matrix)
            results.append({
                "algorithm": outcome["algorithm"],
                "key": key,
                "total_distance_km": outcome["total_distance_km"],
                "elapsed_seconds": outcome["metrics"]["elapsed_seconds"],
                "comparisons": outcome["metrics"]["comparisons"],
                "route": outcome["route"],
                "order": outcome["order"],
                "success": True,
            })
        except ValueError as error:
            results.append({"algorithm": key, "key": key, "success": False, "reason": str(error)})

    return jsonify({"locations": ordered, "results": results})


@app.route("/api/interval-scheduling/generate")
@login_required
def api_interval_scheduling_generate():
    count = int(request.args.get("count", 10))
    seed = int(request.args.get("seed", 42))
    return jsonify(generate_interval_scheduling(count=count, seed=seed))


@app.route("/api/interval-scheduling/solve", methods=["POST"])
@login_required
def api_interval_scheduling_solve():
    payload = request.get_json(force=True)
    return jsonify(solve_interval_scheduling(payload["intervals"]))


@app.route("/api/interval-partitioning/generate")
@login_required
def api_interval_partitioning_generate():
    count = int(request.args.get("count", 10))
    seed = int(request.args.get("seed", 42))
    return jsonify(generate_interval_partitioning(count=count, seed=seed))


@app.route("/api/interval-partitioning/solve", methods=["POST"])
@login_required
def api_interval_partitioning_solve():
    payload = request.get_json(force=True)
    return jsonify(solve_interval_partitioning(payload["intervals"]))


@app.route("/api/lateness/generate")
@login_required
def api_lateness_generate():
    count = int(request.args.get("count", 8))
    seed = int(request.args.get("seed", 42))
    return jsonify(generate_lateness(count=count, seed=seed))


@app.route("/api/lateness/solve", methods=["POST"])
@login_required
def api_lateness_solve():
    payload = request.get_json(force=True)
    return jsonify(solve_lateness(payload["tasks"]))


@app.route("/api/knapsack/generate")
@login_required
def api_knapsack_generate():
    count = int(request.args.get("count", 6))
    seed = int(request.args.get("seed", 42))
    return jsonify(generate_knapsack(count=count, seed=seed))


@app.route("/api/knapsack/solve", methods=["POST"])
@login_required
def api_knapsack_solve():
    payload = request.get_json(force=True)
    return jsonify(solve_knapsack(payload["items"], float(payload["capacity"])))


@app.route("/api/trocador/solve", methods=["POST"])
@login_required
def api_trocador_solve():
    payload = request.get_json(force=True)
    amount = int(payload["amount"])
    denominations = [int(value) for value in payload["denominations"]]
    return jsonify(solve_trocador(amount, denominations))


@app.route("/api/trocador/cases")
@login_required
def api_trocador_cases():
    return jsonify(TROCADOR_CASES)


@app.route("/api/caminhoneiro/generate")
@login_required
def api_caminhoneiro_generate():
    distance = int(request.args.get("distance", 1000))
    seed = int(request.args.get("seed", 42))
    stations = generate_caminhoneiro(distance=distance, seed=seed)
    return jsonify({"distance": distance, "stations": stations})


@app.route("/api/caminhoneiro/solve", methods=["POST"])
@login_required
def api_caminhoneiro_solve():
    payload = request.get_json(force=True)
    try:
        result = solve_caminhoneiro(
            distance=float(payload["distance"]),
            tank_capacity=float(payload["tank_capacity"]),
            consumption=float(payload["consumption"]),
            stations=payload["stations"],
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@app.route("/api/huffman/solve", methods=["POST"])
@login_required
def api_huffman_solve():
    payload = request.get_json(force=True)
    try:
        result = solve_huffman(payload["text"])
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@app.route("/api/benchmark/travel", methods=["POST"])
@login_required
def api_benchmark_travel():
    payload = request.get_json(force=True)
    algorithm_keys = payload.get("algorithms") or list(TRAVEL_ALGORITHMS.keys())
    sizes = payload.get("sizes")
    results = benchmark.run_travel_benchmark(algorithm_keys, sizes)
    return jsonify(results)


@app.route("/api/benchmark/classic", methods=["POST"])
@login_required
def api_benchmark_classic():
    payload = request.get_json(force=True)
    kind = payload["kind"]
    sizes = payload.get("sizes")
    try:
        results = benchmark.run_classic_benchmark(kind, sizes)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
