"""
Constantes y configuraciones para el SDK de Datadis.

Este módulo centraliza todas las constantes utilizadas para interactuar con la API
de Datadis, incluyendo URLs base, endpoints, códigos de distribuidores y configuraciones
por defecto. Proporciona soporte para ambas versiones de la API (V1 y V2) manteniendo
compatibilidad hacia atrás.

La API de Datadis es la plataforma oficial del gobierno español para acceder a datos
de consumo eléctrico de las distribuidoras eléctricas. Este módulo abstrae toda la
configuración necesaria para facilitar el desarrollo con el SDK.

Organización de constantes:
    - **URLs base**: URLs principales de autenticación y API
    - **Endpoints por versión**: V1 (estables) y V2 (modernos con mejoras)
    - **Códigos de distribuidores**: Mapeo completo de todas las distribuidoras españolas
    - **Configuraciones por defecto**: Timeouts, reintentos y otros parámetros optimizados
    - **Tipos de medida y punto**: Constantes para clasificar datos eléctricos

Example:
    Uso básico de constantes::

        from datadis_python.utils.constants import (
            DATADIS_API_BASE,
            API_V2_ENDPOINTS,
            DISTRIBUTOR_CODES,
            DEFAULT_TIMEOUT
        )

        # Construir URL de endpoint V2
        supplies_url = f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}"

        # Usar código de distribuidor por nombre
        endesa_code = DISTRIBUTOR_CODES["E_DISTRIBUCION"]  # "2"

        # Configurar timeout por defecto
        requests.get(url, timeout=DEFAULT_TIMEOUT)

    Migración de V1 a V2::

        # V1 (endpoints legacy)
        v1_endpoint = API_V1_ENDPOINTS["consumption"]  # "/get-consumption-data"

        # V2 (endpoints modernos)
        v2_endpoint = API_V2_ENDPOINTS["consumption"]  # "/get-consumption-data-v2"

Note:
    Los endpoints V2 incluyen funcionalidades adicionales como manejo de errores
    por distribuidor y estructuras de respuesta mejoradas. Se recomienda usar V2
    para nuevas implementaciones.

Warning:
    La constante ``API_ENDPOINTS`` está marcada como DEPRECATED y se mantiene
    solo para compatibilidad hacia atrás. Use ``API_V1_ENDPOINTS`` o ``API_V2_ENDPOINTS``
    según la versión de API que necesite.

:author: TacoronteRiveroCristian
"""

# URLs base de la plataforma Datadis
#: URL principal del portal web de Datadis
DATADIS_BASE_URL = "https://datadis.es"

#: URL específica para autenticación de usuarios
DATADIS_AUTH_URL = "https://datadis.es/nikola-auth/tokens/login"

#: URL base para todas las peticiones a la API privada de Datadis
DATADIS_API_BASE = "https://datadis.es/api-private/api"

# Endpoints de autenticación (común a todas las versiones)
#: Endpoints para operaciones de autenticación y gestión de tokens.
#: Estos endpoints son compartidos por todas las versiones de la API.
AUTH_ENDPOINTS = {
    "login": "/nikola-auth/tokens/login",
}

# Endpoints de la API V1 (versión estable y legacy)
#: Endpoints para la API V1 de Datadis.
#:
#: La versión 1 de la API proporciona respuestas directas (listas o diccionarios simples)
#: sin estructuras de error por distribuidor. Es la versión original y más estable
#: de la API, pero carece de algunas funcionalidades modernas.
#:
#: Características de V1:
#:     - Respuestas simples: List[SupplyData], List[ConsumptionData], etc.
#:     - Sin manejo de errores por distribuidor
#:     - Funcionalidad básica completa
#:     - Mayor compatibilidad con sistemas legacy
#:
#: Example:
#:     Construir URL de endpoint V1::
#:
#:         from datadis_python.utils.constants import DATADIS_API_BASE, API_V1_ENDPOINTS
#:
#:         supplies_url = f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}"
#:         # Resultado: "https://datadis.es/api-private/api/get-supplies"
API_V1_ENDPOINTS = {
    "supplies": "/get-supplies",
    "contracts": "/get-contract-detail",
    "consumption": "/get-consumption-data",
    "max_power": "/get-max-power",
    "distributors": "/get-distributors-with-supplies",
}

# Endpoints de la API V2 (versión moderna con mejoras)
#: Endpoints para la API V2 de Datadis.
#:
#: La versión 2 de la API introduce mejoras significativas incluyendo manejo
#: robusto de errores por distribuidor, estructuras de respuesta tipadas y
#: funcionalidades adicionales como datos de energía reactiva.
#:
#: Mejoras de V2 sobre V1:
#:     - **Manejo de errores por distribuidor**: Información detallada de fallos
#:     - **Respuestas estructuradas**: SuppliesResponse, ConsumptionResponse, etc.
#:     - **Funcionalidad extendida**: Acceso a datos de energía reactiva
#:     - **Mejor compatibilidad**: Preparada para futuras funcionalidades
#:
#: Note:
#:     Se recomienda usar la API V2 para nuevas implementaciones. Los endpoints V2
#:     mantienen compatibilidad de interfaz con V1 pero devuelven estructuras de datos
#:     más robustas que incluyen información de errores detallada.
#:
#: Example:
#:     Comparación de endpoints V1 vs V2::
#:
#:         # V1 - Respuesta simple
#:         v1_url = f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}"
#:         # GET /get-supplies → List[SupplyData]
#:
#:         # V2 - Respuesta estructurada con manejo de errores
#:         v2_url = f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}"
#:         # GET /get-supplies-v2 → SuppliesResponse (includes distributor_error)
API_V2_ENDPOINTS = {
    "supplies": "/get-supplies-v2",
    "contracts": "/get-contract-detail-v2",
    "consumption": "/get-consumption-data-v2",
    "max_power": "/get-max-power-v2",
    "distributors": "/get-distributors-with-supplies-v2",
    "reactive_data": "/get-reactive-data-v2",
}

# Endpoints de autorización para terceros (funcionalidad avanzada)
#: Endpoints para gestión de autorizaciones entre usuarios.
#:
#: Estos endpoints permiten gestionar autorizaciones para que un usuario pueda
#: consultar los datos de consumo de otro usuario (por ejemplo, un gestor energético
#: consultando datos de sus clientes con autorización previa).
#:
#: Flujo de autorización:
#:     1. **new_authorization**: Crear nueva autorización
#:     2. **list_authorization**: Listar autorizaciones activas
#:     3. **cancel_authorization**: Cancelar autorización existente
#:
#: Note:
#:     Esta funcionalidad requiere configuración especial en la cuenta de Datadis
#:     y está orientada a usuarios avanzados como gestores energéticos o empresas
#:     de servicios energéticos.
AUTHORIZATION_ENDPOINTS = {
    "new_authorization": "/new-authorization",
    "cancel_authorization": "/cancel-authorization",
    "list_authorization": "/list-authorization",
}

# Configuración por defecto optimizada para la API de Datadis
#: Timeout por defecto para peticiones HTTP en segundos.
#:
#: El valor de 90 segundos está optimizado para la API de Datadis, que puede ser
#: notablemente lenta debido a la necesidad de consultar múltiples sistemas de
#: distribuidoras eléctricas en tiempo real.
#:
#: Note:
#:     La API de Datadis puede tardar hasta 60-80 segundos en responder consultas
#:     complejas, especialmente cuando debe agregar datos de múltiples distribuidores
#:     o procesar rangos de fechas extensos.
DEFAULT_TIMEOUT = 90

#: Número máximo de reintentos automáticos para peticiones fallidas.
#:
#: Se incrementa a 5 reintentos debido a la naturaleza inestable de algunos endpoints
#: de Datadis y la dependencia de sistemas externos de las distribuidoras eléctricas.
#: Los reintentos usan backoff exponencial para evitar sobrecargar el servidor.
MAX_RETRIES = 5

#: Duración estimada de validez de los tokens de autenticación en horas.
#:
#: Los tokens de Datadis tienen una validez limitada. Aunque la duración exacta
#: no está documentada oficialmente, la experiencia práctica sugiere que expiran
#: en aproximadamente 24 horas.
#:
#: Note:
#:     El SDK maneja automáticamente la renovación de tokens cuando detecta
#:     errores 401 (Unauthorized), por lo que este valor es principalmente informativo.
TOKEN_EXPIRY_HOURS = 24

# Tipos de medida eléctrica (común a todas las APIs)
#: Constantes para los tipos de medida eléctrica soportados por Datadis.
#:
#: La API de Datadis distingue entre consumo (energía tomada de la red) y
#: generación (energía inyectada a la red, típicamente de instalaciones
#: fotovoltaicas u otras fuentes renovables).
#:
#: Valores válidos:
#:     - **CONSUMPTION (0)**: Energía consumida desde la red eléctrica
#:     - **GENERATION (1)**: Energía generada e inyectada a la red
#:
#: Example:
#:     Usar constantes de tipo de medida::
#:
#:         from datadis_python.utils.constants import MEASUREMENT_TYPES
#:
#:         # Obtener datos de consumo
#:         consumption_data = client.get_consumption(
#:             cups="ES001234567890123456AB",
#:             distributor_code="2",
#:             date_from="2024/01",
#:             date_to="2024/12",
#:             measurement_type=MEASUREMENT_TYPES["CONSUMPTION"]  # 0
#:         )
#:
#:         # Obtener datos de generación (ej: paneles solares)
#:         generation_data = client.get_consumption(
#:             cups="ES001234567890123456AB",
#:             distributor_code="2",
#:             date_from="2024/01",
#:             date_to="2024/12",
#:             measurement_type=MEASUREMENT_TYPES["GENERATION"]  # 1
#:         )
MEASUREMENT_TYPES = {"CONSUMPTION": 0, "GENERATION": 1}

# Tipos de punto de medida eléctrica (común a todas las APIs)
#: Constantes para los tipos de punto de medida eléctrica según normativa española.
#:
#: Los tipos de punto definen la naturaleza y propósito del punto de medida eléctrica
#: según la normativa del sistema eléctrico español. Cada tipo tiene características
#: específicas y se usa en diferentes contextos de la red eléctrica.
#:
#: Tipos de punto válidos:
#:     - **BORDER (1)**: Punto de frontera - Intercambio entre sistemas
#:     - **CONSUMPTION (2)**: Punto de consumo - Usuarios finales domésticos/comerciales
#:     - **GENERATION (3)**: Punto de generación - Plantas de generación eléctrica
#:     - **AUXILIARY_SERVICES (4)**: Servicios auxiliares - Equipos de soporte al sistema
#:     - **AUXILIARY_SERVICES_ALT (5)**: Servicios auxiliares alternativos
#:
#: Note:
#:     El tipo de punto más común para usuarios domésticos y comerciales es
#:     **CONSUMPTION (2)**. Los tipos de generación se usan principalmente para
#:     instalaciones con autoconsumo que inyectan energía a la red.
#:
#: Example:
#:     Filtrar por tipo de punto específico::
#:
#:         from datadis_python.utils.constants import POINT_TYPES
#:
#:         # Datos de consumo doméstico típico
#:         consumption_data = client.get_consumption(
#:             cups="ES001234567890123456AB",
#:             distributor_code="2",
#:             date_from="2024/01",
#:             date_to="2024/12",
#:             point_type=POINT_TYPES["CONSUMPTION"]  # 2
#:         )
#:
#:         # Datos de instalación de generación
#:         generation_data = client.get_consumption(
#:             cups="ES001234567890123456AB",
#:             distributor_code="2",
#:             date_from="2024/01",
#:             date_to="2024/12",
#:             point_type=POINT_TYPES["GENERATION"]  # 3
#:         )
POINT_TYPES = {
    "BORDER": 1,
    "CONSUMPTION": 2,
    "GENERATION": 3,
    "AUXILIARY_SERVICES": 4,
    "AUXILIARY_SERVICES_ALT": 5,
}

# Códigos de distribuidoras eléctricas españolas (mapeo completo)
#: Mapeo completo de todas las distribuidoras eléctricas españolas con sus códigos oficiales.
#:
#: Este diccionario proporciona el mapeo entre nombres de distribuidoras y sus códigos
#: numéricos oficiales utilizados por la API de Datadis. Los códigos son asignados
#: por el sistema eléctrico español y son únicos para cada distribuidora.
#:
#: Distribuidoras por código:
#:     - **"1" - VIESGO**: Cantabria, Asturias (norte de España)
#:     - **"2" - E-DISTRIBUCIÓN**: Filial de Endesa, cobertura nacional amplia
#:     - **"3" - E-REDES**: Galicia y zonas de Castilla y León
#:     - **"4" - ASEME**: Ciudad autónoma de Melilla
#:     - **"5" - UFD (Naturgy)**: Cobertura nacional, especialmente este y sur
#:     - **"6" - EOSA**: Aragón y zonas del noreste
#:     - **"7" - CIDE**: Ciudad autónoma de Ceuta
#:     - **"8" - IDE**: Islas Baleares
#:
#: Coverage geográfico:
#:     - **Nacional**: E-distribución (Endesa), UFD (Naturgy)
#:     - **Regional**: Viesgo (norte), E-redes (noroeste), EOSA (noreste)
#:     - **Insular/Local**: IDE (Baleares), ASEME (Melilla), CIDE (Ceuta)
#:
#: Example:
#:     Usar nombres de distribuidoras en lugar de códigos::
#:
#:         from datadis_python.utils.constants import DISTRIBUTOR_CODES
#:
#:         # Buscar suministros de Endesa por nombre
#:         endesa_code = DISTRIBUTOR_CODES["E_DISTRIBUCION"]  # "2"
#:         supplies = client.get_supplies(distributor_code=endesa_code)
#:
#:         # Buscar suministros de Naturgy por nombre
#:         naturgy_code = DISTRIBUTOR_CODES["UFD"]  # "5"
#:         supplies = client.get_supplies(distributor_code=naturgy_code)
#:
#:         # Iterar sobre todas las distribuidoras
#:         for name, code in DISTRIBUTOR_CODES.items():
#:             print(f"Distribuidor {name}: código {code}")
#:
#: Note:
#:     Los códigos de distribuidor son strings (no enteros) para mantener consistencia
#:     con la API de Datadis. El SDK acepta tanto strings como enteros y convierte
#:     automáticamente al tipo correcto.
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

# Diccionario unificado para compatibilidad hacia atrás (DEPRECATED)
#: Diccionario unificado de endpoints para compatibilidad hacia atrás.
#:
#: .. deprecated:: 2.0
#:    Use ``API_V1_ENDPOINTS`` o ``API_V2_ENDPOINTS`` según la versión de API que necesite.
#:    Este diccionario se mantiene solo para compatibilidad con código legacy y será
#:    eliminado en futuras versiones.
#:
#: Este diccionario combina todos los endpoints disponibles en un solo lugar, pero
#: no proporciona la claridad de separación entre versiones que ofrecen las constantes
#: específicas por versión.
#:
#: Problemas con este enfoque:
#:     - **Ambigüedad de versión**: No queda claro qué versión de API se está usando
#:     - **Mantenimiento complejo**: Requiere sincronización manual entre versiones
#:     - **Falta de tipado**: No aprovecha las mejoras de tipos de V2
#:
#: Migration path:
#:     Reemplazar uso de API_ENDPOINTS::
#:
#:         # ❌ Deprecated - No usar
#:         old_endpoint = API_ENDPOINTS["supplies"]
#:
#:         # ✅ Recomendado - Usar versión específica
#:         v1_endpoint = API_V1_ENDPOINTS["supplies"]  # Para compatibilidad
#:         v2_endpoint = API_V2_ENDPOINTS["supplies"]  # Para nuevas funcionalidades
#:
#: Warning:
#:     Esta constante será eliminada en la versión 3.0 del SDK. Migre su código
#:     para usar las constantes específicas por versión.
API_ENDPOINTS = {
    **AUTH_ENDPOINTS,
    **{k: v for k, v in API_V1_ENDPOINTS.items()},
    **{f"{k}_v2": v for k, v in API_V2_ENDPOINTS.items()},
    **AUTHORIZATION_ENDPOINTS,
}
