from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import VLANGroup
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/vlan-groups", tags=["vlan-groups"])


@router.get("", response_model=list[VLANGroup])
def list_vlan_groups(service: NetBoxService = Depends(get_netbox_service)) -> list[VLANGroup]:
    """List NetBox VLAN groups tagged for BNC management."""
    return service.list_vlan_groups()
