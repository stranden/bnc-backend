from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkProfile:
    name: str
    netbox_tag: str

    multicast: bool = False
    igmp: bool = False
    igmp_querier: bool = False
    qos: bool = False

    ptp_version: str | None = None
    ptp_boundary_clock: bool = False
