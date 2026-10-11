"""
Gràfics financers interactius amb Plotly per a Streamlit.
"""

from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.backtest_engine import BacktestResult
from core.portfolio import Portfolio


def plot_equity_curve(
    result: BacktestResult,
    benchmark_results: Optional[List[BacktestResult]] = None,
    benchmark_result: Optional[BacktestResult] = None,
    log_scale: bool = False,
    show_individual_assets: bool = False,
) -> go.Figure:
    """
    Gràfic interactiu de l'evolució del capital en euros al llarg del temps.
    Permet comparar amb un o diversos benchmarks simultàniament (p. ex. S&P 500 i Nasdaq 100).
    """
    fig = go.Figure()

    # Línia principal de la cartera
    equity = result.equity_series
    fig.add_trace(
        go.Scatter(
            x=equity.index,
            y=equity.values,
            mode="lines",
            name=f"Cartera: {result.portfolio_name}",
            line=dict(color="#1f77b4", width=3),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Valor: %{y:,.2f} €<extra></extra>",
        )
    )

    # Consolidar llista de benchmarks
    bench_list = []
    if benchmark_results:
        bench_list.extend(benchmark_results)
    elif benchmark_result is not None:
        bench_list.append(benchmark_result)

    # Estils per als diferents benchmarks
    bench_styles = [
        {"color": "#475569", "dash": "dot"},      # Gris pissarra puntejat
        {"color": "#9333ea", "dash": "dashdot"},  # Púrpura linia-punt
        {"color": "#ea580c", "dash": "dash"},     # Taronja ratlles
        {"color": "#0d9488", "dash": "longdash"}, # Verd blavós
    ]

    for b_idx, b_res in enumerate(bench_list):
        if b_res is not None and not b_res.equity_series.empty:
            bench_equity = b_res.equity_series
            scaled_bench = (bench_equity / bench_equity.iloc[0]) * result.initial_capital
            style = bench_styles[b_idx % len(bench_styles)]
            fig.add_trace(
                go.Scatter(
                    x=scaled_bench.index,
                    y=scaled_bench.values,
                    mode="lines",
                    name=f"Benchmark: {b_res.portfolio_name}",
                    line=dict(color=style["color"], width=2.2, dash=style["dash"]),
                    hovertemplate=f"<b>%{{x|%d %b %Y}}</b><br>{b_res.portfolio_name}: %{{y:,.2f}} €<extra></extra>",
                )
            )

    # Actius individuals opcionals
    if show_individual_assets and result.individual_assets_series:
        colors = px.colors.qualitative.Plotly
        for idx, (ticker, s) in enumerate(result.individual_assets_series.items()):
            color = colors[(idx + 2) % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=s.index,
                    y=s.values,
                    mode="lines",
                    name=f"Actiu: {ticker}",
                    line=dict(color=color, width=1.2, dash="dash"),
                    hovertemplate=f"<b>%{{x|%d %b %Y}}</b><br>{ticker}: %{{y:,.2f}} €<extra></extra>",
                    opacity=0.6,
                )
            )

    # Línia de capital inicial de referència
    fig.add_hline(
        y=result.initial_capital,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.4)",
        annotation_text=f"Capital Inicial: {result.initial_capital:,.0f} €",
        annotation_position="bottom left",
    )

    y_type = "log" if log_scale else "linear"
    fig.update_layout(
        title=dict(
            text=f"<b>Evolució del Capital ({result.portfolio_name})</b>",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Data",
            showgrid=True,
            gridcolor="rgba(230, 230, 230, 0.5)",
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1A", step="year", stepmode="backward"),
                    dict(count=3, label="3A", step="year", stepmode="backward"),
                    dict(count=5, label="5A", step="year", stepmode="backward"),
                    dict(count=10, label="10A", step="year", stepmode="backward"),
                    dict(step="all", label="Tot"),
                ])
            ),
        ),
        yaxis=dict(
            title="Capital Acumulat (€)",
            type=y_type,
            tickformat=",.0f",
            ticksuffix=" €",
            showgrid=True,
            gridcolor="rgba(230, 230, 230, 0.5)",
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        height=500,
    )

    return fig


def plot_drawdown_curve(result: BacktestResult) -> go.Figure:
    """
    Gràfic de caigudes històriques (Underwater / Drawdown Chart).
    """
    dd = result.drawdowns
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dd.index,
            y=dd.values,
            mode="lines",
            name="Drawdown",
            line=dict(color="#d62728", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(214, 39, 40, 0.15)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Caiguda des de màxims: %{y:.2f}%<extra></extra>",
        )
    )

    # Indicador de caiguda màxima (Max Drawdown)
    max_dd = result.metrics.get("max_drawdown_pct", 0.0)
    trough_date = result.metrics.get("trough_date")
    if trough_date:
        fig.add_annotation(
            x=trough_date,
            y=max_dd,
            text=f"Max Drawdown: {max_dd:.1f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#d62728",
            arrowsize=1,
            arrowwidth=2,
            ax=0,
            ay=-40,
            bgcolor="#ffebee",
            bordercolor="#d62728",
        )

    fig.update_layout(
        title=dict(
            text="<b>Historial de Caigudes des de Màxims Històrics (Drawdown)</b>",
            font=dict(size=16),
        ),
        xaxis=dict(title="Data", showgrid=True),
        yaxis=dict(
            title="Caiguda (%)",
            ticksuffix="%",
            range=[min(dd.min() * 1.15, -5.0) if not dd.empty else -10, 2],
            showgrid=True,
            gridcolor="rgba(230, 230, 230, 0.5)",
        ),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        template="plotly_white",
        height=320,
    )
    return fig


def plot_annual_returns_bar(annual_df: pd.DataFrame) -> go.Figure:
    """
    Gràfic de barres per als retorns de cada any natural.
    """
    if annual_df.empty:
        return go.Figure()

    colors = ["#2ca02c" if r >= 0 else "#d62728" for r in annual_df["Retorn (%)"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=annual_df["Any"].astype(str),
            y=annual_df["Retorn (%)"],
            marker_color=colors,
            text=[f"{r:+.1f}%" for r in annual_df["Retorn (%)"]],
            textposition="outside",
            hovertemplate="<b>Any %{x}</b><br>Rendibilitat: %{y:+.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Rendibilitat Any per Any (%)</b>",
            font=dict(size=16),
        ),
        xaxis=dict(title="Any", type="category"),
        yaxis=dict(
            title="Rendibilitat (%)",
            ticksuffix="%",
            showgrid=True,
            gridcolor="rgba(230, 230, 230, 0.5)",
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        template="plotly_white",
        height=340,
    )
    return fig


def plot_asset_allocation_donut(portfolio: Portfolio) -> go.Figure:
    """
    Gràfic tipus donut per a la distribució d'actius de la cartera.
    """
    labels = list(portfolio.allocations.keys())
    values = list(portfolio.allocations.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Pes: %{value:.1f}%<extra></extra>",
                marker=dict(colors=px.colors.qualitative.Prism),
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="<b>Assignació d'Actius (%)</b>",
            font=dict(size=16),
        ),
        showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        template="plotly_white",
        height=320,
    )
    return fig
