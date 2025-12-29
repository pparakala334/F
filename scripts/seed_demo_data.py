from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import User, Startup, StartupApplication, Round, TierOption, Investment, Contract, Distribution, ServiceProvider
from app.auth.security import hash_password
from app.algorithm.service import calculate_tiers


def seed():
    db: Session = SessionLocal()
    if db.query(User).first():
        print("Seed already applied")
        return

    admin = User(email="admin@demo.com", hashed_password=hash_password("password"), role="admin", country="CA")
    founder = User(email="founder@demo.com", hashed_password=hash_password("password"), role="founder", country="CA")
    investor = User(email="investor@demo.com", hashed_password=hash_password("password"), role="investor", country="CA")
    db.add_all([admin, founder, investor])
    db.commit()

    app = StartupApplication(founder_id=founder.id, status="approved", company_name="Nimbus Health", description="AI scheduling")
    db.add(app)
    startup = Startup(founder_id=founder.id, name="Nimbus Health", country="CA")
    db.add(startup)
    db.commit()

    draft_round = Round(startup_id=startup.id, status="draft", max_raise_cents=2500000)
    db.add(draft_round)
    db.commit()
    db.refresh(draft_round)

    tiers = calculate_tiers(draft_round.max_raise_cents)
    for tier in tiers:
        db.add(
            TierOption(
                round_id=draft_round.id,
                tier=tier.name,
                multiple=tier.multiple,
                revenue_share_percent=tier.revenue_share_percent,
                months=tier.months,
                explanation=tier.explanation,
            )
        )
    db.commit()

    published_round = Round(startup_id=startup.id, status="published", max_raise_cents=5000000, selected_tier="high")
    db.add(published_round)
    db.commit()

    investment = Investment(investor_id=investor.id, round_id=published_round.id, amount_cents=500000)
    db.add(investment)
    db.commit()
    contract = Contract(investment_id=investment.id, payout_cap_multiple=1.5, months_cap=30, min_hold_months=6, status="active", total_paid_cents=10000)
    db.add(contract)
    db.commit()
    distribution = Distribution(contract_id=contract.id, amount_cents=10000)
    db.add(distribution)

    providers = [
        ServiceProvider(name="Maple Legal", category="Legal", description="Startup-friendly counsel."),
        ServiceProvider(name="Northwind Finance", category="Finance", description="Fractional CFO services."),
        ServiceProvider(name="Signal Growth", category="Marketing", description="Growth analytics for fintech."),
    ]
    db.add_all(providers)
    db.commit()

    print("Seed complete")


if __name__ == "__main__":
    seed()
