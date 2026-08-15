from app.netbox import NetBoxClient
from app.netbox.adapter.pynetbox import PynetboxAdapter
from app.services.site import SiteService


def get_netbox_client() -> NetBoxClient:
    return NetBoxClient(
        adapter=PynetboxAdapter(),
    )


def get_site_service() -> SiteService:
    return SiteService(
        netbox=get_netbox_client(),
    )
