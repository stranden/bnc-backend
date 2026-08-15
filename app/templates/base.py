from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkTemplate:
    """
    BNC network template.

    A template describes the intent of a VLAN.

    It does not contain vendor-specific switch configuration.
    """

    key: str
    name: str
    netbox_tag: str

    multicast: bool = False
    igmp: bool = False
    igmp_querier: bool = False
    qos: bool = False

    ptp_version: str | None = None
    ptp_boundary_clock: bool = False
