from dataclasses import dataclass

from app.templates.base import NetworkTemplate


@dataclass(frozen=True)
class DanteTemplate(NetworkTemplate):
    """
    Network template for Dante audio networks.
    """

    ptp_version: int = 1
    multicast: bool = True
    igmp_querier: bool = True


DANTE = DanteTemplate(
    slug="dante",
    name="Dante",
    description="Dante audio network.",
)
