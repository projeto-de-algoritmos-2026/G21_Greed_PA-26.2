document.querySelectorAll(".tab-btn").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((panel) => (panel.style.display = "none"));
    button.classList.add("active");
    document.getElementById(`panel-${button.getAttribute("data-tab")}`).style.display = "block";
  });
});

let currentIntervalScheduling = [];
let currentIntervalPartitioning = [];
let currentLatenessTasks = [];
let currentKnapsackItems = [];
let currentCaminhoneiroStations = [];

let intervalSchedulingReady = null;
let intervalPartitioningReady = null;
let latenessReady = null;
let knapsackReady = null;
let caminhoneiroReady = null;

function metricPill(value, label) {
  return `<div class="metric-pill"><div class="value">${value}</div><div class="label">${label}</div></div>`;
}

function timelineHtml(intervals, classify) {
  const maxEnd = Math.max(...intervals.map((item) => item.end), 1);
  return intervals
    .map((interval) => {
      const leftPct = (interval.start / maxEnd) * 100;
      const widthPct = Math.max(((interval.end - interval.start) / maxEnd) * 100, 2);
      const cls = classify(interval);
      return `
      <div class="interval-bar-row">
        <span style="width:60px; flex-shrink:0;">${interval.id}</span>
        <div class="interval-track">
          <div class="interval-block ${cls}" style="left:${leftPct}%; width:${widthPct}%;">${interval.start}-${interval.end}</div>
        </div>
      </div>`;
    })
    .join("");
}

function generateIntervalScheduling() {
  intervalSchedulingReady = (async () => {
    const count = document.getElementById("is-count").value;
    const seed = document.getElementById("is-seed").value;
    currentIntervalScheduling = await apiGet(`/api/interval-scheduling/generate?count=${count}&seed=${seed}`);
    document.getElementById("is-chart").innerHTML = timelineHtml(currentIntervalScheduling, () => "interval-rejected");
    document.getElementById("is-metrics").innerHTML = "";
  })();
  return intervalSchedulingReady;
}

async function solveIntervalScheduling() {
  if (intervalSchedulingReady) await intervalSchedulingReady;
  const result = await apiPost("/api/interval-scheduling/solve", { intervals: currentIntervalScheduling });
  recordExecution();
  const selectedIds = new Set(result.selected.map((item) => item.id));
  document.getElementById("is-chart").innerHTML = timelineHtml(currentIntervalScheduling, (interval) =>
    selectedIds.has(interval.id) ? "interval-selected" : "interval-rejected"
  );
  document.getElementById("is-metrics").innerHTML =
    metricPill(result.selected_count, "Selecionados") +
    metricPill(result.rejected_count, "Rejeitados") +
    metricPill(result.total_count, "Total de intervalos") +
    metricPill(formatSeconds(result.metrics.elapsed_seconds), "Tempo") +
    metricPill(result.metrics.comparisons, "Comparacoes");
}

function generateIntervalPartitioning() {
  intervalPartitioningReady = (async () => {
    const count = document.getElementById("ip-count").value;
    const seed = document.getElementById("ip-seed").value;
    currentIntervalPartitioning = await apiGet(`/api/interval-partitioning/generate?count=${count}&seed=${seed}`);
    renderPartitioningInput();
    document.getElementById("ip-metrics").innerHTML = "";
  })();
  return intervalPartitioningReady;
}

function renderPartitioningInput() {
  document.getElementById("ip-chart").innerHTML = `<div class="resource-row"><div class="resource-label">Entrada</div><div style="flex:1;">${timelineHtml(
    currentIntervalPartitioning,
    () => "interval-rejected"
  )}</div></div>`;
}

async function solveIntervalPartitioning() {
  if (intervalPartitioningReady) await intervalPartitioningReady;
  const result = await apiPost("/api/interval-partitioning/solve", { intervals: currentIntervalPartitioning });
  recordExecution();

  const colors = ["#2563eb", "#0ea5a3", "#d97706", "#9333ea", "#e0473e", "#16a34a", "#64748b"];
  const rows = result.resources
    .map((resource, index) => {
      const color = colors[index % colors.length];
      const blocks = timelineHtml(resource.intervals, () => "");
      return `<div class="resource-row"><div class="resource-label">Recurso ${resource.resource + 1}</div><div style="flex:1;">${blocks.replaceAll(
        'class="interval-block "',
        `class="interval-block" style="background:${color};"`
      )}</div></div>`;
    })
    .join("");
  document.getElementById("ip-chart").innerHTML = rows;
  document.getElementById("ip-metrics").innerHTML =
    metricPill(result.resources_used, "Recursos utilizados") +
    metricPill(result.depth, "Profundidade do conjunto") +
    metricPill(formatSeconds(result.metrics.elapsed_seconds), "Tempo") +
    metricPill(result.metrics.comparisons, "Comparacoes");
}

function renderLatenessTable(tableId, schedule) {
  const body = document.querySelector(`#${tableId} tbody`);
  body.innerHTML = schedule
    .map(
      (item) => `<tr>
      <td>${item.id}</td><td>${item.processing_time}</td><td>${item.deadline}</td>
      <td>${item.completion}</td>
      <td>${item.lateness > 0 ? `<span class="badge badge-danger">${item.lateness}</span>` : `<span class="badge badge-success">0</span>`}</td>
    </tr>`
    )
    .join("");
}

function generateLateness() {
  latenessReady = (async () => {
    const count = document.getElementById("la-count").value;
    const seed = document.getElementById("la-seed").value;
    currentLatenessTasks = await apiGet(`/api/lateness/generate?count=${count}&seed=${seed}`);
    document.querySelector("#la-table-arbitrary tbody").innerHTML = "";
    document.querySelector("#la-table-greedy tbody").innerHTML = "";
    document.getElementById("la-metrics-arbitrary").innerHTML = "";
    document.getElementById("la-metrics-greedy").innerHTML = "";
  })();
  return latenessReady;
}

async function solveLateness() {
  if (latenessReady) await latenessReady;
  const result = await apiPost("/api/lateness/solve", { tasks: currentLatenessTasks });
  recordExecution();

  renderLatenessTable("la-table-arbitrary", result.arbitrary_order.schedule);
  renderLatenessTable("la-table-greedy", result.greedy_order.schedule);

  document.getElementById("la-metrics-arbitrary").innerHTML =
    metricPill(result.arbitrary_order.max_lateness, "Atraso maximo") +
    metricPill(result.arbitrary_order.total_lateness, "Atraso total") +
    metricPill(result.arbitrary_order.inversions, "Inversoes");

  document.getElementById("la-metrics-greedy").innerHTML =
    metricPill(result.greedy_order.max_lateness, "Atraso maximo") +
    metricPill(result.greedy_order.total_lateness, "Atraso total") +
    metricPill(result.greedy_order.inversions, "Inversoes");
}

function generateKnapsack() {
  knapsackReady = (async () => {
    const count = document.getElementById("kn-count").value;
    const seed = document.getElementById("kn-seed").value;
    currentKnapsackItems = await apiGet(`/api/knapsack/generate?count=${count}&seed=${seed}`);
    document.querySelector("#kn-table tbody").innerHTML = "";
    document.getElementById("kn-bar").innerHTML = "";
    document.getElementById("kn-metrics").innerHTML = "";
  })();
  return knapsackReady;
}

async function solveKnapsack() {
  if (knapsackReady) await knapsackReady;
  const capacity = parseFloat(document.getElementById("kn-capacity").value);
  const result = await apiPost("/api/knapsack/solve", { items: currentKnapsackItems, capacity });
  recordExecution();

  const colors = ["#2563eb", "#0ea5a3", "#d97706", "#9333ea", "#e0473e", "#16a34a", "#64748b", "#db2777"];
  document.getElementById("kn-bar").innerHTML = result.selection
    .filter((item) => item.fraction > 0)
    .map(
      (item, index) =>
        `<div class="knapsack-slice" style="width:${(item.taken_weight / result.capacity) * 100}%; background:${colors[index % colors.length]};" title="${item.name}">${(item.fraction * 100).toFixed(0)}%</div>`
    )
    .join("");

  document.querySelector("#kn-table tbody").innerHTML = result.selection
    .map(
      (item) => `<tr>
      <td>${item.name}</td><td>${item.weight}</td><td>R$ ${formatNumber(item.value)}</td>
      <td>R$ ${formatNumber(item.ratio)}/kg</td>
      <td>${(item.fraction * 100).toFixed(1)}%</td>
    </tr>`
    )
    .join("");

  document.getElementById("kn-metrics").innerHTML =
    metricPill(`R$ ${formatNumber(result.total_value)}`, "Valor total") +
    metricPill(`${formatNumber(result.used_weight)} kg`, "Peso utilizado") +
    metricPill(`${formatNumber(result.remaining_capacity)} kg`, "Capacidade livre") +
    metricPill(formatSeconds(result.metrics.elapsed_seconds), "Tempo");
}

function renderTrocadorTable(tableId, used) {
  const body = document.querySelector(`#${tableId} tbody`);
  if (!used) {
    body.innerHTML = '<tr><td colspan="2">Nao foi possivel calcular.</td></tr>';
    return;
  }
  body.innerHTML = used.map((entry) => `<tr><td>${entry.denomination}</td><td>${entry.quantity}</td></tr>`).join("");
}

async function solveTrocador() {
  const amount = parseInt(document.getElementById("tr-amount").value, 10);
  const denominations = document
    .getElementById("tr-denoms")
    .value.split(",")
    .map((value) => parseInt(value.trim(), 10))
    .filter((value) => !Number.isNaN(value) && value > 0);

  const result = await apiPost("/api/trocador/solve", { amount, denominations });
  recordExecution();

  renderTrocadorTable("tr-table-greedy", result.greedy.used);
  renderTrocadorTable("tr-table-optimal", result.optimal.used);

  document.getElementById("tr-metrics").innerHTML =
    metricPill(result.greedy.total_coins, "Moedas (guloso)") +
    metricPill(result.optimal.total_coins ?? "-", "Moedas (otimo)") +
    metricPill(result.greedy.exact ? "Sim" : "Nao", "Troco exato") +
    metricPill(
      `<span class="badge ${result.is_greedy_optimal ? "badge-success" : "badge-danger"}">${result.is_greedy_optimal ? "OTIMO" : "NAO OTIMO"}</span>`,
      "Guloso e otimo?"
    );
}

async function loadTrocadorCases() {
  const cases = await apiGet("/api/trocador/cases");
  document.getElementById("tr-cases").innerHTML = cases
    .map((item) => `<button class="btn btn-secondary btn-sm" data-case='${JSON.stringify(item)}'>${item.title}</button>`)
    .join(" ");
  document.querySelectorAll("[data-case]").forEach((button) => {
    button.addEventListener("click", () => {
      const data = JSON.parse(button.getAttribute("data-case"));
      document.getElementById("tr-amount").value = data.amount;
      document.getElementById("tr-denoms").value = data.denominations.join(",");
      solveTrocador();
    });
  });
}

function generateCaminhoneiro() {
  caminhoneiroReady = (async () => {
    const distance = document.getElementById("ca-distance").value;
    const seed = document.getElementById("ca-seed").value;
    const result = await apiGet(`/api/caminhoneiro/generate?distance=${distance}&seed=${seed}`);
    currentCaminhoneiroStations = result.stations;
    document.getElementById("ca-route").innerHTML = "";
    document.querySelector("#ca-table tbody").innerHTML = "";
    document.getElementById("ca-metrics").innerHTML = "";
  })();
  return caminhoneiroReady;
}

async function solveCaminhoneiro() {
  if (caminhoneiroReady) await caminhoneiroReady;
  const distance = parseFloat(document.getElementById("ca-distance").value);
  const tankCapacity = parseFloat(document.getElementById("ca-capacity").value);
  const consumption = parseFloat(document.getElementById("ca-consumption").value);

  try {
    const result = await apiPost("/api/caminhoneiro/solve", {
      distance,
      tank_capacity: tankCapacity,
      consumption,
      stations: currentCaminhoneiroStations,
    });
    recordExecution();

    if (!result.feasible) {
      document.getElementById("ca-route").innerHTML = `<div class="warning-box">⚠️ ${result.reason}</div>`;
      document.querySelector("#ca-table tbody").innerHTML = "";
      document.getElementById("ca-metrics").innerHTML = "";
      return;
    }

    const stopPositions = new Set(result.stops.map((stop) => stop.position));
    const stationMarks = currentCaminhoneiroStations
      .map((station) => {
        const pct = (station.position / distance) * 100;
        const usado = stopPositions.has(station.position);
        return `<div style="position:absolute; left:${pct}%; top:-6px; width:2px; height:20px; background:${usado ? "#2563eb" : "#cbd2e1"};" title="${station.name} (${station.position} km)"></div>`;
      })
      .join("");

    document.getElementById("ca-route").innerHTML = `
      <div style="position:relative; height:12px; background:var(--surface-alt); border-radius:6px; margin:20px 0;">
        ${stationMarks}
      </div>
      <small style="color:var(--text-muted);">Linhas azuis = postos escolhidos para abastecimento. Linhas cinzas = postos disponiveis nao utilizados.</small>
    `;

    document.querySelector("#ca-table tbody").innerHTML = result.stops
      .map((stop) => `<tr><td>${stop.station}</td><td>${stop.position}</td><td>${formatNumber(stop.fuel_added_liters)}</td></tr>`)
      .join("");

    document.getElementById("ca-metrics").innerHTML =
      metricPill(result.stops_count, "Paradas") +
      metricPill(`${formatNumber(result.autonomy)} km`, "Autonomia por tanque") +
      metricPill(`${formatNumber(result.total_fuel_liters)} L`, "Combustivel total") +
      metricPill(formatSeconds(result.metrics.elapsed_seconds), "Tempo");
  } catch (error) {
    document.getElementById("ca-route").innerHTML = `<div class="warning-box">⚠️ ${error.message}</div>`;
  }
}

document.getElementById("is-generate").addEventListener("click", generateIntervalScheduling);
document.getElementById("is-solve").addEventListener("click", solveIntervalScheduling);
document.getElementById("ip-generate").addEventListener("click", generateIntervalPartitioning);
document.getElementById("ip-solve").addEventListener("click", solveIntervalPartitioning);
document.getElementById("la-generate").addEventListener("click", generateLateness);
document.getElementById("la-solve").addEventListener("click", solveLateness);
document.getElementById("kn-generate").addEventListener("click", generateKnapsack);
document.getElementById("kn-solve").addEventListener("click", solveKnapsack);
document.getElementById("tr-solve").addEventListener("click", solveTrocador);
document.getElementById("ca-generate").addEventListener("click", generateCaminhoneiro);
document.getElementById("ca-solve").addEventListener("click", solveCaminhoneiro);

generateIntervalScheduling();
generateIntervalPartitioning();
generateLateness();
generateKnapsack();
loadTrocadorCases();
generateCaminhoneiro();
