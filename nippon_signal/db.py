from __future__ import annotations
from pathlib import Path
import sqlite3

from .models import Article


DEFAULT_DB = Path("data/nippon_signal.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL,
    category TEXT NOT NULL,
    signal_score REAL NOT NULL DEFAULT 0,
    fingerprint TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at
ON articles(published_at DESC);

CREATE INDEX IF NOT EXISTS idx_articles_signal_score
ON articles(signal_score DESC);
"""


def connect(db_path=DEFAULT_DB):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DEFAULT_DB):
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_article(article: Article, db_path=DEFAULT_DB) -> bool:
    sql = """
    INSERT OR IGNORE INTO articles (
        source, title, url, summary, published_at, category, signal_score, fingerprint
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with connect(db_path) as conn:
        cursor = conn.execute(
            sql,
            (
                article.source,
                article.title,
                article.url,
                article.summary,
                article.published_at.isoformat(),
                article.category,
                article.signal_score,
                article.fingerprint,
            ),
        )
        return cursor.rowcount == 1


def top_articles(limit=20, db_path=DEFAULT_DB):
    with connect(db_path) as conn:
        return conn.execute(
            """
            SELECT source, title, url, summary, published_at, category, signal_score
            FROM articles
            ORDER BY signal_score DESC, published_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
