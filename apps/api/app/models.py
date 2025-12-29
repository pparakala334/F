from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(2), default="CA")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Startup(Base):
    __tablename__ = "startups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    founder_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    legal_name: Mapped[str] = mapped_column(String(255))
    operating_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str] = mapped_column(String(2), default="CA")
    incorporation_type: Mapped[str] = mapped_column(String(50))
    incorporation_date: Mapped[str] = mapped_column(String(20))
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str] = mapped_column(String(100))
    sub_industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    short_description: Mapped[str] = mapped_column(String(255))
    long_description: Mapped[str] = mapped_column(Text)
    current_monthly_revenue: Mapped[str] = mapped_column(String(50))
    revenue_model: Mapped[str] = mapped_column(String(50))
    revenue_consistency: Mapped[str] = mapped_column(String(50))
    revenue_stage: Mapped[str] = mapped_column(String(50))
    existing_debt: Mapped[bool] = mapped_column(Integer, default=0)
    existing_investors: Mapped[bool] = mapped_column(Integer, default=0)
    intended_use_of_funds: Mapped[str] = mapped_column(Text)
    target_funding_size: Mapped[str] = mapped_column(String(50))
    preferred_timeline: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(ForeignKey("startups.id"))
    name: Mapped[str] = mapped_column(String(255))
    application_type: Mapped[str] = mapped_column(String(50))
    requested_limit_cents: Mapped[int] = mapped_column(Integer)
    risk_preference: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    fee_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(ForeignKey("startups.id"))
    doc_type: Mapped[str] = mapped_column(String(50))
    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Round(Base):
    __tablename__ = "rounds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(ForeignKey("startups.id"))
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    title: Mapped[str] = mapped_column(String(255))
    max_raise_cents: Mapped[int] = mapped_column(Integer)
    tier_selected: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class TierOption(Base):
    __tablename__ = "tier_options"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    tier: Mapped[str] = mapped_column(String(20))
    revenue_share_bps: Mapped[int] = mapped_column(Integer)
    time_cap_months: Mapped[int] = mapped_column(Integer)
    payout_cap_mult: Mapped[float] = mapped_column(Numeric(10, 2))
    min_hold_days: Mapped[int] = mapped_column(Integer)
    exit_fee_bps_quarterly: Mapped[int] = mapped_column(Integer)
    exit_fee_bps_offcycle: Mapped[int] = mapped_column(Integer)
    explanation_json: Mapped[str] = mapped_column(Text)


class Investment(Base):
    __tablename__ = "investments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"))
    investor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    payment_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Contract(Base):
    __tablename__ = "contracts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    investment_id: Mapped[int] = mapped_column(ForeignKey("investments.id"))
    status: Mapped[str] = mapped_column(String(20), default="active")
    principal_cents: Mapped[int] = mapped_column(Integer)
    payout_cap_cents: Mapped[int] = mapped_column(Integer)
    revenue_share_bps: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_date_cap: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paid_to_date_cents: Mapped[int] = mapped_column(Integer, default=0)


class RevenueReport(Base):
    __tablename__ = "revenue_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(ForeignKey("startups.id"))
    month: Mapped[str] = mapped_column(String(20))
    gross_revenue_cents: Mapped[int] = mapped_column(Integer)
    reported_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    distribution_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Distribution(Base):
    __tablename__ = "distributions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startup_id: Mapped[int] = mapped_column(ForeignKey("startups.id"))
    month: Mapped[str] = mapped_column(String(20))
    total_distributed_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Payout(Base):
    __tablename__ = "payouts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    distribution_id: Mapped[int] = mapped_column(ForeignKey("distributions.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    payout_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExitRequest(Base):
    __tablename__ = "exits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exit_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="requested")
    quoted_amount_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fee_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settlement_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    entry_type: Mapped[str] = mapped_column(String(50))
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    startup_id: Mapped[int | None] = mapped_column(ForeignKey("startups.id"), nullable=True)
    round_id: Mapped[int | None] = mapped_column(ForeignKey("rounds.id"), nullable=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    to_address: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    html: Mapped[str] = mapped_column(Text)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    properties: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
