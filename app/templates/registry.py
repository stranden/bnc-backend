from app.templates.aes67 import AES67
from app.templates.data import DATA
from app.templates.dante import DANTE
from app.templates.smpte_2110 import SMPTE_2110
from app.templates.base import NetworkTemplate


TEMPLATES: dict[str, NetworkTemplate] = {
    template.slug: template
    for template in (
        DANTE,
        AES67,
        DATA,
        SMPTE_2110,
    )
}


def get_template(slug: str) -> NetworkTemplate | None:
    return TEMPLATES.get(slug)


def get_templates() -> list[NetworkTemplate]:
    return list(TEMPLATES.values())
