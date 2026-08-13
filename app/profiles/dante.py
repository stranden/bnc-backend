
from app.profiles.base import NetworkProfile


DANTE = NetworkProfile(
    name="dante",
    netbox_tag="bnc-profile-dante",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,

    ptp_version="v1",
    ptp_boundary_clock=False,
)
