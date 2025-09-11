"""
Módulo de utilidades y constantes para el SDK de Datadis.

Este módulo proporciona funciones y constantes comunes utilizadas en el SDK de Datadis.

:author: TacoronteRiveroCristian
"""

from .constants import API_ENDPOINTS  # Compatibilidad hacia atrás
from .constants import (
    API_V1_ENDPOINTS,
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
)
from .http import HTTPClient
from .text_utils import normalize_api_response, normalize_text
from .validators import validate_cups, validate_date_range, validate_distributor_code

__all__ = [
    # Validadores
    "validate_cups",
    "validate_date_range",
    "validate_distributor_code",
    # URLs y endpoints
    "DATADIS_BASE_URL",
    "DATADIS_API_BASE",
    "API_ENDPOINTS",  # Deprecated
    "API_V1_ENDPOINTS",
    "API_V2_ENDPOINTS",
    "AUTH_ENDPOINTS",
    # Configuración
    "DEFAULT_TIMEOUT",
    "MAX_RETRIES",
    # Cliente HTTP
    "HTTPClient",
    # Utilidades de texto
    "normalize_text",
    "normalize_api_response",
]
