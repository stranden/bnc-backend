from dataclasses import dataclass

from app.templates.base import NetworkTemplate


@dataclass(frozen=True)
class SMPTE2110Template(NetworkTemplate):
    """
    Network template for SMPTE ST 2110 networks.
    """

    ptp_version: int = 2
    multicast: bool = True
    igmp_querier: bool = True


SMPTE_2110 = SMPTE2110Template(
    slug="smpte-2110",
    name="SMPTE 2110",
    description="SMPTE ST 2110 media network.",
)
