from nippon_signal.classify import classify


def test_ai_classification():
    assert classify("生成AIエージェントの新サービスを提供開始") == "AI"


def test_robotics_classification():
    assert classify("ヒューマノイドロボットの実証実験") == "Robotics"


def test_energy_classification():
    assert classify("蓄電池を活用した電力需給システム") == "Energy"


def test_default_category():
    assert classify("まったく別の話題", default="XR") == "XR"
