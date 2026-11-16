"""Shared look & feel: palette, Plotly styling, CSS, small UI helpers."""
import plotly.graph_objects as go
import streamlit as st

# Categorical palette (fixed order, colour-blind validated) + one-hue sequential ramp
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE = CAT[0]
ORANGE = CAT[1]
SEQ = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"


def style(fig: go.Figure, height: int = 360, legend: bool = False) -> go.Figure:
    """Apply the dashboard look to any Plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=40, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color=INK2),
        title=dict(x=0.0, xanchor="left", font=dict(size=15, color=INK)),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=AXIS, font=dict(color=INK, size=12)),
        bargap=0.35,
    )
    try:
        fig.update_layout(barcornerradius=4)
    except Exception:
        pass
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED), title_font=dict(color=INK2))
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED), title_font=dict(color=INK2))
    return fig


def show(fig: go.Figure, key: str | None = None):
    try:
        st.plotly_chart(fig, width="stretch", key=key, config={"displayModeBar": False})
    except TypeError:  # older Streamlit
        st.plotly_chart(fig, use_container_width=True, key=key, config={"displayModeBar": False})


def table(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


CSS = f"""
<style>
.block-container {{ padding-top: 3.2rem; max-width: 1280px; }}
[data-testid="stSidebar"] {{ border-right: 1px solid {GRID}; }}
[data-testid="stMetric"] {{
    background: {SURFACE}; border: 1px solid {GRID}; border-radius: 12px;
    padding: 14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,.04);
}}
[data-testid="stMetricLabel"] p {{ color: {INK2}; font-size: .8rem; letter-spacing: .02em; }}
[data-testid="stMetricValue"] {{ font-weight: 650; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 12px; }}
.hero {{
    background: linear-gradient(120deg, #0d366b 0%, #2a78d6 100%);
    color: #fff; border-radius: 16px; padding: 22px 26px; margin-bottom: 18px;
}}
.hero h1 {{ color:#fff; font-size: 1.7rem; margin: 0 0 4px 0; padding: 0; }}
.hero p {{ color:#cde2fb; margin: 0; font-size: .95rem; }}
.pill {{ display:inline-block; padding: 2px 10px; border-radius: 999px; font-size:.75rem;
        border:1px solid {AXIS}; background:{SURFACE}; color:{INK2}; margin: 2px 4px 2px 0; }}
.pill.ok {{ background:#e6f6ee; border-color:#9fd8bd; color:#006300; }}
.pill.no {{ background:#f5f4f0; }}
.insight {{ border-left: 4px solid {BLUE}; background:{SURFACE}; padding: 10px 14px;
           border-radius: 6px; margin: 6px 0; color:{INK}; }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(
        f'<div class="hero"><h1>{icon} {title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def insight(text: str):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


def pill(text: str, ok: bool | None = None) -> str:
    cls = "ok" if ok else ("no" if ok is False else "")
    return f'<span class="pill {cls}">{text}</span>'
