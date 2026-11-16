"""Data Explorer: the fusion dataset, source sheets, candidate lookup, architecture."""
import plotly.express as px
import streamlit as st

import theme
from data_loader import get_workbook
from theme import BLUE, show, style

SOURCES = {
    "Adzuna_Sample": ("Adzuna", "Job listings: title, company, location, salary"),
    "MUSE_Sample": ("The Muse", "Role skills, experience level, career pathway"),
    "Groq_Sample": ("Groq LLM", "ATS score, missing skills, feedback, interview questions"),
    "Gemini_Sample": ("Gemini", "Matching/missing skills and career guidance"),
    "Whisper_Sample": ("Whisper", "Speech-to-text transcripts of candidate voice input"),
}


def render():
    theme.page_header("Data Explorer", "Browse the fused dataset, every source API sheet, and individual candidates.", "🔗")
    wb = get_workbook()
    df = wb["Fused_750_Records"]
    t1, t2, t3, t4 = st.tabs(["Fused dataset", "Source sheets", "Candidate lookup", "Architecture"])

    with t1:
        q = st.text_input("Search", placeholder="Search any text: role, company, skill, candidate...")
        cols = st.multiselect("Columns", list(df.columns), default=[
            "record_id", "candidate_name", "job_title", "company_name", "location", "ats_score",
            "skill_match_percentage", "salary_min_inr", "salary_max_inr", "data_status"])
        view = df
        if q:
            m = df.astype(str).apply(lambda c: c.str.contains(q, case=False, na=False)).any(axis=1)
            view = df[m]
        st.caption(f"{len(view)} of {len(df)} records")
        theme.table(view[cols] if cols else view)
        st.download_button("⬇️ Download fused dataset (CSV)", view.to_csv(index=False), "fusion_dataset.csv", "text/csv")

    with t2:
        name = st.selectbox("Sheet", list(SOURCES), format_func=lambda s: f"{SOURCES[s][0]} · {s}")
        st.caption(SOURCES[name][1])
        theme.table(wb[name])
        if name == "Whisper_Sample":
            st.info(wb[name].transcription_note.iloc[0])

    with t3:
        ids = sorted(df.resume_id.unique())
        rid = st.selectbox("Resume ID", ids)
        sub = df[df.resume_id == rid]
        c0 = sub.iloc[0]
        k = st.columns(4)
        k[0].metric("Candidate", c0.candidate_name)
        k[1].metric("Education", c0.education)
        k[2].metric("Experience", f"{c0.experience_years} yrs")
        k[3].metric("Job matches", len(sub))
        st.markdown("**Skills** " + "".join(theme.pill(s.strip()) for s in c0.candidate_skills.split(",")),
                    unsafe_allow_html=True)
        fig = px.bar(sub.sort_values("ats_score"), x="ats_score", y="job_title", orientation="h",
                     color_discrete_sequence=[BLUE], title="ATS score per job matched",
                     hover_data=["company_name", "location", "skill_match_percentage"])
        fig.update_layout(xaxis_title="ATS score", yaxis_title="")
        show(style(fig, height=max(240, 50 * len(sub) + 80)))
        theme.table(sub[["job_title", "company_name", "location", "ats_score", "skill_match_percentage",
                         "missing_skills", "analysis_feedback"]])

    with t4:
        st.markdown("""
**How the fusion works**

| Step | Source | Adds |
|---|---|---|
| 1 | **Adzuna** | live job listings and salaries |
| 2 | **The Muse** | role skill requirements and career pathways |
| 3 | **Groq LLM** | ATS score, feedback, interview questions |
| 4 | **Gemini** | matching / missing skills and guidance |
| 5 | **Whisper** | voice question transcripts |
| → | **Fusion** | one record per candidate × job, joined on `record_id` |
""")
        g = df.fusion_sources.value_counts().reset_index()
        g.columns = ["sources", "records"]
        fig = px.bar(g, x="records", y="sources", orientation="h", color_discrete_sequence=[BLUE],
                     title="Records per source combination")
        fig.update_layout(xaxis_title="Records", yaxis_title="")
        show(style(fig, height=260))
