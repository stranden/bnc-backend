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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------

    app_name: str = "Broadcast Network Controller (BNC)"
    environment: str = "development"
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    # NetBox
    # ------------------------------------------------------------------

    netbox_url: str = "https://netbox.example.com"
    netbox_token: str = ""
    netbox_verify_ssl: bool = True

    # Only objects tagged with this NetBox tag are visible to BNC.
    netbox_tag_external_ctrl: str = "external-ctrl-bnc"

    # Objects additionally tagged with this tag may be actively managed
    # by BNC. A resource must carry both tags before write operations
    # are allowed.
    netbox_tag_state_manage: str = "bnc-state-manage"

    # Prefix for NetBox template tags. BNC will only consider tags with this
    # prefix as template tags. This allows users to create their own tags
    # without conflicting with BNC template tags.
    netbox_template_tag_prefix: str = "bnc-template-"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
