const ALGORITHM_LABELS = {
  nearest_neighbor: "Nearest Neighbor",
  multi_start_nearest_neighbor: "Multi-Start Nearest Neighbor",
  farthest_neighbor: "Farthest Neighbor",
  cheapest_insertion: "Cheapest Insertion",
  nearest_insertion: "Nearest Insertion",
  farthest_insertion: "Farthest Insertion",
  greedy_edge_selection: "Greedy Edge Selection",
  clarke_wright_savings: "Clarke-Wright Savings",
  greedy_by_region: "Greedy por Regiao",
  greedy_by_cluster: "Greedy por Cluster",
  greedy_benefit_distance: "Greedy por Beneficio/Distancia",
};

const TRAVEL_SIZES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000];
const CLASSIC_SIZES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000];
const CHART_COLORS = ["#2563eb", "#0ea5a3", "#d97706", "#9333ea", "#e0473e", "#16a34a", "#64748b", "#db2777", "#0369a1", "#65a30d", "#ea580c"];

let travelTimeChart = null;
let travelDistanceChart = null;
let classicTimeChart = null;

document.querySelectorAll(".tab-btn").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((panel) => (panel.style.display = "none"));
    button.classList.add("active");
    document.getElementById(`panel-${button.getAttribute("data-tab")}`).style.display = "block";
  });
});

function renderTravelChecklists() {
  document.getElementById("travelAlgorithmChecklist").innerHTML = AVAILABLE_TRAVEL_ALGORITHMS.map(
    (key, index) => `<label class="checkbox-item"><input type="checkbox" value="${key}" ${index < 4 ? "checked" : ""}> ${ALGORITHM_LABELS[key] || key}</label>`
  ).join("");

  document.getElementById("travelSizesChecklist").innerHTML = TRAVEL_SIZES.map(
    (size) => `<label class="checkbox-item"><input type="checkbox" value="${size}" ${size <= 500 ? "checked" : ""}> ${size}</label>`
  ).join("");

  document.getElementById("classicSizesChecklist").innerHTML = CLASSIC_SIZES.map(
    (size) => `<label class="checkbox-item"><input type="checkbox" value="${size}" ${size <= 1000 ? "checked" : ""}> ${size}</label>`
  ).join("");
}

async function runTravelBenchmark() {
  const algorithms = Array.from(document.querySelectorAll("#travelAlgorithmChecklist input:checked")).map((input) => input.value);
  const sizes = Array.from(document.querySelectorAll("#travelSizesChecklist input:checked")).map((input) => parseInt(input.value, 10));
  if (algorithms.length === 0 || sizes.length === 0) {
    alert("Selecione ao menos um algoritmo e um tamanho.");
    return;
  }

  const button = document.getElementById("runTravelBenchBtn");
  button.disabled = true;
  button.textContent = "Executando benchmark...";

  try {
    const results = await apiPost("/api/benchmark/travel", { algorithms, sizes });
    recordExecution(results.length);
    renderTravelResults(results, algorithms);
  } finally {
    button.disabled = false;
    button.textContent = "📈 Executar benchmark";
  }
}

function renderTravelResults(results, algorithms) {
  document.getElementById("travelBenchResult").style.display = "block";

  const successResults = results.filter((item) => item.success);
  const datasetsTime = algorithms.map((key, index) => ({
    label: ALGORITHM_LABELS[key] || key,
    data: successResults.filter((item) => item.algorithm === key).map((item) => ({ x: item.size, y: item.elapsed_seconds })),
    borderColor: CHART_COLORS[index % CHART_COLORS.length],
    backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
    tension: 0.25,
  }));
  const datasetsDistance = algorithms.map((key, index) => ({
    label: ALGORITHM_LABELS[key] || key,
    data: successResults.filter((item) => item.algorithm === key).map((item) => ({ x: item.size, y: item.total_distance_km })),
    borderColor: CHART_COLORS[index % CHART_COLORS.length],
    backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
    tension: 0.25,
  }));

  if (travelTimeChart) travelTimeChart.destroy();
  travelTimeChart = new Chart(document.getElementById("travelTimeChart").getContext("2d"), {
    type: "line",
    data: { datasets: datasetsTime },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { type: "linear", title: { display: true, text: "Tamanho da entrada" } }, y: { title: { display: true, text: "Tempo (s)" } } },
    },
  });

  if (travelDistanceChart) travelDistanceChart.destroy();
  travelDistanceChart = new Chart(document.getElementById("travelDistanceChart").getContext("2d"), {
    type: "line",
    data: { datasets: datasetsDistance },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { type: "linear", title: { display: true, text: "Tamanho da entrada" } }, y: { title: { display: true, text: "Distancia (km)" } } },
    },
  });

  document.querySelector("#travelBenchTable tbody").innerHTML = results
    .map((item) =>
      item.success
        ? `<tr><td>${ALGORITHM_LABELS[item.algorithm] || item.algorithm}</td><td>${item.size}</td><td>${formatNumber(item.total_distance_km)}</td><td>${formatSeconds(item.elapsed_seconds)}</td><td>${item.comparisons}</td></tr>`
        : `<tr><td>${ALGORITHM_LABELS[item.algorithm] || item.algorithm}</td><td>${item.size}</td><td colspan="3"><span class="badge badge-warning">${item.reason}</span></td></tr>`
    )
    .join("");
}

async function runClassicBenchmark() {
  const kind = document.getElementById("classicKind").value;
  const sizes = Array.from(document.querySelectorAll("#classicSizesChecklist input:checked")).map((input) => parseInt(input.value, 10));
  if (sizes.length === 0) {
    alert("Selecione ao menos um tamanho.");
    return;
  }

  const button = document.getElementById("runClassicBenchBtn");
  button.disabled = true;
  button.textContent = "Executando benchmark...";

  try {
    const results = await apiPost("/api/benchmark/classic", { kind, sizes });
    recordExecution(results.length);
    renderClassicResults(results, kind);
  } finally {
    button.disabled = false;
    button.textContent = "📈 Executar benchmark";
  }
}

function renderClassicResults(results, kind) {
  document.getElementById("classicBenchResult").style.display = "block";

  if (classicTimeChart) classicTimeChart.destroy();
  classicTimeChart = new Chart(document.getElementById("classicTimeChart").getContext("2d"), {
    type: "line",
    data: {
      datasets: [
        {
          label: kind,
          data: results.map((item) => ({ x: item.size, y: item.elapsed_seconds })),
          borderColor: "#2563eb",
          backgroundColor: "#2563eb",
          tension: 0.25,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { type: "linear", title: { display: true, text: "Tamanho da entrada" } }, y: { title: { display: true, text: "Tempo (s)" } } },
    },
  });

  document.querySelector("#classicBenchTable tbody").innerHTML = results
    .map((item) => `<tr><td>${item.size}</td><td>${formatSeconds(item.elapsed_seconds)}</td><td>${item.comparisons}</td></tr>`)
    .join("");
}

document.getElementById("runTravelBenchBtn").addEventListener("click", runTravelBenchmark);
document.getElementById("runClassicBenchBtn").addEventListener("click", runClassicBenchmark);

renderTravelChecklists();
