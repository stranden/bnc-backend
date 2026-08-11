"""Pydantic response schemas for NetBox objects exposed by BNC.

These are intentionally slim projections of the full NetBox objects — only
the fields BNC actually needs are exposed.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class NestedRef(BaseModel):
    id: int
    name: str | None = None
    slug: str | None = None
    display: str | None = None


class Site(BaseModel):
    id: int
    name: str
    slug: str
    status: str | None = None
    region: NestedRef | None = None
    description: str | None = None


class DeviceType(BaseModel):
    id: int
    model: str
    slug: str
    manufacturer: NestedRef | None = None
    u_height: float | None = None


class Device(BaseModel):
    id: int
    name: str | None = None
    status: str | None = None
    site: NestedRef | None = None
    device_type: NestedRef | None = None
    device_role: NestedRef | None = None
    primary_ip4: NestedRef | None = None
    primary_ip6: NestedRef | None = None


class Prefix(BaseModel):
    id: int
    prefix: str
    status: str | None = None
    site: NestedRef | None = None
    vlan: NestedRef | None = None
    description: str | None = None


class IPAddress(BaseModel):
    id: int
    address: str
    status: str | None = None
    description: str | None = None
    assigned_object_id: int | None = None
    assigned_object_type: str | None = None


class VLANGroup(BaseModel):
    id: int
    name: str
    slug: str
    site: NestedRef | None = None


class VLAN(BaseModel):
    id: int
    name: str
    vid: int
    status: str | None = None
    group: NestedRef | None = None
    site: NestedRef | None = None


class WebhookPayload(BaseModel):
    """Generic NetBox webhook envelope.

    NetBox sends `event`, `timestamp`, `model`, `username`, `request_id` and
    `data` (the serialized object) for every webhook call.
    """

    event: str
    timestamp: str
    model: str
    username: str | None = None
    request_id: str | None = None
    data: dict[str, Any]
