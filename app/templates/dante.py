
from app.templates.base import NetworkTemplate


DANTE_TEMPLATE = NetworkTemplate(
    key="dante",
    name="Dante",
    netbox_tag="bnc-template-dante",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v1",
    ptp_boundary_clock=False,
)
