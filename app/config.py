"""Application configuration.

All settings are loaded from environment variables (12-factor style), with an
optional local `.env` file for development convenience. Environment variables
always take precedence and are the supported way to configure BNC in Docker /
production (e.g. `docker run -e NETBOX_TOKEN=... -e NETBOX_URL=...`).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- General ---
    app_name: str = "Broadcast Network Controller (BNC)"
    environment: str = "development"
    log_level: str = "INFO"

    # --- NetBox ---
    netbox_url: str = "https://netbox.example.com"
    netbox_token: str = ""
    netbox_verify_ssl: bool = True

    # Only objects tagged with this NetBox tag are visible to BNC.
    # NetBox tags don't natively support "key: value" pairs; by convention
    # this is the *slug* of the tag created in NetBox (e.g. "external-ctrl-bnc").
    netbox_sync_tag: str = "external-ctrl-bnc"

    # Devices additionally tagged with this NetBox tag may be *actively
    # managed* by BNC (e.g. changing switch ports, pushing config). This is a
    # stricter subset of `netbox_sync_tag` — a device must carry both tags
    # before any write/push operation is allowed against it. Slug of the
    # NetBox tag "bnc-state: manage".
    netbox_manage_tag: str = "bnc-state-manage"

    # --- Webhooks ---
    # Shared secret configured on the NetBox webhook (HMAC signature verification).
    netbox_webhook_secret: str = ""

    # --- Nornir / NAPALM ---
    nornir_config_file: str = "nornir_config/config.yaml"
    napalm_username: str = ""
    napalm_password: str = ""
    napalm_timeout: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
