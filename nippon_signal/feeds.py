from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import re
from typing import Iterable

import feedparser
import requests
from dateutil import parser as date_parser

from .models import Article


TAG_RE = re.compile(r"<[^>]+>")


def clean_html(value: str | None) -> str:
    value = TAG_RE.sub(" ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()


def canonicalize_url(url: str) -> str:
    if "?" not in url:
        return url.strip()

    base, query = url.split("?", 1)
    kept = []
    for token in query.split("&"):
        key = token.split("=", 1)[0].lower()
        if key.startswith("utm_") or key in {"fbclid", "gclid"}:
            continue
        kept.append(token)
    return base if not kept else base + "?" + "&".join(kept)


def fingerprint_for(title: str, url: str) -> str:
    normalized_title = re.sub(r"\s+", " ", title).strip().lower()
    payload = f"{canonicalize_url(url)}|{normalized_title}"
    return sha256(payload.encode("utf-8")).hexdigest()


def parse_date(entry) -> datetime:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = date_parser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except (ValueError, TypeError, OverflowError):
                pass
    return datetime.now(timezone.utc)


def fetch_feed(source: dict, timeout: int = 20) -> list[Article]:
    headers = {"User-Agent": "NipponSignal/0.1"}
    response = requests.get(source["url"], headers=headers, timeout=timeout)
    response.raise_for_status()
    parsed = feedparser.parse(response.content)

    articles = []
    for entry in parsed.entries:
        title = clean_html(entry.get("title"))
        url = canonicalize_url(entry.get("link", "").strip())
        summary = clean_html(entry.get("summary") or entry.get("description"))

        if not title or not url:
            continue

        articles.append(
            Article(
                source=source["name"],
                title=title,
                url=url,
                summary=summary[:1200],
                published_at=parse_date(entry),
                fingerprint=fingerprint_for(title, url),
            )
        )
    return articles


def fetch_all(sources: Iterable[dict]):
    articles = []
    errors = []
    for source in sources:
        try:
            articles.extend(fetch_feed(source))
        except Exception as exc:
            errors.append((source.get("name", "unknown"), str(exc)))
    return articles, errors
