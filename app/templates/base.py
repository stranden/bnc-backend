from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkTemplate:
    """
    Base definition for a BNC network service template.

    A NetworkTemplate describes the intended characteristics of
    a network service. It is not a device configuration template.
    """

    slug: str
    name: str
    description: str
