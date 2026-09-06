from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


DB = Path("data/nippon_signal.db")

st.set_page_config(page_title="Nippon Signal", page_icon="🇯🇵", layout="wide")
st.title("Nippon Signal 🇯🇵→🇹🇼")
st.caption("Japan technology signals — v0.1 baseline")

if not DB.exists():
    st.warning("Database not found. Run `nippon-signal ingest` first.")
    st.stop()

with sqlite3.connect(DB) as conn:
    df = pd.read_sql_query(
        """
        SELECT source, title, url, published_at, category, signal_score
        FROM articles
        ORDER BY signal_score DESC, published_at DESC
        """,
        conn,
    )

if df.empty:
    st.info("No articles yet. Run `nippon-signal ingest`.")
    st.stop()

categories = sorted(df["category"].dropna().unique().tolist())
selected = st.multiselect("Category", categories, default=categories)
filtered = df[df["category"].isin(selected)].copy()
filtered["published_at"] = pd.to_datetime(filtered["published_at"], errors="coerce")

c1, c2, c3 = st.columns(3)
c1.metric("Signals", len(filtered))
c2.metric("Sources", filtered["source"].nunique())
c3.metric("Average score", f"{filtered['signal_score'].mean():.1f}")

st.subheader("Top signals")

for _, row in filtered.head(50).iterrows():
    with st.container(border=True):
        left, right = st.columns([5, 1])
        with left:
            st.markdown(f"### [{row['title']}]({row['url']})")
            st.caption(f"{row['source']} · {row['category']} · {row['published_at']}")
        with right:
            st.metric("Signal", f"{row['signal_score']:.1f}")
