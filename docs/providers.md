# Provider Integrations

All providers are optional and fall back to demo implementations when not enabled via `ENABLE_*` or missing keys.

- Stripe Connect + Webhooks: payments provider with simulated fallback.
- Stripe Identity: identity provider with auto-verify fallback.
- AWS S3: storage provider with metadata-only fallback.
- Resend: email provider with outbox storage fallback.
- PostHog: analytics provider with database event storage fallback.
- Sentry: error monitoring provider with console logging fallback.
- Okta OIDC: auth provider with JWT email/password fallback.
