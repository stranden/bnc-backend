from __future__ import annotations

from typing import Any

from app.netbox import NetBoxClient
from app.schemas.vlan import VlanCreate, VlanUpdate


class VlanService:
    def __init__(self, netbox: NetBoxClient) -> None:
        self.netbox = netbox

    # ============================================================
    # VLANs - Read
    # ============================================================

    def get_vlans(
        self,
        site_id: int,
    ) -> list[dict[str, Any]]:
        vlans = self.netbox.get_vlans(
            site_id=site_id,
        )

        return [
            self._to_data(
                vlan,
                site_id=site_id,
            )
            for vlan in vlans
        ]

    def get_vlan(
        self,
        vid: int,
        site_id: int,
    ) -> dict[str, Any]:
        vlan = self.netbox.get_vlan(
            vid=vid,
            site_id=site_id,
        )

        return self._to_data(
            vlan,
            site_id=site_id,
        )

    # ============================================================
    # VLANs - Create
    # ============================================================

    def create_vlan(
        self,
        data: VlanCreate,
    ) -> dict[str, Any]:
        vlan = self.netbox.create_vlan(
            site_id=data.site_id,
            vid=data.vid,
            name=data.name,
            description=data.description,
            template=data.template,
        )

        return self._to_data(
            vlan,
            site_id=data.site_id,
        )

    # ============================================================
    # VLANs - Update
    # ============================================================

    def update_vlan(
        self,
        vid: int,
        data: VlanUpdate,
    ) -> dict[str, Any]:
        """
        Update a VLAN.

        The template field has three possible states:

            template omitted
                Do not change the current template.

            template="dante"
                Set/change the template.

            template=null
                Remove the template.
        """
        vlan = self.netbox.update_vlan(
            vid=vid,
            site_id=data.site_id,
            name=data.name,
            description=data.description,
            template=data.template,
            update_template="template" in data.model_fields_set,
        )

        return self._to_data(
            vlan,
            site_id=data.site_id,
        )

    # ============================================================
    # VLANs - Delete
    # ============================================================

    def delete_vlan(
        self,
        vid: int,
        site_id: int,
    ) -> None:
        self.netbox.delete_vlan(
            vid=vid,
            site_id=site_id,
        )

    # ============================================================
    # Serialization
    # ============================================================

    def _to_data(
        self,
        vlan: Any,
        site_id: int,
    ) -> dict[str, Any]:
        template = self.netbox.get_vlan_template(vlan)

        return {
            "vid": vlan.vid,
            "site_id": site_id,
            "name": vlan.name,
            "description": getattr(
                vlan,
                "description",
                None,
            ),
            "template": (
                template.slug
                if template is not None
                else None
            ),
        }
