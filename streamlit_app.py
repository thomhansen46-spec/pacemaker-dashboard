import streamlit as st
st.set_page_config(
    page_title="Pacemaker Regulatory Intelligence Dashboard",
    layout="wide"
)

st.title("Pacemaker Regulatory Intelligence Dashboard")
st.markdown("### PMA Approvals & Competitive Intelligence Console")
import os
import duckdb
import pandas as pd
import plotly.express as px
from datetime import date

from src.openfda_pma import build_search_query, fetch_openfda_pma, year_chunks

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "cache.duckdb")
TABLE = "pma_cache"

DEFAULT_BRANDS = [
    "Micra", "Azure", "Advisa", "Adapta",
    "AVEIR", "Assurity", "Endurity",
    "Accolade", "Essentio",
    "Edora", "Eluna",
]

def ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            pma_number VARCHAR,
            supplement_number VARCHAR,
            supplement_type VARCHAR,
            applicant VARCHAR,
            trade_name VARCHAR,
            generic_name VARCHAR,
            product_code VARCHAR,
            decision_code VARCHAR,
            decision_date VARCHAR,
            _ingested_at TIMESTAMP DEFAULT now()
        );
    """)
    return con

def upsert(con, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    keep = ["pma_number","supplement_number","supplement_type","applicant","trade_name","generic_name",
            "product_code","decision_code","decision_date"]
    for c in keep:
        if c not in df.columns:
            df[c] = None
    df = df[keep].drop_duplicates()

    con.register("incoming", df)
    before = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    con.execute(f"""
        INSERT INTO {TABLE}
        SELECT i.*
        FROM incoming i
        LEFT JOIN {TABLE} t
          ON COALESCE(t.pma_number,'') = COALESCE(i.pma_number,'')
         AND COALESCE(t.supplement_number,'') = COALESCE(i.supplement_number,'')
         AND COALESCE(t.decision_date,'') = COALESCE(i.decision_date,'')
        WHERE t.pma_number IS NULL;
    """)
    after = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    return after - before

def load_cached(con) -> pd.DataFrame:
    df = con.execute(f"SELECT * FROM {TABLE}").df()
    if df.empty:
        return df
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce")
    df = df.dropna(subset=["decision_date"])
    df["year"] = df["decision_date"].dt.year.astype(int)
    df["is_supplement"] = df["supplement_number"].fillna("").astype(str).str.strip().ne("")
    return df

st.subheader("Live FDA PMA Approvals (openFDA)")

with st.sidebar:
    st.header("PMA Filters")
    today = date.today()
    d_from = st.date_input("Decision date from", value=date(today.year - 5, 1, 1))
    d_to = st.date_input("Decision date to", value=today)

    brand_terms = st.text_area("Brand terms (one per line)", value="\n".join(DEFAULT_BRANDS), height=160).splitlines()
    brand_terms = [b.strip() for b in brand_terms if b.strip()]

    product_codes = st.text_input("Optional product codes (comma-separated)", value="")
    product_codes = [c.strip().upper() for c in product_codes.split(",") if c.strip()]

    include_supplements = st.checkbox("Include supplements", value=True)
    refresh = st.button("Fetch / Refresh PMA data")

api_key = st.secrets.get("FDA_API_KEY", "")

con = ensure_db()

if refresh:
    added_total = 0
    for (yf, yt) in year_chunks(d_from, d_to):
        q = build_search_query(yf, yt, brand_terms, product_codes or None)
       df_new = fetch_openfda_pma(q, api_key=api_key, max_records=3000, page_size=200)
    st.success(f"Done. New rows added: {added_total}")

df = load_cached(con)

if df.empty:
    st.info("No PMA data cached yet. Click **Fetch / Refresh PMA data** in the sidebar.")
else:
    df = df[(df["decision_date"].dt.date >= d_from) & (df["decision_date"].dt.date <= d_to)]
    if not include_supplements:
        df = df[~df["is_supplement"]]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", f"{len(df):,}")
    c2.metric("Applicants", f"{df['applicant'].nunique():,}")
    c3.metric("Unique PMAs", f"{df['pma_number'].nunique():,}")
    c4.metric("Supplement share", f"{(df['is_supplement'].mean()*100):.1f}%")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("**Approvals by Year**")
        by_year = df.groupby("year").size().reset_index(name="approvals").sort_values("year")
        st.plotly_chart(px.bar(by_year, x="year", y="approvals"), use_container_width=True)

    with colB:
        st.markdown("**Approvals by Company (Applicant)**")
        by_app = df.groupby("applicant").size().reset_index(name="approvals").sort_values("approvals", ascending=False).head(20)
        st.plotly_chart(px.bar(by_app, x="approvals", y="applicant", orientation="h"), use_container_width=True)

    st.markdown("**PMA Detail (filtered)**")
    show = ["decision_date","year","applicant","trade_name","generic_name","product_code","pma_number","supplement_number","supplement_type"]
    st.dataframe(df[show].sort_values("decision_date", ascending=False), use_container_width=True)
