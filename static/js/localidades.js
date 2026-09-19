async function loadCountries() {
  const meta = await apiGet("/api/locations/meta");
  const select = document.getElementById("filterCountry");
  meta.countries.forEach((country) => {
    const option = document.createElement("option");
    option.value = country;
    option.textContent = country;
    select.appendChild(option);
  });
}

function renderRows(locations) {
  const body = document.getElementById("locationsTableBody");
  document.getElementById("totalInfo").textContent = `${locations.length} localidade(s) exibida(s)`;
  body.innerHTML = locations
    .map(
      (location) => `
      <tr>
        <td>${location.id}</td>
        <td>${location.name}</td>
        <td>${location.country}</td>
        <td>${location.region}</td>
        <td>${location.latitude.toFixed(4)}</td>
        <td>${location.longitude.toFixed(4)}</td>
        <td style="white-space:nowrap;">
          <button class="btn btn-secondary btn-sm" data-edit="${location.id}">Editar</button>
          <button class="btn btn-danger btn-sm" data-delete="${location.id}">Excluir</button>
        </td>
      </tr>`
    )
    .join("");

  body.querySelectorAll("[data-edit]").forEach((button) => {
    button.addEventListener("click", () => openForm(locations.find((item) => item.id === parseInt(button.getAttribute("data-edit"), 10))));
  });
  body.querySelectorAll("[data-delete]").forEach((button) => {
    button.addEventListener("click", () => deleteLocation(parseInt(button.getAttribute("data-delete"), 10)));
  });
}

async function refresh() {
  const query = document.getElementById("filterQuery").value;
  const country = document.getElementById("filterCountry").value;
  const params = new URLSearchParams({ limit: "150" });
  if (query) params.set("q", query);
  if (country) params.set("country", country);
  const locations = await apiGet(`/api/locations?${params.toString()}`);
  renderRows(locations);
}

function openForm(location) {
  document.getElementById("formCard").style.display = "block";
  document.getElementById("formTitle").textContent = location ? `Editar: ${location.name}` : "Nova localidade";
  document.getElementById("editId").value = location ? location.id : "";
  document.getElementById("fieldName").value = location ? location.name : "";
  document.getElementById("fieldCountry").value = location ? location.country : "";
  document.getElementById("fieldRegion").value = location ? location.region : "";
  document.getElementById("fieldLat").value = location ? location.latitude : "";
  document.getElementById("fieldLon").value = location ? location.longitude : "";
  document.getElementById("fieldScore").value = location ? location.score : 50;
}

async function saveLocation() {
  const id = document.getElementById("editId").value;
  const payload = {
    name: document.getElementById("fieldName").value.trim(),
    country: document.getElementById("fieldCountry").value.trim(),
    region: document.getElementById("fieldRegion").value.trim(),
    latitude: parseFloat(document.getElementById("fieldLat").value),
    longitude: parseFloat(document.getElementById("fieldLon").value),
    score: parseInt(document.getElementById("fieldScore").value, 10) || 50,
  };
  if (!payload.name || !payload.country || !payload.region || Number.isNaN(payload.latitude) || Number.isNaN(payload.longitude)) {
    alert("Preencha todos os campos obrigatorios corretamente.");
    return;
  }
  if (id) {
    await fetch(`/api/locations/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await apiPost("/api/locations", payload);
  }
  document.getElementById("formCard").style.display = "none";
  await refresh();
}

async function deleteLocation(id) {
  if (!confirm("Confirma a exclusao desta localidade?")) return;
  await fetch(`/api/locations/${id}`, { method: "DELETE" });
  await refresh();
}

document.getElementById("filterBtn").addEventListener("click", refresh);
document.getElementById("newLocationBtn").addEventListener("click", () => openForm(null));
document.getElementById("cancelFormBtn").addEventListener("click", () => {
  document.getElementById("formCard").style.display = "none";
});
document.getElementById("saveLocationBtn").addEventListener("click", saveLocation);

loadCountries();
refresh();
