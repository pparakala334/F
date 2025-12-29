from app.algorithm.service import calculate_tiers


def test_calculate_tiers():
    tiers = calculate_tiers(100000)
    assert [tier.name for tier in tiers] == ["low", "medium", "high"]
    assert tiers[0].multiple == 1.2
    assert tiers[1].months == 30
    assert "Max raise" in tiers[0].explanation
