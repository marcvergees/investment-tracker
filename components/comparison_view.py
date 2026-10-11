"""
Component de comparació interactiva multi-cartera (propostes de bancs vs benchmarks).
"""

from typing import List, Optional, Dict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.backtest_engine import BacktestResult
from core.xray_engine import XRayEngine
from core.portfolio import Portfolio


def plot_comparison_equity_curve(
    results: List[BacktestResult],
    benchmark_results: Optional[List[BacktestResult]] = None,
    benchmark_result: Optional[BacktestResult] = None,
    log_scale: bool = False,
) -> go.Figure:
    """
    Gràfic multillínia amb l'evolució paral·lela de totes les carteres seleccionades i múltiples benchmarks.
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, res in enumerate(results):
        color = colors[idx % len(colors)]
        equity = res.equity_series
        fig.add_trace(
            go.Scatter(
                x=equity.index,
                y=equity.values,
                mode="lines",
                name=res.portfolio_name,
                line=dict(color=color, width=2.8),
                hovertemplate=f"<b>%{{x|%d %b %Y}}</b><br>{res.portfolio_name}: %{{y:,.2f}} €<extra></extra>",
            )
        )

    # Consolidar llista de benchmarks
    bench_list = []
    if benchmark_results:
        bench_list.extend(benchmark_results)
    elif benchmark_result is not None:
        bench_list.append(benchmark_result)

    bench_styles = [
        {"color": "#475569", "dash": "dot"},
        {"color": "#9333ea", "dash": "dashdot"},
        {"color": "#ea580c", "dash": "dash"},
        {"color": "#0d9488", "dash": "longdash"},
    ]

    base_cap = results[0].initial_capital if results else 10000.0

    for b_idx, b_res in enumerate(bench_list):
        if b_res is not None and not b_res.equity_series.empty:
            bench_equity = b_res.equity_series
            scaled_bench = (bench_equity / bench_equity.iloc[0]) * base_cap
            style = bench_styles[b_idx % len(bench_styles)]
            fig.add_trace(
                go.Scatter(
                    x=scaled_bench.index,
                    y=scaled_bench.values,
                    mode="lines",
                    name=f"Benchmark ({b_res.portfolio_name})",
                    line=dict(color=style["color"], width=2.2, dash=style["dash"]),
                    hovertemplate=f"<b>%{{x|%d %b %Y}}</b><br>{b_res.portfolio_name}: %{{y:,.2f}} €<extra></extra>",
                )
            )

    y_type = "log" if log_scale else "linear"
    fig.update_layout(
        title=dict(
            text="<b>Comparativa d'Evolució del Capital (€)</b>",
            font=dict(size=18),
        ),
        xaxis=dict(title="Data", showgrid=True),
        yaxis=dict(
            title="Capital Acumulat (€)",
            type=y_type,
            tickformat=",.0f",
            ticksuffix=" €",
            showgrid=True,
            gridcolor="rgba(230, 230, 230, 0.5)",
        ),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        height=520,
    )
    return fig


def build_comparison_metrics_table(
    results: List[BacktestResult],
    benchmark_results: Optional[List[BacktestResult]] = None,
    benchmark_result: Optional[BacktestResult] = None,
) -> pd.DataFrame:
    """
    Construeix la taula comparativa cara a cara de mètriques financeres (carteres i benchmarks).
    """
    all_results = list(results)
    if benchmark_results:
        all_results.extend(benchmark_results)
    elif benchmark_result is not None:
        all_results.append(benchmark_result)

    rows = []
    for res in all_results:
        m = res.metrics
        rows.append({
            "Cartera / Proposta": res.portfolio_name,
            "Capital Inicial": f"{m.get('initial_capital', 0):,.0f} €",
            "Capital Final": f"{m.get('final_capital', 0):,.0f} €",
            "Retorn Total": f"{m.get('total_return_pct', 0):+.2f}%",
            "CAGR (Anual)": f"{m.get('cagr_pct', 0):+.2f}%",
            "Volatilitat": f"{m.get('volatility_pct', 0):.2f}%",
            "Ràtio Sharpe": f"{m.get('sharpe_ratio', 0):.2f}",
            "Ràtio Sortino": f"{m.get('sortino_ratio', 0):.2f}",
            "Max Drawdown": f"{m.get('max_drawdown_pct', 0):.2f}%",
            "Millor Any": f"{m.get('best_year_pct', 0):+.2f}%",
            "Pitjor Any": f"{m.get('worst_year_pct', 0):+.2f}%",
        })

    return pd.DataFrame(rows)


def plot_comparison_annual_returns(results: List[BacktestResult]) -> go.Figure:
    """
    Gràfic de barres agrupades comparant els retorns any per any de les carteres.
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, res in enumerate(results):
        df = res.annual_returns
        if df.empty:
            continue
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(
                x=df["Any"].astype(str),
                y=df["Retorn (%)"],
                name=res.portfolio_name,
                marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{res.portfolio_name}: %{{y:+.2f}}%<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        title=dict(text="<b>Rendibilitat Anual Comparativa (%)</b>", font=dict(size=16)),
        xaxis=dict(title="Any", type="category"),
        yaxis=dict(title="Rendibilitat (%)", ticksuffix="%", showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        height=380,
    )
    return fig


def plot_comparison_sector_exposure(portfolios: List[Portfolio]) -> go.Figure:
    """
    Gràfic comparatiu de l'exposició sectorial entre les diferents carteres seleccionades.
    """
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    # Recopilar tots els sectors únics
    all_sectors = set()
    xray_data = []

    for p in portfolios:
        xray = XRayEngine.calculate_portfolio_xray(p)
        xray_data.append((p.name, xray.get("sectors", {})))
        all_sectors.update(xray.get("sectors", {}).keys())

    # Seleccionar els 8 sectors principals més representatius
    sorted_sectors = sorted(list(all_sectors))[:10]

    for idx, (p_name, sec_dict) in enumerate(xray_data):
        y_vals = [sec_dict.get(s, 0.0) for s in sorted_sectors]
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(
                x=sorted_sectors,
                y=y_vals,
                name=p_name,
                marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{p_name}: %{{y:.1f}}%<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        title=dict(text="<b>Comparativa d'Exposició Sectorial (%)</b>", font=dict(size=16)),
        xaxis=dict(title="Sector", tickangle=-30),
        yaxis=dict(title="Pes a la Cartera (%)", ticksuffix="%", showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=60),
        template="plotly_white",
        height=400,
    )
    return fig
