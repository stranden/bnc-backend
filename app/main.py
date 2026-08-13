"""FastAPI application entrypoint for the Broadcast Network Controller (BNC) backend."""
import logging

from fastapi import FastAPI

from app.config.settings import get_settings

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
)
