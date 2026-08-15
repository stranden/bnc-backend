# app/templates/exceptions.py

class TemplateError(Exception):
    """Base exception for network template errors."""


class TemplateNotFoundError(TemplateError):
    """Requested network template does not exist."""


class TemplateConfigurationError(TemplateError):
    """NetBox template configuration is invalid."""
