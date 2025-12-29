from app.algorithm.service import calculate_tiers


def test_monotonicity():
    tiers = calculate_tiers(100000, risk_level="high")
    low = next(t for t in tiers if t.name == "low")
    high = next(t for t in tiers if t.name == "high")
    assert high.revenue_share_bps >= low.revenue_share_bps
    assert high.payout_cap_mult >= low.payout_cap_mult


def test_invariants():
    tiers = calculate_tiers(250000, risk_level="low")
    for tier in tiers:
        assert tier.payout_cap_mult >= 1.0
        assert tier.min_hold_days <= tier.time_cap_months * 30
