"""FastAPI application entrypoint for the Broadcast Network Controller (BNC) backend."""
import logging

from fastapi import FastAPI

from config.settings import get_settings
from api import api_router

settings = get_settings()

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Reads Sites, Devices, Device Types, Prefixes, IP Addresses, VLAN "
        "Groups and VLANs from NetBox, scoped strictly to objects tagged "
        f"'{settings.netbox_tag_external_ctrl}'."
    ),
    version="0.1.0",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url=None
)

app.include_router(api_router, prefix="/api")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "RangeConnectBackend have been started correctly!"}

@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"message": "Application ready"}
