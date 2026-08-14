from __future__ import annotations

from typing import Any

import pynetbox

from config.settings import settings


class PynetboxAdapter:
    """
    Low-level NetBox adapter using pynetbox.

    This class contains no BNC business rules.

    It only knows how to communicate with NetBox.
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

    # ==================================================================
    # Sites
    # ==================================================================

    def get_site(
        self,
        site_id: int,
    ) -> Any | None:
        return self.api.dcim.sites.get(
            site_id
        )

    def filter_sites(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.dcim.sites.filter(
                **filters
            )
        )

    # ==================================================================
    # Devices
    # ==================================================================

    def filter_devices(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.dcim.devices.filter(
                **filters
            )
        )

    # ==================================================================
    # VLAN Groups
    # ==================================================================

    def get_vlan_group(
        self,
        vlan_group_id: int,
    ) -> Any | None:
        return self.api.ipam.vlan_groups.get(
            vlan_group_id
        )

    def filter_vlan_groups(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlan_groups.filter(
                **filters
            )
        )

    # ==================================================================
    # VLANs
    # ==================================================================

    def get_vlan(
        self,
        vlan_id: int,
    ) -> Any | None:
        return self.api.ipam.vlans.get(
            vlan_id
        )

    def filter_vlans(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlans.filter(
                **filters
            )
        )

    def create_vlan(
        self,
        data: dict[str, Any],
    ) -> Any:
        return self.api.ipam.vlans.create(
            data
        )

    def update_vlan(
        self,
        vlan_id: int,
        data: dict[str, Any],
    ) -> Any | None:
        vlan = self.get_vlan(vlan_id)

        if vlan is None:
            return None

        vlan.update(data)

        return vlan

    def delete_vlan(
        self,
        vlan_id: int,
    ) -> bool:
        vlan = self.get_vlan(vlan_id)

        if vlan is None:
            return False

        vlan.delete()

        return True

    # ==================================================================
    # Prefixes
    # ==================================================================

    def get_prefix(
        self,
        prefix_id: int,
    ) -> Any | None:
        return self.api.ipam.prefixes.get(
            prefix_id
        )

    def filter_prefixes(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.prefixes.filter(
                **filters
            )
        )

    def create_prefix(
        self,
        data: dict[str, Any],
    ) -> Any:
        return self.api.ipam.prefixes.create(
            data
        )

    def update_prefix(
        self,
        prefix_id: int,
        data: dict[str, Any],
    ) -> Any | None:
        prefix = self.get_prefix(prefix_id)

        if prefix is None:
            return None

        prefix.update(data)

        return prefix

    def delete_prefix(
        self,
        prefix_id: int,
    ) -> bool:
        prefix = self.get_prefix(prefix_id)

        if prefix is None:
            return False

        prefix.delete()

        return True

    # ==================================================================
    # IP Ranges
    # ==================================================================

    def get_ip_range(
        self,
        ip_range_id: int,
    ) -> Any | None:
        return self.api.ipam.ip_ranges.get(
            ip_range_id
        )

    def filter_ip_ranges(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.ip_ranges.filter(
                **filters
            )
        )

    def create_ip_range(
        self,
        data: dict[str, Any],
    ) -> Any:
        return self.api.ipam.ip_ranges.create(
            data
        )

    def update_ip_range(
        self,
        ip_range_id: int,
        data: dict[str, Any],
    ) -> Any | None:
        ip_range = self.get_ip_range(
            ip_range_id
        )

        if ip_range is None:
            return None

        ip_range.update(data)

        return ip_range

    def delete_ip_range(
        self,
        ip_range_id: int,
    ) -> bool:
        ip_range = self.get_ip_range(
            ip_range_id
        )

        if ip_range is None:
            return False

        ip_range.delete()

        return True

    # ==================================================================
    # Tags
    # ==================================================================

    def get_tag(
        self,
        slug: str,
    ) -> Any | None:
        return self.api.extras.tags.get(
            slug=slug
        )

    def get_tag_id(
        self,
        slug: str,
    ) -> int:
        tag = self.get_tag(slug)

        if tag is None:
            raise RuntimeError(
                f"Required NetBox tag does not exist: {slug}"
            )

        return tag.id
