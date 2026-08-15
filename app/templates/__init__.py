"""
Network templates.
"""
from app.templates.base import NetworkTemplate
from app.templates.registry import (
    get_template,
    get_template_by_tag,
    get_templates,
)

__all__ = [
    "NetworkTemplate",
    "get_template",
    "get_template_by_tag",
    "get_templates",
]
