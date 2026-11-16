"""Home: analytics dashboard over the 750-record fusion dataset."""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import theme
from data_loader import EXP_ORDER, MATCH_ORDER, count_skills, get_fusion
from theme import BLUE, CAT, SEQ, SURFACE, show, style


def _filters(df):
    c = st.columns(5)
    pick = lambda col, label, i: c[i].multiselect(label, sorted(df[col].dropna().unique(), key=str))
    role = pick("job_title", "Job role", 0)
    loc = pick("location", "Location", 1)
    mode = pick("work_mode", "Work mode", 2)
    jtype = pick("job_type", "Job type", 3)
    exp = c[4].multiselect("Experience", EXP_ORDER)
    m = np.ones(len(df), dtype=bool)
    for col, sel in (("job_title", role), ("location", loc), ("work_mode", mode),
                     ("job_type", jtype), ("experience_level", exp)):
        if sel:
            m &= df[col].astype(str).isin(sel).to_numpy()
    return df[m]


def render():
    theme.page_header("Career Intelligence Dashboard",
                      "Insights from 750 fused records · Adzuna + MUSE + Groq + Gemini + Whisper", "📊")
    df_all = get_fusion()
    df = _filters(df_all)
    if df.empty:
        st.warning("No records match these filters.")
        return

    # ---- KPI row
    k = st.columns(6)
    k[0].metric("Records", f"{len(df):,}")
    k[1].metric("Avg ATS score", f"{df.ats_score.mean():.1f}")
    k[2].metric("Avg skill match", f"{df.skill_match_percentage.mean():.1f}%")
    k[3].metric("Strong matches", f"{(df.ats_score >= 60).mean() * 100:.0f}%", help="ATS score of 60 or more")
    k[4].metric("Median max pay", f"₹{df.salary_max_lpa.median():.1f}L", help="Median of max salary, in lakhs per annum")
    k[5].metric("Data complete", f"{(df.data_status == 'Complete').mean() * 100:.0f}%")

    t1, t2, t3, t4 = st.tabs(["Overview", "Skills & match", "Geography & salary", "Data quality"])

    # ---- Overview
    with t1:
        a, b = st.columns(2)
        with a:
            fig = px.histogram(df, x="ats_score", nbins=16, color_discrete_sequence=[BLUE],
                               title="ATS score distribution")
            fig.update_traces(marker_line_color=SURFACE, marker_line_width=2,
                              hovertemplate="ATS %{x}<br>%{y} resumes<extra></extra>")
            fig.update_layout(xaxis_title="ATS score", yaxis_title="Resumes")
            show(style(fig))
        with b:
            g = df.groupby("job_title").ats_score.mean().sort_values().reset_index()
            fig = px.bar(g, x="ats_score", y="job_title", orientation="h", color_discrete_sequence=[BLUE],
                         title="Average ATS score by role")
            fig.update_traces(hovertemplate="%{y}<br>Avg ATS %{x:.1f}<extra></extra>")
            fig.update_layout(xaxis_title="Avg ATS score", yaxis_title="")
            show(style(fig))
        a, b = st.columns(2)
        with a:
            g = df.groupby(["job_type", "work_mode"]).size().reset_index(name="jobs")
            fig = px.bar(g, x="job_type", y="jobs", color="work_mode", barmode="group",
                         color_discrete_sequence=CAT[:3], title="Job type by work mode")
            fig.update_layout(xaxis_title="", yaxis_title="Jobs")
            show(style(fig, legend=True))
        with b:
            g = df.analysis_feedback.value_counts().sort_values().reset_index()
            g.columns = ["feedback", "count"]
            fig = px.bar(g, x="count", y="feedback", orientation="h", color_discrete_sequence=[BLUE],
                         title="Most common AI feedback")
            fig.update_layout(xaxis_title="Resumes", yaxis_title="")
            show(style(fig))

    # ---- Skills & match
    with t2:
        a, b = st.columns(2)
        with a:
            fig = px.scatter(df, x="skill_match_percentage", y="ats_score", opacity=0.55,
                             color_discrete_sequence=[BLUE], title="Skill match vs ATS score",
                             hover_data=["job_title", "candidate_name", "experience_level"])
            if len(df) > 2:
                slope, icpt = np.polyfit(df.skill_match_percentage, df.ats_score, 1)
                xs = np.array([df.skill_match_percentage.min(), df.skill_match_percentage.max()])
                fig.add_trace(go.Scatter(x=xs, y=slope * xs + icpt, mode="lines", name="Trend",
                                         line=dict(color=CAT[1], width=2), hoverinfo="skip"))
            fig.update_traces(marker=dict(size=8, line=dict(color=SURFACE, width=1)), selector=dict(mode="markers"))
            fig.update_layout(xaxis_title="Skill match %", yaxis_title="ATS score")
            show(style(fig))
        with b:
            piv = df.pivot_table(index="job_title", columns="experience_level", values="ats_score",
                                 aggfunc="mean", observed=False).reindex(columns=EXP_ORDER)
            fig = px.imshow(piv, text_auto=".0f", aspect="auto", color_continuous_scale=SEQ,
                            title="Avg ATS: role × experience", labels=dict(color="Avg ATS"))
            fig.update_layout(xaxis_title="", yaxis_title="", coloraxis_showscale=False)
            show(style(fig))
        a, b = st.columns(2)
        with a:
            rows = []
            for col, label in (("experience_match", "Experience"), ("education_match", "Education")):
                vc = df[col].value_counts(normalize=True).reindex(MATCH_ORDER).fillna(0) * 100
                rows += [{"Dimension": label, "Match": m, "Share": v} for m, v in vc.items()]
            fig = px.bar(pd_df(rows), y="Dimension", x="Share", color="Match", orientation="h",
                         barmode="stack", category_orders={"Match": MATCH_ORDER},
                         color_discrete_map={"Low": SEQ[0], "Partial": SEQ[2], "Good": SEQ[4]},
                         title="Experience & education fit")
            fig.update_traces(marker_line_color=SURFACE, marker_line_width=2,
                              hovertemplate="%{y} · %{fullData.name}<br>%{x:.0f}%<extra></extra>")
            fig.update_layout(xaxis_title="% of resumes", yaxis_title="")
            show(style(fig, height=300, legend=True))
        with b:
            miss = count_skills(df, "missing_skills").head(10).sort_values().reset_index()
            miss.columns = ["skill", "count"]
            fig = px.bar(miss, x="count", y="skill", orientation="h", color_discrete_sequence=[CAT[1]],
                         title="Top 10 missing skills")
            fig.update_layout(xaxis_title="Times missing", yaxis_title="")
            show(style(fig, height=300))

    # ---- Geography & salary
    with t3:
        a, b = st.columns(2)
        with a:
            g = df.location.value_counts().sort_values().reset_index()
            g.columns = ["location", "jobs"]
            fig = px.bar(g, x="jobs", y="location", orientation="h", color_discrete_sequence=[BLUE],
                         title="Jobs by location")
            fig.update_layout(xaxis_title="Jobs", yaxis_title="")
            show(style(fig))
        with b:
            g = df.groupby("job_title")[["salary_min_lpa", "salary_max_lpa"]].mean().sort_values("salary_max_lpa")
            fig = go.Figure(go.Bar(
                y=g.index, x=g.salary_max_lpa - g.salary_min_lpa, base=g.salary_min_lpa, orientation="h",
                marker_color=BLUE, customdata=np.c_[g.salary_min_lpa, g.salary_max_lpa],
                hovertemplate="%{y}<br>₹%{customdata[0]:.1f}–%{customdata[1]:.1f} LPA<extra></extra>"))
            fig.update_layout(title="Average salary range by role (LPA)", xaxis_title="₹ LPA")
            show(style(fig))
        g = df.groupby("experience_level", observed=True).salary_max_lpa.mean().reindex(EXP_ORDER).dropna().reset_index()
        fig = px.bar(g, x="experience_level", y="salary_max_lpa", color_discrete_sequence=[BLUE],
                     title="Average max salary by experience (LPA)")
        fig.update_layout(xaxis_title="", yaxis_title="₹ LPA")
        show(style(fig, height=300))

    # ---- Data quality
    with t4:
        a, b = st.columns(2)
        with a:
            g = df.groupby(["fusion_sources", "data_status"]).size().reset_index(name="records")
            fig = px.bar(g, y="fusion_sources", x="records", color="data_status", orientation="h",
                         barmode="stack", color_discrete_map={"Complete": CAT[0], "Needs review": CAT[1]},
                         title="Fusion source combinations")
            fig.update_traces(marker_line_color=SURFACE, marker_line_width=2)
            fig.update_layout(xaxis_title="Records", yaxis_title="")
            show(style(fig, legend=True))
        with b:
            g = df.job_source.value_counts().reset_index()
            g.columns = ["source", "records"]
            fig = px.bar(g, x="source", y="records", color_discrete_sequence=[BLUE], title="Job source")
            fig.update_layout(xaxis_title="", yaxis_title="Records")
            show(style(fig))
        review = df[df.data_status == "Needs review"]
        theme.insight(f"<b>{len(review)}</b> of {len(df)} records are flagged <i>Needs review</i> "
                      f"({len(review) / len(df) * 100:.0f}%). Check them in the <b>Data Explorer</b>.")


def pd_df(rows):
    import pandas as pd
    return pd.DataFrame(rows)
