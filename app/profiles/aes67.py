from profiles.base import NetworkProfile


AES67 = NetworkProfile(
    name="aes67",
    netbox_tag="bnc-profile-aes67",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v2",
    ptp_boundary_clock=True,
)
