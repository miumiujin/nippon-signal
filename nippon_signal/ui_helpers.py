from __future__ import annotations

from functools import lru_cache
import html
import re

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover
    GoogleTranslator = None

try:
    from opencc import OpenCC
    _to_tw = OpenCC("s2twp")
except Exception:  # pragma: no cover
    _to_tw = None


CATEGORY_EMOJI = {
    "AI": "🤖",
    "Robotics": "🦾",
    "Semiconductor": "💠",
    "Energy": "⚡",
    "Mobility": "🚄",
    "XR": "🥽",
    "Consumer Tech": "📱",
    "Gov/DX": "🏛️",
    "Other": "📰",
}

CATEGORY_COLORS = {
    "AI": "#7c3aed",
    "Robotics": "#0ea5e9",
    "Semiconductor": "#14b8a6",
    "Energy": "#f59e0b",
    "Mobility": "#10b981",
    "XR": "#ec4899",
    "Consumer Tech": "#6366f1",
    "Gov/DX": "#f97316",
    "Other": "#64748b",
}


def safe_text(text: str) -> str:
    return html.escape(str(text or ""))


def short_text(text: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


@lru_cache(maxsize=1024)
def translate_ja_to_zh_tw(text: str) -> str:
    """Best-effort free translation. Never expose provider errors in the UI."""
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text or GoogleTranslator is None:
        return ""

    try:
        # zh-CN is more consistently supported by the unofficial translator;
        # OpenCC then converts it to Taiwan Traditional Chinese wording.
        result = GoogleTranslator(source="ja", target="zh-CN").translate(text)
        if not result:
            return ""
        if "No translation was found" in result:
            return ""
        return _to_tw.convert(result) if _to_tw is not None else result
    except Exception:
        return ""
