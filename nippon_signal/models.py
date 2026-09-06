from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Article:
    source: str
    title: str
    url: str
    summary: str
    published_at: datetime
    category: str = "Other"
    signal_score: float = 0.0
    fingerprint: str = ""
