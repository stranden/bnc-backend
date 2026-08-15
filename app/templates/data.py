
from app.templates.base import NetworkTemplate


DATA_TEMPLATE = NetworkTemplate(
    key="data",
    name="Data",
    netbox_tag="bnc-template-data",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,
)
