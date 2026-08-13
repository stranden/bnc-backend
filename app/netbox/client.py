from __future__ import annotations

import ipaddress
from typing import Any

from app.config.settings import settings
from app.netbox.adapter.pynetbox import PynetboxAdapter


class NetBoxError(Exception):
    """Base exception for NetBox related errors."""


class NetBoxNotFoundError(NetBoxError):
    """The requested object does not exist or is not exposed to BNC."""


class NetBoxPermissionError(NetBoxError):
    """BNC is not allowed to perform the requested operation."""


class NetBoxValidationError(NetBoxError):
    """The requested operation contains invalid data."""


class NetBoxClient:
    """
    BNC's interface to NetBox.

    This class contains BNC-specific rules and business logic.

    The rest of the application should use this class and should not
    access pynetbox directly.
    """

    def __init__(
        self,
        adapter: PynetboxAdapter | None = None,
    ) -> None:
        """
        Create a NetBox client.

        An adapter can optionally be supplied for testing or if we
        later want to use another NetBox implementation.

        Normal application code should simply use:

            netbox = NetBoxClient()
        """

        self.adapter = adapter or PynetboxAdapter()

        self._tag_cache: dict[str, int] = {}

    # ==================================================================
    # Tags
    # ==================================================================

    def _get_tag_id(self, slug: str) -> int:
        """
        Resolve a NetBox tag slug to its NetBox ID.

        Results are cached because tags are used frequently.
        """

        if slug not in self._tag_cache:
            tag_id = self.adapter.get_tag_id(slug)

            self._tag_cache[slug] = tag_id

        return self._tag_cache[slug]

    def _get_bnc_tags(self) -> list[int]:
        """
        Return the tags that identify an object as BNC-managed.
        """

        return [
            self._get_tag_id(
                settings.netbox_tag_external_ctrl
            ),
            self._get_tag_id(
                settings.netbox_tag_state_manage
            ),
        ]

    # ==================================================================
    # Tag helpers
    # ==================================================================

    @staticmethod
    def _has_tag(
        record: Any,
        slug: str,
    ) -> bool:
        """
        Check whether a NetBox object contains a specific tag.
        """

        tags = getattr(record, "tags", None) or []

        for tag in tags:
            if isinstance(tag, dict):
                if tag.get("slug") == slug:
                    return True

            elif getattr(tag, "slug", None) == slug:
                return True

        return False

    def _is_exposed(self, record: Any) -> bool:
        """
        Determine whether an object is exposed to BNC.
        """

        return self._has_tag(
            record,
            settings.netbox_tag_external_ctrl,
        )

    def _is_managed(self, record: Any) -> bool:
        """
        Determine whether BNC is allowed to modify an object.

        An object must first be exposed to BNC and must then have
        the manage tag.
        """

        return (
            self._is_exposed(record)
            and self._has_tag(
                record,
                settings.netbox_tag_state_manage,
            )
        )

    def _require_exposed(
        self,
        record: Any | None,
        object_type: str,
        object_id: int,
    ) -> Any:
        """
        Require an object to exist and be exposed to BNC.
        """

        if record is None:
            raise NetBoxNotFoundError(
                f"{object_type} {object_id} does not exist"
            )

        if not self._is_exposed(record):
            raise NetBoxNotFoundError(
                f"{object_type} {object_id} is not exposed to BNC"
            )

        return record

    def _require_managed(
        self,
        record: Any | None,
        object_type: str,
        object_id: int,
    ) -> Any:
        """
        Require an object to exist, be exposed, and be managed by BNC.
        """

        if record is None:
            raise NetBoxNotFoundError(
                f"{object_type} {object_id} does not exist"
            )

        if not self._is_exposed(record):
            raise NetBoxPermissionError(
                f"{object_type} {object_id} is not exposed to BNC"
            )

        if not self._has_tag(
            record,
            settings.netbox_tag_state_manage,
        ):
            raise NetBoxPermissionError(
                f"{object_type} {object_id} is not managed by BNC"
            )

        return record

    # ==================================================================
    # VLAN Groups
    # ==================================================================

    def get_vlan_groups(self) -> list[Any]:
        """
        Get VLAN Groups exposed to BNC.
        """

        return self.adapter.filter_vlan_groups(
            tag=settings.netbox_tag_external_ctrl,
        )

    def get_vlan_group(
        self,
        vlan_group_id: int,
    ) -> Any:
        """
        Get a VLAN Group exposed to BNC.
        """

        vlan_group = self.adapter.get_vlan_group(
            vlan_group_id
        )

        return self._require_exposed(
            vlan_group,
            "VLAN Group",
            vlan_group_id,
        )

    def get_managed_vlan_group(
        self,
        vlan_group_id: int,
    ) -> Any:
        """
        Get a VLAN Group managed by BNC.
        """

        vlan_group = self.adapter.get_vlan_group(
            vlan_group_id
        )

        return self._require_managed(
            vlan_group,
            "VLAN Group",
            vlan_group_id,
        )

    # ==================================================================
    # VLANs
    # ==================================================================

    def get_vlans(self) -> list[Any]:
        """
        Get VLANs exposed to BNC.
        """

        return self.adapter.filter_vlans(
            tag=settings.netbox_tag_external_ctrl,
        )

    def get_vlan(
        self,
        vlan_id: int,
    ) -> Any:
        """
        Get a VLAN exposed to BNC.
        """

        vlan = self.adapter.get_vlan(vlan_id)

        return self._require_exposed(
            vlan,
            "VLAN",
            vlan_id,
        )

    def get_managed_vlan(
        self,
        vlan_id: int,
    ) -> Any:
        """
        Get a VLAN managed by BNC.
        """

        vlan = self.adapter.get_vlan(vlan_id)

        return self._require_managed(
            vlan,
            "VLAN",
            vlan_id,
        )

    def create_vlan(
        self,
        *,
        vlan_group_id: int,
        vid: int,
        name: str,
        profile_tag: str,
        description: str | None = None,
        status: str = "active",
    ) -> Any:
        """
        Create a VLAN inside a BNC-managed VLAN Group.

        The new VLAN receives:

            external-ctrl: bnc
            bnc-state: manage
            <network profile tag>
        """

        vlan_group = self.get_managed_vlan_group(
            vlan_group_id
        )

        if not profile_tag.startswith(
            "bnc-profile-"
        ):
            raise NetBoxValidationError(
                f"Invalid network profile tag: {profile_tag}"
            )

        tags = self._get_bnc_tags()

        tags.append(
            self._get_tag_id(profile_tag)
        )

        data: dict[str, Any] = {
            "group": vlan_group.id,
            "vid": vid,
            "name": name,
            "status": status,
            "tags": tags,
        }

        if description is not None:
            data["description"] = description

        return self.adapter.create_vlan(data)

    def update_vlan(
        self,
        vlan_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Any:
        """
        Update an existing BNC-managed VLAN.
        """

        vlan = self.get_managed_vlan(vlan_id)

        changes: dict[str, Any] = {}

        if name is not None:
            changes["name"] = name

        if description is not None:
            changes["description"] = description

        if status is not None:
            changes["status"] = status

        if not changes:
            return vlan

        return self.adapter.update_vlan(
            vlan.id,
            changes,
        )

    # ==================================================================
    # Prefixes
    # ==================================================================

    def get_prefixes(self) -> list[Any]:
        """
        Get prefixes exposed to BNC.
        """

        return self.adapter.filter_prefixes(
            tag=settings.netbox_tag_external_ctrl,
        )

    def get_prefix(
        self,
        prefix_id: int,
    ) -> Any:
        """
        Get a prefix exposed to BNC.
        """

        prefix = self.adapter.get_prefix(prefix_id)

        return self._require_exposed(
            prefix,
            "Prefix",
            prefix_id,
        )

    def get_managed_prefix(
        self,
        prefix_id: int,
    ) -> Any:
        """
        Get a prefix managed by BNC.
        """

        prefix = self.adapter.get_prefix(prefix_id)

        return self._require_managed(
            prefix,
            "Prefix",
            prefix_id,
        )

    def create_prefix(
        self,
        *,
        vlan_id: int,
        prefix: str,
        description: str | None = None,
        status: str = "active",
    ) -> Any:
        """
        Create a prefix attached to a BNC-managed VLAN.
        """

        vlan = self.get_managed_vlan(vlan_id)

        try:
            network = ipaddress.ip_network(
                prefix,
                strict=False,
            )
        except ValueError as exc:
            raise NetBoxValidationError(
                f"Invalid prefix: {prefix}"
            ) from exc

        data: dict[str, Any] = {
            "prefix": str(network),
            "vlan": vlan.id,
            "status": status,
            "tags": self._get_bnc_tags(),
        }

        if description is not None:
            data["description"] = description

        return self.adapter.create_prefix(data)

    def update_prefix(
        self,
        prefix_id: int,
        *,
        description: str | None = None,
        status: str | None = None,
    ) -> Any:
        """
        Update an existing BNC-managed prefix.
        """

        prefix = self.get_managed_prefix(prefix_id)

        changes: dict[str, Any] = {}

        if description is not None:
            changes["description"] = description

        if status is not None:
            changes["status"] = status

        if not changes:
            return prefix

        return self.adapter.update_prefix(
            prefix.id,
            changes,
        )

    # ==================================================================
    # IP Ranges
    # ==================================================================

    def get_ip_ranges(self) -> list[Any]:
        """
        Get IP ranges exposed to BNC.
        """

        return self.adapter.filter_ip_ranges(
            tag=settings.netbox_tag_external_ctrl,
        )

    def get_ip_range(
        self,
        ip_range_id: int,
    ) -> Any:
        """
        Get an IP range exposed to BNC.
        """

        ip_range = self.adapter.get_ip_range(
            ip_range_id
        )

        return self._require_exposed(
            ip_range,
            "IP Range",
            ip_range_id,
        )

    def get_managed_ip_range(
        self,
        ip_range_id: int,
    ) -> Any:
        """
        Get an IP range managed by BNC.
        """

        ip_range = self.adapter.get_ip_range(
            ip_range_id
        )

        return self._require_managed(
            ip_range,
            "IP Range",
            ip_range_id,
        )

    def create_ip_range(
        self,
        *,
        prefix_id: int,
        start_address: str,
        end_address: str,
        description: str | None = None,
        status: str = "active",
    ) -> Any:
        """
        Create an IP range inside a BNC-managed prefix.

        This is the operation BNC uses for DHCP pools.
        """

        prefix_record = self.get_managed_prefix(
            prefix_id
        )

        try:
            start = ipaddress.ip_interface(
                start_address
            ).ip

            end = ipaddress.ip_interface(
                end_address
            ).ip

            network = ipaddress.ip_network(
                prefix_record.prefix,
                strict=False,
            )

        except ValueError as exc:
            raise NetBoxValidationError(
                "Invalid IP address or prefix"
            ) from exc

        if start not in network:
            raise NetBoxValidationError(
                f"{start} is not inside {network}"
            )

        if end not in network:
            raise NetBoxValidationError(
                f"{end} is not inside {network}"
            )

        if int(start) > int(end):
            raise NetBoxValidationError(
                "Start address must be before end address"
            )

        data: dict[str, Any] = {
            "start_address": start_address,
            "end_address": end_address,
            "status": status,
            "tags": self._get_bnc_tags(),
        }

        if description is not None:
            data["description"] = description

        return self.adapter.create_ip_range(data)

    def update_ip_range(
        self,
        ip_range_id: int,
        *,
        description: str | None = None,
        status: str | None = None,
    ) -> Any:
        """
        Update an existing BNC-managed IP range.
        """

        ip_range = self.get_managed_ip_range(
            ip_range_id
        )

        changes: dict[str, Any] = {}

        if description is not None:
            changes["description"] = description

        if status is not None:
            changes["status"] = status

        if not changes:
            return ip_range

        return self.adapter.update_ip_range(
            ip_range.id,
            changes,
        )
