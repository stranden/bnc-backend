"""Service layer: converts raw pynetbox records into BNC's slim schemas."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from app.core.netbox_client import NetBoxClient
from app.models.schemas import (
    Device,
    DeviceType,
    IPAddress,
    Prefix,
    Site,
    VLAN,
    VLANGroup,
)


def _nested(value: Any) -> dict | None:
    if value is None:
        return None
    return value.dict() if hasattr(value, "dict") else dict(value)


def _serialize(records: Iterable[Any], mapper: Callable[[Any], dict]) -> list[dict]:
    return [mapper(record) for record in records]


def _site(record: Any) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "slug": record.slug,
        "status": getattr(record.status, "value", None) if record.status else None,
        "region": _nested(getattr(record, "region", None)),
        "description": record.description or None,
    }


def _device_type(record: Any) -> dict:
    return {
        "id": record.id,
        "model": record.model,
        "slug": record.slug,
        "manufacturer": _nested(getattr(record, "manufacturer", None)),
        "u_height": getattr(record, "u_height", None),
    }


def _device(record: Any) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "status": getattr(record.status, "value", None) if record.status else None,
        "site": _nested(getattr(record, "site", None)),
        "device_type": _nested(getattr(record, "device_type", None)),
        "device_role": _nested(getattr(record, "device_role", None) or getattr(record, "role", None)),
        "primary_ip4": _nested(getattr(record, "primary_ip4", None)),
        "primary_ip6": _nested(getattr(record, "primary_ip6", None)),
    }


def _prefix(record: Any) -> dict:
    return {
        "id": record.id,
        "prefix": str(record.prefix),
        "status": getattr(record.status, "value", None) if record.status else None,
        "site": _nested(getattr(record, "site", None)),
        "vlan": _nested(getattr(record, "vlan", None)),
        "description": record.description or None,
    }


def _ip_address(record: Any) -> dict:
    return {
        "id": record.id,
        "address": str(record.address),
        "status": getattr(record.status, "value", None) if record.status else None,
        "description": record.description or None,
        "assigned_object_id": getattr(record, "assigned_object_id", None),
        "assigned_object_type": getattr(record, "assigned_object_type", None),
    }


def _vlan_group(record: Any) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "slug": record.slug,
        "site": _nested(getattr(record, "site", None)),
    }


def _vlan(record: Any) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "vid": record.vid,
        "status": getattr(record.status, "value", None) if record.status else None,
        "group": _nested(getattr(record, "group", None)),
        "site": _nested(getattr(record, "site", None)),
    }


class NetBoxService:
    """Fetches BNC-scoped NetBox objects and maps them to BNC schemas."""

    def __init__(self, client: NetBoxClient) -> None:
        self._client = client

    def list_sites(self, **filters: Any) -> list[Site]:
        records = _serialize(self._client.get_sites(**filters), _site)
        return [Site(**r) for r in records]

    def list_devices(self, **filters: Any) -> list[Device]:
        records = _serialize(self._client.get_devices(**filters), _device)
        return [Device(**r) for r in records]

    def list_device_types(self, **filters: Any) -> list[DeviceType]:
        records = _serialize(self._client.get_device_types(**filters), _device_type)
        return [DeviceType(**r) for r in records]

    def list_prefixes(self, **filters: Any) -> list[Prefix]:
        records = _serialize(self._client.get_prefixes(**filters), _prefix)
        return [Prefix(**r) for r in records]

    def list_ip_addresses(self, **filters: Any) -> list[IPAddress]:
        records = _serialize(self._client.get_ip_addresses(**filters), _ip_address)
        return [IPAddress(**r) for r in records]

    def list_vlan_groups(self, **filters: Any) -> list[VLANGroup]:
        records = _serialize(self._client.get_vlan_groups(**filters), _vlan_group)
        return [VLANGroup(**r) for r in records]

    def list_vlans(self, **filters: Any) -> list[VLAN]:
        records = _serialize(self._client.get_vlans(**filters), _vlan)
        return [VLAN(**r) for r in records]
