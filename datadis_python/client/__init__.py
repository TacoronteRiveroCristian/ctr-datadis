"""
Clientes para la API de Datadis - Todas las versiones.

Este módulo proporciona clientes para interactuar con las diferentes versiones de la API de Datadis.
"""

# Cliente legacy (compatibilidad hacia atrás)
from .datadis_client import DatadisClient as DatadisClientLegacy

# Cliente unificado (recomendado)
from .unified import DatadisClient

# Clientes específicos por versión
from .v1 import DatadisClientV1
from .v2 import DatadisClientV2

__all__ = [
    "DatadisClient",  # Cliente unificado (recomendado)
    "DatadisClientV1",  # API v1 (raw responses)
    "DatadisClientV2",  # API v2 (typed responses)
    "DatadisClientLegacy",  # Cliente original (deprecated)
]
