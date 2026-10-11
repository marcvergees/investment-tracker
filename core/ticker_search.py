"""
Cercador i Validador d'Actius Financers via Yahoo Finance API.
Permet cercar per nom d'empresa o ticker, obtenir suggeriments en desplegables
i previsualitzar les dades oficials abans d'afegir un actiu a la cartera.
"""

from typing import List, Dict, Any, Optional
import requests
import datetime
import yfinance as yf
from config import TICKER_ALIASES, POPULAR_ASSETS


SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def search_yahoo_tickers(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Cerca tickers a Yahoo Finance a partir d'un text (nom o codi).
    Retorna una llista de candidats amb símbol, nom, borsa i tipus d'actiu.
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    results = []
    seen_symbols = set()

    # 1. Comprovar si tenim un àlies configurat per a aquesta cerca exacta
    upper_query = clean_query.upper()
    if upper_query in TICKER_ALIASES:
        aliased = TICKER_ALIASES[upper_query]
        results.append({
            "symbol": aliased,
            "name": f"{upper_query} (Àlies automàtic a {aliased})",
            "type": "ETF",
            "exchange": "Recomanat",
        })
        seen_symbols.add(aliased)

    # 2. Comprovar als actius populars locals
    for a in POPULAR_ASSETS:
        t = a["ticker"]
        n = a["name"]
        if upper_query in t or clean_query.lower() in n.lower():
            if t not in seen_symbols:
                results.append({
                    "symbol": t,
                    "name": n,
                    "type": a.get("asset_class", "Actiu"),
                    "exchange": a.get("category", "Popular"),
                })
                seen_symbols.add(t)

    # 3. Consultar l'API de cerca de Yahoo Finance
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={clean_query}&quotesCount={limit}&newsCount=0"
    try:
        resp = requests.get(url, headers=SEARCH_HEADERS, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            quotes = data.get("quotes", [])
            for q in quotes:
                sym = q.get("symbol")
                if not sym or sym in seen_symbols:
                    continue

                name = q.get("shortname") or q.get("longname") or sym
                q_type = q.get("quoteType", "Actiu")
                exch = q.get("exchange", "")

                results.append({
                    "symbol": sym,
                    "name": name,
                    "type": q_type,
                    "exchange": exch,
                })
                seen_symbols.add(sym)
                if len(results) >= limit:
                    break
    except Exception:
        pass

    return results


def get_ticker_preview(symbol: str) -> Dict[str, Any]:
    """
    Obté informació detallada i valida si el ticker té dades reals a Yahoo Finance.
    Retorna informació sobre l'actiu, preu actual i antiguitat de les dades.
    """
    sym = symbol.strip().upper()
    real_sym = TICKER_ALIASES.get(sym, sym)

    try:
        yf_ticker = yf.Ticker(real_sym)
        # Obtenir històric recent per comprovar que és actiu
        df = yf_ticker.history(period="1mo")
        if df.empty:
            return {
                "is_valid": False,
                "symbol": real_sym,
                "error": f"No s'han trobat cotitzacions recents per al símbol '{real_sym}' a Yahoo Finance.",
            }

        last_price = float(df["Close"].iloc[-1])
        info = yf_ticker.info or {}

        name = info.get("longName") or info.get("shortName") or real_sym
        currency = info.get("currency", "EUR")
        quote_type = info.get("quoteType", "ETF")
        exchange = info.get("exchange", "Borsa")

        # Obtenir data més antiga
        max_df = yf_ticker.history(period="max")
        first_date = max_df.index[0].date() if not max_df.empty else None
        num_sessions = len(max_df)
        years_available = round((datetime.date.today() - first_date).days / 365.25, 1) if first_date else 0.0

        return {
            "is_valid": True,
            "symbol": real_sym,
            "name": name,
            "currency": currency,
            "quote_type": quote_type,
            "exchange": exchange,
            "last_price": last_price,
            "first_date": first_date.strftime("%d/%m/%Y") if first_date else "Desconeguda",
            "years_history": years_available,
            "num_sessions": num_sessions,
        }

    except Exception as e:
        return {
            "is_valid": False,
            "symbol": real_sym,
            "error": str(e),
        }
