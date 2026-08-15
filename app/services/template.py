from __future__ import annotations

from typing import Any

from app.templates.base import NetworkTemplate
from app.templates.exceptions import TemplateNotFoundError
from app.templates.registry import get_template, get_templates


class TemplateService:
    def get_templates(self) -> list[dict[str, Any]]:
        return [
            self._to_data(template)
            for template in get_templates()
        ]

    def get_template(self, slug: str) -> dict[str, Any]:
        template = get_template(slug)

        if template is None:
            raise TemplateNotFoundError(
                f"Network template '{slug}' not found."
            )

        return self._to_data(template)

    @staticmethod
    def _to_data(
        template: NetworkTemplate,
    ) -> dict[str, Any]:
        return {
            "slug": template.slug,
            "name": template.name,
            "description": template.description,
        }
