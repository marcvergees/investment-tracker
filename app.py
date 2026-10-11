"""
Aplicació Principal: ETF & Portfolio Tracker & Backtester
Eina visual interactiva per a l'anàlisi històrica, exposició (X-Ray) i comparació de carteres d'inversió.
"""

import datetime
import streamlit as st
import pandas as pd
from config import (
    TIME_HORIZONS,
    BENCHMARK_OPTIONS,
    DEFAULT_INITIAL_CAPITAL,
    RISK_FREE_RATE_ANNUAL,
)
from core.data_fetcher import DataFetcher
from core.portfolio import Portfolio
from core.backtest_engine import BacktestEngine, BacktestResult
from core.xray_engine import XRayEngine
from storage.portfolio_storage import PortfolioStorage
from components.chart_views import (
    plot_equity_curve,
    plot_drawdown_curve,
    plot_annual_returns_bar,
    plot_asset_allocation_donut,
)
from components.xray_views import (
    plot_country_exposure,
    plot_sector_exposure,
    plot_top_holdings_overlap,
)
from components.comparison_view import (
    plot_comparison_equity_curve,
    build_comparison_metrics_table,
    plot_comparison_annual_returns,
    plot_comparison_sector_exposure,
)
from components.portfolio_builder import render_portfolio_builder


# Configuració de la pàgina
st.set_page_config(
    page_title="ETF & Portfolio Backtester",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estils personalitzats
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-val {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_storage():
    return PortfolioStorage()


@st.cache_resource
def get_fetcher():
    return DataFetcher()


storage = get_storage()
fetcher = get_fetcher()


# Barra Lateral (Sidebar)
st.sidebar.title("📈 ETF Tracker & Backtest")
st.sidebar.caption("Simulació històrica i comparativa de carteres (ETFs, fons i accions).")

menu_choice = st.sidebar.radio(
    "Navegació Principal:",
    [
        "📊 Anàlisi de Cartera (Backtesting)",
        "🔍 Anàlisi d'Exposició (X-Ray)",
        "⚖️ Comparador de Carteres",
        "🛠️ Gestor de Carteres",
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Paràmetres Globals")

horizon_label = st.sidebar.selectbox(
    "Horitzó Temporal:",
    list(TIME_HORIZONS.keys()),
    index=2,  # 10 Anys per defecte
)
horizon_years = TIME_HORIZONS[horizon_label]

benchmark_labels = st.sidebar.multiselect(
    "Benchmarks de Referència:",
    list(BENCHMARK_OPTIONS.keys()),
    default=["S&P 500 (SPY)", "Nasdaq 100 (QQQ)"],
    help="Pots activar un, dos o més benchmarks simultàniament (p. ex. S&P 500 i Nasdaq 100) per veure'ls junts als gràfics."
)
benchmark_tickers = [BENCHMARK_OPTIONS[label] for label in benchmark_labels if label in BENCHMARK_OPTIONS]

log_scale = st.sidebar.checkbox("Escala Logarítmica als gràfics", value=False)


# Càlcul de dates
today = datetime.date.today()
if horizon_years == 99:
    start_date = datetime.date(1990, 1, 1)
else:
    start_date = today - datetime.timedelta(days=int(horizon_years * 365.25))


# -----------------------------------------------------------------------------------------
# PESTANYA 1: ANÀLISI DE CARTERA (BACKTESTING)
# -----------------------------------------------------------------------------------------
if menu_choice == "📊 Anàlisi de Cartera (Backtesting)":
    st.title("📊 Anàlisi Històrica de Cartera (Backtesting)")
    
    portfolios = storage.list_portfolios()
    if not portfolios:
        st.warning("No hi ha cap cartera disponible. Ves a '🛠️ Gestor de Carteres' per crear-ne una.")
        st.stop()

    p_names = [p.name for p in portfolios]
    selected_p_name = st.selectbox("Selecciona la Cartera a analitzar:", p_names, index=0)
    current_portfolio = storage.load_portfolio(selected_p_name)

    if not current_portfolio or not current_portfolio.allocations:
        st.error("Aquesta cartera no conté actius vàlids.")
        st.stop()

    # Informació de la cartera seleccionada
    with st.expander("ℹ️ Detalls i Composició d'aquesta Cartera", expanded=False):
        c_desc, c_alloc = st.columns([2, 1])
        with c_desc:
            st.write(f"**Descripció:** {current_portfolio.description or 'Sense descripció.'}")
            st.write(f"**Capital Inicial:** {current_portfolio.initial_capital:,.2f} €")
            st.write(f"**Rebalançament:** {current_portfolio.rebalance_freq.capitalize()}")
        with c_alloc:
            st.write("**Ponderacions:**")
            for t, w in current_portfolio.allocations.items():
                st.write(f"- `{t}`: **{w:.1f}%**")

    # Obtenir dades històriques
    tickers_to_fetch = list(current_portfolio.allocations.keys()) + benchmark_tickers

    with st.spinner("Descarregant i processant cotitzacions històriques..."):
        prices_df, warnings = fetcher.fetch_multiple_tickers(tickers_to_fetch, start_date=start_date, end_date=today)

    for w in warnings:
        st.warning(w)

    if prices_df.empty:
        st.error("No s'han pogut carregar les dades de mercat per als actius d'aquesta cartera.")
        st.stop()

    # Executar Backtest de la Cartera
    backtest_res = BacktestEngine.run_backtest(
        portfolio=current_portfolio,
        prices_df=prices_df,
        risk_free_rate=RISK_FREE_RATE_ANNUAL
    )

    # Executar Backtests dels Benchmarks seleccionats
    benchmark_results = []
    for b_ticker in benchmark_tickers:
        if b_ticker in prices_df.columns:
            b_res = BacktestEngine.run_benchmark(
                benchmark_ticker=b_ticker,
                prices_df=prices_df,
                initial_capital=current_portfolio.initial_capital,
                risk_free_rate=RISK_FREE_RATE_ANNUAL
            )
            if b_res:
                benchmark_results.append(b_res)

    # Tauler de KPIs / Mètriques clau
    m = backtest_res.metrics
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Capital Final</div>
            <div class="metric-val">{m['final_capital']:,.0f} €</div>
            <span style="color: {'green' if m['total_return_pct'] >= 0 else 'red'}; font-size: 13px;">
                {m['total_return_pct']:+.1f}% Total
            </span>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CAGR (Anualitzat)</div>
            <div class="metric-val">{m['cagr_pct']:+.2f}%</div>
            <span style="color: #64748b; font-size: 12px;">{m['num_years']} anys simulats</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Volatilitat Anual</div>
            <div class="metric-val">{m['volatility_pct']:.2f}%</div>
            <span style="color: #64748b; font-size: 12px;">Risc de fluctuació</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ràtio de Sharpe</div>
            <div class="metric-val">{m['sharpe_ratio']:.2f}</div>
            <span style="color: #64748b; font-size: 12px;">Retorn / Risc</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-val" style="color: #dc2626;">{m['max_drawdown_pct']:.2f}%</div>
            <span style="color: #64748b; font-size: 12px;">Caiguda màxima</span>
        </div>
        """, unsafe_allow_html=True)

    with kpi6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Millor / Pitjor Any</div>
            <div class="metric-val" style="font-size: 17px;">{m['best_year_pct']:+.1f}%</div>
            <span style="color: #dc2626; font-size: 13px;">Pitjor: {m['worst_year_pct']:+.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gràfic principal d'evolució
    show_indiv = st.checkbox("Mostrar també la corba de cada actiu individual per separat", value=False)
    fig_equity = plot_equity_curve(
        result=backtest_res,
        benchmark_results=benchmark_results,
        log_scale=log_scale,
        show_individual_assets=show_indiv
    )
    st.plotly_chart(fig_equity, width="stretch")

    # Gràfics secundaris: Drawdown & Retorns Anuals
    col_dd, col_alloc = st.columns([3, 2])
    with col_dd:
        fig_dd = plot_drawdown_curve(backtest_res)
        st.plotly_chart(fig_dd, width="stretch")
    with col_alloc:
        fig_donut = plot_asset_allocation_donut(current_portfolio)
        st.plotly_chart(fig_donut, width="stretch")

    # Retorns Any per Any
    st.plotly_chart(plot_annual_returns_bar(backtest_res.annual_returns), width="stretch")


# -----------------------------------------------------------------------------------------
# PESTANYA 2: ANÀLISI D'EXPOSICIÓ (PORTFOLIO X-RAY)
# -----------------------------------------------------------------------------------------
elif menu_choice == "🔍 Anàlisi d'Exposició (X-Ray)":
    st.title("🔍 Anàlisi d'Exposició de Cartera (Portfolio X-Ray)")
    st.caption("Inspecciona la composició real de la teva cartera: països, sectors i principals accions individuals (solapament entre ETFs).")

    portfolios = storage.list_portfolios()
    if not portfolios:
        st.warning("No hi ha cap cartera desada per analitzar.")
        st.stop()

    p_names = [p.name for p in portfolios]
    selected_p_name = st.selectbox("Selecciona la Cartera:", p_names, index=0)
    current_portfolio = storage.load_portfolio(selected_p_name)

    if not current_portfolio:
        st.stop()

    # Calcular exposició agregada
    xray = XRayEngine.calculate_portfolio_xray(current_portfolio)

    st.info(
        "💡 **Per què és clau l'anàlisi de solapament?** "
        "Quan s'inverteix en diversos ETFs alhora (per exemple, un MSCI World i un S&P 500 o sectorial), "
        "sovint es repeteixen les mateixes companyies (Apple, Microsoft, NVIDIA...). "
        "Aquests gràfics calculen el pes real agregat per evitar una sobreconcentració involuntària."
    )

    # Fila 1: Països i Sectors
    col_c, col_s = st.columns(2)
    with col_c:
        fig_countries = plot_country_exposure(xray.get("countries", {}))
        st.plotly_chart(fig_countries, width="stretch")

    with col_s:
        fig_sectors = plot_sector_exposure(xray.get("sectors", {}))
        st.plotly_chart(fig_sectors, width="stretch")

    # Fila 2: Top Accions Individuals (Holdings Overlap)
    st.markdown("---")
    st.subheader("🏢 Principals Accions Individuals a la Cartera Agregada")
    st.caption("Suma del pes de cada empresa dins de tots els teus ETFs combinats:")
    
    top_n_choice = st.slider("Nombre d'accions destacades a mostrar:", min_value=5, max_value=25, value=12)
    fig_holdings = plot_top_holdings_overlap(xray.get("top_holdings", {}), top_n=top_n_choice)
    st.plotly_chart(fig_holdings, width="stretch")

    # Taula detallada de Top Holdings
    with st.expander("📋 Veure taula completa de posicions agregades", expanded=False):
        holdings_dict = xray.get("top_holdings", {})
        if holdings_dict:
            df_holdings = pd.DataFrame([
                {"Empresa / Actiu": k, "Pes a la Cartera (%)": f"{v:.2f}%"}
                for k, v in holdings_dict.items()
            ])
            st.dataframe(df_holdings, width="stretch", hide_index=True)


# -----------------------------------------------------------------------------------------
# PESTANYA 3: COMPARADOR DE CARTERES
# -----------------------------------------------------------------------------------------
elif menu_choice == "⚖️ Comparador de Carteres":
    st.title("⚖️ Comparador de Carteres d'Inversió")
    st.caption("Enfronta diferents propostes d'inversió (p. ex. propostes de diferents bancs vs la teva pròpia cartera) partint del mateix capital.")

    portfolios = storage.list_portfolios()
    if len(portfolios) < 2:
        st.info("Cal tenir almenys dues carteres creades per fer una comparació. Ves a '🛠️ Gestor de Carteres' per afegir-ne.")
        st.stop()

    p_names = [p.name for p in portfolios]
    selected_p_names = st.multiselect(
        "Tria les carteres que vols comparar cara a cara:",
        p_names,
        default=p_names[:min(3, len(p_names))]
    )

    if len(selected_p_names) < 1:
        st.warning("Selecciona com a mínim una cartera.")
        st.stop()

    selected_objs = [storage.load_portfolio(name) for name in selected_p_names if storage.load_portfolio(name)]

    # Recollir tots els tickers necessaris (carteres + benchmarks)
    all_tickers = set()
    for p in selected_objs:
        all_tickers.update(p.allocations.keys())
    for b_ticker in benchmark_tickers:
        all_tickers.add(b_ticker)

    with st.spinner("Descarregant cotitzacions per a totes les carteres seleccionades..."):
        prices_df, warnings = fetcher.fetch_multiple_tickers(list(all_tickers), start_date=start_date, end_date=today)

    for w in warnings:
        st.warning(w)

    if prices_df.empty:
        st.error("No s'han pogut carregar les dades de mercat.")
        st.stop()

    # Executar backtests per a cadascuna
    backtest_results = []
    base_capital = selected_objs[0].initial_capital if selected_objs else DEFAULT_INITIAL_CAPITAL

    for p in selected_objs:
        # Homogeneïtzar capital inicial per a la comparació justa
        p_temp = Portfolio(
            name=p.name,
            allocations=p.allocations,
            initial_capital=base_capital,
            rebalance_freq=p.rebalance_freq,
        )
        res = BacktestEngine.run_backtest(p_temp, prices_df, risk_free_rate=RISK_FREE_RATE_ANNUAL)
        backtest_results.append(res)

    # Executar simulacions de tots els benchmarks seleccionats
    benchmark_results = []
    for b_ticker in benchmark_tickers:
        if b_ticker in prices_df.columns:
            b_res = BacktestEngine.run_benchmark(
                benchmark_ticker=b_ticker,
                prices_df=prices_df,
                initial_capital=base_capital,
                risk_free_rate=RISK_FREE_RATE_ANNUAL
            )
            if b_res:
                benchmark_results.append(b_res)

    # Gràfic comparatiu de creixement
    st.plotly_chart(
        plot_comparison_equity_curve(backtest_results, benchmark_results=benchmark_results, log_scale=log_scale),
        width="stretch"
    )

    # Taula cara a cara de KPIs
    st.subheader("📋 Taula Comparativa Cara a Cara de Mètriques")
    st.caption(f"Simulació iniciada amb una inversió de {base_capital:,.0f} € per a totes les carteres i benchmarks.")
    metrics_table = build_comparison_metrics_table(backtest_results, benchmark_results=benchmark_results)
    st.dataframe(metrics_table, width="stretch", hide_index=True)

    # Gràfic comparatiu de retorns anuals
    st.markdown("---")
    st.subheader("📊 Rendibilitats Anuals Comparades")
    st.plotly_chart(plot_comparison_annual_returns(backtest_results), width="stretch")

    # Comparativa d'exposició sectorial
    st.markdown("---")
    st.subheader("🏭 Comparativa de Sectors Econòmics entre Propostes")
    st.plotly_chart(plot_comparison_sector_exposure(selected_objs), width="stretch")


# -----------------------------------------------------------------------------------------
# PESTANYA 4: GESTOR DE CARTERES
# -----------------------------------------------------------------------------------------
elif menu_choice == "🛠️ Gestor de Carteres":
    render_portfolio_builder(storage)
