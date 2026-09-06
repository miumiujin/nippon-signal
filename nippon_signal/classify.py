from __future__ import annotations
import re


CATEGORY_KEYWORDS = {
    "AI": [
        "ai", "人工知能", "生成ai", "生成 ai", "llm", "大規模言語モデル",
        "機械学習", "ディープラーニング", "agent", "エージェント", "基盤モデル",
    ],
    "Robotics": [
        "ロボット", "robot", "ヒューマノイド", "自律", "協働ロボット",
        "フィジカルai", "physical ai",
    ],
    "Semiconductor": [
        "半導体", "チップ", "chip", "gpu", "npu", "ファウンドリ",
        "先端プロセス", "パワー半導体",
    ],
    "Energy": [
        "エネルギー", "電力", "蓄電池", "太陽光", "再生可能", "再エネ",
        "水素", "電池", "battery", "grid", "系統", "脱炭素",
    ],
    "Mobility": [
        "自動運転", "モビリティ", "ev", "電気自動車", "車載", "adas",
        "ドローン", "物流",
    ],
    "XR": [
        "vr", "ar", "xr", "メタバース", "空間コンピューティング",
        "virtual reality", "augmented reality",
    ],
    "Consumer Tech": [
        "スマートフォン", "スマホ", "ウェアラブル", "ガジェット",
        "デバイス", "イヤホン", "スマートグラス",
    ],
    "Gov/DX": [
        "デジタル庁", "行政", "自治体", "政府", "dx",
        "デジタルトランスフォーメーション", "ガバメントai",
        "規制", "ガイドライン",
    ],
}


def _matches(text: str, keyword: str) -> bool:
    k = keyword.lower()
    if re.fullmatch(r"[a-z0-9+.-]{1,4}", k):
        return re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", text) is not None
    return k in text


def classify(title: str, summary: str = "", default: str = "Other") -> str:
    text = f"{title} {summary}".lower()
    scores = {
        category: sum(1 for kw in keywords if _matches(text, kw))
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category, best_score = max(scores.items(), key=lambda item: item[1])
    return best_category if best_score > 0 else default
