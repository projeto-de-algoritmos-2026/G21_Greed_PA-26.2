<div align="center">

# 🗺️ Greedy Travel Lab
### Planejador de Viagens & Laboratório de Algoritmos Ambiciosos

**Projeto de Algoritmos — Módulo Algoritmos Ambiciosos (Greedy) — PA 26.2**

![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-black)
![Localidades](https://img.shields.io/badge/localidades-5.200%2B-orange)
![Algoritmos](https://img.shields.io/badge/algoritmos-18-purple)
![Testes](https://img.shields.io/badge/testes-117%20passing-success)
![Banco%20de%20Dados](https://img.shields.io/badge/banco%20de%20dados-nenhum%20(JSON)-lightgrey)
![Licença](https://img.shields.io/badge/licença-acadêmica-informational)

Repositório de referência: `projeto-de-algoritmos-2026/G21_Greed_PA-26.2`

</div>

---

<div align="center">
  <h2>🎯 Objetivos</h2>
</div>

Este projeto foi desenvolvido para a disciplina de **Projeto de Algoritmos**, no módulo de **Algoritmos Ambiciosos (Greedy)**, com os seguintes objetivos:

- Demonstrar, de forma **visual e experimental**, como cada algoritmo ambicioso toma decisões locais para construir uma solução global.
- Implementar todos os algoritmos ambiciosos estudados na disciplina — **Interval Scheduling**, **Interval Partitioning**, **Scheduling to Minimize Lateness**, **Knapsack com itens divisíveis**, **Algoritmo do Trocador**, **Algoritmo do Caminhoneiro** e **Huffman** — com visualizações dedicadas.
- Aplicar esses conceitos a um problema real e tangível: um **Planejador de Viagens**, incluindo heurísticas ambiciosas para roteirização (TSP) sobre um dataset geográfico de larga escala.
- Permitir **comparação** entre algoritmos e **benchmarks** reproduzíveis, medindo tempo de execução, número de comparações e qualidade da solução conforme o tamanho da entrada cresce.
- Evidenciar, em uma seção dedicada de **Contraexemplos**, que estratégias ambiciosas nem sempre alcançam a solução ótima.

---

<div align="center">
  <h2>📖 Sobre o projeto</h2>
</div>

O **Greedy Travel Lab** é uma aplicação web que combina duas frentes:

1. **🗺️ Planejador de Viagens** — o usuário seleciona localidades reais (ou carrega um exemplo pronto com 10 capitais brasileiras), escolhe um algoritmo ambicioso de roteirização e visualiza a rota resultante em um mapa interativo, com distância total, tempo de execução e decisões tomadas.
2. **🧠 Laboratório de Algoritmos Ambiciosos** — cada algoritmo da disciplina possui uma página dedicada onde é possível gerar casos de teste (com *seed* reprodutível), executar o algoritmo e visualizar o resultado passo a passo: intervalos selecionados/rejeitados, recursos utilizados, cronogramas, ocupação da mochila, troco calculado, paradas de abastecimento e a árvore de Huffman.

Nenhum resultado exibido é inventado: todos os números vêm de cálculos reais executados pelo backend em Python no momento da requisição.

---

<div align="center">
  <h2>🚀 Funcionalidades</h2>
</div>

| Módulo | Descrição |
|---|---|
| 🔐 Login demonstrativo | Autenticação simulada (qualquer usuário/senha), deixada explícita na tela como demonstração acadêmica |
| 🏠 Dashboard | Estatísticas gerais, atalhos para todos os módulos e contador de execuções da sessão |
| 🗺️ Planejador de Viagens | Busca de localidades, mapa Leaflet, seleção de algoritmo e visualização da rota |
| 📍 Cadastro de Localidades | CRUD completo (criar, editar, excluir, buscar, filtrar) sobre o dataset local em JSON |
| 🧠 Laboratório de Algoritmos | 6 abas: Interval Scheduling, Interval Partitioning, Minimize Lateness, Knapsack, Trocador e Caminhoneiro |
| 🌳 Huffman | Codificação/decodificação de texto com árvore de Huffman desenhada em SVG |
| ⚔️ Comparação | Executa múltiplos algoritmos de roteirização sobre o mesmo conjunto de localidades e compara resultados |
| 📊 Benchmarks | Mede tempo, comparações e qualidade da solução para tamanhos de entrada crescentes, com gráficos |
| 📚 Teoria | Problema, critério ambicioso, pseudocódigo, complexidade e corretude de cada algoritmo |
| ⚠️ Contraexemplos | Casos verificados onde a estratégia ambiciosa não é ótima (Trocador, Mochila 0/1, Nearest Neighbor) |

---

<div align="center">
  <h2>🧠 Algoritmos implementados</h2>
</div>


- Interval Scheduling
- Interval Partitioning
- Scheduling to Minimize Lateness
- Knapsack com itens divisíveis
- Algoritmo do Trocador
- Algoritmo do Caminhoneiro

**Compressão**

- Huffman

**Algoritmos bônus**

- Nearest Neighbor
- Multi-Start Nearest Neighbor
- Farthest Neighbor
- Cheapest Insertion
- Nearest Insertion
- Farthest Insertion
- Greedy Edge Selection
- Clarke-Wright Savings
- Estratégia Greedy por Região
- Estratégia Greedy por Cluster
- Greedy por Benefício/Distância

---

<div align="center">
  <h2>🏗️ Arquitetura</h2>
</div>

Arquitetura intencionalmente simples — sem Docker, sem banco de dados, sem serviços externos obrigatórios:

```text
Frontend  → HTML + CSS + JavaScript puro (sem build step)
Backend   → Python + Flask
Dados     → Arquivos JSON locais (data/)
Mapas     → Leaflet + OpenStreetMap
Gráficos  → Chart.js
Testes    → pytest
```

### Estrutura de diretórios

```text
G21_Greed_PA-26.2/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── algorithms/
│   ├── locations_store.py
│   ├── benchmark.py
│   ├── interval_scheduling/
│   ├── interval_partitioning/
│   ├── scheduling_lateness/
│   ├── knapsack/
│   ├── trocador/
│   ├── caminhoneiro/
│   ├── huffman/
│   └── travel/
│
├── data/
│   ├── locations.json      (5.200+ localidades)
│   ├── test_10.json ... test_5000.json
│
├── scripts/
│   ├── core_cities.py
│   └── generate_dataset.py
│
├── tests/
├── static/{css,js,img}/
└── templates/
```

---

<div align="center">
  <h2>⚙️ Instalação</h2>
</div>

### 1. Pré-requisitos

- Python 3.11 ou superior instalado

### 2. Obtenha o projeto

Extraia ou copie a pasta do projeto para o seu computador (este repositório é utilizado apenas localmente pela dupla, conforme orientação acadêmica).

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Regenere o dataset de localidades

O dataset já é entregue pronto em `data/`. Caso queira regenerá-lo (mesma *seed*, resultado idêntico):

```bash
python scripts/generate_dataset.py
```

---

<div align="center">
  <h2>▶️ Execução</h2>
</div>

```bash
python app.py
```

Em seguida, acesse no navegador:

```text
http://localhost:5000
```

Use qualquer usuário e senha na tela de login — a autenticação é simulada para fins acadêmicos.

### Executando os testes

```bash
pytest
```

---

<div align="center">
  <h2>📦 Dataset</h2>
</div>

- **5.200 localidades** cadastradas em `data/locations.json`, combinando cidades reais (todas as 27 capitais brasileiras, dezenas de outras cidades brasileiras e mais de 150 cidades internacionais em 95 países) com localidades geradas proceduralmente (bairros/distritos ao redor das cidades reais, com *seed* fixa `42`) para viabilizar benchmarks em larga escala.
- Subconjuntos reproduzíveis para testes de desempenho: `test_10.json`, `test_50.json`, `test_100.json`, `test_500.json`, `test_1000.json`, `test_2500.json`, `test_5000.json`.
- Cada localidade possui `id`, `name`, `country`, `region`, `latitude`, `longitude`, `capital` e um `score` sintético (usado apenas pelo algoritmo Greedy por Benefício/Distância, claramente identificado como sintético na interface).

---

<div align="center">
  <h2>📊 Benchmarks</h2>
</div>

A página **Benchmarks** executa, em tempo real, os algoritmos sobre tamanhos de entrada crescentes (10, 25, 50, 100, 250, 500, 1000, 2500, 5000) e plota:

- Tempo de execução × tamanho da entrada
- Distância da rota × tamanho da entrada
- Tabela detalhada com número de comparações por algoritmo

Algoritmos com complexidade cúbica (Cheapest Insertion) ou que dependem da ordenação de todos os pares de arestas (Greedy Edge Selection, Clarke-Wright Savings) possuem um limite prático de localidades nesta demonstração interativa — o sistema informa claramente quando o limite é excedido, em vez de travar o servidor ou apresentar um resultado incompleto.

---

<div align="center">
  <h2>🧪 Testes</h2>
</div>

117 testes automatizados com `pytest`, cobrindo:

- Cálculo de distância (Haversine) e matriz de distâncias
- CRUD de localidades (isolado do dataset real via arquivos temporários)
- Interval Scheduling, Interval Partitioning, Scheduling to Minimize Lateness, Knapsack
- Algoritmo do Trocador (incluindo contraexemplos) e Algoritmo do Caminhoneiro
- Huffman (codificação, decodificação, prefixo único)
- Todas as 11 heurísticas de roteirização (TSP)
- Rotas HTTP da aplicação (login, autenticação, páginas, API)
- Casos extremos: entrada vazia, uma única localidade/intervalo/item, duplicatas, entradas grandes
- **Corretude contra referência independente**: Interval Scheduling e Interval Partitioning comparados a força bruta, Knapsack comparado a uma implementação de referência isolada, Trocador comparado a programação dinâmica em centenas de casos aleatórios, heurísticas de roteirização comparadas ao ótimo por força bruta em instâncias pequenas, Huffman comparado ao limite teórico de entropia de Shannon
- Validação end-to-end em navegador real (Playwright): todas as páginas, abas e fluxos de CRUD percorridos sem erros de console, incluindo testes de estresse para condições de corrida

```bash
pytest -v
```

---

<div align="center">
  <h2>🎥 Apresentação</h2>
</div>

🔗 Link da apresentação será adicionado posteriormente.

---

<div align="center">
  <h2>👩‍💻 Contribuidores</h2>
</div>

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/xGabrielCv">
        <img src="https://github.com/xGabrielCv.png" width="90" alt="Jésus Gabriel Carvalho Ventura"/><br>
        <sub><b>Jésus Gabriel Carvalho Ventura</b></sub>
      </a><br>
      <sub>Matrícula: 211062956</sub><br>
      <sub><a href="mailto:jgabrielcv1903@gmail.com">jgabrielcv1903@gmail.com</a></sub>
    </td>
    <td align="center">
      <a href="https://github.com/cwtshh">
        <img src="https://github.com/cwtshh.png" width="90" alt="Gustavo Costa"/><br>
        <sub><b>Gustavo Costa</b></sub>
      </a><br>
      <sub>Matrícula: 211061814</sub><br>
      <sub><a href="mailto:gucosta1719@gmail.com">gucosta1719@gmail.com</a></sub>
    </td>
  </tr>
</table>

---

<div align="center">
  <sub>Projeto acadêmico desenvolvido para a disciplina de Projeto de Algoritmos — 2026.2</sub>
</div>
