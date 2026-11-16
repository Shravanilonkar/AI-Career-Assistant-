"""Job Search: live API fusion, with offline fallback to the dataset."""
import plotly.express as px
import streamlit as st

import theme
from data_loader import get_fusion
from theme import BLUE, show, style


def _find_col(df, *needles):
    for c in df.columns:
        if any(n in c.lower() for n in needles):
            return c
    return None


def render():
    theme.page_header("Job Recommendations", "Search live jobs through your fusion API, or browse the dataset offline.", "💼")
    ss = st.session_state

    c = st.columns([3, 2, 1])
    keyword = c[0].text_input("Job title", placeholder="Example: Python Developer", label_visibility="collapsed")
    location = c[1].text_input("Location", value="India", label_visibility="collapsed")
    go_btn = c[2].button("🔎 Search", type="primary")
    offline = st.toggle("Use offline dataset instead of the live API", value=False)

    if go_btn:
        if not keyword:
            st.warning("Please enter a job title.")
        else:
            with st.spinner("Searching jobs..."):
                try:
                    if offline:
                        raise RuntimeError("offline mode")
                    from api.fusion import create_fusion_data
                    ss.jobs_df = create_fusion_data(keyword, location)
                    ss.jobs_source = "live"
                except Exception as e:
                    df = get_fusion()
                    m = df.job_title.str.contains(keyword, case=False, na=False)
                    if location and location.lower() != "india":
                        m &= df.location.str.contains(location, case=False, na=False)
                    ss.jobs_df = df[m].drop(columns=["salary_mid_inr", "salary_max_lpa", "salary_min_lpa"])
                    ss.jobs_source = "offline"
                    if str(e) != "offline mode":
                        st.warning(f"Live API unavailable ({e}). Showing matches from the dataset.")
            ss.jobs_query = keyword

    jobs = ss.jobs_df
    if jobs is None:
        st.info("Enter a job title and press Search.")
        return
    if jobs.empty:
        st.warning("No jobs found.")
        return

    st.success(f"Found {len(jobs)} jobs for **{ss.jobs_query}** ({ss.get('jobs_source', 'live')}).")
    q = st.text_input("Filter results", placeholder="Filter by any text: company, city, skill...")
    view = jobs
    if q:
        mask = jobs.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        view = jobs[mask]

    # charts built from whatever columns your API returns
    cc = _find_col(view, "company")
    lc = _find_col(view, "location", "city")
    sc = _find_col(view, "salary_max", "salary")
    ch = st.columns(2)
    with ch[0]:
        col = cc or lc
        if col and not view.empty:
            g = view[col].astype(str).value_counts().head(10).sort_values().reset_index()
            g.columns = [col, "jobs"]
            fig = px.bar(g, x="jobs", y=col, orientation="h", color_discrete_sequence=[BLUE], title=f"Jobs by {col}")
            fig.update_layout(xaxis_title="Jobs", yaxis_title="")
            show(style(fig, height=320))
    with ch[1]:
        if sc and view[sc].dtype.kind in "if" and not view.empty:
            fig = px.histogram(view, x=sc, nbins=15, color_discrete_sequence=[BLUE], title=f"Distribution of {sc}")
            fig.update_layout(yaxis_title="Jobs")
            show(style(fig, height=320))

    theme.table(view)
    st.download_button("⬇️ Download results (CSV)", view.to_csv(index=False), "fusion_jobs.csv", "text/csv")
