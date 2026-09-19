const menuToggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");

if (menuToggle && sidebar) {
  menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
}

async function apiGet(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Erro ${response.status}`);
  }
  return response.json();
}

async function apiPost(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Erro ${response.status}`);
  }
  return response.json();
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) return "-";
  return Number(value).toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function formatSeconds(value) {
  if (value === null || value === undefined) return "-";
  if (value < 0.001) return `${(value * 1e6).toFixed(1)} µs`;
  if (value < 1) return `${(value * 1000).toFixed(2)} ms`;
  return `${value.toFixed(3)} s`;
}

function recordExecution(count = 1) {
  try {
    const current = parseInt(localStorage.getItem("gtl_executions") || "0", 10);
    localStorage.setItem("gtl_executions", String(current + count));
  } catch (error) {
    return;
  }
}

function getExecutionCount() {
  try {
    return parseInt(localStorage.getItem("gtl_executions") || "0", 10);
  } catch (error) {
    return 0;
  }
}
