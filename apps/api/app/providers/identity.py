from app.settings import settings


def verify_identity(user_id: int, role: str) -> str:
    if not settings.enable_stripe or not settings.stripe_secret_key:
        return "verified"
    return "pending"
