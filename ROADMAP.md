# 🗺️ Full de Ruta (Roadmap)

Aquest document recull les funcionalitats previstes i objectius de futur per a **ETF Portfolio Tracker & Backtester**.

---

## 🚀 Properes Versions

### 🎲 Simulació de Monte Carlo (v1.3.0)
- [ ] Generació de 1.000 camins estocàstics basats en la mitjana i variància històrica de la cartera.
- [ ] Conus de probabilitat (percentils 10è, 25è, 50è, 75è i 90è) per a projeccions futures de capital a 10, 20 i 30 anys.
- [ ] Càlcul de probabilitat d'èxit de jubilació (Taxa de Retirada Segura / *Safe Withdrawal Rate 4%*).

### 💶 Optimització Fiscal i Aportacions Periòdiques (v1.4.0)
- [ ] **Aportacions periòdiques (DCA / Dollar-Cost Averaging)**: Possibilitat d'afegir 100 €, 300 € o 500 € mensuals a la simulació.
- [ ] **Model fiscal espanyol/europeu**:
  - Traspàs entre fons d'inversió sense peatge fiscal.
  - Simulació d'impost sobre guanys de capital (19% - 28%) en rebalançament d'ETFs vs fons indexats.

### 📊 Reinversió de Dividends i Renda Fixa (v1.5.0)
- [ ] Desglossament entre rendibilitat per preu (*Price Return*) i rendibilitat per dividends (*Total Return / Gross Return*).
- [ ] Anàlisi de yield de dividend estimat de la cartera.
- [ ] Distinció de durada i corba de tipus d'interès per a fons de renda fixa.

### 🌐 Ampliació de la Versió Web (v1.6.0)
- [ ] Connector amb API en temps real mitjançant servidors proxy lliures de CORS o WebAssembly Pyodide.
- [ ] Suport per a múltiples idiomes (Català, Castellà, Anglès).
- [ ] Mode clar / mode fosc alternable.

---

Si tens suggeriments o vols liderar alguna d'aquestes iniciatives, si us plau obre un issue a GitHub o consulta la nostra guia a [CONTRIBUTING.md](CONTRIBUTING.md)!
