from typing import Any

from app.netbox import NetBoxClient
from app.schemas.site import SiteCounts, SiteResponse


class SiteService:

    def __init__(
        self,
        netbox: NetBoxClient,
    ) -> None:
        self.netbox = netbox

    def get_sites(self) -> list[SiteResponse]:
        sites = self.netbox.get_sites()

        return [
            self._to_response(
                site,
                self.netbox.get_site_counts(
                    site.id
                ),
            )
            for site in sites
        ]

    def get_site(
        self,
        site_id: int,
    ) -> SiteResponse:
        site = self.netbox.get_site(
            site_id
        )

        counts = self.netbox.get_site_counts(
            site_id
        )

        return self._to_response(
            site,
            counts,
        )

    @staticmethod
    def _to_response(
        site: Any,
        counts: SiteCounts | dict[str, int],
    ) -> SiteResponse:
        if isinstance(counts, dict):
            counts = SiteCounts(
                **counts
            )

        tenant = getattr(
            site,
            "tenant",
            None,
        )

        site_group = getattr(
            site,
            "group",
            None,
        )

        return SiteResponse(
            id=site.id,
            name=site.name,
            description=getattr(
                site,
                "description",
                None,
            ),
            tenant=(
                tenant.name
                if tenant is not None
                else None
            ),
            site_group=(
                site_group.name
                if site_group is not None
                else None
            ),
            device_count=counts.device_count,
            vlan_group_count=counts.vlan_group_count,
            vlan_count=counts.vlan_count,
            prefix_count=counts.prefix_count,
        )
