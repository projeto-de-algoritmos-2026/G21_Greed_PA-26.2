async function renderTrocadorCase(container, caseData) {
  const result = await apiPost("/api/trocador/solve", { amount: caseData.amount, denominations: caseData.denominations });
  const badge = result.is_greedy_optimal
    ? '<span class="badge badge-success">GULOSO OTIMO</span>'
    : '<span class="badge badge-danger">GULOSO NAO OTIMO</span>';

  const block = document.createElement("div");
  block.className = "theory-block";
  block.innerHTML = `
    <h4>${caseData.title} ${badge}</h4>
    <p>Valor: <strong>${caseData.amount}</strong> — Denominacoes: <strong>${caseData.denominations.join(", ")}</strong></p>
    <div class="metric-row">
      <div class="metric-pill"><div class="value">${result.greedy.total_coins}</div><div class="label">Moedas (guloso)</div></div>
      <div class="metric-pill"><div class="value">${result.optimal.total_coins ?? "-"}</div><div class="label">Moedas (otimo)</div></div>
    </div>
    <p style="font-size:13px; color:var(--text-muted);">Guloso: ${result.greedy.used.map((item) => `${item.quantity}x${item.denomination}`).join(" + ")}</p>
    <p style="font-size:13px; color:var(--text-muted);">Otimo: ${(result.optimal.used || []).map((item) => `${item.quantity}x${item.denomination}`).join(" + ")}</p>
  `;
  container.appendChild(block);
}

async function renderAllCases() {
  const container = document.getElementById("trocadorCases");
  for (const caseData of TROCADOR_CASES) {
    await renderTrocadorCase(container, caseData);
  }
}

renderAllCases();
