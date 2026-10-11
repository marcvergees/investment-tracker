"""
Components gràfics per a l'anàlisi d'exposició (Portfolio X-Ray):
Països/Regions, Sectors/Indústries i Principals Accions Individuals.
"""

from typing import Dict
import plotly.graph_objects as go
import plotly.express as px


def plot_country_exposure(countries: Dict[str, float]) -> go.Figure:
    """
    Gràfic de barres horitzontals de l'exposició per països i regions.
    """
    if not countries:
        return go.Figure()

    labels = list(countries.keys())[:10]  # Top 10
    values = [countries[k] for k in labels]

    # Invertir per mostrar el primer a dalt de tot
    labels.reverse()
    values.reverse()

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color="#3b82f6"),
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            hovertemplate="<b>%{y}</b>: %{x:.2f}% de la cartera<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Exposició Geogràfica per Països (%)</b>", font=dict(size=16)),
        xaxis=dict(title="Pes a la Cartera (%)", ticksuffix="%", showgrid=True),
        yaxis=dict(title="", showgrid=False),
        margin=dict(l=30, r=40, t=50, b=30),
        template="plotly_white",
        height=380,
    )
    return fig


def plot_sector_exposure(sectors: Dict[str, float]) -> go.Figure:
    """
    Gràfic tipus donut / barres de l'exposició sectorial (indústries).
    """
    if not sectors:
        return go.Figure()

    labels = list(sectors.keys())[:10]
    values = [sectors[k] for k in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b>: %{value:.1f}%<extra></extra>",
                marker=dict(colors=px.colors.qualitative.Safe),
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Exposició per Sectors / Indústries (%)</b>", font=dict(size=16)),
        showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        template="plotly_white",
        height=380,
    )
    return fig


def plot_top_holdings_overlap(holdings: Dict[str, float], top_n: int = 12) -> go.Figure:
    """
    Gràfic de les principals accions individuals agregades a la cartera.
    Permet detectar si diferents ETFs concentren massa pes en les mateixes accions.
    """
    if not holdings:
        return go.Figure()

    top_keys = list(holdings.keys())[:top_n]
    top_vals = [holdings[k] for k in top_keys]

    # Invertir per tenir el primer a dalt
    top_keys.reverse()
    top_vals.reverse()

    fig = go.Figure(
        go.Bar(
            x=top_vals,
            y=top_keys,
            orientation="h",
            marker=dict(
                color=top_vals,
                colorscale="Blues",
                showscale=False,
            ),
            text=[f"{v:.2f}%" for v in top_vals],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Pes agregat a la cartera: %{x:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Top {top_n} Accions Individuals a la Cartera (Pes Real Acumulat)</b>",
            font=dict(size=16),
        ),
        xaxis=dict(
            title="Percentatge Real a la Cartera (%)",
            ticksuffix="%",
            showgrid=True,
        ),
        yaxis=dict(title="", showgrid=False),
        margin=dict(l=30, r=40, t=50, b=30),
        template="plotly_white",
        height=420,
    )
    return fig
