from fastapi import APIRouter
from . import (
    sites,
    vlans,
    templates,
)

api_router = APIRouter()
api_router.include_router(sites.router, prefix="/sites", tags=["Sites"])
api_router.include_router(vlans.router, prefix="/vlans", tags=["VLANs"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
