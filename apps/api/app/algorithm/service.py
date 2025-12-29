from dataclasses import dataclass
import json


@dataclass
class Tier:
    name: str
    revenue_share_bps: int
    time_cap_months: int
    payout_cap_mult: float
    min_hold_days: int
    exit_fee_bps_quarterly: int
    exit_fee_bps_offcycle: int
    explanation_json: str


def calculate_tiers(
    max_raise_cents: int,
    risk_level: str = "medium",
    baseline_monthly_revenue_cents: int | None = None,
    stage: str = "seed",
) -> list[Tier]:
    base_raise = max(250000, max_raise_cents)
    risk_multiplier = {"low": 0.9, "medium": 1.0, "high": 1.15}.get(risk_level, 1.0)
    stage_bias = {"seed": 1.05, "growth": 0.95}.get(stage, 1.0)
    base_share = int(350 * risk_multiplier * stage_bias)
    base_cap = 1.3 if stage == "growth" else 1.5

    tiers = []
    for name, share_bps, months, cap_mult, min_hold in [
        ("low", int(base_share * 0.8), 18, base_cap, 60),
        ("medium", base_share, 24, base_cap + 0.2, 90),
        ("high", int(base_share * 1.25), 30, base_cap + 0.4, 120),
    ]:
        explanation = {
            "summary": "Tier balances revenue share with time and payout caps.",
            "max_raise": base_raise,
            "risk_level": risk_level,
            "stage": stage,
            "baseline_monthly_revenue_cents": baseline_monthly_revenue_cents,
            "why": f"{name.title()} tier adjusts revenue share and cap based on risk and stage.",
        }
        tiers.append(
            Tier(
                name=name,
                revenue_share_bps=share_bps,
                time_cap_months=months,
                payout_cap_mult=cap_mult,
                min_hold_days=min_hold,
                exit_fee_bps_quarterly=50,
                exit_fee_bps_offcycle=150,
                explanation_json=json.dumps(explanation),
            )
        )
    return tiers
