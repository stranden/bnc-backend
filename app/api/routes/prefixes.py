from fastapi import APIRouter, Depends

from app.api.deps import get_netbox_service
from app.models.schemas import Prefix
from app.services.netbox_service import NetBoxService

router = APIRouter(prefix="/prefixes", tags=["prefixes"])


@router.get("", response_model=list[Prefix])
def list_prefixes(service: NetBoxService = Depends(get_netbox_service)) -> list[Prefix]:
    """List NetBox prefixes tagged for BNC management."""
    return service.list_prefixes()
