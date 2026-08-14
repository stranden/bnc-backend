
from profiles.base import NetworkProfile


DATA = NetworkProfile(
    name="data",
    netbox_tag="bnc-profile-data",

    multicast=True,
    igmp=True,
    igmp_querier=True,
    qos=True,
)
