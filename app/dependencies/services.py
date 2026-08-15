from app.netbox import NetBoxClient
from app.netbox.adapter.pynetbox import PynetboxAdapter
from app.services.site import SiteService
from app.services.vlan import VlanService
from app.services.template import TemplateService

def get_netbox_client() -> NetBoxClient:
    return NetBoxClient(
        adapter=PynetboxAdapter(),
    )


def get_site_service() -> SiteService:
    return SiteService(
        netbox=get_netbox_client(),
    )


def get_vlan_service() -> VlanService:
    return VlanService(
        netbox=get_netbox_client(),
    )


def get_template_service() -> TemplateService:
    return TemplateService()
