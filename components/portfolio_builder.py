"""
Component per a la creació, edició i gestió de carteres d'inversió en Streamlit.
"""

from typing import Dict, Any, Optional
import streamlit as st
from config import POPULAR_ASSETS, DEFAULT_INITIAL_CAPITAL
from core.portfolio import Portfolio
from storage.portfolio_storage import PortfolioStorage
from core.ticker_search import search_yahoo_tickers, get_ticker_preview


def render_portfolio_builder(storage: PortfolioStorage):
    """
    Renderitza el formulari complet de creació i edició de carteres.
    """
    st.subheader("🛠️ Gestor i Creador de Carteres d'Inversió")
    st.caption("Afegeix actius financers (ETFs, fons d'inversió o accions), assigna ponderacions i desa les teves propostes.")

    # Inicialitzar estat de la sessió per a la creació de carteres si cal
    if "builder_assets" not in st.session_state:
        st.session_state.builder_assets = [
            {"ticker": "IWDA.AS", "weight": 70.0},
            {"ticker": "AGGH.AS", "weight": 30.0},
        ]

    # Carregar una cartera existent per editar-la
    existing_portfolios = storage.list_portfolios()
    existing_names = ["-- Crear una Cartera Nova --"] + [p.name for p in existing_portfolios]

    selected_existing = st.selectbox(
        "📂 Opcional: Carregar una cartera desada per modificar-la:",
        existing_names,
        key="load_existing_select"
    )

    if selected_existing != "-- Crear una Cartera Nova --":
        p_loaded = storage.load_portfolio(selected_existing)
        if p_loaded and st.button("📥 Importar dades d'aquesta cartera a l'editor"):
            st.session_state.builder_assets = [
                {"ticker": t, "weight": w} for t, w in p_loaded.allocations.items()
            ]
            st.session_state.builder_name = p_loaded.name
            st.session_state.builder_desc = p_loaded.description
            st.session_state.builder_capital = p_loaded.initial_capital
            st.session_state.builder_rebal = p_loaded.rebalance_freq
            st.rerun()

    st.markdown("---")

    # Camps principals de la cartera
    col_name, col_cap = st.columns([2, 1])
    with col_name:
        p_name = st.text_input(
            "Nom de la Cartera / Proposta:",
            value=st.session_state.get("builder_name", "La Meva Cartera"),
            placeholder="Ex: Proposta Banc Santander o Cartera Indexada Global",
            key="input_portfolio_name"
        )
    with col_cap:
        p_capital = st.number_input(
            "Capital Inicial (€):",
            min_value=100.0,
            max_value=10_000_000.0,
            value=float(st.session_state.get("builder_capital", DEFAULT_INITIAL_CAPITAL)),
            step=1000.0,
            format="%.0f",
            key="input_portfolio_capital"
        )

    col_desc, col_rebal = st.columns([2, 1])
    with col_desc:
        p_desc = st.text_input(
            "Descripció o Notes:",
            value=st.session_state.get("builder_desc", ""),
            placeholder="Ex: Proposta conservadora recomanada pel gestor del banc...",
            key="input_portfolio_desc"
        )
    with col_rebal:
        rebal_options = {
            "Anual (Recomanat)": "yearly",
            "Trimestral": "quarterly",
            "Sense Rebalançar (Buy & Hold)": "none",
        }
        rebal_choice = st.selectbox(
            "Estratègia de Rebalançament:",
            list(rebal_options.keys()),
            index=0,
            key="input_portfolio_rebal"
        )
        p_rebal = rebal_options[rebal_choice]

    st.markdown("#### 🎯 Actius i Ponderació de la Cartera")

    # Afegir actius amb cercador i validador interactiu de Yahoo Finance
    with st.expander("➕ Afegir Actius a la Cartera (Cercador i Validador Oficial)", expanded=True):
        tab_search, tab_popular = st.tabs(["🔍 Cercador i Validador de Nous Tickers", "⭐ Llista d'Actius Populars Predefinits"])

        # PESTANYA 1: CERCADOR EN VIU AMB DESPLEGABLE I VALIDACIÓ
        with tab_search:
            st.caption("Escriu qualsevol ticker o nom d'empresa/fons per cercar a Yahoo Finance i validar abans d'afegir-lo:")
            col_search_input, _ = st.columns([3, 1])
            with col_search_input:
                search_query = st.text_input(
                    "Cercar ticker o nom:",
                    placeholder="Ex: IS3N, IUSN, Bitcoin, Nvidia, Small Cap, Santander, Vanguard...",
                    key="live_ticker_search_input"
                ).strip()

            if search_query:
                with st.spinner("Cercant actius coincidents a Yahoo Finance..."):
                    search_results = search_yahoo_tickers(search_query, limit=10)

                if search_results:
                    options_labels = [
                        f"{r['symbol']} — {r['name']} ({r['type']} · {r['exchange']})"
                        for r in search_results
                    ]
                    selected_label = st.selectbox(
                        "📋 Desplegable de tickers coincidents trobats (selecciona el que vols validar):",
                        options_labels,
                        key="search_results_dropdown"
                    )

                    # Obtenir el símbol seleccionat
                    selected_symbol = search_results[options_labels.index(selected_label)]["symbol"]

                    # Previsualitzar i validar dades en viu
                    with st.spinner(f"Verificant dades oficials per a '{selected_symbol}'..."):
                        preview = get_ticker_preview(selected_symbol)

                    if preview.get("is_valid"):
                        # Targeta visual d'èxit i resum
                        curr_symbol = "€" if preview['currency'] in ["EUR", "eur"] else ("$" if preview['currency'] in ["USD", "usd"] else preview['currency'])
                        st.markdown(f"""
                        <div style="background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 12px 16px; margin: 10px 0;">
                            <div style="font-size: 16px; font-weight: 700; color: #166534;">
                                ✅ Ticker Vàlid a Yahoo Finance: <code>{preview['symbol']}</code> — {preview['name']}
                            </div>
                            <div style="font-size: 13px; color: #15803d; margin-top: 6px; line-height: 1.5;">
                                🏢 <b>Tipus:</b> {preview['quote_type']} &nbsp;|&nbsp; 
                                🏛️ <b>Borsa:</b> {preview['exchange']} &nbsp;|&nbsp; 
                                💶 <b>Moneda:</b> {preview['currency']} &nbsp;|&nbsp; 
                                🏷️ <b>Últim Preu:</b> {preview['last_price']:,.2f} {curr_symbol}<br>
                                📅 <b>Històric de cotització:</b> {preview['years_history']} anys disponibles ({preview['num_sessions']:,} sessions des de {preview['first_date']})
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Botó per afegir a la cartera
                        if st.button(f"➕ Afegir '{preview['symbol']}' a la Cartera", key=f"btn_add_verified_{preview['symbol']}", type="primary"):
                            existing_tickers = [a["ticker"] for a in st.session_state.builder_assets]
                            if preview["symbol"] in existing_tickers:
                                st.warning(f"L'actiu {preview['symbol']} ja és a la teva cartera.")
                            else:
                                st.session_state.builder_assets.append({"ticker": preview["symbol"], "weight": 10.0})
                                st.success(f"S'ha afegit {preview['symbol']} a la cartera!")
                                st.rerun()

                    else:
                        err_msg = preview.get('error', "No s'han trobat dades valides per a aquest ticker.")
                        st.error(f"❌ {err_msg}")

                else:
                    st.warning(f"No s'han trobat actius a Yahoo Finance per a la cerca '{search_query}'. Prova amb el nom de l'empresa o gestora (ex: Apple, iShares, Vanguard).")

        # PESTANYA 2: SELECCIÓ RÀPIDA D'ACTIUS POPULARS
        with tab_popular:
            col_pop, col_btn_pop = st.columns([3, 1])
            with col_pop:
                popular_choices = ["-- Triar de la llista popular --"] + [
                    f"{a['ticker']} - {a['name']} ({a['category']})" for a in POPULAR_ASSETS
                ]
                picked_pop = st.selectbox("ETFs i Actius Populars Precarregats:", popular_choices, key="pick_pop_asset")

            with col_btn_pop:
                st.write("")
                if st.button("Afegir Actiu Popular", width="stretch", key="btn_add_pop"):
                    if picked_pop != "-- Triar de la llista popular --":
                        ticker_to_add = picked_pop.split(" - ")[0].strip()
                        existing_tickers = [a["ticker"] for a in st.session_state.builder_assets]
                        if ticker_to_add in existing_tickers:
                            st.warning(f"L'actiu {ticker_to_add} ja és a la cartera.")
                        else:
                            st.session_state.builder_assets.append({"ticker": ticker_to_add, "weight": 10.0})
                            st.rerun()

    # Llista d'actius afegits amb controls de pes
    current_assets = st.session_state.builder_assets
    if not current_assets:
        st.info("La cartera no té cap actiu afegit. Afegeix el teu primer ETF o acció.")
        return

    st.write("##### Ponderació de cada actiu (%):")
    total_weight = 0.0
    items_to_delete = []

    for idx, item in enumerate(current_assets):
        t_col, w_col, del_col = st.columns([2, 3, 1])
        
        with t_col:
            st.markdown(f"**`{item['ticker']}`**")
        with w_col:
            new_weight = st.number_input(
                f"Pes % per a {item['ticker']}",
                min_value=0.0,
                max_value=100.0,
                value=float(item["weight"]),
                step=5.0,
                key=f"weight_input_{idx}_{item['ticker']}",
                label_visibility="collapsed"
            )
            item["weight"] = new_weight
            total_weight += new_weight
        with del_col:
            if st.button("🗑️", key=f"del_btn_{idx}_{item['ticker']}", help="Eliminar actiu"):
                items_to_delete.append(idx)

    # Eliminar ítems marcats
    if items_to_delete:
        for idx in reversed(items_to_delete):
            st.session_state.builder_assets.pop(idx)
        st.rerun()

    # Barra d'estat del pes total
    st.markdown("---")
    col_status, col_balance = st.columns([3, 2])
    
    with col_status:
        if abs(total_weight - 100.0) < 0.1:
            st.success(f"✅ Suma total dels pesos: **{total_weight:.1f}%** (Correcte)")
        else:
            diff = 100.0 - total_weight
            if diff > 0:
                st.warning(f"⚠️ Suma actual: **{total_weight:.1f}%**. Falta assignar un **{diff:.1f}%** per arribar al 100%.")
            else:
                st.error(f"❌ Suma actual: **{total_weight:.1f}%**. Sobrepassa el 100% per un **{-diff:.1f}%**.")

    with col_balance:
        if st.button("⚖️ Normalitzar automàticament al 100%"):
            if total_weight > 0:
                for item in st.session_state.builder_assets:
                    item["weight"] = round((item["weight"] / total_weight) * 100.0, 1)
                st.rerun()

    # Botó per Desar la Cartera
    if st.button("💾 Desar Cartera al Disc", type="primary", width="stretch"):
        if not p_name.strip():
            st.error("Si us plau, especifica un nom per a la cartera.")
            return

        if not current_assets:
            st.error("Has d'afegir com a mínim un actiu financer.")
            return

        allocs = {item["ticker"]: item["weight"] for item in current_assets if item["weight"] > 0}
        portfolio_obj = Portfolio(
            name=p_name,
            allocations=allocs,
            initial_capital=p_capital,
            rebalance_freq=p_rebal,
            description=p_desc,
        )

        saved_path = storage.save_portfolio(portfolio_obj)
        st.success(f"🎉 Cartera **'{portfolio_obj.name}'** desada correctament!")
        st.rerun()

    # Taula de carteres desades amb opcions de reanomenar i eliminar
    st.markdown("---")
    st.markdown("#### 📁 Carteres Guardades Actualment")
    all_p = storage.list_portfolios()

    # Inicialitzar estat de confirmació per a esborraments i edició de noms
    if "pending_delete" not in st.session_state:
        st.session_state.pending_delete = None
    if "rename_active" not in st.session_state:
        st.session_state.rename_active = {}

    if all_p:
        for p in all_p:
            with st.container(border=True):
                col_info, col_rename_btn, col_delete_btn = st.columns([4, 1, 1])

                with col_info:
                    alloc_str = ", ".join([f"{t} ({w:.0f}%)" for t, w in p.allocations.items()])
                    st.markdown(f"**{p.name}** — {p.initial_capital:,.0f} €")
                    st.caption(alloc_str)
                    if p.description:
                        st.caption(f"_{p.description}_")

                with col_rename_btn:
                    rename_key = f"rename_toggle_{p.name}"
                    if st.button("✏️ Reanomenar", key=rename_key):
                        # Toggle el formulari de reanomenar
                        current = st.session_state.rename_active.get(p.name, False)
                        st.session_state.rename_active = {}  # Tancar altres
                        st.session_state.rename_active[p.name] = not current
                        st.session_state.pending_delete = None
                        st.rerun()

                with col_delete_btn:
                    if st.session_state.pending_delete == p.name:
                        if st.button("✅ Confirmar", key=f"confirm_del_{p.name}", type="primary"):
                            storage.delete_portfolio(p.name)
                            st.session_state.pending_delete = None
                            st.rerun()
                    else:
                        if st.button("🗑️ Eliminar", key=f"delete_saved_{p.name}"):
                            st.session_state.pending_delete = p.name
                            st.session_state.rename_active = {}
                            st.rerun()

                # Formulari de reanomenar (expandible)
                if st.session_state.rename_active.get(p.name, False):
                    with st.container():
                        r_col1, r_col2, r_col3 = st.columns([3, 1, 1])
                        with r_col1:
                            new_name = st.text_input(
                                "Nou nom:",
                                value=p.name,
                                key=f"new_name_input_{p.name}",
                                label_visibility="collapsed",
                                placeholder="Escriu el nou nom de la cartera..."
                            )
                        with r_col2:
                            if st.button("💾 Desar nom", key=f"save_rename_{p.name}", type="primary"):
                                new_name_clean = new_name.strip()
                                if not new_name_clean:
                                    st.error("El nom no pot estar buit.")
                                elif new_name_clean == p.name:
                                    st.session_state.rename_active[p.name] = False
                                    st.rerun()
                                else:
                                    ok = storage.rename_portfolio(p.name, new_name_clean)
                                    if ok:
                                        st.session_state.rename_active = {}
                                        st.rerun()
                                    else:
                                        st.error("No s'ha pogut reanomenar la cartera.")
                        with r_col3:
                            if st.button("❌ Cancel·lar", key=f"cancel_rename_{p.name}"):
                                st.session_state.rename_active[p.name] = False
                                st.rerun()

                # Missatge de confirmació d'esborrament
                if st.session_state.pending_delete == p.name:
                    st.warning(
                        f"⚠️ Segur que vols eliminar la cartera **'{p.name}'**? "
                        "Aquesta acció no es pot desfer. Clica '✅ Confirmar' per continuar."
                    )
    else:
        st.info("No hi ha carteres guardades.")
