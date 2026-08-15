from __future__ import annotations

from typing import Any

from app.netbox import NetBoxClient
from app.schemas.vlan import VlanCreate, VlanUpdate


class VlanService:
    """
    BNC VLAN service.

    Contains BNC/application-level VLAN operations.
    NetBox-specific implementation details remain in NetBoxClient.
    """

    def __init__(
        self,
        netbox: NetBoxClient,
    ) -> None:
        self.netbox = netbox

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

    def create_vlan(
        self,
        data: VlanCreate,
    ) -> dict[str, Any]:
        vlan = self.netbox.create_vlan(
            site_id=data.site_id,
            vid=data.vid,
            name=data.name,
            description=data.description,
        )

        return self._to_data(
            vlan,
            site_id=data.site_id,
        )

    def update_vlan(
        self,
        vid: int,
        data: VlanUpdate,
    ) -> dict[str, Any]:
        vlan = self.netbox.update_vlan(
            vid=vid,
            site_id=data.site_id,
            name=data.name,
            description=data.description,
        )

        return self._to_data(
            vlan,
            site_id=data.site_id,
        )

    def delete_vlan(
        self,
        vid: int,
        site_id: int,
    ) -> None:
        self.netbox.delete_vlan(
            vid=vid,
            site_id=site_id,
        )

    @staticmethod
    def _to_data(
        vlan: Any,
        site_id: int,
    ) -> dict[str, Any]:
        return {
            "id": vlan.id,
            "site_id": site_id,
            "vid": vlan.vid,
            "name": vlan.name,
            "description": getattr(
                vlan,
                "description",
                None,
            ),
        }
