"""
Motor de descàrrega i gestió de dades financeres amb yfinance i cache local en Parquet.
"""

import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import yfinance as yf
from config import CACHE_DIR, TICKER_ALIASES


class DataFetcher:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def _normalize_ticker(self, ticker: str) -> str:
        """Aplica àlies coneguts per corregir símbols canviats o delistats a Yahoo."""
        t = ticker.strip().upper()
        return TICKER_ALIASES.get(t, t)

    def _get_cache_file(self, ticker: str) -> Path:
        normalized = self._normalize_ticker(ticker)
        sanitized = normalized.replace("^", "IDX_").replace("/", "_").replace(".", "_")
        return self.cache_dir / f"{sanitized}.parquet"

    def fetch_ticker_series(
        self,
        ticker: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        max_cache_age_hours: int = 12
    ) -> pd.Series:
        """
        Obté la sèrie històrica de preus de tancament ajustats per a un ticker determinat.
        Utilitza cache local en format Parquet per evitar peticions innecessàries i bloquejos de xarxa.
        """
        raw_ticker = ticker.strip().upper()
        real_ticker = self._normalize_ticker(raw_ticker)
        cache_file = self._get_cache_file(real_ticker)
        cached_df = None

        if cache_file.exists():
            try:
                mod_time = datetime.datetime.fromtimestamp(cache_file.stat().st_mtime)
                age = (datetime.datetime.now() - mod_time).total_seconds() / 3600
                
                cached_df = pd.read_parquet(cache_file)
                if not cached_df.empty:
                    first_cached_date = cached_df.index[0].date()
                    need_older_data = start_date is not None and start_date < first_cached_date
                    # Si el cache és recent i cobreix la data d'inici
                    if age < max_cache_age_hours and not need_older_data:
                        series = cached_df["Close"]
                        if start_date:
                            series = series[series.index.date >= start_date]
                        if end_date:
                            series = series[series.index.date <= end_date]
                        series.name = raw_ticker
                        return series
            except Exception:
                cached_df = None

        # Si no tenim cache vàlid, descarreguem via yfinance
        try:
            download_start = "1990-01-01" if start_date is None else start_date.strftime("%Y-%m-%d")
            raw_data = yf.download(real_ticker, start=download_start, progress=False, auto_adjust=True)
            
            if raw_data.empty:
                if cached_df is not None and not cached_df.empty:
                    series = cached_df["Close"]
                    series.name = raw_ticker
                    return series
                return pd.Series(dtype=float, name=raw_ticker)

            # Processar columnes
            if isinstance(raw_data.columns, pd.MultiIndex):
                if "Close" in raw_data.columns.levels[0]:
                    close_df = raw_data["Close"]
                    if isinstance(close_df, pd.DataFrame):
                        close_series = close_df.iloc[:, 0]
                    else:
                        close_series = close_df
                else:
                    close_series = raw_data.iloc[:, 0]
            else:
                close_series = raw_data["Close"] if "Close" in raw_data else raw_data.iloc[:, 0]

            # Netejar index de dates
            close_series = close_series.dropna()
            close_series.index = pd.to_datetime(close_series.index).tz_localize(None)

            # Desar al cache Parquet
            save_df = pd.DataFrame({"Close": close_series})
            save_df.to_parquet(cache_file)

            if start_date:
                close_series = close_series[close_series.index.date >= start_date]
            if end_date:
                close_series = close_series[close_series.index.date <= end_date]

            close_series.name = raw_ticker
            return close_series

        except Exception as e:
            if cached_df is not None and not cached_df.empty:
                series = cached_df["Close"]
                series.name = raw_ticker
                return series
            raise RuntimeError(f"Error en obtenir dades per al ticker '{raw_ticker}': {str(e)}")

    def fetch_multiple_tickers(
        self,
        tickers: List[str],
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Descarrega i alinea les sèries històriques de múltiples actius.
        Alinea els calendaris festius de diferents borses amb ffill() i troba
        la data comuna d'inici exacta.
        """
        series_dict = {}
        warnings = []
        earliest_dates = {}

        unique_tickers = list(dict.fromkeys(tickers))

        for ticker in unique_tickers:
            try:
                s = self.fetch_ticker_series(ticker, start_date=start_date, end_date=end_date)
                if s.empty:
                    warnings.append(f"No s'han trobat dades per a l'actiu '{ticker}'.")
                else:
                    series_dict[ticker] = s
                    earliest_dates[ticker] = s.index[0].date()
            except Exception as e:
                warnings.append(f"No s'han pogut carregar les dades de '{ticker}': {str(e)}")

        if not series_dict:
            return pd.DataFrame(), warnings

        # Crear DataFrame combinat amb l'índex de dates conjunt
        combined_df = pd.DataFrame(series_dict)
        combined_df = combined_df.sort_index()

        # Omplir festius de borses diferents (per exemple EUA obert i Europa tancada)
        combined_df = combined_df.ffill()

        # Trobar la data comuna a partir de la qual TOTS els actius tenen cotització
        first_valid_indices = {}
        for col in combined_df.columns:
            fvi = combined_df[col].first_valid_index()
            if fvi is not None:
                first_valid_indices[col] = fvi

        if not first_valid_indices:
            return pd.DataFrame(), warnings

        common_start_dt = max(first_valid_indices.values())
        clean_df = combined_df.loc[common_start_dt:].dropna()

        # Comprovar si algun ticker limita el rang temporal demanat
        if start_date and common_start_dt.date() > start_date:
            limiting_ticker = max(first_valid_indices, key=lambda k: first_valid_indices[k])
            warnings.append(
                f"ℹ️ L'actiu '{limiting_ticker}' només té dades a partir de {common_start_dt.strftime('%d/%m/%Y')}. "
                f"El període de la simulació s'ha ajustat automàticament a aquesta data per mantenir la coherència."
            )

        return clean_df, warnings

    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """Obté informació bàsica d'un actiu."""
        ticker = ticker.strip().upper()
        real_ticker = self._normalize_ticker(ticker)
        try:
            yf_ticker = yf.Ticker(real_ticker)
            info = yf_ticker.info or {}
            return {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName") or ticker,
                "currency": info.get("currency", "EUR"),
                "quote_type": info.get("quoteType", "ETF"),
                "category": info.get("category", ""),
            }
        except Exception:
            return {
                "ticker": ticker,
                "name": ticker,
                "currency": "EUR",
                "quote_type": "ETF",
                "category": "",
            }
