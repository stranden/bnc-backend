from dataclasses import dataclass

from app.templates.base import NetworkTemplate


@dataclass(frozen=True)
class AES67Template(NetworkTemplate):
    """
    Network template for AES67 audio networks.
    """

    ptp_version: int = 2
    multicast: bool = True
    igmp_querier: bool = True


AES67 = AES67Template(
    slug="aes67",
    name="AES67",
    description="AES67 audio network.",
)
