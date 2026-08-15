from fastapi import APIRouter, Depends

from app.dependencies.services import get_site_service
from app.schemas.site import SiteResponse
from app.services.site import SiteService


router = APIRouter()


@router.get(
    "",
    response_model=list[SiteResponse],
)
def get_sites(
    service: SiteService = Depends(get_site_service),
):
    return service.get_sites()


@router.get(
    "/{site_id}",
    response_model=SiteResponse,
)
def get_site(
    site_id: int,
    service: SiteService = Depends(get_site_service),
):
    return service.get_site(site_id)
