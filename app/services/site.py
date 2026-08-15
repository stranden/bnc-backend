from __future__ import annotations

from typing import Any

from app.netbox import NetBoxClient


class SiteService:
    def __init__(
        self,
        netbox: NetBoxClient,
    ) -> None:
        self.netbox = netbox

    def get_sites(self) -> list[dict[str, Any]]:
        sites = self.netbox.get_sites()

        return [
            self._to_data(
                site,
                self.netbox.get_site_counts(site.id),
            )
            for site in sites
        ]

    def get_site(
        self,
        site_id: int,
    ) -> dict[str, Any]:
        site = self.netbox.get_site(site_id)
        counts = self.netbox.get_site_counts(site_id)

        return self._to_data(
            site,
            counts,
        )

    @staticmethod
    def _to_data(
        site: Any,
        counts: dict[str, int],
    ) -> dict[str, Any]:
        tenant = getattr(site, "tenant", None)
        site_group = getattr(site, "group", None)

        return {
            "id": site.id,
            "name": site.name,
            "description": getattr(
                site,
                "description",
                None,
            ),
            "tenant": (
                tenant.name
                if tenant is not None
                else None
            ),
            "site_group": (
                site_group.name
                if site_group is not None
                else None
            ),
            "device_count": counts["device_count"],
            "vlan_count": counts["vlan_count"],
            "prefix_count": counts["prefix_count"],
        }
