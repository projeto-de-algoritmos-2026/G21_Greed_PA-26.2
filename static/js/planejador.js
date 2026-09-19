const trip = [];
let map;
let markersLayer;
let routeLayer;

function initMap() {
  map = L.map("map").setView([-14.235, -51.925], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 18,
  }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
}

function renderTripList() {
  const container = document.getElementById("tripList");
  document.getElementById("tripCount").textContent = trip.length;
  if (trip.length === 0) {
    container.innerHTML = '<div class="empty-state">Nenhuma localidade adicionada.</div>';
    return;
  }
  container.innerHTML = trip
    .map(
      (location, index) => `
      <div class="resource-row" style="justify-content:space-between;">
        <span>${index + 1}. ${location.name} <small style="color:var(--text-muted);">(${location.country})</small></span>
        <button class="btn btn-secondary btn-sm" data-remove="${location.id}">✕</button>
      </div>`
    )
    .join("");

  container.querySelectorAll("[data-remove]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = parseInt(button.getAttribute("data-remove"), 10);
      const index = trip.findIndex((item) => item.id === id);
      if (index >= 0) trip.splice(index, 1);
      renderTripList();
      renderMarkers();
    });
  });
}

function renderMarkers() {
  markersLayer.clearLayers();
  trip.forEach((location, index) => {
    const marker = L.marker([location.latitude, location.longitude]).bindPopup(
      `<strong>${index + 1}. ${location.name}</strong><br>${location.region}, ${location.country}`
    );
    markersLayer.addLayer(marker);
  });
  if (trip.length > 0) {
    const bounds = L.latLngBounds(trip.map((location) => [location.latitude, location.longitude]));
    map.fitBounds(bounds, { padding: [40, 40] });
  }
}

function addLocation(location) {
  if (trip.some((item) => item.id === location.id)) return;
  trip.push(location);
  renderTripList();
  renderMarkers();
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
    .map(
      (location) => `
      <div class="resource-row" data-add="${location.id}" style="cursor:pointer;">
        <span>${location.name} <small style="color:var(--text-muted);">(${location.country})</small></span>
      </div>`
    )
    .join("") || '<div class="empty-state">Nenhum resultado.</div>';

  resultsBox.querySelectorAll("[data-add]").forEach((row) => {
    row.addEventListener("click", () => {
      const id = parseInt(row.getAttribute("data-add"), 10);
      const location = results.find((item) => item.id === id);
      if (location) addLocation(location);
    });
  });
}

async function loadDemo() {
  const demoLocations = await apiGet("/api/travel/demo");
  trip.length = 0;
  demoLocations.forEach((location) => trip.push(location));
  renderTripList();
  renderMarkers();
}

function drawRoute(order, locationsByIndex) {
  routeLayer.clearLayers();
  const latlngs = order.map((index) => {
    const location = locationsByIndex[index];
    return [location.latitude, location.longitude];
  });
  const polyline = L.polyline(latlngs, { color: "#2563eb", weight: 4, opacity: 0.85 });
  routeLayer.addLayer(polyline);
  map.fitBounds(polyline.getBounds(), { padding: [40, 40] });
}

async function runAlgorithm() {
  if (trip.length < 2) {
    alert("Adicione pelo menos duas localidades para executar um algoritmo de roteirizacao.");
    return;
  }
  const algorithm = document.getElementById("algorithmSelect").value;
  const runButton = document.getElementById("runBtn");
  runButton.disabled = true;
  runButton.textContent = "Executando...";

  try {
    const result = await apiPost("/api/travel/run", {
      algorithm,
      location_ids: trip.map((location) => location.id),
    });
    recordExecution();

    drawRoute(result.order, trip);

    document.getElementById("resultCard").style.display = "block";
    document.getElementById("resultMetrics").innerHTML = `
      <div class="metric-pill"><div class="value">${formatNumber(result.total_distance_km)} km</div><div class="label">Distancia total</div></div>
      <div class="metric-pill"><div class="value">${formatSeconds(result.metrics.elapsed_seconds)}</div><div class="label">Tempo de execucao</div></div>
      <div class="metric-pill"><div class="value">${result.metrics.comparisons}</div><div class="label">Comparacoes</div></div>
      <div class="metric-pill"><div class="value">${result.metrics.cities}</div><div class="label">Localidades</div></div>
    `;
    document.getElementById("routeChain").innerHTML = result.route
      .map((name, index) => `<span class="stop">${index + 1}. ${name}</span>${index < result.route.length - 1 ? '<span class="arrow">→</span>' : ""}`)
      .join("");
  } catch (error) {
    alert(error.message);
  } finally {
    runButton.disabled = false;
    runButton.textContent = "▶️ Executar algoritmo";
  }
}

document.getElementById("searchInput").addEventListener("input", handleSearch);
document.getElementById("loadDemoBtn").addEventListener("click", loadDemo);
document.getElementById("clearTripBtn").addEventListener("click", () => {
  trip.length = 0;
  renderTripList();
  renderMarkers();
  document.getElementById("resultCard").style.display = "none";
});
document.getElementById("runBtn").addEventListener("click", runAlgorithm);

initMap();
renderTripList();
