function layoutTree(node, depth, counter) {
  if (!node) return null;
  const layoutNode = { char: node.char, freq: node.freq, depth, children: [] };
  if (node.left === null && node.right === null) {
    layoutNode.x = counter.value;
    counter.value += 1;
  } else {
    const left = layoutTree(node.left, depth + 1, counter);
    const right = layoutTree(node.right, depth + 1, counter);
    if (left) layoutNode.children.push(left);
    if (right) layoutNode.children.push(right);
    const xs = layoutNode.children.map((child) => child.x);
    layoutNode.x = xs.reduce((a, b) => a + b, 0) / xs.length;
  }
  return layoutNode;
}

function renderTree(root) {
  const svg = document.getElementById("huffmanTree");
  svg.innerHTML = "";
  const counter = { value: 0 };
  const layout = layoutTree(root, 0, counter);

  const leafCount = Math.max(counter.value, 1);
  const width = Math.max(leafCount * 70, 400);
  const height = 60 + (Math.max(...collectDepths(layout)) + 1) * 80;
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const xScale = (x) => 40 + x * 70;
  const yScale = (depth) => 40 + depth * 80;

  drawEdges(svg, layout, xScale, yScale);
  drawNodes(svg, layout, xScale, yScale);
}

function collectDepths(node, acc = []) {
  acc.push(node.depth);
  node.children.forEach((child) => collectDepths(child, acc));
  return acc;
}

function drawEdges(svg, node, xScale, yScale) {
  node.children.forEach((child, index) => {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", xScale(node.x));
    line.setAttribute("y1", yScale(node.depth));
    line.setAttribute("x2", xScale(child.x));
    line.setAttribute("y2", yScale(child.depth));
    line.setAttribute("stroke", "#94a3b8");
    line.setAttribute("stroke-width", "2");
    svg.appendChild(line);

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", (xScale(node.x) + xScale(child.x)) / 2);
    label.setAttribute("y", (yScale(node.depth) + yScale(child.depth)) / 2 - 4);
    label.setAttribute("font-size", "11");
    label.setAttribute("fill", "#2563eb");
    label.setAttribute("font-weight", "700");
    label.textContent = index === 0 ? "0" : "1";
    svg.appendChild(label);

    drawEdges(svg, child, xScale, yScale);
  });
}

function drawNodes(svg, node, xScale, yScale) {
  const isLeaf = node.children.length === 0;
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", xScale(node.x));
  circle.setAttribute("cy", yScale(node.depth));
  circle.setAttribute("r", isLeaf ? 20 : 16);
  circle.setAttribute("fill", isLeaf ? "#2563eb" : "#0ea5a3");
  svg.appendChild(circle);

  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttribute("x", xScale(node.x));
  text.setAttribute("y", yScale(node.depth) + 4);
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("font-size", "11");
  text.setAttribute("fill", "#fff");
  text.setAttribute("font-weight", "700");
  text.textContent = isLeaf ? (node.char === " " ? "␣" : node.char) : node.freq;
  svg.appendChild(text);

  const freqLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
  freqLabel.setAttribute("x", xScale(node.x));
  freqLabel.setAttribute("y", yScale(node.depth) - (isLeaf ? 26 : 22));
  freqLabel.setAttribute("text-anchor", "middle");
  freqLabel.setAttribute("font-size", "10");
  freqLabel.setAttribute("fill", "#667085");
  freqLabel.textContent = isLeaf ? `f=${node.freq}` : "";
  svg.appendChild(freqLabel);

  node.children.forEach((child) => drawNodes(svg, child, xScale, yScale));
}

function metricPill(value, label) {
  return `<div class="metric-pill"><div class="value">${value}</div><div class="label">${label}</div></div>`;
}

async function solveHuffman() {
  const text = document.getElementById("huffmanText").value;
  if (!text) {
    alert("Digite um texto para codificar.");
    return;
  }
  const result = await apiPost("/api/huffman/solve", { text });
  recordExecution();

  document.getElementById("huffmanResult").style.display = "block";
  document.getElementById("huffmanMetrics").innerHTML =
    metricPill(`${result.original_bits} bits`, "Tamanho original (ASCII)") +
    metricPill(`${result.encoded_bits} bits`, "Tamanho codificado") +
    metricPill(`${(result.compression_ratio * 100).toFixed(1)}%`, "Taxa de compressao") +
    metricPill(result.average_code_length.toFixed(2), "Comprimento medio do codigo") +
    metricPill(result.decoding_matches_original ? "Sim" : "Nao", "Decodificacao correta");

  document.querySelector("#freqTable tbody").innerHTML = result.frequencies
    .map((item) => `<tr><td>${item.char === " " ? "␣ (espaco)" : item.char}</td><td>${item.count}</td></tr>`)
    .join("");

  document.querySelector("#codesTable tbody").innerHTML = result.codes
    .map((item) => `<tr><td>${item.char === " " ? "␣ (espaco)" : item.char}</td><td class="mono">${item.code}</td></tr>`)
    .join("");

  renderTree(result.tree);

  document.getElementById("originalText").textContent = result.text;
  document.getElementById("encodedText").textContent = result.encoded_text;
  document.getElementById("decodedText").textContent = result.decoded_text;
}

document.getElementById("huffmanSolveBtn").addEventListener("click", solveHuffman);
solveHuffman();
