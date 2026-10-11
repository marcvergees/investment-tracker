"""
Motor de Backtesting per a la simulació de carteres d'inversió.
Suporta estratègies Buy & Hold i Rebalançament periòdic (anual, trimestral, mensual).
"""

from typing import Dict, Any, Optional
import pandas as pd
from core.portfolio import Portfolio
from core.metrics import (
    summarize_portfolio_metrics,
    calculate_drawdown_series,
    calculate_annual_returns,
)


class BacktestResult:
    def __init__(
        self,
        portfolio_name: str,
        equity_series: pd.Series,
        individual_assets_series: Dict[str, pd.Series],
        initial_capital: float,
        metrics: Dict[str, Any],
        annual_returns: pd.DataFrame,
        drawdowns: pd.Series,
    ):
        self.portfolio_name = portfolio_name
        self.equity_series = equity_series
        self.individual_assets_series = individual_assets_series
        self.initial_capital = initial_capital
        self.metrics = metrics
        self.annual_returns = annual_returns
        self.drawdowns = drawdowns


class BacktestEngine:
    @staticmethod
    def run_backtest(
        portfolio: Portfolio,
        prices_df: pd.DataFrame,
        risk_free_rate: float = 0.025
    ) -> BacktestResult:
        """
        Executa la simulació històrica de la cartera donat un DataFrame de preus històrics.
        """
        if prices_df.empty:
            empty_s = pd.Series(dtype=float)
            return BacktestResult(
                portfolio_name=portfolio.name,
                equity_series=empty_s,
                individual_assets_series={},
                initial_capital=portfolio.initial_capital,
                metrics=summarize_portfolio_metrics(empty_s, portfolio.initial_capital),
                annual_returns=pd.DataFrame(),
                drawdowns=empty_s,
            )

        weights = portfolio.normalized_weights()
        # Assegurar que només usem els tickers presents a prices_df
        active_tickers = [t for t in weights.keys() if t in prices_df.columns]
        
        if not active_tickers:
            raise ValueError("Cap dels actius de la cartera està present en les dades de preus.")

        # Re-normalitzar pesos si cal
        tot_active_w = sum(weights[t] for t in active_tickers)
        norm_w = {t: weights[t] / tot_active_w for t in active_tickers}

        initial_capital = portfolio.initial_capital
        rebal_freq = portfolio.rebalance_freq.lower()

        dates = prices_df.index
        n_dates = len(dates)

        portfolio_values = []
        individual_series: Dict[str, list] = {t: [] for t in active_tickers}

        if rebal_freq == "none":
            # Buy & Hold pur: es compren participacions el dia 0 i no es toca mai
            first_prices = prices_df.iloc[0]
            shares = {t: (initial_capital * norm_w[t]) / first_prices[t] for t in active_tickers}

            for idx in range(n_dates):
                row_prices = prices_df.iloc[idx]
                day_val = 0.0
                for t in active_tickers:
                    asset_val = shares[t] * row_prices[t]
                    individual_series[t].append(asset_val)
                    day_val += asset_val
                portfolio_values.append(day_val)

        else:
            # Rebalançament periòdic: anual, trimestral o mensual
            first_prices = prices_df.iloc[0]
            current_capital = initial_capital
            shares = {t: (current_capital * norm_w[t]) / first_prices[t] for t in active_tickers}

            last_period = None

            for idx in range(n_dates):
                current_date = dates[idx]
                row_prices = prices_df.iloc[idx]

                # Determinar el període segons la freqüència de rebalançament
                if rebal_freq == "monthly":
                    current_period = (current_date.year, current_date.month)
                elif rebal_freq == "quarterly":
                    quarter = (current_date.month - 1) // 3 + 1
                    current_period = (current_date.year, quarter)
                else:
                    # Per defecte anual
                    current_period = current_date.year

                # Càlcul del valor actual de cada actiu
                day_val = 0.0
                for t in active_tickers:
                    asset_val = shares[t] * row_prices[t]
                    individual_series[t].append(asset_val)
                    day_val += asset_val

                # Si entrem en un nou període (i no és el primer dia), es rebalança
                if last_period is not None and current_period != last_period:
                    current_capital = day_val
                    shares = {t: (current_capital * norm_w[t]) / row_prices[t] for t in active_tickers}

                last_period = current_period
                portfolio_values.append(day_val)

        equity_series = pd.Series(portfolio_values, index=dates, name=portfolio.name)
        ind_assets = {t: pd.Series(vals, index=dates, name=t) for t, vals in individual_series.items()}

        drawdowns = calculate_drawdown_series(equity_series)
        annual_returns = calculate_annual_returns(equity_series)
        metrics = summarize_portfolio_metrics(
            equity_series,
            initial_capital=initial_capital,
            risk_free_rate=risk_free_rate
        )

        return BacktestResult(
            portfolio_name=portfolio.name,
            equity_series=equity_series,
            individual_assets_series=ind_assets,
            initial_capital=initial_capital,
            metrics=metrics,
            annual_returns=annual_returns,
            drawdowns=drawdowns,
        )

    @staticmethod
    def run_benchmark(
        benchmark_ticker: str,
        prices_df: pd.DataFrame,
        initial_capital: float = 10000.0,
        risk_free_rate: float = 0.025
    ) -> Optional[BacktestResult]:
        """
        Executa una simulació d'un sol actiu de referència (benchmark).
        """
        if benchmark_ticker not in prices_df.columns:
            return None

        p = Portfolio(
            name=f"Benchmark ({benchmark_ticker})",
            allocations={benchmark_ticker: 100.0},
            initial_capital=initial_capital,
            rebalance_freq="none",
        )
        return BacktestEngine.run_backtest(p, prices_df, risk_free_rate=risk_free_rate)
