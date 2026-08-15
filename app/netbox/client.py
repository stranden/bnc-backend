from __future__ import annotations

from typing import Any

from app.config.settings import settings
from app.netbox.adapter.pynetbox import PynetboxAdapter
from app.netbox.exceptions import (
    NetBoxConfigurationError,
    NetBoxNotFoundError,
    NetBoxPermissionError,
)
from app.templates.base import NetworkTemplate
from app.templates.exceptions import (
    TemplateConfigurationError,
    TemplateNotFoundError,
)
from app.templates.registry import get_template


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

    def get_site(
        self,
        site_id: int,
    ) -> Any:
        """
        Return a Site exposed to BNC.

        Raises:
            NetBoxNotFoundError:
                Site does not exist or is not exposed to BNC.
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
                f"Site {site_id} is not exposed to BNC."
            )

        return site

    def get_site_counts(
        self,
        site_id: int,
    ) -> dict[str, int]:
        """
        Return resource counts for a BNC-managed Site.
        """
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

    def _get_site_vlan_count(
        self,
        site_id: int,
    ) -> int:
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
    # VLANs - Read
    # ============================================================

    def get_vlans(
        self,
        site_id: int,
    ) -> list[Any]:
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

    # ============================================================
    # VLANs - Create
    # ============================================================

    def create_vlan(
        self,
        site_id: int,
        vid: int,
        name: str,
        description: str | None = None,
        template: str | None = None,
    ) -> Any:
        """
        Create a VLAN in the managed VLAN Group for a Site.

        The VLAN inherits its Tenant from the Site.

        The VLAN is associated with the Site indirectly through
        its VLAN Group. The deprecated NetBox VLAN site field
        is deliberately not used.

        Every VLAN created by BNC receives:
            - external-control tag
            - BNC management-state tag

        If a template is supplied, the corresponding BNC
        template tag is also assigned.
        """

        # --------------------------------------------------------
        # Resolve Site
        # --------------------------------------------------------

        site = self.get_site(site_id)

        # --------------------------------------------------------
        # Resolve Tenant from Site
        # --------------------------------------------------------

        tenant = getattr(site, "tenant", None)

        if tenant is None:
            raise NetBoxConfigurationError(
                f"Site '{site.name}' does not have a tenant."
            )

        # --------------------------------------------------------
        # Resolve managed VLAN Group
        # --------------------------------------------------------

        vlan_group = self._get_managed_vlan_group(
            site_id,
        )

        self._require_manage_permission(
            vlan_group,
        )

        # --------------------------------------------------------
        # Validate template
        # --------------------------------------------------------

        if template is not None:
            network_template = get_template(template)

            if network_template is None:
                raise TemplateNotFoundError(
                    f"Network template '{template}' not found."
                )

        # --------------------------------------------------------
        # Build tags
        # --------------------------------------------------------

        tags = [
            settings.netbox_tag_external_ctrl,
            settings.netbox_tag_state_manage,
        ]

        if template is not None:
            tags.append(
                f"{settings.netbox_template_tag_prefix}-{template}"
            )

        # --------------------------------------------------------
        # Build VLAN data
        # --------------------------------------------------------

        data: dict[str, Any] = {
            "tenant": tenant.id,
            "group": vlan_group.id,
            "vid": vid,
            "name": name,
            "tags": tags,
        }

        if description is not None:
            data["description"] = description

        # --------------------------------------------------------
        # Create VLAN
        # --------------------------------------------------------

        return self.adapter.create_vlan(
            data,
        )

    # ============================================================
    # VLANs - Update
    # ============================================================

    def update_vlan(
        self,
        vid: int,
        site_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        template: str | None = None,
        update_template: bool = False,
    ) -> Any:
        """
        Update a VLAN identified by VID within a Site.

        Template semantics:

            update_template=False
                Do not modify the template.

            template="dante"
                Set/change the template.

            template=None
                Remove the template.
        """
        vlan, vlan_group = self._get_vlan_context(
            vid=vid,
            site_id=site_id,
        )

        self._require_manage_permission(
            vlan_group,
        )

        # --------------------------------------------------------
        # Update normal VLAN properties
        # --------------------------------------------------------

        data: dict[str, Any] = {}

        if name is not None:
            data["name"] = name

        if description is not None:
            data["description"] = description

        if data:
            updated_vlan = self.adapter.update_vlan(
                vlan_id=vlan.id,
                data=data,
            )

            if updated_vlan is None:
                raise NetBoxNotFoundError(
                    f"VLAN {vid} not found."
                )

            vlan = updated_vlan

        # --------------------------------------------------------
        # Update template
        # --------------------------------------------------------

        if update_template:
            if template is not None:
                network_template = get_template(template)

                if network_template is None:
                    raise TemplateNotFoundError(
                        f"Network template '{template}' not found."
                    )

            vlan = self._set_vlan_template(
                vlan=vlan,
                template=template,
            )

        return vlan

    # ============================================================
    # VLANs - Delete
    # ============================================================

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

        self._require_manage_permission(
            vlan_group,
        )

        deleted = self.adapter.delete_vlan(
            vlan_id=vlan.id,
        )

        if not deleted:
            raise NetBoxNotFoundError(
                f"VLAN {vid} not found."
            )

    # ============================================================
    # VLAN Templates
    # ============================================================

    def get_vlan_template(
        self,
        vlan: Any,
    ) -> NetworkTemplate | None:
        """
        Resolve the NetworkTemplate assigned to a VLAN.

        A VLAN may have:
            - zero template tags
            - exactly one template tag

        An unknown template is treated as no BNC template.

        More than one template tag is considered invalid
        BNC configuration.
        """
        template_slugs = self._get_template_slugs(
            vlan,
        )

        if not template_slugs:
            return None

        if len(template_slugs) > 1:
            raise TemplateConfigurationError(
                f"VLAN {vlan.vid} has multiple network templates: "
                f"{', '.join(template_slugs)}."
            )

        slug = template_slugs[0]

        return get_template(slug)

    @staticmethod
    def _get_template_slugs(
        vlan: Any,
    ) -> list[str]:
        """
        NetBox template tags use:

            <prefix>-<template-slug>

        Example:

            bnc-template-dante
            bnc-template-aes67
        """
        prefix = settings.netbox_template_tag_prefix

        template_slugs: list[str] = []

        tags = getattr(vlan, "tags", [])

        for tag in tags:
            slug = NetBoxClient._get_tag_name(
                tag,
            )

            if not slug:
                continue

            if not slug.startswith(
                f"{prefix}-"
            ):
                continue

            template_slug = slug[
                len(prefix) + 1:
            ]

            if template_slug:
                template_slugs.append(
                    template_slug
                )

        return template_slugs

    def _set_vlan_template(
        self,
        vlan: Any,
        template: str | None,
    ) -> Any:
        """
        Set or remove the BNC NetworkTemplate on a VLAN.

        Only BNC template tags are modified.
        All unrelated NetBox tags are preserved.

        Examples:

            template="dante"
                Adds bnc-template-dante.

            template=None
                Removes all bnc-template-* tags.
        """
        prefix = settings.netbox_template_tag_prefix

        current_tags = getattr(
            vlan,
            "tags",
            [],
        )

        tags: list[str] = []

        for tag in current_tags:
            slug = self._get_tag_name(
                tag,
            )

            if not slug:
                continue

            # Preserve all non-template tags.
            if not slug.startswith(
                f"{prefix}-"
            ):
                tags.append(slug)

        # Add the new template tag.
        if template is not None:
            tags.append(
                f"{prefix}-{template}"
            )

        updated_vlan = self.adapter.update_vlan_tags(
            vlan_id=vlan.id,
            tags=tags,
        )

        if updated_vlan is None:
            raise NetBoxNotFoundError(
                f"VLAN {vlan.vid} not found."
            )

        return updated_vlan

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

        The VLAN is always looked up inside the VLAN Group
        belonging to the requested Site.
        """
        vlan_group = self._get_managed_vlan_group(
            site_id,
        )

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
        """
        self.get_site(
            site_id,
        )

        vlan_groups = self.adapter.filter_vlan_groups(
            site_id=site_id,
            tag=settings.netbox_tag_external_ctrl,
        )

        if not vlan_groups:
            raise NetBoxNotFoundError(
                f"No BNC-managed VLAN Group found "
                f"for Site {site_id}."
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
        Check whether a NetBox resource has a specific tag.
        """
        tags = getattr(
            resource,
            "tags",
            [],
        )

        for tag in tags:
            tag_name = NetBoxClient._get_tag_name(
                tag,
            )

            if tag_name == tag_slug:
                return True

        return False

    @staticmethod
    def _get_tag_name(
        tag: Any,
    ) -> str | None:
        """
        Return the most useful identifier from a pynetbox tag.
        """
        if isinstance(tag, str):
            return tag

        slug = getattr(
            tag,
            "slug",
            None,
        )

        if slug:
            return slug

        name = getattr(
            tag,
            "name",
            None,
        )

        if name:
            return name

        return None
