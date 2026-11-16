"""Salary & Market."""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import theme
from data_loader import EXP_ORDER, get_fusion
from theme import BLUE, CAT, SEQ, SURFACE, show, style


def render():
    theme.page_header("Salary & Market", "Where the money and the jobs are.", "💰")
    df = get_fusion()
    types = st.multiselect("Job type", sorted(df.job_type.unique()), default=sorted(df.job_type.unique()))
    df = df[df.job_type.isin(types)]
    if df.empty:
        st.warning("Select at least one job type.")
        return

    top_role = df.groupby("job_title").salary_max_lpa.mean().idxmax()
    top_loc = df.groupby("location").salary_max_lpa.mean().idxmax()
    wm = df.groupby("work_mode").salary_max_lpa.mean()
    k = st.columns(4)
    k[0].metric("Highest-paying role", top_role)
    k[1].metric("Highest-paying city", top_loc)
    k[2].metric("Remote vs on-site", f"{(wm['Remote'] / wm['On-site'] - 1) * 100:+.1f}%", help="Avg max salary difference")
    k[3].metric("Avg max salary", f"₹{df.salary_max_lpa.mean():.1f} LPA")

    a, b = st.columns(2)
    with a:
        fig = px.box(df, x="work_mode", y="salary_max_lpa", color_discrete_sequence=[BLUE],
                     title="Max salary by work mode (LPA)")
        fig.update_layout(xaxis_title="", yaxis_title="₹ LPA")
        show(style(fig))
    with b:
        g = df.groupby("experience_level", observed=True).agg(lo=("salary_min_lpa", "mean"), hi=("salary_max_lpa", "mean")).reindex(EXP_ORDER).dropna()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=g.index, y=g.hi, name="Max", mode="lines+markers", line=dict(color=CAT[0], width=2),
                                 marker=dict(size=8, line=dict(color=SURFACE, width=2))))
        fig.add_trace(go.Scatter(x=g.index, y=g.lo, name="Min", mode="lines+markers", line=dict(color=CAT[1], width=2),
                                 marker=dict(size=8, line=dict(color=SURFACE, width=2))))
        fig.update_layout(title="Salary growth with experience (LPA)", yaxis_title="₹ LPA", xaxis_title="", hovermode="x unified")
        show(style(fig, legend=True))

    piv = df.pivot_table(index="job_title", columns="location", values="salary_max_lpa", aggfunc="mean")
    fig = px.imshow(piv, text_auto=".1f", aspect="auto", color_continuous_scale=SEQ,
                    title="Avg max salary (LPA): role × city", labels=dict(color="LPA"))
    fig.update_layout(xaxis_title="", yaxis_title="", coloraxis_showscale=False)
    show(style(fig, height=480))

    fig = px.scatter(df, x="experience_years", y="salary_max_lpa", opacity=0.55, color_discrete_sequence=[BLUE],
                     hover_data=["job_title", "location", "work_mode"], title="Experience years vs max salary")
    fig.update_traces(marker=dict(size=8, line=dict(color=SURFACE, width=1)))
    fig.update_layout(xaxis_title="Experience (years)", yaxis_title="₹ LPA")
    show(style(fig, height=340))
    corr = np.corrcoef(df.experience_years, df.salary_max_lpa)[0, 1]
    theme.insight(f"Correlation between experience and max salary is <b>{corr:.2f}</b>. "
                  + ("Experience barely moves pay in this dataset." if abs(corr) < 0.2 else "Experience clearly affects pay."))
