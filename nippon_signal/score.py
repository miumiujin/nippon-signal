from __future__ import annotations
from datetime import datetime, timezone
import re


OPPORTUNITY_TERMS = [
    "新サービス", "新製品", "新機能", "提供開始", "正式提供", "実証",
    "実証実験", "導入", "採用", "商用", "量産", "資金調達", "提携",
    "共同開発", "事業化", "発売", "開発", "スタートアップ",
    "launch", "pilot", "partnership", "funding",
]

HIGH_SIGNAL_CATEGORIES = {
    "AI", "Robotics", "Semiconductor", "Energy", "Mobility", "Gov/DX",
}


def _term_count(text: str) -> int:
    lower = text.lower()
    count = 0
    for term in OPPORTUNITY_TERMS:
        t = term.lower()
        if re.fullmatch(r"[a-z0-9+.-]+", t):
            if re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", lower):
                count += 1
        elif t in lower:
            count += 1
    return count


def score_breakdown(
    title: str,
    summary: str,
    published_at: datetime,
    category: str,
    source_weight: float = 1.0,
    now: datetime | None = None,
) -> dict[str, float]:
    now = now or datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    age_hours = max(0.0, (now - published_at).total_seconds() / 3600)

    if age_hours <= 24:
        recency = 35
    elif age_hours <= 72:
        recency = 30
    elif age_hours <= 168:
        recency = 24
    elif age_hours <= 336:
        recency = 15
    else:
        recency = 6

    opportunity = min(30.0, _term_count(f"{title} {summary}") * 7.5)
    category_score = (
        20.0 if category in HIGH_SIGNAL_CATEGORIES
        else 14.0 if category in {"XR", "Consumer Tech"}
        else 8.0
    )
    source = max(0.0, min(15.0, 15.0 * source_weight))
    total = min(100.0, recency + opportunity + category_score + source)

    return {
        "recency": float(recency),
        "opportunity": float(opportunity),
        "category": float(category_score),
        "source": float(source),
        "total": round(total, 1),
    }


def score_signal(
    title: str,
    summary: str,
    published_at: datetime,
    category: str,
    source_weight: float = 1.0,
    now: datetime | None = None,
) -> float:
    return score_breakdown(
        title,
        summary,
        published_at,
        category,
        source_weight=source_weight,
        now=now,
    )["total"]
