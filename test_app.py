"""
Script de proves automatitzades per validar tots els components del projecte.
"""

import sys
import datetime
from core.portfolio import Portfolio
from core.metrics import calculate_cagr, calculate_max_drawdown, summarize_portfolio_metrics
from core.data_fetcher import DataFetcher
from core.backtest_engine import BacktestEngine
from core.xray_engine import XRayEngine
from storage.portfolio_storage import PortfolioStorage
import pandas as pd


def test_portfolio_model():
    print("Testing Portfolio model...")
    p = Portfolio("Test", {"SPY": 60.0, "QQQ": 40.0}, initial_capital=10000.0)
    assert p.is_valid
    norm = p.normalized_weights()
    assert abs(norm["SPY"] - 0.6) < 1e-5
    assert abs(norm["QQQ"] - 0.4) < 1e-5
    print("  -> Portfolio model OK")


def test_storage():
    print("Testing Storage...")
    storage = PortfolioStorage()
    portfolios = storage.list_portfolios()
    assert len(portfolios) >= 4, f"Expected at least 4 sample portfolios, got {len(portfolios)}"
    p0 = storage.load_portfolio(portfolios[0].name)
    assert p0 is not None
    print(f"  -> Storage OK ({len(portfolios)} carteres trobades)")


def test_xray():
    print("Testing X-Ray engine...")
    p = Portfolio("Global Test", {"IWDA.AS": 70.0, "QQQ": 30.0})
    xray = XRayEngine.calculate_portfolio_xray(p)
    assert "countries" in xray
    assert "sectors" in xray
    assert "top_holdings" in xray
    assert len(xray["countries"]) > 0
    assert len(xray["sectors"]) > 0
    assert len(xray["top_holdings"]) > 0
    print("  -> X-Ray Top countries:", list(xray["countries"].items())[:3])
    print("  -> X-Ray Top sectors:", list(xray["sectors"].items())[:3])
    print("  -> X-Ray Top holdings:", list(xray["top_holdings"].items())[:3])
    print("  -> X-Ray OK")


def test_metrics():
    print("Testing Metrics...")
    # Sèrie de prova de 3 anys creixent de 10.000 a 13.310 (+10% CAGR)
    dates = pd.date_range("2020-01-01", "2023-01-01", freq="B")
    values = [10000.0 * (1.10 ** (i / 252)) for i in range(len(dates))]
    s = pd.Series(values, index=dates)
    m = summarize_portfolio_metrics(s, 10000.0)
    assert m["total_return_pct"] > 0
    assert abs(m["cagr_pct"] - 10.0) < 1.0
    print(f"  -> Metrics OK (CAGR: {m['cagr_pct']}%, Sharpe: {m['sharpe_ratio']})")


def test_backtest_with_mock():
    print("Testing BacktestEngine with mock data...")
    dates = pd.date_range("2020-01-01", "2023-01-01", freq="B")
    mock_df = pd.DataFrame({
        "SPY": [100.0 * (1 + 0.0005 * i) for i in range(len(dates))],
        "QQQ": [200.0 * (1 + 0.0008 * i) for i in range(len(dates))],
    }, index=dates)

    p = Portfolio("Mock 60/40", {"SPY": 60.0, "QQQ": 40.0}, initial_capital=10000.0, rebalance_freq="yearly")
    res = BacktestEngine.run_backtest(p, mock_df)
    assert not res.equity_series.empty
    assert res.equity_series.iloc[0] == 10000.0
    assert res.metrics["final_capital"] > 10000.0
    print(f"  -> Backtest OK (Capital final mock: {res.metrics['final_capital']} €)")


if __name__ == "__main__":
    test_portfolio_model()
    test_storage()
    test_xray()
    test_metrics()
    test_backtest_with_mock()
    print("\n✅ TOTES LES PROVES HAN PASSAT AMB ÈXIT!")
