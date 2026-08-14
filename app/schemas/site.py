from pydantic import BaseModel


class SiteCounts(BaseModel):
    device_count: int = 0
    vlan_group_count: int = 0
    vlan_count: int = 0
    prefix_count: int = 0


class SiteResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    tenant: str | None = None
    site_group: str | None = None

    device_count: int = 0
    vlan_group_count: int = 0
    vlan_count: int = 0
    prefix_count: int = 0
