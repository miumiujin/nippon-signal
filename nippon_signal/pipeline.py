from pathlib import Path
import yaml

from .classify import classify
from .db import DEFAULT_DB, init_db, upsert_article
from .feeds import fetch_all
from .score import score_signal


DEFAULT_SOURCES = Path("config/sources.yaml")


def load_sources(path=DEFAULT_SOURCES):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]


def run_ingestion(sources_path=DEFAULT_SOURCES, db_path=DEFAULT_DB):
    init_db(db_path)
    sources = load_sources(sources_path)
    articles, errors = fetch_all(sources)
    source_map = {s["name"]: s for s in sources}

    inserted = 0
    for article in articles:
        source = source_map[article.source]
        article.category = classify(
            article.title,
            article.summary,
            default=source.get("default_category", "Other"),
        )
        article.signal_score = score_signal(
            article.title,
            article.summary,
            article.published_at,
            article.category,
            source_weight=float(source.get("weight", 1.0)),
        )
        inserted += int(upsert_article(article, db_path))

    return {
        "fetched": len(articles),
        "inserted": inserted,
        "duplicates": len(articles) - inserted,
        "errors": errors,
    }
