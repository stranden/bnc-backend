from fastapi import APIRouter
from . import (
    sites,
    vlans,
)

api_router = APIRouter()
api_router.include_router(sites.router, prefix="/sites", tags=["Sites"])
api_router.include_router(vlans.router, prefix="/vlans", tags=["VLANs"])
