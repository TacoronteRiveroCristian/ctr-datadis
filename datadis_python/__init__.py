"""
Datadis Python SDK

Un SDK modular para interactuar con la API oficial de Datadis.
Soporta tanto API v1 (respuestas raw) como v2 (respuestas tipadas).
"""

# Cliente principal (unificado - recomendado)
from .client import DatadisClient

# Clientes específicos por versión
from .client import DatadisClientV1, DatadisClientV2

# Cliente legacy (compatibilidad hacia atrás)
from .client import DatadisClientLegacy

# Excepciones
from .exceptions import DatadisError, AuthenticationError, APIError

# Modelos (para usuarios que usen v2)
from .models import (
    SupplyData, ContractData, ConsumptionData, MaxPowerData,
    SuppliesResponse, ContractResponse, ConsumptionResponse, MaxPowerResponse
)

__version__ = "0.2.0"
__all__ = [
    # Clientes
    "DatadisClient",          # Cliente unificado (v1 + v2)
    "DatadisClientV1",        # API v1 raw
    "DatadisClientV2",        # API v2 tipado
    "DatadisClientLegacy",    # Cliente original
    
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
    "MaxPowerResponse"
]