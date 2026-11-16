"""Resume Report: LLM analysis + instant local skill match and health check."""
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import theme
from core import require_docs
from data_loader import find_skills
from theme import BLUE, CAT, show, style

SECTIONS = {
    "Summary / objective": r"\b(summary|objective|profile)\b",
    "Education": r"\beducation\b",
    "Experience": r"\b(experience|employment|internship)\b",
    "Projects": r"\bprojects?\b",
    "Skills": r"\bskills\b",
    "Certifications": r"\b(certification|certificate|courses?)\b",
}


def health_checks(text: str) -> pd.DataFrame:
    low = text.lower()
    words = len(text.split())
    checks = [
        ("Email address", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)), "Add a professional email"),
        ("Phone number", bool(re.search(r"(\+?\d[\d\s-]{8,}\d)", text)), "Add a contact number"),
        ("LinkedIn / GitHub", bool(re.search(r"linkedin|github", low)), "Link your profiles"),
        ("Length 250–900 words", 250 <= words <= 900, f"Currently {words} words"),
        ("Quantified achievements", len(re.findall(r"\d+\s?%|\d+\+|\b\d{2,}\b", text)) >= 3,
         "Add numbers: %, users, time saved"),
        ("Action verbs", len(re.findall(r"\b(built|developed|designed|led|implemented|created|improved|"
                                        r"optimized|deployed|automated|analy[sz]ed)\b", low)) >= 4,
         "Start bullets with verbs like built, led, optimized"),
    ]
    for name, pat in SECTIONS.items():
        checks.append((f"Section: {name}", bool(re.search(pat, low)), f"Add a clear '{name}' section"))
    return pd.DataFrame(checks, columns=["Check", "Passed", "Tip"])


def render():
    theme.page_header("Resume Report", "AI analysis plus an instant skill-match and ATS-style health check.", "📝")
    if not require_docs():
        return
    ss = st.session_state
    resume_skills = set(find_skills(ss.resume_text))
    job_skills = find_skills(ss.job_text)
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    score = round(len(matched) / len(job_skills) * 100) if job_skills else 0
    health = health_checks(ss.resume_text)
    hscore = round(health.Passed.mean() * 100)

    k = st.columns(4)
    k[0].metric("Skill match vs job", f"{score}%")
    k[1].metric("Skills matched", len(matched))
    k[2].metric("Skills missing", len(missing))
    k[3].metric("Resume health", f"{hscore}%")

    t1, t2, t3 = st.tabs(["🤖 AI analysis", "🎯 Skill match", "✅ Health check"])

    with t1:
        st.write(ss.analysis)
        st.download_button("⬇️ Download analysis", str(ss.analysis), "resume_analysis.txt")

    with t2:
        if not job_skills:
            st.info("No known skills were detected in the job description text.")
        else:
            a, b = st.columns([3, 2])
            with a:
                rows = [(s, 1, "In your resume") for s in matched] + [(s, 1, "Missing") for s in missing]
                d = pd.DataFrame(rows, columns=["Skill", "v", "Status"])
                fig = go.Figure()
                for status, color in (("In your resume", BLUE), ("Missing", CAT[1])):
                    sub = d[d.Status == status]
                    fig.add_trace(go.Bar(y=sub.Skill, x=sub.v, name=status, orientation="h", marker_color=color,
                                         hovertemplate="%{y}: " + status + "<extra></extra>"))
                fig.update_layout(title="Skills the job asks for", barmode="stack")
                fig.update_xaxes(visible=False)
                fig.update_yaxes(autorange="reversed")
                show(style(fig, height=max(260, 28 * len(job_skills) + 80), legend=True))
            with b:
                st.markdown("**Matched**")
                st.markdown("".join(theme.pill(s, True) for s in matched) or "_none_", unsafe_allow_html=True)
                st.markdown("**Missing: learn these next**")
                st.markdown("".join(theme.pill(s, False) for s in missing) or "_none 🎉_", unsafe_allow_html=True)
                extra = sorted(resume_skills - set(job_skills))
                st.markdown("**Extra skills on your resume**")
                st.markdown("".join(theme.pill(s) for s in extra) or "_none_", unsafe_allow_html=True)
        st.caption("Detected by keyword matching against a skill list built from the dataset, not by the LLM.")

    with t3:
        view = health.copy()
        view["Result"] = view.Passed.map({True: "✅ Pass", False: "⚠️ Improve"})
        view["Tip"] = view.apply(lambda r: "" if r.Passed else r.Tip, axis=1)
        theme.table(view[["Check", "Result", "Tip"]])
