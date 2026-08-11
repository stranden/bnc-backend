from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import IPAddress
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/ip-addresses", tags=["ip-addresses"])


@router.get("", response_model=list[IPAddress])
def list_ip_addresses(service: NetBoxService = Depends(get_netbox_service)) -> list[IPAddress]:
    """List NetBox IP addresses tagged for BNC management."""
    return service.list_ip_addresses()
