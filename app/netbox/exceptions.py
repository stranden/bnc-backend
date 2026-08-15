class NetBoxError(Exception):
    """Base exception for NetBox-related errors."""


class NetBoxNotFoundError(NetBoxError):
    """Requested NetBox resource was not found."""


class NetBoxPermissionError(NetBoxError):
    """The requested NetBox operation is not permitted."""


class NetBoxValidationError(NetBoxError):
    """NetBox rejected the requested operation."""


class NetBoxConfigurationError(NetBoxError):
    """NetBox configuration is incompatible with BNC."""
