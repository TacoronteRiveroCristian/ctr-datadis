"""
Constantes para la API de Datadis separadas por versión.

Este módulo define las constantes utilizadas para interactuar con las diferentes versiones de la API de Datadis.

:author: TacoronteRiveroCristian
"""

# URLs base
DATADIS_BASE_URL = "https://datadis.es"
DATADIS_AUTH_URL = "https://datadis.es/nikola-auth/tokens/login"
DATADIS_API_BASE = "https://datadis.es/api-private/api"

# Autenticación (común a ambas versiones)
AUTH_ENDPOINTS = {
    "login": "/nikola-auth/tokens/login",
}

# Endpoints API v1 (estables, respuestas raw)
API_V1_ENDPOINTS = {
    "supplies": "/get-supplies",
    "contracts": "/get-contract-detail",
    "consumption": "/get-consumption-data",
    "max_power": "/get-max-power",
    "distributors": "/get-distributors-with-supplies",
}

# Endpoints API v2 (modernos, respuestas estructuradas)
API_V2_ENDPOINTS = {
    "supplies": "/get-supplies-v2",
    "contracts": "/get-contract-detail-v2",
    "consumption": "/get-consumption-data-v2",
    "max_power": "/get-max-power-v2",
    "distributors": "/get-distributors-with-supplies-v2",
    "reactive_data": "/get-reactive-data-v2",
}

# Endpoints de autorización (común)
AUTHORIZATION_ENDPOINTS = {
    "new_authorization": "/new-authorization",
    "cancel_authorization": "/cancel-authorization",
    "list_authorization": "/list-authorization",
}

# Configuración por defecto (aumentar timeout para Datadis)
DEFAULT_TIMEOUT = 90  # Datadis puede ser lento
MAX_RETRIES = 5  # Más reintentos
TOKEN_EXPIRY_HOURS = 24

# Tipos de medida (común)
MEASUREMENT_TYPES = {"CONSUMPTION": 0, "GENERATION": 1}

# Tipos de punto (común)
POINT_TYPES = {
    "BORDER": 1,
    "CONSUMPTION": 2,
    "GENERATION": 3,
    "AUXILIARY_SERVICES": 4,
    "AUXILIARY_SERVICES_ALT": 5,
}

# Códigos de distribuidoras (común)
DISTRIBUTOR_CODES = {
    "VIESGO": "1",
    "E_DISTRIBUCION": "2",
    "E_REDES": "3",
    "ASEME": "4",
    "UFD": "5",
    "EOSA": "6",
    "CIDE": "7",
    "IDE": "8",
}

# Compatibilidad hacia atrás (DEPRECATED)
API_ENDPOINTS = {
    **AUTH_ENDPOINTS,
    **{k: v for k, v in API_V1_ENDPOINTS.items()},
    **{f"{k}_v2": v for k, v in API_V2_ENDPOINTS.items()},
    **AUTHORIZATION_ENDPOINTS,
}
