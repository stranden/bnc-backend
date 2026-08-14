from netbox import NetBoxClient
from services.site import SiteService


def get_netbox_client() -> NetBoxClient:
    return NetBoxClient()


def get_site_service() -> SiteService:
    return SiteService(
        netbox=get_netbox_client(),
    )
