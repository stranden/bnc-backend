from app.templates.aes67 import AES67_TEMPLATE
from app.templates.base import NetworkTemplate
from app.templates.data import DATA_TEMPLATE
from app.templates.dante import DANTE_TEMPLATE
from app.templates.smpte_2110 import SMPTE_2110_TEMPLATE


TEMPLATES: tuple[NetworkTemplate, ...] = (
    DATA_TEMPLATE,
    DANTE_TEMPLATE,
    AES67_TEMPLATE,
    SMPTE_2110_TEMPLATE,
)


TEMPLATES_BY_KEY: dict[str, NetworkTemplate] = {
    template.key: template
    for template in TEMPLATES
}


TEMPLATES_BY_TAG: dict[str, NetworkTemplate] = {
    template.netbox_tag: template
    for template in TEMPLATES
}


def get_template(
    key: str,
) -> NetworkTemplate | None:
    return TEMPLATES_BY_KEY.get(key)


def get_template_by_tag(
    tag: str,
) -> NetworkTemplate | None:
    return TEMPLATES_BY_TAG.get(tag)


def get_templates() -> tuple[NetworkTemplate, ...]:
    return TEMPLATES
