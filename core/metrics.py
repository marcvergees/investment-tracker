"""
Mòdul de càlculs i mètriques financeres per al seguiment de carteres.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def calculate_total_return(start_val: float, end_val: float) -> float:
    """Calcula el retorn total percentual."""
    if start_val <= 0:
        return 0.0
    return ((end_val - start_val) / start_val) * 100.0


def calculate_cagr(start_val: float, end_val: float, num_years: float) -> float:
    """
    Calcula el CAGR (Compound Annual Growth Rate / Taxa de Creixement Anual Compost).
    CAGR = (End / Start) ** (1 / n) - 1
    """
    if start_val <= 0 or end_val <= 0 or num_years <= 0:
        return 0.0
    return (((end_val / start_val) ** (1.0 / num_years)) - 1.0) * 100.0


def calculate_volatility(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calcula la volatilitat anualitzada (desviació estàndard) en percentatge."""
    clean_returns = daily_returns.dropna()
    if len(clean_returns) < 2:
        return 0.0
    daily_std = clean_returns.std()
    return float(daily_std * np.sqrt(periods_per_year) * 100.0)


def calculate_sharpe_ratio(
    daily_returns: pd.Series,
    risk_free_rate: float = 0.025,
    periods_per_year: int = 252
) -> float:
    """
    Calcula el Ràtio de Sharpe anualitzat.
    Sharpe = (E[R] - Rf) / Volatilitat
    """
    clean_returns = daily_returns.dropna()
    if len(clean_returns) < 2:
        return 0.0
    
    mean_daily = clean_returns.mean()
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    daily_std = clean_returns.std()
    
    if daily_std == 0 or np.isnan(daily_std):
        return 0.0
    
    sharpe = (mean_daily - daily_rf) / daily_std * np.sqrt(periods_per_year)
    return float(sharpe)


def calculate_sortino_ratio(
    daily_returns: pd.Series,
    risk_free_rate: float = 0.025,
    periods_per_year: int = 252
) -> float:
    """
    Calcula el Ràtio de Sortino anualitzat (només penalitza la volatilitat negativa / downside deviation).
    """
    clean_returns = daily_returns.dropna()
    if len(clean_returns) < 2:
        return 0.0
    
    mean_daily = clean_returns.mean()
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    downside_returns = clean_returns[clean_returns < daily_rf] - daily_rf
    
    if len(downside_returns) == 0:
        return 0.0
    
    downside_std = np.sqrt(np.mean(downside_returns ** 2))
    if downside_std == 0 or np.isnan(downside_std):
        return 0.0
        
    sortino = (mean_daily - daily_rf) / downside_std * np.sqrt(periods_per_year)
    return float(sortino)


def calculate_drawdown_series(equity_series: pd.Series) -> pd.Series:
    """
    Calcula la sèrie de caigudes (Drawdown) des del màxim històric acumulat en percentatge.
    """
    running_max = equity_series.cummax()
    drawdowns = (equity_series - running_max) / running_max * 100.0
    return drawdowns


def calculate_max_drawdown(equity_series: pd.Series) -> Tuple[float, Any, Any]:
    """
    Calcula el màxim drawdown històric, la data del pic i la data del fons.
    Retorna (max_dd_percent, peak_date, trough_date).
    """
    if len(equity_series) == 0:
        return 0.0, None, None
        
    running_max = equity_series.cummax()
    drawdowns = (equity_series - running_max) / running_max * 100.0
    
    trough_date = drawdowns.idxmin()
    max_dd = float(drawdowns.min())
    
    # Trobar la data del pic anterior a la vall
    peak_series = equity_series.loc[:trough_date]
    peak_date = peak_series.idxmax() if len(peak_series) > 0 else equity_series.index[0]
    
    return max_dd, peak_date, trough_date


def calculate_annual_returns(equity_series: pd.Series) -> pd.DataFrame:
    """
    Calcula els retorns de cada any natural (any a any).
    Retorna un DataFrame amb columnes ['Any', 'Retorn (%)', 'Capital Final'].
    """
    if len(equity_series) < 2:
        return pd.DataFrame(columns=["Any", "Retorn (%)", "Capital Final (€)"])
    
    # Agrupar per any
    df = equity_series.to_frame(name="Value")
    df["Year"] = df.index.year
    
    annual_data = []
    years = sorted(df["Year"].unique())
    
    for i, y in enumerate(years):
        sub = df[df["Year"] == y]
        end_val = sub["Value"].iloc[-1]
        
        if i == 0:
            start_val = sub["Value"].iloc[0]
        else:
            prev_year_sub = df[df["Year"] == years[i - 1]]
            start_val = prev_year_sub["Value"].iloc[-1]
            
        ret_pct = ((end_val - start_val) / start_val) * 100.0
        annual_data.append({
            "Any": int(y),
            "Retorn (%)": round(ret_pct, 2),
            "Capital Final (€)": round(end_val, 2)
        })
        
    return pd.DataFrame(annual_data)


def summarize_portfolio_metrics(
    equity_series: pd.Series,
    initial_capital: float,
    risk_free_rate: float = 0.025
) -> Dict[str, Any]:
    """
    Calcula un resum complet de tots els indicadors clau (KPIs) per a una sèrie de capital.
    """
    if len(equity_series) < 2:
        return {
            "initial_capital": initial_capital,
            "final_capital": initial_capital,
            "total_return_pct": 0.0,
            "cagr_pct": 0.0,
            "volatility_pct": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown_pct": 0.0,
            "peak_date": None,
            "trough_date": None,
            "num_years": 0.0,
            "best_year_pct": 0.0,
            "worst_year_pct": 0.0,
        }
    
    final_capital = float(equity_series.iloc[-1])
    total_days = (equity_series.index[-1] - equity_series.index[0]).days
    num_years = max(total_days / 365.25, 0.01)
    
    daily_returns = equity_series.pct_change().dropna()
    total_ret = calculate_total_return(initial_capital, final_capital)
    cagr = calculate_cagr(initial_capital, final_capital, num_years)
    volatility = calculate_volatility(daily_returns)
    sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate=risk_free_rate)
    sortino = calculate_sortino_ratio(daily_returns, risk_free_rate=risk_free_rate)
    max_dd, peak_date, trough_date = calculate_max_drawdown(equity_series)
    
    annual_df = calculate_annual_returns(equity_series)
    best_year = float(annual_df["Retorn (%)"].max()) if not annual_df.empty else 0.0
    worst_year = float(annual_df["Retorn (%)"].min()) if not annual_df.empty else 0.0
    
    return {
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "total_return_pct": round(total_ret, 2),
        "cagr_pct": round(cagr, 2),
        "volatility_pct": round(volatility, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "peak_date": str(peak_date.date()) if peak_date is not None else None,
        "trough_date": str(trough_date.date()) if trough_date is not None else None,
        "num_years": round(num_years, 2),
        "best_year_pct": round(best_year, 2),
        "worst_year_pct": round(worst_year, 2),
    }
