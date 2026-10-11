"""
Configuració global per a l'aplicació ETF & Portfolio Tracker.
"""

from pathlib import Path

# Rutes del sistema
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
PORTFOLIOS_DIR = BASE_DIR / "saved_portfolios"

# Crear carpetes si no existeixen
CACHE_DIR.mkdir(exist_ok=True)
PORTFOLIOS_DIR.mkdir(exist_ok=True)

# Paràmetres per defecte
DEFAULT_INITIAL_CAPITAL = 10000.0  # 10.000 €
DEFAULT_CURRENCY = "EUR"
RISK_FREE_RATE_ANNUAL = 0.025  # 2.5% Taxa lliure de risc

# Opcions d'horitzó temporal
TIME_HORIZONS = {
    "3 Anys": 3,
    "5 Anys": 5,
    "10 Anys": 10,
    "15 Anys": 15,
    "20 Anys": 20,
    "Màxim Històric Disponible": 99,
}

# Àlies de tickers per corregir automàticament codis habituals de Yahoo Finance
TICKER_ALIASES = {
    "IS3N": "IS3N.DE",      # iShares Core MSCI EM IMI a Xetra
    "IUSN": "IUSN.DE",      # iShares MSCI World Small Cap a Xetra
    "EUNK": "EUNK.DE",      # iShares Core MSCI Europe a Xetra
    "BTC": "BTC-EUR",       # Bitcoin en Euros (Yahoo Finance té un ETF BTC del 2024 amb el ticker simple BTC)
    "BITCOIN": "BTC-EUR",
    "EIMI.AS": "EMIM.AS",   # iShares Emerging Markets a Euronext Amsterdam
    "EIMI.L": "EMIM.AS",
    "EQAC.DE": "EXXT.DE",   # iShares Nasdaq 100 a Xetra
    "MEUD.PA": "EXSA.DE",   # STOXX Europe 600 amb llarg històric des de 2008
}

# Llista d'actius i ETFs populars predefinits amb ampli històric
POPULAR_ASSETS = [
    # Renda Variable Global
    {"ticker": "IWDA.AS", "name": "iShares Core MSCI World (Acc, EUR)", "category": "Renda Variable Global", "asset_class": "Equity"},
    {"ticker": "VWCE.DE", "name": "Vanguard FTSE All-World (Acc, EUR)", "category": "Renda Variable Global", "asset_class": "Equity"},
    {"ticker": "IUSN.DE", "name": "iShares MSCI World Small Cap (EUR)", "category": "Renda Variable Small Cap", "asset_class": "Equity"},
    {"ticker": "URTH", "name": "iShares MSCI World ETF (USD)", "category": "Renda Variable Global", "asset_class": "Equity"},
    
    # Renda Variable EUA (S&P 500 / Nasdaq)
    {"ticker": "CSPX.AS", "name": "iShares Core S&P 500 (Acc, EUR)", "category": "EUA - S&P 500", "asset_class": "Equity"},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust (USD)", "category": "EUA - S&P 500", "asset_class": "Equity"},
    {"ticker": "QQQ", "name": "Invesco QQQ - Nasdaq 100 (USD)", "category": "EUA - Tecnologia", "asset_class": "Equity"},
    {"ticker": "EXXT.DE", "name": "iShares Nasdaq 100 UCITS (EUR)", "category": "EUA - Tecnologia", "asset_class": "Equity"},
    
    # Renda Variable Europa
    {"ticker": "EUNK.DE", "name": "iShares Core MSCI Europe (Acc, EUR)", "category": "Europa", "asset_class": "Equity"},
    {"ticker": "EXSA.DE", "name": "iShares STOXX Europe 600 (EUR)", "category": "Europa", "asset_class": "Equity"},
    {"ticker": "VGK", "name": "Vanguard FTSE Europe ETF (USD)", "category": "Europa", "asset_class": "Equity"},
    
    # Mercats Emergents
    {"ticker": "IS3N.DE", "name": "iShares Core MSCI EM IMI (Acc, EUR)", "category": "Emergents", "asset_class": "Equity"},
    {"ticker": "EMIM.AS", "name": "iShares Core MSCI Emerging Markets (Acc, EUR)", "category": "Emergents", "asset_class": "Equity"},
    {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF (USD)", "category": "Emergents", "asset_class": "Equity"},
    
    # Criptoactius & Or
    {"ticker": "BTC-EUR", "name": "Bitcoin (EUR)", "category": "Criptoactius", "asset_class": "Crypto"},
    
    # Renda Fixa / Bons
    {"ticker": "EUNH.DE", "name": "iShares Euro Aggregate Bond (EUR)", "category": "Renda Fixa Euro (Històric des de 2009)", "asset_class": "Fixed Income"},
    {"ticker": "BND", "name": "Vanguard Total Bond Market ETF (USD)", "category": "Renda Fixa EUA (Històric des de 2007)", "asset_class": "Fixed Income"},
    {"ticker": "AGGH.AS", "name": "iShares Global Aggregate Bond (EUR Hedged)", "category": "Renda Fixa Global", "asset_class": "Fixed Income"},
    
    # Matèries Primeres & Or
    {"ticker": "GLD", "name": "SPDR Gold Shares (USD)", "category": "Matèries Primeres / Or", "asset_class": "Commodities"},
    {"ticker": "SGLD.L", "name": "Invesco Physical Gold ETC (EUR/USD)", "category": "Matèries Primeres / Or", "asset_class": "Commodities"},
    
    # Accions Globals Destacades
    {"ticker": "AAPL", "name": "Apple Inc.", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "ITX.MC", "name": "Inditex SA (Ibex 35, EUR)", "category": "Accions Individuals", "asset_class": "Equity"},
    {"ticker": "SAN.MC", "name": "Banco Santander SA (Ibex 35, EUR)", "category": "Accions Individuals", "asset_class": "Equity"},
]

# Benchmarks per defecte per a comparacions
BENCHMARK_OPTIONS = {
    "S&P 500 (SPY)": "SPY",
    "MSCI World (URTH)": "URTH",
    "MSCI World EUR (IWDA.AS)": "IWDA.AS",
    "Nasdaq 100 (QQQ)": "QQQ",
}
