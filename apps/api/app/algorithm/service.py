from dataclasses import dataclass


@dataclass
class Tier:
    name: str
    multiple: float
    revenue_share_percent: float
    months: int
    explanation: str


def calculate_tiers(max_raise_cents: int) -> list[Tier]:
    base = max(50000, max_raise_cents)
    tiers = [
        Tier(
            name="low",
            multiple=1.2,
            revenue_share_percent=4.0,
            months=24,
            explanation="Lower cap, shorter duration for conservative founders.",
        ),
        Tier(
            name="medium",
            multiple=1.5,
            revenue_share_percent=6.0,
            months=30,
            explanation="Balanced cap with moderate revenue share.",
        ),
        Tier(
            name="high",
            multiple=1.8,
            revenue_share_percent=8.0,
            months=36,
            explanation="Higher cap to align with higher return expectations.",
        ),
    ]
    for tier in tiers:
        tier.explanation += f" Max raise baseline: ${base/100:,.0f}."
    return tiers
