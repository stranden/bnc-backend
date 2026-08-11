"""FastAPI application entrypoint for the Broadcast Network Controller (BNC) backend."""
import logging

from fastapi import FastAPI

from app.api.routes import (
    device_types,
    devices,
    health,
    ip_addresses,
    prefixes,
    sites,
    vlan_groups,
    vlans,
    webhooks,
)
from app.config import get_settings

settings = get_settings()

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Reads Sites, Devices, Device Types, Prefixes, IP Addresses, VLAN "
        "Groups and VLANs from NetBox, scoped strictly to objects tagged "
        f"'{settings.netbox_sync_tag}'."
    ),
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(sites.router)
app.include_router(devices.router)
app.include_router(device_types.router)
app.include_router(prefixes.router)
app.include_router(ip_addresses.router)
app.include_router(vlan_groups.router)
app.include_router(vlans.router)
app.include_router(webhooks.router)
