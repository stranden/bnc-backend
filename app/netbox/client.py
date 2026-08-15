from __future__ import annotations

from typing import Any

from app.netbox.adapter.pynetbox import PynetboxAdapter
from app.netbox.exceptions import NetBoxNotFoundError

from app.config.settings import settings


class NetBoxClient:
    """
    BNC-facing interface to NetBox.

    This class hides NetBox/pynetbox implementation details
    and applies BNC-specific NetBox rules.
    """

    def __init__(
        self,
        adapter: PynetboxAdapter,
    ) -> None:
        self.adapter = adapter

    # ------------------------------------------------------------------
    # Sites
    # ------------------------------------------------------------------

    def get_sites(self) -> list[Any]:
        """
        Return Sites exposed to BNC.
        """
        return self.adapter.filter_sites(
            tag=settings.tag_external_ctrl,
        )

    def get_site(
        self,
        site_id: int,
    ) -> Any:
        """
        Return a Site exposed to BNC.
        """
        site = self.adapter.get_site(site_id)

        if site is None:
            raise NetBoxNotFoundError(
                f"Site {site_id} not found."
            )

        if not self._has_tag(
            site,
            settings.tag_external_ctrl,
        ):
            raise NetBoxNotFoundError(
                f"Site {site_id} is not exposed to BNC."
            )

        return site

    def get_site_counts(
        self,
        site_id: int,
    ) -> dict[str, int]:
        """
        Return BNC-relevant resource counts for a Site.
        """

        device_count = len(
            self.adapter.filter_devices(
                site_id=site_id,
            )
        )

        prefix_count = len(
            self.adapter.filter_prefixes(
                site_id=site_id,
            )
        )

        vlan_count = self._get_site_vlan_count(
            site_id,
        )

        return {
            "device_count": device_count,
            "vlan_count": vlan_count,
            "prefix_count": prefix_count,
        }

    def _get_site_vlan_count(
        self,
        site_id: int,
    ) -> int:
        """
        Count VLANs belonging to the BNC-managed VLAN Groups
        associated with a Site.
        """

        vlan_groups = self.adapter.filter_vlan_groups(
            site_id=site_id,
            tag=settings.tag_external_ctrl,
        )

        count = 0

        for vlan_group in vlan_groups:
            count += len(
                self.adapter.filter_vlans(
                    group_id=vlan_group.id,
                )
            )

        return count

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_tag(
        resource: Any,
        tag_slug: str,
    ) -> bool:
        tags = getattr(resource, "tags", None) or []

        for tag in tags:
            if isinstance(tag, dict):
                slug = tag.get("slug")
            else:
                slug = getattr(tag, "slug", None)

            if slug == tag_slug:
                return True

        return False
