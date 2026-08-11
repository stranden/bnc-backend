from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import Device
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[Device])
def list_devices(service: NetBoxService = Depends(get_netbox_service)) -> list[Device]:
    """List NetBox devices tagged for BNC management."""
    return service.list_devices()
