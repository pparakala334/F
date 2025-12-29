from app.settings import settings


def capture_exception(exc: Exception, context: dict | None = None) -> None:
    if not settings.enable_sentry or not settings.sentry_dsn:
        print(f"[sentry][demo] {exc} context={context}")
        return
    print(f"[sentry] {exc} context={context}")
