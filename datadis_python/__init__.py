"""
Datadis Python SDK

Un SDK sencillo para interactuar con la API oficial de Datadis.
"""

from .client.datadis_client import DatadisClient
from .exceptions import DatadisError, AuthenticationError, APIError

__version__ = "0.1.0"
__all__ = ["DatadisClient", "DatadisError", "AuthenticationError", "APIError"]