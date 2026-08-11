"""FastAPI dependencies."""
from app.core.netbox_client import get_netbox_client
from app.services.netbox_service import NetBoxService


def get_netbox_service() -> NetBoxService:
    return NetBoxService(get_netbox_client())
