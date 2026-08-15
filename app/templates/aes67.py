from app.templates.base import NetworkTemplate


AES67_TEMPLATE = NetworkTemplate(
    key="aes67",
    name="AES67",
    netbox_tag="bnc-template-aes67",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v2",
    ptp_boundary_clock=True,
)
