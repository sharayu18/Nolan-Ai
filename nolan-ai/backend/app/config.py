from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database (Supabase Postgres connection string)
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/nolan_ai"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    # Instagram Graph API — see Setup Dependencies in HANDOFF.md.
    # Left blank until Rishi's account is Business/Creator + Meta app is approved.
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""

    # Email (SMTP — Resend/SendGrid or compatible)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = "nolan-ai@physicsexperimental.local"
    alert_recipient_email: str = ""

    # Supabase Auth — Google login. The frontend talks to Supabase directly;
    # the backend verifies access tokens against the project's public JWKS
    # (SUPABASE_URL/auth/v1/.well-known/jwks.json), so it only needs the
    # project URL — same value as the frontend's VITE_SUPABASE_URL
    # (Project Settings -> API -> Project URL).
    supabase_url: str = ""

    # App
    cors_origins: str = "http://localhost:5173"
    channel_handle: str = "@physicsexperimental"


settings = Settings()
