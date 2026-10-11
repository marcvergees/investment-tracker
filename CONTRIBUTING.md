# 🤝 Guia de Contribució a ETF Portfolio Tracker

Gràcies pel teu interès a col·laborar en **ETF Portfolio Tracker & Backtester**! Aquest projecte és 100% de codi obert (*Open Source*) i qualsevol aportació —des de millores al motor financer, addició de nous perfils d'ETFs, correcció d'errors o traduccions— és molt benvinguda.

---

## 🧭 Com començar

### 1. Clonar el repositori
```bash
git clone https://github.com/teu-usuari/etf-tracker.git
cd etf-tracker
```

### 2. Entorn de desenvolupament (Versió Python / Streamlit)
```bash
# Crear entorn virtual
python3 -m venv venv
source venv/bin/activate

# Instal·lar dependències
pip install -r requirements.txt

# Executar l'aplicació Streamlit
streamlit run app.py
```

### 3. Entorn de desenvolupament (Versió Web / GitHub Pages)
La versió estàtica web no requereix cap backend ni compilador especial:
```bash
# Pots obrir index.html directament al teu navegador o servir-lo amb qualsevol servidor estàtic:
python3 -m http.server 8000
```
Visita `http://localhost:8000` al teu navegador.

Si s'afegeixen nous tickers o es canvien els fitxers de cache `.parquet`, regenera les dades estàtiques amb:
```bash
python scripts/export_static_data.py
```

---

## 🛠️ Com contribuir

### Reportar errors (Bugs)
Si trobes un problema o discrepància en les dades:
1. Revisa la pestanya d'**Issues** per comprovar que no estigui ja reportat.
2. Obre un nou issue utilitzant la plantilla de *Bug Report* descrivint:
   - Passos per reproduir l'error.
   - Ticker o cartera afectada.
   - Resultat esperat vs resultat obtingut.
   - Captures de pantalla o traces de la terminal si s'escau.

### Proposar noves funcionalitats
Tenim un [ROADMAP.md](ROADMAP.md) actiu. Si vols proposar una nova mètrica financera, integració amb nous proveïdors o millores visuals, si us plau obre un issue de tipus *Feature Request* per discutir-ho abans d'implementar-ho.

### Enviar un Pull Request (PR)
1. Fes un fork del repositori.
2. Crea una branca per a la teva funcionalitat:
   ```bash
   git checkout -b feature/nova-funcionalitat
   ```
3. Fes els teus canvis i assegura't que els tests passin:
   ```bash
   python test_app.py
   ```
4. Fes commit seguint missatges clars i concisos (recomanat estil *Conventional Commits*):
   ```bash
   git commit -m "feat: afegir càlcul de ràtio Calmar al motor de mètriques"
   ```
5. Envia la branca al teu fork i obre un Pull Request cap a `main` utilitzant la plantilla proporcionada.

---

## 🧪 Tests i Qualitat del Codi

- Executa els tests unitaris:
  ```bash
  python test_app.py
  ```
- Assegura't que els fitxers no continguin errors de sintaxi:
  ```bash
  python -m py_compile app.py core/*.py components/*.py storage/*.py
  ```

---

## 📜 Codi de Conducta

Si us plau, tingues en compte que aquest projecte segueix el nostre [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Ens comprometem a mantenir un entorn respectuós i inclusiu per a tothom.

Gràcies per ajudar a fer créixer la comunitat d'inversió independent i de codi obert! 🚀
