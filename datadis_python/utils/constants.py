"""
Constantes para la API de Datadis
"""

DATADIS_BASE_URL = "https://datadis.es"
DATADIS_AUTH_URL = "https://datadis.es/nikola-auth/tokens/login"
DATADIS_API_BASE = "https://datadis.es/api-private/api"

API_ENDPOINTS = {
    # Autenticación
    "login": "/nikola-auth/tokens/login",
    
    # Endpoints v1 (legacy)
    "supplies": "/get-supplies",
    "contracts": "/get-contract-detail", 
    "consumption": "/get-consumption-data",
    "max_power": "/get-max-power",
    "distributors": "/get-distributors-with-supplies",
    
    # Endpoints v2 (recomendados)
    "supplies_v2": "/get-supplies-v2",
    "contracts_v2": "/get-contract-detail-v2",
    "consumption_v2": "/get-consumption-data-v2", 
    "max_power_v2": "/get-max-power-v2",
    "distributors_v2": "/get-distributors-with-supplies-v2",
    "reactive_data": "/get-reactive-data-v2",
    
    # Autorizaciones
    "new_authorization": "/new-authorization",
    "cancel_authorization": "/cancel-authorization", 
    "list_authorization": "/list-authorization"
}

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

MEASUREMENT_TYPES = {
    "CONSUMPTION": 0,
    "GENERATION": 1
}

POINT_TYPES = {
    "BORDER": 1,
    "CONSUMPTION": 2,
    "GENERATION": 3,
    "AUXILIARY_SERVICES": 4
}