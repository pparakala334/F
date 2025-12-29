from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    company_name: str = "Steelman"
    country_mode: str = "CA"
    database_url: str = "postgresql+psycopg://radion:radion@db:5432/radion"
    jwt_secret: str = "dev_secret"
    jwt_expire_minutes: int = 60
    admin_email: str = "admin@demo.com"
    admin_password: str = "password"

    enable_stripe: bool = False
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    enable_okta: bool = False
    okta_issuer: str | None = None
    okta_client_id: str | None = None
    okta_client_secret: str | None = None
    okta_redirect_uri: str | None = None

    enable_s3: bool = False
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_bucket: str | None = None
    aws_region: str = "us-east-1"

    enable_resend: bool = False
    resend_api_key: str | None = None

    enable_posthog: bool = False
    posthog_api_key: str | None = None
    posthog_host: str | None = None

    enable_sentry: bool = False
    sentry_dsn: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
