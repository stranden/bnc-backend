from app.templates.base import NetworkTemplate


SMPTE_2110_TEMPLATE = NetworkTemplate(
    key="smpte-2110",
    name="SMPTE 2110",
    netbox_tag="bnc-template-smpte-2110",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v2",
    ptp_boundary_clock=True,
)
