"""
Excepciones personalizadas para el SDK de Datadis.

:author: TacoronteRiveroCristian
"""

class DatadisError(Exception):
    """Base exception for Datadis SDK"""

    pass


class AuthenticationError(DatadisError):
    """Authentication related errors"""

    pass


class APIError(DatadisError):
    """API response errors"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(DatadisError):
    """Parameter validation errors"""

    pass


__all__ = ["DatadisError", "AuthenticationError", "APIError", "ValidationError"]
