# app/netbox/adapter/pynetbox.py

from __future__ import annotations

from typing import Any

import pynetbox

from app.config.settings import settings
from app.netbox.exceptions import NetBoxConfigurationError


class PynetboxAdapter:
    """
    Low-level NetBox adapter using pynetbox.

    This class contains no BNC business rules.
    It only provides access to the NetBox API and translates
    between BNC-friendly values and pynetbox/NetBox objects.
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

    # ============================================================
    # Sites
    # ============================================================

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

    # ============================================================
    # Devices
    # ============================================================

    def filter_devices(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.dcim.devices.filter(**filters)
        )

    # ============================================================
    # VLAN Groups
    # ============================================================

    def filter_vlan_groups(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlan_groups.filter(**filters)
        )

    # ============================================================
    # VLANs
    # ============================================================

    def filter_vlans(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.vlans.filter(**filters)
        )

    def create_vlan(
        self,
        data: dict[str, Any],
    ) -> Any:
        """
        Create a VLAN in NetBox.

        Tags supplied in the data dictionary are expected to be
        NetBox tag slugs. They are resolved to NetBox tag IDs
        before being passed to pynetbox.
        """
        data = data.copy()

        if "tags" in data:
            data["tags"] = self._resolve_tags(
                data["tags"],
            )

        return self.api.ipam.vlans.create(data)

    def update_vlan(
        self,
        vlan_id: int,
        data: dict[str, Any],
    ) -> Any | None:
        vlan = self.api.ipam.vlans.get(vlan_id)

        if vlan is None:
            return None

        for key, value in data.items():
            setattr(vlan, key, value)

        vlan.save()

        return vlan

    def update_vlan_tags(
        self,
        vlan_id: int,
        tags: list[str],
    ) -> Any | None:
        """
        Replace the tags assigned to a VLAN.

        Tags are supplied as NetBox tag slugs.

        The slugs are resolved to NetBox tag IDs before
        being assigned to the pynetbox record.
        """
        vlan = self.api.ipam.vlans.get(vlan_id)

        if vlan is None:
            return None

        vlan.tags = self._resolve_tags(
            tags,
        )

        vlan.save()

        return vlan

    def delete_vlan(
        self,
        vlan_id: int,
    ) -> bool:
        vlan = self.api.ipam.vlans.get(vlan_id)

        if vlan is None:
            return False

        return vlan.delete()

    # ============================================================
    # Prefixes
    # ============================================================

    def filter_prefixes(
        self,
        **filters: Any,
    ) -> list[Any]:
        return list(
            self.api.ipam.prefixes.filter(**filters)
        )

    # ============================================================
    # Tags
    # ============================================================

    def _resolve_tags(
        self,
        tags: list[str],
    ) -> list[dict[str, int]]:
        """
        Resolve NetBox tag slugs to NetBox tag references.

        NetBox accepts related objects by numeric ID or by a
        dictionary containing the object ID.

        Returns:
            A list suitable for use in a NetBox API request.

        Raises:
            NetBoxConfigurationError:
                A requested tag does not exist in NetBox.
        """
        tag_references: list[dict[str, int]] = []

        for tag_slug in tags:
            tag = self.api.extras.tags.get(
                slug=tag_slug,
            )

            if tag is None:
                raise NetBoxConfigurationError(
                    f"NetBox tag '{tag_slug}' does not exist."
                )

            tag_references.append(
                {
                    "id": tag.id,
                }
            )

        return tag_references
