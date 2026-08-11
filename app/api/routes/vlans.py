from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import VLAN
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/vlans", tags=["vlans"])


@router.get("", response_model=list[VLAN])
def list_vlans(service: NetBoxService = Depends(get_netbox_service)) -> list[VLAN]:
    """List NetBox VLANs tagged for BNC management."""
    return service.list_vlans()
