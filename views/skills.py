"""Skills Lab: demand vs supply, role heatmap, and a role matcher."""
import pandas as pd
import plotly.express as px
import streamlit as st

import theme
from data_loader import count_skills, find_skills, get_workbook, role_profiles, skill_vocabulary
from theme import BLUE, CAT, SEQ, show, style


def render():
    theme.page_header("Skills Lab", "What employers ask for, what candidates have, and which role fits your skills.", "🧠")
    wb = get_workbook()
    df = wb["Fused_750_Records"]
    cands = wb["Base_Candidates"]
    t1, t2, t3 = st.tabs(["Demand vs supply", "Role × skill heatmap", "🎯 Role matcher"])

    with t1:
        demand = (count_skills(df, "required_skills") / len(df) * 100)
        supply = (count_skills(cands, "candidate_skills") / len(cands) * 100)
        d = pd.DataFrame({"Demand (job postings)": demand, "Supply (candidates)": supply}).fillna(0)
        d = d.sort_values("Demand (job postings)", ascending=False).head(15)
        long = d.reset_index(names="skill").melt("skill", var_name="Series", value_name="share")
        fig = px.bar(long, x="skill", y="share", color="Series", barmode="group",
                     color_discrete_sequence=[CAT[0], CAT[1]], title="Top skills: % of postings requiring vs % of candidates having")
        fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.0f}%<extra></extra>")
        fig.update_layout(xaxis_title="", yaxis_title="% share", xaxis_tickangle=-35)
        show(style(fig, height=400, legend=True))
        gap = (d["Demand (job postings)"] - d["Supply (candidates)"]).sort_values(ascending=False)
        theme.insight(f"Biggest gap: <b>{gap.index[0]}</b> is required in {d.loc[gap.index[0], 'Demand (job postings)']:.0f}% "
                      f"of postings but only {d.loc[gap.index[0], 'Supply (candidates)']:.0f}% of candidates list it.")

    with t2:
        prof = role_profiles(df)
        top = prof.mean().sort_values(ascending=False).head(14).index
        fig = px.imshow((prof[top] * 100), text_auto=".0f", aspect="auto", color_continuous_scale=SEQ,
                        title="% of postings per role that require each skill", labels=dict(color="%"))
        fig.update_layout(xaxis_title="", yaxis_title="", coloraxis_showscale=False)
        show(style(fig, height=480))

    with t3:
        vocab = [s for s in skill_vocabulary() if s in set(count_skills(df, "required_skills").index)]
        default = [s for s in find_skills(st.session_state.resume_text, vocab)] if st.session_state.resume_text else []
        if default:
            st.caption("Pre-filled from your uploaded resume. Edit as you like.")
        owned = st.multiselect("Your skills", vocab, default=default)
        if not owned:
            st.info("Pick the skills you have to see which roles fit best.")
            return
        prof = role_profiles(df)
        mass = prof.sum(axis=1)
        score = (prof[[s for s in owned if s in prof.columns]].sum(axis=1) / mass * 100).sort_values()
        fig = px.bar(score.reset_index(), x=0, y="index", orientation="h", color_discrete_sequence=[BLUE],
                     title="Role fit score (share of the role's skill demand you cover)")
        fig.update_traces(hovertemplate="%{y}<br>%{x:.0f}%<extra></extra>")
        fig.update_layout(xaxis_title="Fit %", yaxis_title="")
        show(style(fig, height=420))
        best = score.index[-1]
        role = st.selectbox("Learning plan for role", score.index[::-1], index=0)
        gaps = prof.loc[role].drop(labels=owned, errors="ignore").sort_values(ascending=False).head(6)
        c = st.columns(2)
        c[0].metric("Best match", best, f"{score[best]:.0f}% fit")
        with c[1]:
            st.markdown(f"**Learn next for {role}**")
            st.markdown("".join(theme.pill(f"{s} · {v * 100:.0f}% of postings") for s, v in gaps.items()),
                        unsafe_allow_html=True)
