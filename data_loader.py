"""Loads the 750-record fusion workbook and provides skill helpers."""
import re
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "career_fusion_datasets_750_records.xlsx"
FUSION_SHEET = "Fused_750_Records"
EXP_ORDER = ["Fresher", "0-1 years", "1-2 years", "2-3 years", "3-5 years", "5+ years"]
MATCH_ORDER = ["Low", "Partial", "Good"]

# Skills commonly found on real resumes, on top of the ones in the dataset
EXTRA_SKILLS = [
    "C++", "C#", "Go", "TypeScript", "Node.js", "Angular", "Vue", "Spring Boot", "FastAPI",
    "Kubernetes", "Jenkins", "CI/CD", "Terraform", "GCP", "MongoDB", "PostgreSQL", "Redis",
    "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision", "LLM", "LangChain",
    "Streamlit", "Spark", "Hadoop", "Kafka", "Airflow", "Statistics", "Data Visualization",
    "Cybersecurity", "Networking", "Leadership", "Problem Solving", "Teamwork", "Scrum",
]


def _clean_list(value) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    return [s.strip() for s in value.split(",") if s.strip()]


@st.cache_data(show_spinner="Loading fusion dataset...")
def _load(path: str, mtime: float) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(path, sheet_name=None)
    f = sheets[FUSION_SHEET].copy()
    f["matching_skills"] = f["matching_skills"].fillna("")
    f["missing_skills"] = f["missing_skills"].fillna("")
    f["salary_mid_inr"] = (f["salary_min_inr"] + f["salary_max_inr"]) / 2
    f["salary_max_lpa"] = f["salary_max_inr"] / 1e5
    f["salary_min_lpa"] = f["salary_min_inr"] / 1e5
    f["experience_level"] = pd.Categorical(f["experience_level"], EXP_ORDER, ordered=True)
    sheets[FUSION_SHEET] = f
    return sheets


def get_workbook() -> dict[str, pd.DataFrame]:
    """Returns all sheets. If the file is missing, asks the user to upload it."""
    if DATA_PATH.exists():
        return _load(str(DATA_PATH), DATA_PATH.stat().st_mtime)
    st.warning(f"Dataset not found at `{DATA_PATH}`. Upload the Excel file to continue.")
    up = st.file_uploader("career_fusion_datasets_750_records.xlsx", type=["xlsx"])
    if up is None:
        st.stop()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_bytes(up.getbuffer())
    st.rerun()


def get_fusion() -> pd.DataFrame:
    return get_workbook()[FUSION_SHEET]


def count_skills(df: pd.DataFrame, col: str) -> pd.Series:
    """How many rows mention each skill in a comma-separated column."""
    s = df[col].map(_clean_list).explode().dropna()
    return s.value_counts()


@st.cache_data(show_spinner=False)
def skill_vocabulary() -> list[str]:
    f = get_fusion()
    vocab = set(EXTRA_SKILLS)
    for col in ("required_skills", "candidate_skills"):
        vocab.update(count_skills(f, col).index)
    return sorted(vocab, key=str.lower)


def find_skills(text: str, vocab: list[str] | None = None) -> list[str]:
    """Skills from the vocabulary that appear in free text (whole-word match)."""
    if not text:
        return []
    vocab = vocab or skill_vocabulary()
    aliases = {"ML": "Machine Learning", "JS": "JavaScript", "DL": "Deep Learning",
               "PowerBI": "Power BI", "Scikit Learn": "Scikit-learn", "NodeJS": "Node.js",
               "ReactJS": "React", "Rest APIs": "REST API", "RESTful": "REST API",
               "Postgres": "PostgreSQL", "k8s": "Kubernetes"}
    found = set()
    low = text.lower()

    def present(term: str) -> bool:
        pat = r"(?<![A-Za-z0-9+#])" + re.escape(term.lower()) + r"(?![A-Za-z0-9+#])"
        return re.search(pat, low) is not None

    for s in vocab:
        if present(s):
            found.add(s)
    for alias, canon in aliases.items():
        if canon in vocab and present(alias):
            found.add(canon)
    return sorted(found, key=str.lower)


def role_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Rows = job titles, columns = skills, value = share of postings requiring the skill."""
    rows = {}
    for role, g in df.groupby("job_title"):
        counts = count_skills(g, "required_skills")
        rows[role] = counts / len(g)
    return pd.DataFrame(rows).T.fillna(0.0)
