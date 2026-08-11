"""Thin wrapper around pynetbox that enforces the BNC tag scope.

Every read from NetBox goes through this client so that we have a single
place enforcing the rule: BNC may only ever see objects tagged with the
configured sync tag (see `Settings.netbox_sync_tag`).

A second, stricter tag (see `Settings.netbox_manage_tag`) marks devices BNC
is additionally allowed to *actively manage* (e.g. change switch ports, push
config). That tag is only relevant for future write/push operations, not for
the read-only sync scope.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

import pynetbox

from app.config import get_settings


class DeviceNotManagedError(Exception):
    """Raised when a write/push operation is attempted against a device that
    is not tagged with the BNC "manage" tag (`Settings.netbox_manage_tag`)."""


class NetBoxClient:
    """Wrapper around `pynetbox.api` scoped to the BNC-managed tag."""

    def __init__(
        self,
        url: str,
        token: str,
        tag: str,
        manage_tag: str = "bnc-state-manage",
        verify_ssl: bool = True,
    ) -> None:
        self._tag = tag
        self._manage_tag = manage_tag
        self.api = pynetbox.api(url, token=token)
        self.api.http_session.verify = verify_ssl

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def manage_tag(self) -> str:
        return self._manage_tag

    def _tagged(self, endpoint, **filters: Any) -> Iterable[Any]:
        """Return records from `endpoint`, always filtered by the BNC tag."""
        return endpoint.filter(tag=self._tag, **filters)

    # --- DCIM ---
    def get_sites(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.dcim.sites, **filters)

    def get_devices(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.dcim.devices, **filters)

    def get_device_types(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.dcim.device_types, **filters)

    def get_device(self, device_id: int) -> Any | None:
        device = self.api.dcim.devices.get(device_id)
        return device if device and self._has_tag(device, self._tag) else None

    def is_device_manageable(self, device: Any) -> bool:
        """Return True if `device` carries the BNC "manage" tag.

        Devices must carry both `netbox_sync_tag` (to be visible to BNC at
        all) and `netbox_manage_tag` (to be eligible for write/push
        operations such as changing switch ports or pushing config).
        """
        return self._has_tag(device, self._tag) and self._has_tag(device, self._manage_tag)

    def require_manageable_device(self, device: Any) -> None:
        """Raise `DeviceNotManagedError` unless `device` is BNC-manageable."""
        if not self.is_device_manageable(device):
            name = getattr(device, "name", None) or getattr(device, "id", "unknown")
            raise DeviceNotManagedError(
                f"Device '{name}' is not tagged '{self._manage_tag}'; write/push operations are not allowed"
            )

    def get_manageable_devices(self, **filters: Any) -> Iterable[Any]:
        """Return devices tagged with both the sync tag and the manage tag."""
        return self.api.dcim.devices.filter(tag=[self._tag, self._manage_tag], **filters)

    # --- IPAM ---
    def get_prefixes(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.ipam.prefixes, **filters)

    def get_ip_addresses(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.ipam.ip_addresses, **filters)

    def get_vlan_groups(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.ipam.vlan_groups, **filters)

    def get_vlans(self, **filters: Any) -> Iterable[Any]:
        return self._tagged(self.api.ipam.vlans, **filters)

    def _has_tag(self, record: Any, tag: str) -> bool:
        tags = getattr(record, "tags", None) or []
        return any(getattr(t, "slug", t) == tag for t in tags)


@lru_cache
def get_netbox_client() -> NetBoxClient:
    settings = get_settings()
    return NetBoxClient(
        url=settings.netbox_url,
        token=settings.netbox_token,
        tag=settings.netbox_sync_tag,
        manage_tag=settings.netbox_manage_tag,
        verify_ssl=settings.netbox_verify_ssl,
    )
