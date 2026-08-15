from fastapi import APIRouter, Depends

from app.dependencies.services import get_template_service
from app.schemas.template import NetworkTemplateResponse
from app.services.template import TemplateService


router = APIRouter()


@router.get(
    "",
    response_model=list[NetworkTemplateResponse],
)
def get_templates(
    service: TemplateService = Depends(get_template_service),
):
    return service.get_templates()


@router.get(
    "/{slug}",
    response_model=NetworkTemplateResponse,
)
def get_template(
    slug: str,
    service: TemplateService = Depends(get_template_service),
):
    return service.get_template(slug)
