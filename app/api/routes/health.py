from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> dict:
    """Readiness probe: confirms BNC has NetBox connection details configured."""
    settings = get_settings()
    ready = bool(settings.netbox_url and settings.netbox_token)
    return {"status": "ready" if ready else "not-ready"}
