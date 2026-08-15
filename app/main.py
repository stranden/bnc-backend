"""FastAPI application entrypoint for the Broadcast Network Controller (BNC) backend."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.netbox import NetBoxNotFoundError
from app.templates import TemplateNotFoundError
from app.api import api_router

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
    redoc_url=None,
)

app.include_router(api_router, prefix="/api")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Broadcast Network Controller (BNC) has been started correctly!"}

@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"message": "Application ready"}

@app.exception_handler(NetBoxNotFoundError)
async def netbox_not_found_handler(
    request: Request,
    exc: NetBoxNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )

@app.exception_handler(TemplateNotFoundError)
async def template_not_found_handler(
    request: Request,
    exc: TemplateNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )
