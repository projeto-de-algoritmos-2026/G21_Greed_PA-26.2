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

const trip = [];
let compareChart = null;

function renderChecklist() {
  const container = document.getElementById("algorithmChecklist");
  container.innerHTML = AVAILABLE_ALGORITHMS.map(
    (key, index) => `
    <label class="checkbox-item">
      <input type="checkbox" value="${key}" ${index < 5 ? "checked" : ""}>
      ${ALGORITHM_LABELS[key] || key}
    </label>`
  ).join("");
}

function renderTripSummary() {
  const el = document.getElementById("tripSummary");
  el.textContent = trip.length ? `${trip.length} localidade(s): ${trip.map((item) => item.name).join(", ")}` : "Nenhuma localidade adicionada.";
}

async function handleSearch() {
  const query = document.getElementById("searchInput").value.trim();
  const resultsBox = document.getElementById("searchResults");
  if (query.length < 2) {
    resultsBox.innerHTML = "";
    return;
  }
  const results = await apiGet(`/api/locations?q=${encodeURIComponent(query)}&limit=20`);
  resultsBox.innerHTML = results
    .map((location) => `<div class="resource-row" data-add="${location.id}" style="cursor:pointer;"><span>${location.name} (${location.country})</span></div>`)
    .join("");
  resultsBox.querySelectorAll("[data-add]").forEach((row) => {
    row.addEventListener("click", () => {
      const id = parseInt(row.getAttribute("data-add"), 10);
      const location = results.find((item) => item.id === id);
      if (location && !trip.some((item) => item.id === id)) trip.push(location);
      renderTripSummary();
    });
  });
}

async function loadDemo() {
  const demoLocations = await apiGet("/api/travel/demo");
  trip.length = 0;
  demoLocations.forEach((location) => trip.push(location));
  renderTripSummary();
}

async function runComparison() {
  if (trip.length < 2) {
    alert("Adicione pelo menos duas localidades.");
    return;
  }
  const selected = Array.from(document.querySelectorAll("#algorithmChecklist input:checked")).map((input) => input.value);
  if (selected.length === 0) {
    alert("Selecione pelo menos um algoritmo.");
    return;
  }

  const data = await apiPost("/api/travel/compare", {
    algorithms: selected,
    location_ids: trip.map((location) => location.id),
  });
  recordExecution(selected.length);

  document.getElementById("resultCard").style.display = "block";
  const successResults = data.results.filter((item) => item.success);
  const best = successResults.reduce((min, item) => (item.total_distance_km < (min ? min.total_distance_km : Infinity) ? item : min), null);

  document.querySelector("#compareTable tbody").innerHTML = data.results
    .map((item) => {
      if (!item.success) {
        return `<tr><td>${ALGORITHM_LABELS[item.key] || item.key}</td><td colspan="4"><span class="badge badge-warning">Indisponivel: ${item.reason}</span></td></tr>`;
      }
      const isBest = best && item.key === best.key;
      return `<tr ${isBest ? 'style="background:#dcfce7;"' : ""}>
        <td>${item.algorithm} ${isBest ? '<span class="badge badge-success">MELHOR</span>' : ""}</td>
        <td>${formatNumber(item.total_distance_km)}</td>
        <td>${formatSeconds(item.elapsed_seconds)}</td>
        <td>${item.comparisons}</td>
        <td>${trip.length}</td>
      </tr>`;
    })
    .join("");

  const chartCtx = document.getElementById("compareChart").getContext("2d");
  if (compareChart) compareChart.destroy();
  compareChart = new Chart(chartCtx, {
    type: "bar",
    data: {
      labels: successResults.map((item) => item.algorithm),
      datasets: [
        {
          label: "Distancia total (km)",
          data: successResults.map((item) => item.total_distance_km),
          backgroundColor: "#2563eb",
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

document.getElementById("searchInput").addEventListener("input", handleSearch);
document.getElementById("loadDemoBtn").addEventListener("click", loadDemo);
document.getElementById("clearBtn").addEventListener("click", () => {
  trip.length = 0;
  renderTripSummary();
});
document.getElementById("runCompareBtn").addEventListener("click", runComparison);

renderChecklist();
renderTripSummary();
