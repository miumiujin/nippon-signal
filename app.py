from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st
import yaml

from nippon_signal.classify import detect_tags
from nippon_signal.pipeline import run_ingestion
from nippon_signal.score import score_breakdown
from nippon_signal.ui_helpers import (
    CATEGORY_COLORS,
    CATEGORY_EMOJI,
    safe_text,
    short_text,
    translate_ja_to_zh_tw,
)


DB = Path("data/nippon_signal.db")
SOURCE_CONFIG = Path("config/sources.yaml")

st.set_page_config(
    page_title="Nippon Signal",
    page_icon="🇯🇵",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Noto Sans TC', 'Noto Sans JP', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 94% 4%, rgba(225,29,72,.14), transparent 24%),
                radial-gradient(circle at 8% 20%, rgba(14,165,233,.08), transparent 20%),
                linear-gradient(180deg, #06101f 0%, #071426 48%, #050d18 100%);
            color: #f8fafc;
        }

        .main .block-container {
            max-width: 1280px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,.09);
            background: linear-gradient(135deg, rgba(9,17,35,.97), rgba(15,23,42,.88));
            border-radius: 28px;
            padding: 30px 32px 26px;
            margin-bottom: 22px;
            box-shadow: 0 18px 50px rgba(0,0,0,.28);
        }

        .hero::after {
            content: "日";
            position: absolute;
            right: 34px;
            top: -26px;
            font-family: 'Noto Sans JP';
            font-size: 13rem;
            font-weight: 900;
            color: rgba(244,63,94,.055);
            line-height: 1;
            pointer-events: none;
        }

        .eyebrow {
            display:inline-block;
            color:#fda4af;
            font-size:.78rem;
            font-weight:800;
            letter-spacing:.14em;
            margin-bottom:10px;
        }

        .hero-title {
            font-size:3.1rem;
            line-height:1.05;
            font-weight:900;
            margin:0 0 12px;
        }

        .jp-accent { color:#f43f5e; }

        .hero-sub {
            max-width:930px;
            color:#cbd5e1;
            line-height:1.8;
            font-size:1rem;
        }

        .hero-note {
            margin-top:14px;
            color:#7dd3fc;
            font-size:.86rem;
        }

        .section-title {
            font-size:1.75rem;
            font-weight:900;
            margin:28px 0 8px;
        }

        .jp-kicker {
            color:#fb7185;
            font-size:.75rem;
            letter-spacing:.16em;
            font-weight:800;
            margin-bottom:5px;
        }

        .article-title a {
            color:#f8fafc !important;
            text-decoration:none !important;
            font-size:1.3rem;
            line-height:1.45;
            font-weight:800;
        }

        .article-title a:hover { color:#fda4af !important; }

        .meta {
            color:#94a3b8;
            font-size:.88rem;
            margin-top:8px;
        }

        .zh-box, .jp-box {
            border-radius:16px;
            padding:13px 15px;
            margin-top:12px;
            line-height:1.72;
        }

        .jp-box {
            background:rgba(255,255,255,.035);
            border:1px solid rgba(255,255,255,.065);
            color:#cbd5e1;
        }

        .zh-box {
            background:rgba(244,63,94,.065);
            border:1px solid rgba(244,63,94,.18);
            color:#f8fafc;
        }

        .box-label {
            font-size:.72rem;
            font-weight:800;
            letter-spacing:.1em;
            color:#fda4af;
            margin-bottom:6px;
        }

        .pill {
            display:inline-block;
            margin:10px 6px 0 0;
            padding:5px 10px;
            border-radius:999px;
            font-size:.78rem;
            font-weight:700;
            border:1px solid rgba(255,255,255,.1);
            background:rgba(255,255,255,.045);
        }

        .score-number {
            font-size:2.35rem;
            font-weight:900;
            line-height:1;
            margin:5px 0 8px;
        }

        .score-label {
            color:#94a3b8;
            font-size:.78rem;
            letter-spacing:.07em;
        }

        .breakdown {
            color:#cbd5e1;
            font-size:.76rem;
            line-height:1.7;
            margin-top:10px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background:linear-gradient(180deg, rgba(12,23,43,.91), rgba(7,17,32,.93));
            border:1px solid rgba(255,255,255,.08) !important;
            border-radius:22px !important;
            box-shadow:0 12px 30px rgba(0,0,0,.18);
        }

        section[data-testid="stSidebar"] {
            background:linear-gradient(180deg,#0c162b,#08111f);
            border-right:1px solid rgba(255,255,255,.06);
        }

        .stMultiSelect div[data-baseweb="tag"] {
            background:rgba(244,63,94,.18) !important;
            border:1px solid rgba(244,63,94,.28) !important;
        }

        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_source_weights() -> dict[str, float]:
    try:
        with open(SOURCE_CONFIG, "r", encoding="utf-8") as f:
            sources = yaml.safe_load(f)["sources"]
        return {s["name"]: float(s.get("weight", 1.0)) for s in sources}
    except Exception:
        return {}


@st.cache_resource
def bootstrap_database():
    if not DB.exists():
        return run_ingestion()
    return None


inject_css()

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">JAPAN TECHNOLOGY INTELLIGENCE / 日本科技訊號</div>
      <div class="hero-title">Nippon Signal <span class="jp-accent">JP→TW</span></div>
      <div class="hero-sub">
        從日本科技媒體與產業訊號中，整理 AI、機器人、半導體、能源、XR 與新創動向。
        保留日文原始脈絡，同時提供繁體中文輔助閱讀，目標不是做新聞聚合器，
        而是持續找出「日本已開始發生、台灣可能仍有落差」的產品與技術機會。
      </div>
      <div class="hero-note">読む → 見つける → 比べる → 作る</div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    bootstrap_result = bootstrap_database()
except Exception as exc:
    bootstrap_result = None
    st.error(f"第一次建立資料庫失敗：{exc}")

with st.sidebar:
    st.markdown("## 🇯🇵 Nippon Signal")
    st.caption("探索日本科技訊號")

    if st.button("↻ Refresh 最新資料", use_container_width=True):
        try:
            with st.spinner("正在更新日本科技訊號…"):
                result = run_ingestion()
            st.success(
                f"抓取 {result['fetched']} 則，新增 {result['inserted']} 則。"
            )
            st.cache_data.clear()
            st.rerun()
        except Exception as exc:
            st.error(f"更新失敗：{exc}")

if not DB.exists():
    st.warning("尚未建立資料庫。請按左側「Refresh 最新資料」重試。")
    st.stop()


@st.cache_data(ttl=300)
def read_articles():
    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query(
            """
            SELECT source, title, url, summary, published_at, category, signal_score
            FROM articles
            ORDER BY signal_score DESC, published_at DESC
            """,
            conn,
        )


df = read_articles()
if df.empty:
    st.info("目前沒有文章資料。請按左側 Refresh。")
    st.stop()

df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
df["summary"] = df["summary"].fillna("")
df["date"] = df["published_at"].dt.strftime("%Y-%m-%d %H:%M UTC")

source_weights = load_source_weights()

with st.sidebar:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected = st.multiselect("Category", categories, default=categories)
    min_score = st.slider("Minimum Signal Score", 0, 100, 35, 5)
    top_n = st.slider("顯示數量", 5, 50, 20, 5)
    show_translation = st.toggle("繁體中文翻譯", value=True)
    show_original_summary = st.toggle("日文摘要", value=True)

filtered = df[
    df["category"].isin(selected) & (df["signal_score"] >= min_score)
].copy()

m1, m2, m3 = st.columns(3)
m1.metric("SIGNALS", len(filtered))
m2.metric("SOURCES", filtered["source"].nunique())
m3.metric(
    "AVG SCORE",
    f"{filtered['signal_score'].mean():.1f}" if len(filtered) else "0.0",
)

st.markdown('<div class="section-title">注目のシグナル</div>', unsafe_allow_html=True)
st.caption("值得優先閱讀的日本科技訊號 · Ranked by Nippon Signal baseline")

if filtered.empty:
    st.info("目前沒有符合條件的訊號。")
    st.stop()

for _, row in filtered.head(top_n).iterrows():
    category = row["category"]
    emoji = CATEGORY_EMOJI.get(category, "📰")
    color = CATEGORY_COLORS.get(category, "#64748b")
    tags = detect_tags(row["title"], row["summary"])

    title_zh = translate_ja_to_zh_tw(row["title"]) if show_translation else ""
    summary_short = short_text(row["summary"], 300)
    summary_zh = (
        translate_ja_to_zh_tw(summary_short)
        if show_translation and summary_short
        else ""
    )

    published_dt = row["published_at"].to_pydatetime()
    breakdown = score_breakdown(
        row["title"],
        row["summary"],
        published_dt,
        category,
        source_weight=source_weights.get(row["source"], 1.0),
    )

    with st.container(border=True):
        left, right = st.columns([5.4, 1.15], gap="large")

        with left:
            st.markdown(
                f"""
                <div class="jp-kicker">{emoji} {safe_text(category)} / {safe_text(row["source"])}</div>
                <div class="article-title">
                  <a href="{safe_text(row["url"])}" target="_blank">
                    {safe_text(row["title"])}
                  </a>
                </div>
                <div class="meta">{safe_text(row["date"])}</div>
                """,
                unsafe_allow_html=True,
            )

            pills = []
            for tag in tags:
                tag_emoji = CATEGORY_EMOJI.get(tag, "•")
                tag_color = CATEGORY_COLORS.get(tag, "#64748b")
                pills.append(
                    f'<span class="pill" style="border-color:{tag_color}66;">'
                    f'{tag_emoji} {safe_text(tag)}</span>'
                )
            if pills:
                st.markdown("".join(pills), unsafe_allow_html=True)

            if show_translation and title_zh:
                zh_html = f"""
                <div class="zh-box">
                  <div class="box-label">繁體中文 / ZH-TW</div>
                  <strong>{safe_text(title_zh)}</strong>
                """
                if summary_zh:
                    zh_html += f"<div style='margin-top:8px'>{safe_text(summary_zh)}</div>"
                zh_html += "</div>"
                st.markdown(zh_html, unsafe_allow_html=True)

            if show_original_summary and summary_short:
                st.markdown(
                    f"""
                    <div class="jp-box">
                      <div class="box-label">ORIGINAL / 日本語</div>
                      {safe_text(summary_short)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with right:
            st.markdown(
                f"""
                <div class="score-label">SIGNAL SCORE</div>
                <div class="score-number">{row["signal_score"]:.1f}</div>
                <div class="breakdown">
                  新鮮度 {breakdown["recency"]:.0f}/35<br>
                  機會訊號 {breakdown["opportunity"]:.1f}/30<br>
                  類別 {breakdown["category"]:.0f}/20<br>
                  來源 {breakdown["source"]:.1f}/15
                </div>
                """,
                unsafe_allow_html=True,
            )

st.caption(
    "v0.1.2 · source-aware classification · multi-tags · zh-TW translation · deploy-ready"
)
