from datetime import datetime, timedelta, timezone
from nippon_signal.score import score_signal


def test_recent_launch_scores_higher_than_old_generic_story():
    now = datetime(2026, 9, 6, tzinfo=timezone.utc)

    recent = score_signal(
        "生成AIの新サービスを正式提供開始",
        "企業向けに導入",
        now - timedelta(hours=4),
        "AI",
        source_weight=1.0,
        now=now,
    )

    old = score_signal(
        "テクノロジーについて考える",
        "",
        now - timedelta(days=30),
        "Other",
        source_weight=0.8,
        now=now,
    )

    assert recent > old
    assert 0 <= recent <= 100
