# 📈 ETF Portfolio Tracker & Backtester

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-success.svg)](https://pages.github.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75.svg)](https://plotly.com/)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)

Una eina visual interactiva i de codi obert per **analitzar, simular, radiografiar (X-Ray) i comparar carteres d'inversió** (ETFs, fons indexats, accions i criptoactius) dels darrers 10 a 20 anys.

El projecte disposa de **dues modalitats d'execució**:
1. 🌐 **Versió Web Client-Side (GitHub Pages)**: 100% autònoma en HTML5, Tailwind CSS i Plotly.js, desplegable gratuïtament a GitHub Pages sense cap servidor ni instal·lació.
2. 🖥️ **Versió d'Escriptori / Servidor (Python & Streamlit)**: Executable en local amb descàrrega directa de dades mitjançant `yfinance` i memòria cau en format Parquet.

---

## ✨ Funcionalitats Principals

### 1. 📊 Anàlisi Històrica de Cartera (Backtesting)
- **Simulació d'evolució de capital**: Partint de 10.000 € (o quantitat configurable) a **3, 5, 10, 15, 20 anys o màxim històric**.
- **Multi-Benchmark Simultani**: Visualitza i compara la teva cartera amb **dos o més benchmarks alhora** (p. ex. **S&P 500** i **Nasdaq 100** simultàniament).
- **Freqüències de Rebalançament**: Suport per a rebalançament **Anual**, **Trimestral** o estratègia passiva **Buy & Hold**.
- **Mètriques Financeres Professionals**:
  - **Capital Final** i **Rendibilitat Total (%)**.
  - **CAGR** (Taxa de creixement anual compost / TIR anualitzada).
  - **Volatilitat Anualitzada** ($\sigma$).
  - **Ràtio de Sharpe** (rendibilitat ajustada al risc respecte a una taxa lliure de risc del 2%).
  - **Ràtio de Sortino** (penalització exclusiva de la volatilitat a la baixa).
  - **Max Drawdown** (caiguda màxima des de màxims històrics).
  - **Rendiments any a any** per cada any natural.
- **Gràfics interactius de Plotly**:
  - Evolució del capital amb opció d'**escala logarítmica** o lineal.
  - *Underwater Plot* (gràfic d'àrea vermella de caigudes històriques).
  - Gràfic de barres de retorns anuals (verds per a positius, vermells per a negatius).
  - Donut d'assignació d'actius.

### 2. 🔍 Anàlisi d'Exposició Profunda (Portfolio X-Ray)
- **Exposició Geogràfica per Països**: Percentatge ponderat real invertit a Estats Units, Europa, Japó, Mercats Emergents, etc.
- **Exposició Sectorial per Indústries**: Desglossament per Tecnologia, Serveis Financers, Salut, Consum Cíclic, Indústria, Energia, etc.
- **Top Accions Individuals i Solapament (*Holdings Overlap*)**: Calcula quant tens realment invertit en empreses gegants com **Microsoft, Apple, NVIDIA, Amazon, Alphabet, TSMC o ASML** combinant tots els teus ETFs i accions individuals.

### 3. ⚖️ Comparador de Carteres (Bancs vs Propostes)
- Enfronta múltiples carteres cara a cara partint del mateix capital inicial (ideal per comparar propostes de bancs com Caixabank, Banc Santander o BBVA contra la teva cartera pròpia indexada).
- Gràfic multillínia interactiu superposat.
- **Taula comparativa cara a cara** amb tots els indicadors clau (CAGR, Volatilitat, Sharpe, Sortino, Drawdown).

### 4. 🛠️ Gestor i Creador de Carteres
- **Cercador i verificador en temps real**: Comprova instantàniament a Yahoo Finance si un ticker existeix, mostrant nom de la gestora/empresa, divisa i darrer preu abans d'afegir-lo.
- **Gestió intel·ligent d'àlies**: Mapeig automàtic de tickers sense sufix com `IS3N` → `IS3N.DE`, `IUSN` → `IUSN.DE`, `EUNK` → `EUNK.DE` o `BTC` → `BTC-EUR`.
- **Alineament de dades multiactiu (`ffill`)**: Correcció automàtica de calendaris de festius diferents entre borses internacionals.
- **Normalització automàtica al 100%**: Ajusta tots els percentatges amb un sol clic.
- **Reanomenar carteres (`✏️`)**: Formulari inline per canviar el nom de qualsevol cartera guardada.
- **Eliminar amb confirmació de seguretat (`🗑️`)**: Evita esborrats accidentals amb un pas de confirmació explícita.
- **Importació i exportació en format JSON**: Permet compartir carteres fàcilment o migrar-les entre navegadors.

---

## 🌐 Com utilitzar la Versió Web (GitHub Pages)

La versió web està continguda a `index.html` i la carpeta `static/` i no requereix instal·lar Python.

### Desplegament a GitHub Pages en 2 passos:
1. Puja aquest repositori a GitHub:
   ```bash
   git add .
   git commit -m "feat: afegir versió web per a GitHub Pages"
   git push origin main
   ```
2. Al teu repositori de GitHub:
   - Ves a **Settings** > **Pages**.
   - A **Source**, selecciona **GitHub Actions** (ja inclou el workflow a `.github/workflows/deploy.yml`) o selecciona **Deploy from a branch** > Branca `main` / `root`.
   - En pocs segons, la teva aplicació estarà disponible a:  
     `https://<el-teu-usuari>.github.io/<el-teu-repositori>/`

### Execució local de la versió web:
Pots obrir el fitxer `index.html` directament al teu navegador fent-hi doble clic, o servir-lo localment:
```bash
python3 -m http.server 8000
```
Obre el navegador a `http://localhost:8000`.

---

## 🖥️ Com executar la Versió Python (Streamlit)

Si prefereixes l'entorn de desenvolupament local en Python amb connexió directa a l'API de `yfinance`:

### Opció 1: Arrencada ràpida amb script
```bash
./run.sh
```

### Opció 2: Arrencada manual
```bash
# 1. Crear i activar entorn virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instal·lar dependències
pip install -r requirements.txt

# 3. Executar l'aplicació
streamlit run app.py
```
L'aplicació s'obrirà a `http://localhost:8501`.

---

## 📁 Estructura del Projecte

```text
etf-tracker/
├── index.html                  # Aplicació web principal per a GitHub Pages
├── docs/                       # Còpia de la web estàtica per a GitHub Pages (/docs)
├── static/
│   ├── css/styles.css          # Estils i animacions personalitzades
│   └── js/
│       ├── app.js              # Controlador principal de la interfície web
│       ├── backtest.js         # Motor financer complet en JavaScript
│       └── market_data.js      # Dades històriques precarregades (offline)
├── data/
│   └── market_data.json        # Base de dades històrica en format JSON
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md       # Plantilla d'informe d'errors
│   │   └── feature_request.md  # Plantilla de propostes de millora
│   ├── PULL_REQUEST_TEMPLATE.md# Plantilla per a Pull Requests
│   └── workflows/
│       └── deploy.yml          # Desplegament automàtic a GitHub Pages
├── app.py                      # Aplicació Streamlit (versió Python)
├── run.sh                      # Script d'arrencada d'un sol clic (Streamlit)
├── config.py                   # Configuració global, àlies de tickers i actius populars
├── requirements.txt            # Dependències de Python (Streamlit, yfinance, plotly, etc.)
├── core/
│   ├── data_fetcher.py         # Descàrrega de cotitzacions i cache Parquet
│   ├── portfolio.py            # Model de dades de la cartera
│   ├── backtest_engine.py      # Motor de simulació i rendibilitats (Python)
│   ├── metrics.py              # Mètriques financeres (CAGR, Sharpe, Sortino, Drawdown)
│   ├── xray_engine.py          # Càlcul d'exposició a països, sectors i accions
│   └── ticker_search.py        # Cerca i validació de tickers a Yahoo Finance
├── components/
│   ├── chart_views.py          # Vistes de gràfics de Plotly per a Streamlit
│   ├── xray_views.py           # Vistes de radiografia sectorial i geogràfica
│   ├── comparison_view.py      # Vistes del comparador multi-cartera
│   └── portfolio_builder.py    # Creador i gestor de carteres (Streamlit)
├── storage/
│   └── portfolio_storage.py    # Persistència JSON (desar, carregar, reanomenar, eliminar)
├── saved_portfolios/           # Carteres desades en fitxers JSON individuals
├── scripts/
│   ├── export_static_data.py   # Script d'exportació de Parquet a JSON/JS per a la web
│   └── cache_all.py            # Precarregador de tot l'històric de Yahoo Finance
├── test_app.py                 # Tests unitaris del motor financer
├── LICENSE                     # Llicència de codi obert (MIT)
├── CONTRIBUTING.md             # Guia de contribució per a nous desenvolupadors
├── CODE_OF_CONDUCT.md          # Codi de conducta de la comunitat
├── SECURITY.md                 # Política de seguretat i privacitat
├── CHANGELOG.md                # Registre detallat de canvis per versió
└── ROADMAP.md                  # Full de ruta de funcionalitats futures
```

---

## 🧪 Tests Unitaris

Per verificar que tots els càlculs financers de la versió Python funcionen correctament:
```bash
python test_app.py
```

---

## 📜 Llicència i Comunitat

Aquest projecte està llicenciat sota la **[Llicència MIT](LICENSE)**. Pots utilitzar-lo, modificar-lo i redistribuir-lo lliurement.

- 🤝 **Vols col·laborar?** Llegeix la nostra [Guia de Contribució (CONTRIBUTING.md)](CONTRIBUTING.md).
- 📜 **Codi de conducta**: Consulta [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- 🗺️ **Properes millores**: Revisa el nostre [Full de Ruta (ROADMAP.md)](ROADMAP.md).
- 🔒 **Seguretat**: Consulta la nostra [Política de Seguretat (SECURITY.md)](SECURITY.md).

---
*Creat amb propòsit educatiu i d'anàlisi independent. No constitueix cap assessorament financer.*
