from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import Site
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[Site])
def list_sites(service: NetBoxService = Depends(get_netbox_service)) -> list[Site]:
    """List NetBox sites tagged for BNC management."""
    return service.list_sites()
