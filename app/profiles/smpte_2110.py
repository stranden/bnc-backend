from profiles.base import NetworkProfile


SMPTE_2110 = NetworkProfile(
    name="smpte-2110",
    netbox_tag="bnc-profile-smpte-2110",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v2",
    ptp_boundary_clock=True,
)
