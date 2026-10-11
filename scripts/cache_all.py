"""
Script per precarregar el cache històric de tots els actius populars i de les carteres d'exemple.
"""

import sys
import datetime
from pathlib import Path

# Afegir arrel al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import POPULAR_ASSETS, BENCHMARK_OPTIONS
from storage.portfolio_storage import PortfolioStorage
from core.data_fetcher import DataFetcher

def precache_all():
    fetcher = DataFetcher()
    storage = PortfolioStorage()

    tickers_to_fetch = set()

    # Tickers de benchmarks
    for b_ticker in BENCHMARK_OPTIONS.values():
        tickers_to_fetch.add(b_ticker)

    # Tickers d'actius populars
    for a in POPULAR_ASSETS:
        tickers_to_fetch.add(a["ticker"])

    # Tickers de les carteres desades
    for p in storage.list_portfolios():
        for t in p.allocations.keys():
            tickers_to_fetch.add(t)

    print(f"Descarregant dades històriques per a {len(tickers_to_fetch)} actius...")
    start_date = datetime.date(2000, 1, 1)

    for ticker in sorted(tickers_to_fetch):
        print(f"-> Descarregant {ticker}...")
        try:
            s = fetcher.fetch_ticker_series(ticker, start_date=start_date)
            if s.empty:
                print(f"   ⚠️ Sense dades per a {ticker}")
            else:
                print(f"   ✅ {ticker}: {len(s)} sessions ({s.index[0].strftime('%Y-%m-%d')} a {s.index[-1].strftime('%Y-%m-%d')})")
        except Exception as e:
            print(f"   ❌ Error a {ticker}: {e}")

    print("Precarregat finalitzat!")

if __name__ == "__main__":
    precache_all()
