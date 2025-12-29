from uuid import uuid4
from sqlalchemy.orm import Session

from app.settings import settings
from app.models import LedgerEntry


def _record_simulated(db: Session, entry_type: str, amount_cents: int, meta: str) -> None:
    entry = LedgerEntry(entry_type=entry_type, amount_cents=amount_cents, metadata_json=meta)
    db.add(entry)
    db.commit()


def _demo_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def charge_application_fee(db: Session, founder_id: int, amount_cents: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payment_id = _demo_id("pay_demo")
        _record_simulated(db, "application_fee", amount_cents, f"founder={founder_id}")
        return payment_id
    return _demo_id("pay_stripe")


def create_connected_account(db: Session, founder_id: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        account_id = _demo_id("acct_demo")
        _record_simulated(db, "connected_account", 0, f"founder={founder_id}")
        return account_id
    return _demo_id("acct_stripe")


def collect_investment(db: Session, investor_id: int, round_id: int, amount_cents: int) -> str:
    platform_fee_cents = int(amount_cents * 0.02)
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payment_id = _demo_id("pay_demo")
        _record_simulated(db, "investment", amount_cents, f"investor={investor_id} round={round_id}")
        _record_simulated(db, "platform_fee", platform_fee_cents, f"investor={investor_id}")
        return payment_id
    return _demo_id("pay_stripe")


def payout_investor(db: Session, investor_id: int, amount_cents: int) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        payout_id = _demo_id("po_demo")
        _record_simulated(db, "payout", amount_cents, f"investor={investor_id}")
        return payout_id
    return _demo_id("po_stripe")
