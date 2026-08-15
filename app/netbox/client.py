# app/netbox/client.py

from __future__ import annotations

from typing import Any

from app.config.settings import settings
from app.netbox.adapter.pynetbox import PynetboxAdapter
from app.netbox.exceptions import (
    NetBoxConfigurationError,
    NetBoxNotFoundError,
    NetBoxPermissionError,
)


class NetBoxClient:
    """
    BNC-facing interface to NetBox.

    This class contains BNC-specific rules and hides the underlying
    NetBox/pynetbox implementation from the rest of the application.
    """

    def __init__(self, adapter: PynetboxAdapter) -> None:
        self.adapter = adapter

    # ============================================================
    # Sites
    # ============================================================

    def get_sites(self) -> list[Any]:
        """
        Return all Sites exposed to BNC.
        """
        return self.adapter.filter_sites(
            tag=settings.netbox_tag_external_ctrl,
        )

    def get_site(self, site_id: int) -> Any:
        """
        Return a Site exposed to BNC.

        Raises:
            NetBoxNotFoundError: Site does not exist or is not
                                 exposed to BNC.
        """
        site = self.adapter.get_site(site_id)

        if site is None:
            raise NetBoxNotFoundError(
                f"Site {site_id} not found."
            )

        if not self._has_tag(
            site,
            settings.netbox_tag_external_ctrl,
        ):
            raise NetBoxNotFoundError(
                f"Site {site_id} not found."
            )

        return site

    def get_site_counts(self, site_id: int) -> dict[str, int]:
        """
        Return resource counts for a BNC-managed Site.
        """
        # This also validates that the Site is exposed to BNC.
        self.get_site(site_id)

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

        vlan_count = self._get_site_vlan_count(site_id)

        return {
            "device_count": device_count,
            "vlan_count": vlan_count,
            "prefix_count": prefix_count,
        }

    def _get_site_vlan_count(self, site_id: int) -> int:
        """
        Count VLANs belonging to BNC-visible VLAN Groups
        for a Site.

        VLAN Groups are an internal NetBox implementation detail
        and are not exposed by the BNC API.
        """
        vlan_groups = self.adapter.filter_vlan_groups(
            site_id=site_id,
            tag=settings.netbox_tag_external_ctrl,
        )

        count = 0

        for vlan_group in vlan_groups:
            count += len(
                self.adapter.filter_vlans(
                    group_id=vlan_group.id,
                )
            )

        return count

    # ============================================================
    # VLANs
    # ============================================================

    def get_vlans(self, site_id: int) -> list[Any]:
        """
        Return all VLANs belonging to the managed VLAN Group
        for a Site.
        """
        vlan_group = self._get_managed_vlan_group(site_id)

        return self.adapter.filter_vlans(
            group_id=vlan_group.id,
        )

    def get_vlan(
        self,
        vid: int,
        site_id: int,
    ) -> Any:
        """
        Return a VLAN by VID within a Site.

        The NetBox internal VLAN ID is deliberately not exposed
        to the BNC application.
        """
        vlan_group = self._get_managed_vlan_group(site_id)

        vlans = self.adapter.filter_vlans(
            group_id=vlan_group.id,
            vid=vid,
        )

        if not vlans:
            raise NetBoxNotFoundError(
                f"VLAN {vid} not found."
            )

        return vlans[0]

    def create_vlan(
        self,
        site_id: int,
        vid: int,
        name: str,
        description: str | None = None,
    ) -> Any:
        """
        Create a VLAN in the managed VLAN Group for a Site.
        """
        vlan_group = self._get_managed_vlan_group(site_id)

        self._require_manage_permission(vlan_group)

        data: dict[str, Any] = {
            "group": vlan_group.id,
            "vid": vid,
            "name": name,
        }

        if description is not None:
            data["description"] = description

        return self.adapter.create_vlan(data)

    def update_vlan(
        self,
        vid: int,
        site_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        new_vid: int | None = None,
    ) -> Any:
        """
        Update a VLAN identified by VID within a Site.
        """
        vlan, vlan_group = self._get_vlan_context(
            vid=vid,
            site_id=site_id,
        )

        self._require_manage_permission(vlan_group)

        data: dict[str, Any] = {}

        if new_vid is not None:
            data["vid"] = new_vid

        if name is not None:
            data["name"] = name

        if description is not None:
            data["description"] = description

        if not data:
            return vlan

        updated_vlan = self.adapter.update_vlan(
            vlan_id=vlan.id,
            data=data,
        )

        if updated_vlan is None:
            raise NetBoxNotFoundError(
                f"VLAN {vid} not found."
            )

        return updated_vlan

    def delete_vlan(
        self,
        vid: int,
        site_id: int,
    ) -> None:
        """
        Delete a VLAN identified by VID within a Site.
        """
        vlan, vlan_group = self._get_vlan_context(
            vid=vid,
            site_id=site_id,
        )

        self._require_manage_permission(vlan_group)

        deleted = self.adapter.delete_vlan(
            vlan_id=vlan.id,
        )

        if not deleted:
            raise NetBoxNotFoundError(
                f"VLAN {vid} not found."
            )

    # ============================================================
    # VLAN context / boundaries
    # ============================================================

    def _get_vlan_context(
        self,
        vid: int,
        site_id: int,
    ) -> tuple[Any, Any]:
        """
        Resolve a VLAN and its managed VLAN Group.

        The VLAN is always looked up inside the VLAN Group belonging
        to the requested Site. This prevents accessing a VLAN from
        another Site.
        """
        vlan_group = self._get_managed_vlan_group(site_id)

        vlans = self.adapter.filter_vlans(
            group_id=vlan_group.id,
            vid=vid,
        )

        if not vlans:
            raise NetBoxNotFoundError(
                f"VLAN {vid} not found."
            )

        return vlans[0], vlan_group

    def _get_managed_vlan_group(
        self,
        site_id: int,
    ) -> Any:
        """
        Return the single VLAN Group managed by BNC for a Site.

        A Site must have exactly one VLAN Group tagged for
        external BNC control.

        Raises:
            NetBoxNotFoundError:
                Site or managed VLAN Group does not exist.

            NetBoxConfigurationError:
                More than one managed VLAN Group exists.
        """
        # Validate Site first.
        self.get_site(site_id)

        vlan_groups = self.adapter.filter_vlan_groups(
            site_id=site_id,
            tag=settings.netbox_tag_external_ctrl,
        )

        if not vlan_groups:
            raise NetBoxNotFoundError(
                f"No BNC-managed VLAN Group found for Site {site_id}."
            )

        if len(vlan_groups) > 1:
            raise NetBoxConfigurationError(
                f"Multiple BNC-managed VLAN Groups found "
                f"for Site {site_id}."
            )

        return vlan_groups[0]

    # ============================================================
    # Permissions / tags
    # ============================================================

    @staticmethod
    def _require_manage_permission(
        resource: Any,
    ) -> None:
        """
        Verify that a NetBox resource can be managed by BNC.

        A resource must have both:
            - external-control tag
            - BNC management-state tag
        """
        if not NetBoxClient._has_tag(
            resource,
            settings.netbox_tag_external_ctrl,
        ):
            raise NetBoxPermissionError(
                "Resource is not exposed to BNC."
            )

        if not NetBoxClient._has_tag(
            resource,
            settings.netbox_tag_state_manage,
        ):
            raise NetBoxPermissionError(
                "Resource is not managed by BNC."
            )

    @staticmethod
    def _has_tag(
        resource: Any,
        tag_slug: str,
    ) -> bool:
        """
        Check whether a pynetbox resource has a specific tag.
        """
        tags = getattr(resource, "tags", [])

        for tag in tags:
            if isinstance(tag, str):
                if tag == tag_slug:
                    return True
                continue

            if getattr(tag, "slug", None) == tag_slug:
                return True

            if getattr(tag, "name", None) == tag_slug:
                return True

        return False
