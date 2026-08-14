from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.services import get_site_service
from netbox.client import NetBoxNotFoundError
from schemas.site import SiteResponse
from services.site import SiteService

router = APIRouter()

@router.get(
    "",
    response_model=list[SiteResponse],
)
def get_sites(
    service: SiteService = Depends(get_site_service),
) -> list[SiteResponse]:
    return service.get_sites()


@router.get(
    "/{site_id}",
    response_model=SiteResponse,
)
def get_site(
    site_id: int,
    service: SiteService = Depends(get_site_service),
) -> SiteResponse:
    try:
        return service.get_site(site_id)

    except NetBoxNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    