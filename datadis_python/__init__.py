"""
Datadis Python SDK.

Un SDK modular para interactuar con la API oficial de Datadis.
Soporta tanto API v1 (respuestas raw) como v2 (respuestas tipadas).
"""

__version__ = "0.1.3"

# Cliente legacy (compatibilidad hacia atrás)
# Clientes específicos por versión
# Cliente principal (unificado - recomendado)
from .client import DatadisClient, DatadisClientLegacy, DatadisClientV1, DatadisClientV2

# Excepciones
from .exceptions import APIError, AuthenticationError, DatadisError

# Modelos (para usuarios que usen v2)
from .models import (
    ConsumptionData,
    ConsumptionResponse,
    ContractData,
    ContractResponse,
    MaxPowerData,
    MaxPowerResponse,
    SuppliesResponse,
    SupplyData,
)

__all__ = [
    # Clientes
    "DatadisClient",  # Cliente unificado (v1 + v2)
    "DatadisClientV1",  # API v1 raw
    "DatadisClientV2",  # API v2 tipado
    "DatadisClientLegacy",  # Cliente original
    # Excepciones
    "DatadisError",
    "AuthenticationError",
    "APIError",
    # Modelos (para v2)
    "SupplyData",
    "ContractData",
    "ConsumptionData",
    "MaxPowerData",
    "SuppliesResponse",
    "ContractResponse",
    "ConsumptionResponse",
    "MaxPowerResponse",
]
