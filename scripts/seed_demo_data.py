from app.db import SessionLocal
from app.models import User, Startup, Application, Round, TierOption
from app.auth.security import hash_password
from app.algorithm.service import calculate_tiers
from app.settings import settings
import json


def seed():
    db = SessionLocal()
    if db.query(User).first():
        print("Seed already applied")
        return

    admin = User(
        email=settings.admin_email,
        hashed_password=hash_password(settings.admin_password),
        role="admin",
        country="CA",
    )
    founder = User(email="founder@demo.com", hashed_password=hash_password("password"), role="founder", country="CA")
    investor = User(email="investor@demo.com", hashed_password=hash_password("password"), role="investor", country="CA")
    db.add_all([admin, founder, investor])
    db.commit()

    startup = Startup(
        founder_user_id=founder.id,
        legal_name="Steelman Industries",
        operating_name="Steelman",
        country="CA",
        incorporation_type="Corp",
        incorporation_date="2021-01-01",
        website="https://steelman.example",
        logo_key=None,
        industry="Fintech",
        sub_industry="Revenue share",
        short_description="Compliance-first revenue-share platform.",
        long_description="A revenue-share marketplace for aligned capital.",
        current_monthly_revenue="$25k-$50k",
        revenue_model="SaaS",
        revenue_consistency="Stable",
        revenue_stage="Stable",
        existing_debt=0,
        existing_investors=1,
        intended_use_of_funds=json.dumps(["Hiring", "Product"]),
        target_funding_size="$250k-$1M",
        preferred_timeline="3-6 months",
        status="draft",
    )
    db.add(startup)
    db.commit()

    application = Application(
        startup_id=startup.id,
        name="Initial Funding Application",
        application_type="Initial Funding Application",
        requested_limit_cents=5000000,
        risk_preference="medium",
        status="approved",
    )
    db.add(application)
    db.commit()

    round_obj = Round(
        startup_id=startup.id,
        application_id=application.id,
        title="Revenue Share Round",
        max_raise_cents=5000000,
        status="published",
        tier_selected="medium",
    )
    db.add(round_obj)
    db.commit()

    for tier in calculate_tiers(round_obj.max_raise_cents):
        db.add(
            TierOption(
                round_id=round_obj.id,
                tier=tier.name,
                revenue_share_bps=tier.revenue_share_bps,
                time_cap_months=tier.time_cap_months,
                payout_cap_mult=tier.payout_cap_mult,
                min_hold_days=tier.min_hold_days,
                exit_fee_bps_quarterly=tier.exit_fee_bps_quarterly,
                exit_fee_bps_offcycle=tier.exit_fee_bps_offcycle,
                explanation_json=tier.explanation_json,
            )
        )
    db.commit()
    print("Seed complete")


if __name__ == "__main__":
    seed()
