from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import DeviceType
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/device-types", tags=["device-types"])


@router.get("", response_model=list[DeviceType])
def list_device_types(service: NetBoxService = Depends(get_netbox_service)) -> list[DeviceType]:
    """List NetBox device types tagged for BNC management."""
    return service.list_device_types()
