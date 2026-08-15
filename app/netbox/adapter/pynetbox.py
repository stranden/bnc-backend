from __future__ import annotations

from typing import Any

import pynetbox

from app.config.settings import settings


class PynetboxAdapter:
    """
    Low-level NetBox adapter using pynetbox.

    This class contains no BNC business rules.
    """

    def __init__(self) -> None:
        self.api = pynetbox.api(
            settings.netbox_url,
            token=settings.netbox_token,
        )

        self.api.http_session.verify = (
            settings.netbox_verify_ssl
        )

        self.api.http_session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Sites
    # ------------------------------------------------------------------

    def get_site(
        self,
        site_id: int,
    ) -> Any | None:
        return self.api.dcim.sites.get(site_id)

    def filter_sites(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.dcim.sites.filter(**filters)
        )

    # ------------------------------------------------------------------
    # Devices
    # ------------------------------------------------------------------

    def filter_devices(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.dcim.devices.filter(**filters)
        )

    # ------------------------------------------------------------------
    # VLAN Groups
    # ------------------------------------------------------------------

    def filter_vlan_groups(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlan_groups.filter(**filters)
        )

    # ------------------------------------------------------------------
    # VLANs
    # ------------------------------------------------------------------

    def filter_vlans(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlans.filter(**filters)
        )

    # ------------------------------------------------------------------
    # Prefixes
    # ------------------------------------------------------------------

    def filter_prefixes(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.prefixes.filter(**filters)
        )
