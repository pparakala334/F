from uuid import uuid4
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import LedgerEntry


def _record_simulated(db: Session, entry_type: str, amount_cents: int, meta: str) -> None:
    entry = LedgerEntry(entry_type=entry_type, amount_cents=amount_cents, currency="CAD", meta=meta)
    db.add(entry)
    db.commit()


def charge_application_fee(db: Session, founder_id: int, amount_cents: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payment_id = f"sim_app_fee_{uuid4().hex[:8]}"
        _record_simulated(db, "application_fee", amount_cents, f"simulated founder {founder_id}")
        return payment_id
    return f"stripe_app_fee_{uuid4().hex[:8]}"


def create_connected_account(db: Session, founder_id: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        account_id = f"sim_connect_{uuid4().hex[:8]}"
        _record_simulated(db, "connected_account", 0, f"simulated founder {founder_id}")
        return account_id
    return f"stripe_connect_{uuid4().hex[:8]}"


def collect_investment(db: Session, investor_id: int, round_id: int, amount_cents: int) -> str:
    platform_fee_cents = int(amount_cents * 0.02)
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payment_id = f"sim_invest_{uuid4().hex[:8]}"
        _record_simulated(db, "investment", amount_cents, f"simulated investor {investor_id} round {round_id}")
        _record_simulated(db, "platform_fee", platform_fee_cents, f"simulated investor {investor_id}")
        return payment_id
    return f"stripe_invest_{uuid4().hex[:8]}"


def payout_investor(db: Session, investor_id: int, amount_cents: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payout_id = f"sim_payout_{uuid4().hex[:8]}"
        _record_simulated(db, "payout", amount_cents, f"simulated investor {investor_id}")
        return payout_id
    return f"stripe_payout_{uuid4().hex[:8]}"
