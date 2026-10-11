# 📈 ETF Portfolio Tracker & Backtester

Una eina visual interactiva construïda en **Python (Streamlit + Plotly + yfinance)** per analitzar, simular i comparar carteres d'inversió (ETFs, fons i accions) dels darrers 10 a 20 anys.

---

## ✨ Funcionalitats Clau

1. **📊 Anàlisi Històrica de Cartera (Backtesting)**:
   - Descàrrega automàtica de cotitzacions històriques ajustades via `yfinance`.
   - Simulació de capital partint de 10.000 € (o quantitat configurable) a **3, 5, 10, 15, 20 anys o màxim històric**.
   - Opcions de rebalançament periòdic (**Anual**, **Trimestral** o **Buy & Hold**).
   - Indicadors financers clau: **Capital Final**, **CAGR** (rendibilitat anualitzada), **Volatilitat**, **Ràtio de Sharpe**, **Sortino**, **Max Drawdown** i retorns any per any.
   - Gràfics interactius de Plotly amb zoom, tooltips i gràfic de caigudes (*drawdown underwater plot*).

2. **🔍 Anàlisi d'Exposició (Portfolio X-Ray)**:
   - **Exposició Geogràfica**: Percentatge de la teva cartera invertit en cada país/regió (EUA, Europa, Japó, Mercats Emergents, etc.).
   - **Exposició Sectorial**: Repartiment per indústries (Tecnologia, Serveis Financers, Salut, Consum, Indústria...).
   - **Top Accions Individuals i Solapament (*Overlap*)**: Calcula el percentatge real ponderat de la teva cartera que està invertit en empreses individuals com Apple, Microsoft, NVIDIA, Amazon, TSMC, etc., tenint en compte tots els teus ETFs combinats.

3. **⚖️ Comparador de Carteres (Bancs vs Benchmarks)**:
   - Enfronta múltiples carteres simultàniament partint del mateix capital inicial (ideal per comparar propostes de diferents entitats bancàries com Banc Santander, CaixaBank, BBVA, etc.).
   - Gràfic multillínia superposat d'evolució del capital.
   - Taula comparativa cara a cara amb totes les mètriques de rendibilitat i risc.
   - Comparació d'exposició sectorial i retorns any a any.
   - Comparació directa amb benchmarks mundials (**S&P 500**, **MSCI World**, **Nasdaq 100**).

4. **🛠️ Creador i Gestor de Carteres**:
   - Creació i edició visual de carteres amb assignació de pesos percentuals (comprovador automàtic de suma 100%).
   - Cerca per ticker lliure o selecció d'un sol clic a la llista d'ETFs més populars.
   - Desat i càrrega de carteres en format JSON local (`saved_portfolios/`).

---

## 🚀 Com executar l'aplicació

### Opció 1: Amb el script directe
Executa a la terminal:
```bash
./run.sh
```

### Opció 2: Execució manual
```bash
source venv/bin/activate
streamlit run app.py
```

L'aplicació s'obrirà automàticament al teu navegador a `http://localhost:8501`.

---

## 📁 Estructura del Projecte

```text
etf-tracker/
├── app.py                     # Interfície Streamlit principal
├── run.sh                     # Script d'arrencada d'un sol clic
├── config.py                  # Paràmetres globals i llista d'ETFs populars
├── requirements.txt           # Llibreries necessàries
├── core/
│   ├── data_fetcher.py        # Descàrrega de cotitzacions i cache Parquet
│   ├── portfolio.py           # Model de dades de la cartera
│   ├── backtest_engine.py     # Motor de simulació i càlcul de rendibilitats
│   ├── metrics.py             # Mètriques financeres (CAGR, Sharpe, Drawdown)
│   └── xray_engine.py         # Càlcul d'exposició a països, sectors i accions
├── components/
│   ├── chart_views.py         # Gràfics interactius de Plotly (evolució i drawdowns)
│   ├── xray_views.py          # Gràfics de països, sectors i top accions
│   ├── comparison_view.py     # Comparativa multi-cartera i taula cara a cara
│   └── portfolio_builder.py   # Formulari de creació i edició de carteres
├── storage/
│   └── portfolio_storage.py   # Persistència de carteres en format JSON
└── saved_portfolios/          # Fitxers JSON amb les carteres creades
```
