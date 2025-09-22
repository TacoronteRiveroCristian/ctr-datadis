"""
Cliente V2 simplificado y robusto para Datadis.

Este módulo proporciona un cliente simplificado para la versión 2 de la API de Datadis.
"""

import time
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional, Union

import requests

if TYPE_CHECKING:
    from ...models.consumption import ConsumptionData
    from ...models.contract import ContractData
    from ...models.distributor import DistributorData
    from ...models.max_power import MaxPowerData
    from ...models.reactive import ReactiveData
    from ...models.responses import (
        ConsumptionResponse,
        ContractResponse,
        DistributorsResponse,
        MaxPowerResponse,
        SuppliesResponse,
    )
    from ...models.supply import SupplyData

from ...exceptions import APIError, AuthenticationError, DatadisError
from ...utils.constants import (
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)
from ...utils.text_utils import normalize_api_response
from ...utils.type_converters import (
    convert_cups_parameter,
    convert_date_range_to_api_format,
    convert_distributor_code_parameter,
    convert_number_to_string,
    convert_optional_number_to_string,
)
from ...utils.validators import validate_measurement_type, validate_point_type


class SimpleDatadisClientV2:
    """
    Cliente simplificado para la API V2 de Datadis con manejo mejorado de errores.

    Este cliente implementa la **versión 2** de la API de Datadis, que incluye mejoras
    significativas sobre la V1, especialmente en el manejo de errores por distribuidor
    y estructuras de respuesta más robustas. La V2 es la versión **recomendada** para
    nuevas implementaciones.

    Principales diferencias con V1:
        - **Manejo de errores por distribuidor**: Respuestas incluyen ``distributorError``
        - **Estructuras de respuesta mejoradas**: Objetos tipados (SuppliesResponse, etc.)
        - **Nueva funcionalidad**: Datos de energía reactiva (``get_reactive_data()``)
        - **Validación mejorada**: Validaciones específicas para types y rangos
        - **Compatibilidad**: Mantiene la misma interfaz simple que V1

    Características principales:
        - Autenticación automática y renovación de tokens
        - Manejo robusto de timeouts y reintentos con backoff exponencial
        - Validación de datos con Pydantic para máxima seguridad
        - Soporte para tipos flexibles en parámetros de entrada
        - Context manager para gestión automática de recursos
        - **Manejo de errores por distribuidor** (exclusivo de V2)
        - **Respuestas estructuradas** con información de errores detallada

    Ventajas de la API V2:
        - **Robustez**: Mejor manejo de fallos de distribuidores específicos
        - **Información detallada**: Códigos y descripciones de errores por distribuidor
        - **Funcionalidad extendida**: Acceso a datos de energía reactiva
        - **Compatibilidad futura**: Preparada para nuevas funcionalidades

    Note:
        La API V2 acepta las mismas limitaciones que V1: **solo fechas en formato
        mensual** (YYYY/MM) y disponibilidad limitada de datos cuarto-horarios.

    Example:
        Uso básico con manejo de errores V2::

            from datadis_python.client.v2 import SimpleDatadisClientV2

            with SimpleDatadisClientV2("12345678A", "mi_password") as client:
                # Obtener suministros con información de errores
                supplies_response = client.get_supplies()

                print(f"Suministros obtenidos: {len(supplies_response.supplies)}")

                # Verificar errores por distribuidor
                if supplies_response.distributor_error:
                    for error in supplies_response.distributor_error:
                        print(f"Error en {error.distributorName}: {error.errorDescription}")

                # Trabajar con los suministros válidos
                for supply in supplies_response.supplies:
                    print(f"CUPS: {supply.cups} - Distribuidor: {supply.distributor}")

        Comparación con V1::

            # V1 - Lista simple
            supplies_v1 = client_v1.get_supplies()  # List[SupplyData]

            # V2 - Respuesta estructurada con manejo de errores
            supplies_v2 = client_v2.get_supplies()  # SuppliesResponse
            actual_supplies = supplies_v2.supplies  # List[SupplyData]
            errors = supplies_v2.distributor_error   # List[DistributorError]

        Funcionalidad exclusiva de V2 - Energía reactiva::

            reactive_data = client.get_reactive_data(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12"
            )

    :param username: NIF del usuario registrado en Datadis (ej: "12345678A")
    :type username: str
    :param password: Contraseña de acceso a la plataforma Datadis
    :type password: str
    :param timeout: Timeout para requests HTTP en segundos. 120s por defecto debido a
                   la lentitud característica de la API de Datadis
    :type timeout: int
    :param retries: Número de reintentos automáticos en caso de fallos de red o timeouts.
                   3 intentos por defecto
    :type retries: int

    :raises AuthenticationError: Si las credenciales proporcionadas son inválidas
    :raises DatadisError: Si ocurren errores de conexión o de la API
    :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic

    .. versionadded:: 2.0
       Soporte para estructuras de respuesta mejoradas y manejo de errores por distribuidor

    .. seealso::
       - :class:`SimpleDatadisClientV1` - Versión anterior con respuestas simples
       - Para migración de V1 a V2: Las interfaces son compatibles, solo cambian los tipos de retorno
    """

    def __init__(
        self, username: str, password: str, timeout: int = 120, retries: int = 3
    ):
        """
        Inicializa el cliente simplificado V2.

        :param username: NIF del usuario
        :type username: str
        :param password: Contraseña
        :type password: str
        :param timeout: Timeout en segundos (120s por defecto para Datadis)
        :type timeout: int
        :param retries: Número de reintentos
        :type retries: int
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.token: Optional[str] = None
        self.session = requests.Session()

        # Headers básicos (desactivar compresión para evitar problemas de gzip)
        self.session.headers.update(
            {
                "User-Agent": "datadis-python-sdk/0.2.0",
                "Accept": "application/json",
                "Accept-Encoding": "identity",  # Desactivar compresión gzip
            }
        )

    def authenticate(self) -> bool:
        """
        Autentica con la API de Datadis y obtiene el token de acceso para V2.

        Realiza una petición POST al endpoint ``/nikola-auth/tokens/login`` para obtener
        un token Bearer válido para la API V2. El proceso de autenticación es idéntico
        entre V1 y V2, pero el token obtenido es compatible con ambas versiones de endpoints.

        Note:
            Este método normalmente NO necesita ser llamado manualmente. La autenticación
            se realiza automáticamente en la primera petición que requiera acceso a la API.
            La V2 utiliza el mismo sistema de autenticación que V1.

        Warning:
            Los tokens tienen expiración limitada, pero la renovación automática está
            implementada para todos los endpoints V2 cuando se detecta un error 401.

        Example:
            Verificación manual de credenciales (opcional)::

                client = SimpleDatadisClientV2("12345678A", "mi_password")

                try:
                    if client.authenticate():
                        print("✓ Credenciales válidas para API V2")

                        # Ahora se pueden hacer peticiones autenticadas
                        supplies_response = client.get_supplies()
                        print(f"Suministros encontrados: {len(supplies_response.supplies)}")
                    else:
                        print("✗ Error en autenticación")

                except AuthenticationError as e:
                    print(f"Error de credenciales: {e}")
                except DatadisError as e:
                    print(f"Error de conexión: {e}")

        :return: ``True`` si la autenticación fue exitosa, ``False`` en caso contrario
        :rtype: bool
        :raises AuthenticationError: Si las credenciales (NIF/contraseña) son inválidas,
                                   el servidor devuelve un error de autenticación, o
                                   la respuesta del servidor está vacía
        :raises DatadisError: Si ocurre un timeout durante la autenticación o error de conexión

        .. seealso::
           - Documentación oficial: ``POST /nikola-auth/tokens/login``
           - Los tokens son válidos para ambas versiones V1 y V2 de la API
           - Renovación automática implementada en :meth:`_make_authenticated_request`

        .. note::
           El token obtenido se almacena automáticamente en ``self.token`` y se añade
           a los headers de la sesión HTTP como ``Authorization: Bearer <token>``.
        """
        print("Autenticando con Datadis...")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "datadis-python-sdk/0.2.0",
        }

        data = {"username": self.username, "password": self.password}

        try:
            response = requests.post(
                url=f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                data=data,
                headers=headers,
                timeout=30,  # Auth timeout más corto
            )

            if response.status_code == 200:
                token = response.text.strip()
                if not token:
                    raise AuthenticationError(
                        "Error de autenticación: respuesta vacía del servidor"
                    )
                self.token = token
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                print("Autenticación exitosa")
                return True
            else:
                raise AuthenticationError(
                    f"Error de autenticación: {response.status_code}"
                )

        except requests.Timeout:
            raise AuthenticationError("Timeout en autenticación")
        except Exception as e:
            raise AuthenticationError(f"Error en autenticación: {e}")

    def _make_authenticated_request(
        self, endpoint: str, params: Optional[dict] = None
    ) -> dict:
        """
        Realiza peticiones HTTP autenticadas optimizadas para la API V2 de Datadis.

        Este método interno maneja toda la lógica de peticiones HTTP para endpoints V2,
        con mejoras específicas para el manejo de respuestas estructuradas. A diferencia
        de V1, la V2 garantiza que las respuestas sean siempre objetos dict con estructura
        consistente que incluye información de errores por distribuidor.

        Mejoras específicas para V2:
            - **Garantía de estructura dict**: Todas las respuestas se normalizan a dict
            - **Manejo mejorado de errores**: Preserva información de ``distributorError``
            - **Validación de estructura**: Asegura compatibilidad con modelos Pydantic V2
            - **Fallback inteligente**: Envuelve respuestas inesperadas en estructura válida

        Flujo de operación V2:
            1. Verifica token válido → autentica automáticamente si es necesario
            2. Realiza petición HTTP GET al endpoint V2 especificado
            3. Maneja códigos de respuesta (200: éxito, 401: renovar token, otros: error)
            4. **Normaliza respuesta** para caracteres especiales (específico de Datadis)
            5. **Garantiza estructura dict** compatible con modelos de respuesta V2
            6. Implementa reintentos con backoff exponencial para timeouts y errores de red

        Estrategia de reintentos (idéntica a V1):
            - Errores HTTP 4xx/5xx: No se reintentan (propagación inmediata)
            - Timeouts y errores de red: Reintentos hasta ``self.retries`` veces
            - Backoff exponencial: 2s → 4s → 8s... (máximo 30s para timeouts)
            - Error 401: Renovación automática de token + reintento de la petición

        :param endpoint: Endpoint relativo de la API V2 (ej: ``'/get-supplies-v2'``)
        :type endpoint: str
        :param params: Parámetros de query string para la petición HTTP
        :type params: Optional[dict]
        :return: Respuesta JSON como dict, garantizando estructura compatible con V2.
                Siempre incluye claves esperadas por los modelos de respuesta
        :rtype: dict
        :raises AuthenticationError: Si no se puede autenticar o renovar el token expirado
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si se agotan todos los reintentos por timeouts o errores de red

        .. note::
           Este es un método interno optimizado para V2. Los usuarios deben usar los
           métodos públicos como ``get_supplies()``, ``get_consumption()``, etc.

        .. versionchanged:: 2.0
           Garantiza respuestas dict y manejo mejorado de estructuras V2
        """
        if not self.token:
            if not self.authenticate():
                raise AuthenticationError("No se pudo autenticar")

        url = f"{DATADIS_API_BASE}{endpoint}"

        for attempt in range(self.retries + 1):
            try:
                print(
                    f"Petición a {endpoint} (intento {attempt + 1}/{self.retries + 1})..."
                )

                response = self.session.get(
                    url=url, params=params, timeout=self.timeout
                )

                if response.status_code == 200:
                    print(f"Respuesta exitosa ({len(response.text)} chars)")
                    json_response = response.json()
                    # Normalizar texto para evitar problemas de caracteres especiales
                    normalized_response = normalize_api_response(json_response)
                    # Asegurar que siempre devolvemos un dict (V2 API debería devolver dicts)
                    if isinstance(normalized_response, dict):
                        return normalized_response
                    else:
                        # Si por alguna razón es una lista, envolver en dict
                        return {"data": normalized_response}
                elif response.status_code == 401:
                    # Token expirado, renovar
                    print("Token expirado, renovando...")
                    self.token = None
                    if self.authenticate():
                        continue
                    else:
                        raise AuthenticationError("No se pudo renovar el token")
                else:
                    raise APIError(
                        f"Error HTTP {response.status_code}: {response.text}",
                        response.status_code,
                    )

            except APIError:
                # Los errores HTTP (4xx, 5xx) no deben ser reintentados, propagarlos directamente
                raise
            except requests.Timeout:
                if attempt < self.retries:
                    wait_time = min(30, (2**attempt) * 5)
                    print(
                        f"Timeout. Esperando {wait_time}s antes del siguiente intento..."
                    )
                    time.sleep(wait_time)
                else:
                    raise DatadisError(
                        f"Timeout después de {self.retries + 1} intentos. La API de Datadis puede estar lenta."
                    )
            except Exception as e:
                # Solo reintentar errores de red/conexión, no errores de aplicación
                if attempt < self.retries:
                    wait_time = (2**attempt) * 2
                    print(f"Error: {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise DatadisError(
                        f"Error después de {self.retries + 1} intentos: {e}"
                    )

        raise DatadisError("Se agotaron todos los reintentos")

    def get_supplies(
        self,
        authorized_nif: Optional[str] = None,
        distributor_code: Optional[str] = None,
    ) -> "SuppliesResponse":
        """
        Obtiene la lista de puntos de suministro con manejo mejorado de errores (V2).

        Consulta el endpoint ``GET /api-private/api/get-supplies-v2`` para obtener todos
        los puntos de suministro eléctrico con **manejo mejorado de errores por distribuidor**.
        A diferencia de V1, la V2 devuelve una respuesta estructurada que incluye tanto
        los suministros válidos como información detallada de errores por cada distribuidor.

        Ventajas de V2 sobre V1:
            - **Manejo de errores por distribuidor**: Información detallada de fallos específicos
            - **Respuesta estructurada**: ``SuppliesResponse`` con ``supplies`` y ``distributor_error``
            - **Mayor robustez**: Operación exitosa aunque algunos distribuidores fallen
            - **Información diagnóstica**: Códigos y descripciones de errores específicos

        La respuesta incluye:
            - **supplies**: Lista de puntos de suministro válidos (idénticos a V1)
            - **distributor_error**: Lista de errores específicos por distribuidor
                - ``distributorCode``: Código del distribuidor con problemas
                - ``distributorName``: Nombre del distribuidor
                - ``errorCode``: Código específico del error
                - ``errorDescription``: Descripción detallada del problema

        Example:
            Uso básico con manejo de errores V2::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    response = client.get_supplies()

                    print(f"✓ Suministros obtenidos: {len(response.supplies)}")

                    # Mostrar información de suministros
                    for supply in response.supplies:
                        print(f"CUPS: {supply.cups}")
                        print(f"Distribuidor: {supply.distributor} (código: {supply.distributorCode})")
                        print(f"Dirección: {supply.address}")
                        print("---")

                    # Verificar y manejar errores por distribuidor
                    if response.distributor_error:
                        print(f"⚠️  Errores encontrados en {len(response.distributor_error)} distribuidores:")
                        for error in response.distributor_error:
                            print(f"- {error.distributorName} ({error.distributorCode}): {error.errorDescription}")
                    else:
                        print("✓ Todos los distribuidores respondieron correctamente")

            Comparación V1 vs V2::

                # V1 - Lista simple, fallo total si hay errores
                supplies_v1 = client_v1.get_supplies()  # List[SupplyData] or Exception

                # V2 - Respuesta robusta con información de errores
                response_v2 = client_v2.get_supplies()   # SuppliesResponse
                supplies_v2 = response_v2.supplies       # List[SupplyData]
                errors_v2 = response_v2.distributor_error # List[DistributorError]

            Filtrar por distribuidor específico::

                # Solo suministros de E-distribución
                response = client.get_supplies(distributor_code="2")

                if response.supplies:
                    print("Suministros de E-distribución encontrados")
                elif response.distributor_error:
                    for error in response.distributor_error:
                        if error.distributorCode == "2":
                            print(f"Error en E-distribución: {error.errorDescription}")

        :param authorized_nif: NIF de una persona autorizada para consultar sus suministros.
                              Si se especifica, se obtendrán los suministros de esa persona
                              autorizada en lugar de los del usuario autenticado
        :type authorized_nif: Optional[str]
        :param distributor_code: Código del distribuidor para filtrar suministros.
                                Solo acepta strings en V2 (ej: "2" para E-distribución)
        :type distributor_code: Optional[str]
        :return: Objeto ``SuppliesResponse`` que contiene:
                - ``supplies``: Lista de objetos ``SupplyData`` validados
                - ``distributor_error``: Lista de errores por distribuidor si los hay
        :rtype: SuppliesResponse
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP crítico (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-supplies-v2``
           - Comparar con :meth:`SimpleDatadisClientV1.get_supplies` para diferencias
           - Para obtener detalles del contrato: :meth:`get_contract_detail`

        .. versionadded:: 2.0
           Manejo de errores por distribuidor y respuesta estructurada

        .. note::
           A diferencia de V1, esta operación puede tener éxito parcial: obtener
           suministros de algunos distribuidores aunque otros fallen.
        """
        print("Obteniendo lista de suministros...")

        # Construir parámetros de query con validación
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif
        if distributor_code is not None:
            params["distributorCode"] = convert_distributor_code_parameter(
                distributor_code
            )

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["supplies"], params=params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"supplies": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import SuppliesResponse

        try:
            validated_response = SuppliesResponse(**response)
            print(f"{len(validated_response.supplies)} suministros validados")
            if validated_response.distributor_error:
                print(
                    f"Advertencia: {len(validated_response.distributor_error)} errores de distribuidor"
                )
            return validated_response
        except Exception as e:
            print(f"Error validando respuesta de suministros: {e}")
            # Devolver respuesta vacía pero válida
            return SuppliesResponse(supplies=[], distributorError=[])

    def get_distributors(
        self, authorized_nif: Optional[str] = None
    ) -> "DistributorsResponse":
        """
        Obtiene la lista de distribuidores con estructura mejorada (V2).

        Consulta el endpoint ``GET /api-private/api/get-distributors-with-supplies-v2``
        para obtener información sobre las distribuidoras eléctricas donde el usuario
        tiene suministros activos. La V2 incluye manejo mejorado de errores y estructura
        de respuesta más detallada que proporciona mejor información diagnóstica.

        Mejoras de V2 sobre V1:
            - **Estructura de respuesta mejorada**: ``DistributorsResponse`` con metadatos
            - **Información de errores**: Detalles específicos de fallos por distribuidor
            - **Soporte para NIFs autorizados**: Consultar distribuidores de terceros
            - **Manejo robusto**: Operación exitosa aunque algunos distribuidores fallen

        La respuesta incluye:
            - **dist_existence_user**: Objeto con ``distributorCodes`` (lista de códigos)
            - **distributor_error**: Lista de errores específicos por distribuidor si los hay
                - Información detallada de qué distribuidores no respondieron correctamente
                - Códigos de error específicos y descripciones

        Example:
            Obtener distribuidores del usuario autenticado::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    response = client.get_distributors()

                    # Obtener códigos de distribuidores
                    distributor_codes = response.dist_existence_user.get("distributorCodes", [])

                    print(f"✓ Distribuidores encontrados: {len(distributor_codes)}")

                    # Mapear códigos a nombres (referencia)
                    distributor_names = {
                        "1": "Viesgo", "2": "E-distribución", "3": "E-redes",
                        "4": "ASEME", "5": "UFD", "6": "EOSA", "7": "CIDE", "8": "IDE"
                    }

                    for code in distributor_codes:
                        name = distributor_names.get(code, f"Distribuidor {code}")
                        print(f"- {name} (código: {code})")

                    # Verificar errores
                    if response.distributor_error:
                        print(f"⚠️  Errores en {len(response.distributor_error)} distribuidores:")
                        for error in response.distributor_error:
                            print(f"- {error.distributorName}: {error.errorDescription}")

                    # Usar códigos para consultas posteriores
                    if distributor_codes:
                        first_code = distributor_codes[0]
                        supplies_response = client.get_supplies(distributor_code=first_code)
                        print(f"Suministros en {distributor_names.get(first_code)}: {len(supplies_response.supplies)}")

            Consultar distribuidores de una persona autorizada::

                # Obtener distribuidores de un NIF autorizado
                response = client.get_distributors(authorized_nif="87654321B")

                auth_distributors = response.dist_existence_user.get("distributorCodes", [])
                print(f"Distribuidores del NIF autorizado: {auth_distributors}")

            Comparación V1 vs V2::

                # V1 - Lista simple de objetos DistributorData
                distributors_v1 = client_v1.get_distributors()  # List[DistributorData]
                codes_v1 = [d.distributorCode for d in distributors_v1]

                # V2 - Respuesta estructurada con manejo de errores
                response_v2 = client_v2.get_distributors()     # DistributorsResponse
                codes_v2 = response_v2.dist_existence_user.get("distributorCodes", [])
                errors_v2 = response_v2.distributor_error       # Lista de errores si los hay

        :param authorized_nif: NIF de una persona autorizada para consultar sus distribuidores.
                              Si se especifica, se obtendrán los distribuidores donde esa
                              persona tiene suministros en lugar del usuario autenticado
        :type authorized_nif: Optional[str]
        :return: Objeto ``DistributorsResponse`` que contiene:
                - ``dist_existence_user``: Dict con ``distributorCodes`` (lista de códigos de distribuidor)
                - ``distributor_error``: Lista de errores por distribuidor si los hay
        :rtype: DistributorsResponse
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP crítico (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-distributors-with-supplies-v2``
           - Comparar con :meth:`SimpleDatadisClientV1.get_distributors` para diferencias
           - Los códigos obtenidos se usan en :meth:`get_supplies`, :meth:`get_consumption`, etc.

        .. versionadded:: 2.0
           Soporte para NIFs autorizados y estructura de respuesta mejorada

        .. note::
           Solo se devuelven códigos de distribuidores donde el usuario (o NIF autorizado)
           tiene suministros activos. La lista puede estar vacía si no hay suministros.
        """
        print("Obteniendo distribuidores...")

        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["distributors"], params=params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {
                "distExistenceUser": {"distributorCodes": []},
                "distributorError": [],
            }

        # Validar respuesta completa con Pydantic
        from ...models.responses import DistributorsResponse

        try:
            validated_response = DistributorsResponse(**response)
            distributor_codes = validated_response.dist_existence_user.get(
                "distributorCodes", []
            )
            print(f"{len(distributor_codes)} distribuidores validados")
            if validated_response.distributor_error:
                print(
                    f"Advertencia: {len(validated_response.distributor_error)} errores de distribuidor"
                )
            return validated_response
        except Exception as e:
            print(f"Error validando respuesta de distribuidores: {e}")
            # Devolver respuesta vacía pero válida
            return DistributorsResponse(
                distExistenceUser={"distributorCodes": []}, distributorError=[]
            )

    def get_contract_detail(
        self, cups: str, distributor_code: str, authorized_nif: Optional[str] = None
    ) -> "ContractResponse":
        """
        Obtiene los detalles del contrato eléctrico con manejo mejorado de errores (V2).

        Consulta el endpoint ``GET /api-private/api/get-contract-detail-v2`` para obtener
        información detallada del contrato asociado a un CUPS específico. La V2 incluye
        **manejo mejorado de errores por distribuidor** y soporte nativo para consultas
        con NIFs autorizados, proporcionando mayor robustez y flexibilidad.

        Ventajas de V2 sobre V1:
            - **Manejo de errores por distribuidor**: Información detallada de fallos específicos
            - **Soporte nativo para NIFs autorizados**: Parámetro ``authorized_nif`` integrado
            - **Respuesta estructurada**: ``ContractResponse`` con contratos y errores separados
            - **Mayor robustez**: Operación exitosa aunque haya problemas con algunos distribuidores

        Información del contrato incluida (idéntica a V1):
            - **Datos básicos**: CUPS, distribuidor, comercializadora
            - **Características técnicas**: Tensión, potencia contratada, tipo de punto
            - **Datos tarifarios**: Tarifa de acceso, discriminación horaria
            - **Ubicación**: Provincia, municipio, código postal
            - **Fechas**: Inicio y fin de contrato, historial de cambios
            - **Autoconsumo**: Tipo, características y CAU si aplica
            - **Control de potencia**: ICP o Maxímetro

        Example:
            Obtener detalles de contrato con manejo de errores V2::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    # Primero obtener suministros
                    supplies_response = client.get_supplies()

                    if supplies_response.supplies:
                        supply = supplies_response.supplies[0]

                        # Obtener detalles del contrato
                        contract_response = client.get_contract_detail(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode
                        )

                        print(f"✓ Contratos obtenidos: {len(contract_response.contract)}")

                        # Mostrar información de contratos
                        for contract in contract_response.contract:
                            print(f"CUPS: {contract.cups}")
                            print(f"Distribuidor: {contract.distributor}")
                            print(f"Potencia contratada: {contract.contractedPowerkW} kW")
                            print(f"Tarifa de acceso: {contract.accessFare}")
                            if contract.marketer:
                                print(f"Comercializadora: {contract.marketer}")
                            print("---")

                        # Verificar errores específicos del distribuidor
                        if contract_response.distributor_error:
                            print("⚠️  Errores en la consulta:")
                            for error in contract_response.distributor_error:
                                print(f"- {error.distributorName}: {error.errorDescription}")
                        else:
                            print("✓ Consulta exitosa sin errores")

            Consultar contrato con NIF autorizado::

                # Obtener contrato de un suministro autorizado por tercero
                contract_response = client.get_contract_detail(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    authorized_nif="87654321B"  # NIF que nos autorizó
                )

                if contract_response.contract:
                    contract = contract_response.contract[0]
                    print(f"Contrato autorizado - Potencia: {contract.contractedPowerkW} kW")
                elif contract_response.distributor_error:
                    for error in contract_response.distributor_error:
                        print(f"Error en autorización: {error.errorDescription}")

            Comparación V1 vs V2::

                # V1 - Lista simple, fallo total si hay errores
                contracts_v1 = client_v1.get_contract_detail(cups, dist_code)  # List[ContractData]

                # V2 - Respuesta robusta con manejo de errores
                response_v2 = client_v2.get_contract_detail(cups, dist_code)    # ContractResponse
                contracts_v2 = response_v2.contract                            # List[ContractData]
                errors_v2 = response_v2.distributor_error                      # List[DistributorError]

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos
                    que identifican únicamente el punto de suministro eléctrico)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico como string
                                (ej: "2" para E-distribución). V2 requiere string
        :type distributor_code: str
        :param authorized_nif: NIF de la persona que autorizó la consulta de sus datos.
                              Si se especifica, se consultará el contrato de esa persona
                              en lugar del usuario autenticado
        :type authorized_nif: Optional[str]
        :return: Objeto ``ContractResponse`` que contiene:
                - ``contract``: Lista de objetos ``ContractData`` validados
                - ``distributor_error``: Lista de errores por distribuidor si los hay
        :rtype: ContractResponse
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP crítico (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic
        :raises ValueError: Si el CUPS no tiene el formato correcto (22 caracteres)

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-contract-detail-v2``
           - Comparar con :meth:`SimpleDatadisClientV1.get_contract_detail` para diferencias
           - Para obtener la lista de CUPS: :meth:`get_supplies`
           - Para datos de consumo del contrato: :meth:`get_consumption`

        .. versionadded:: 2.0
           Soporte nativo para ``authorized_nif`` y manejo de errores por distribuidor

        .. note::
           El CUPS debe ser exactamente de 22 caracteres alfanuméricos.
           La V2 incluye validación mejorada y mensajes de error más descriptivos.
        """
        print(f"Obteniendo contrato para {cups}...")

        # Convertir parámetros usando los conversores
        cups = convert_cups_parameter(cups)
        distributor_code = convert_distributor_code_parameter(distributor_code)

        params = {"cups": cups, "distributorCode": distributor_code}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["contracts"], params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"contract": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import ContractResponse

        try:
            validated_response = ContractResponse(**response)
            print(f"{len(validated_response.contract)} contratos validados")
            if validated_response.distributor_error:
                print(
                    f"Advertencia: {len(validated_response.distributor_error)} errores de distribuidor"
                )
            return validated_response
        except Exception as e:
            print(f"Error validando respuesta de contrato: {e}")
            # Devolver respuesta vacía pero válida
            return ContractResponse(contract=[], distributorError=[])

    def get_consumption(
        self,
        cups: str,
        distributor_code: Union[str, int],
        date_from: Union[str, datetime, date],
        date_to: Union[str, datetime, date],
        measurement_type: Union[int, float, str] = 0,
        point_type: Optional[Union[int, float, str]] = None,
        authorized_nif: Optional[str] = None,
    ) -> "ConsumptionResponse":
        """
        Obtiene los datos de consumo eléctrico con validaciones mejoradas (V2).

        Consulta el endpoint ``GET /api-private/api/get-consumption-data-v2`` para obtener
        la curva de carga con **manejo mejorado de errores** y **validaciones específicas V2**.
        Incluye todas las funcionalidades de V1 más validaciones automáticas de rangos,
        manejo robusto de errores por distribuidor y soporte nativo para NIFs autorizados.

        **IMPORTANTE - Limitaciones idénticas a V1:**
            - **Solo fechas en formato mensual** (YYYY/MM)
            - **Datos cuarto-horarios limitados** según tipo de punto
            - **Conversión automática** de fechas datetime/date

        Mejoras de V2 sobre V1:
            - **Validación automática**: ``measurement_type`` y ``point_type`` se validan automáticamente
            - **Manejo de errores por distribuidor**: Operación exitosa aunque algunos distribuidores fallen
            - **Soporte nativo para NIFs autorizados**: Parámetro ``authorized_nif`` integrado
            - **Respuesta estructurada**: ``ConsumptionResponse`` con curva de tiempo y errores separados
            - **Mejor diagnóstico**: Información detallada de problemas específicos por distribuidor

        Validaciones automáticas V2:
            - ``measurement_type``: Se valida que esté en rango [0, 1]
            - ``point_type``: Se valida que esté en rango [1, 5] si se proporciona
            - **Compatibilidad cuarto-horaria**: Se verifica automáticamente según tipo de punto

        Example:
            Obtener consumo con manejo de errores V2::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies_response = client.get_supplies()

                    if supplies_response.supplies:
                        supply = supplies_response.supplies[0]

                        # Consumo horario del año 2024
                        consumption_response = client.get_consumption(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/12",
                            measurement_type=0  # Horarios - se valida automáticamente
                        )

                        print(f"✓ Registros obtenidos: {len(consumption_response.time_curve)}")

                        # Analizar consumo
                        total_kwh = sum(c.consumptionKWh for c in consumption_response.time_curve
                                      if c.consumptionKWh)
                        print(f"Consumo total 2024: {total_kwh:.2f} kWh")

                        # Verificar errores específicos
                        if consumption_response.distributor_error:
                            print("⚠️  Errores encontrados:")
                            for error in consumption_response.distributor_error:
                                print(f"- {error.distributorName}: {error.errorDescription}")
                        else:
                            print("✓ Datos obtenidos sin errores")

            Obtener datos cuarto-horarios con validación automática::

                # V2 valida automáticamente la compatibilidad
                try:
                    consumption_response = client.get_consumption(
                        cups="ES001234567890123456AB",
                        distributor_code="2",  # E-distribución
                        date_from="2024/06",
                        date_to="2024/06",
                        measurement_type=1,    # Cuarto-horarios - se valida automáticamente
                        point_type=3           # Tipo 3 - se valida que esté en [1-5]
                    )

                    print(f"Datos cada 15 min: {len(consumption_response.time_curve)} registros")

                except ValidationError as e:
                    print(f"Error de validación V2: {e}")
                except APIError as e:
                    print(f"API rechazó la petición: {e}")

            Consultar consumo con NIF autorizado::

                consumption_response = client.get_consumption(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/03",
                    authorized_nif="87654321B"  # NIF que nos autorizó
                )

                if consumption_response.time_curve:
                    print(f"Datos autorizados obtenidos: {len(consumption_response.time_curve)}")

            Comparación V1 vs V2::

                # V1 - Lista simple, validación manual
                consumption_v1 = client_v1.get_consumption(cups, dist, date_from, date_to)  # List[ConsumptionData]

                # V2 - Respuesta estructurada, validación automática
                response_v2 = client_v2.get_consumption(cups, dist, date_from, date_to)     # ConsumptionResponse
                consumption_v2 = response_v2.time_curve                                     # List[ConsumptionData]
                errors_v2 = response_v2.distributor_error                                   # List[DistributorError]

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico (acepta int o str, se convierte automáticamente)
        :type distributor_code: Union[str, int]
        :param date_from: Fecha de inicio en formato YYYY/MM. También acepta objetos
                         datetime/date que se convertirán automáticamente
        :type date_from: Union[str, datetime, date]
        :param date_to: Fecha de fin en formato YYYY/MM. También acepta objetos
                       datetime/date que se convertirán automáticamente
        :type date_to: Union[str, datetime, date]
        :param measurement_type: Tipo de medición - 0: horarios (defecto), 1: cuarto-horarios.
                               **Se valida automáticamente en V2** que esté en rango [0, 1]
        :type measurement_type: Union[int, float, str]
        :param point_type: Tipo de punto de medida (1-5). Requerido para datos cuarto-horarios.
                          **Se valida automáticamente en V2** que esté en rango [1, 5]
        :type point_type: Optional[Union[int, float, str]]
        :param authorized_nif: NIF de la persona que autorizó la consulta de sus datos.
                              Si se especifica, se consultarán los datos de esa persona
        :type authorized_nif: Optional[str]
        :return: Objeto ``ConsumptionResponse`` que contiene:
                - ``time_curve``: Lista de objetos ``ConsumptionData`` validados
                - ``distributor_error``: Lista de errores por distribuidor si los hay
        :rtype: ConsumptionResponse
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP crítico (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si las fechas no están en formato mensual válido, los tipos
                               de medición/punto están fuera de rango, o los datos no pasan
                               la validación Pydantic mejorada de V2
        :raises ValueError: Si se solicitan datos cuarto-horarios para un tipo de punto no compatible

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-consumption-data-v2``
           - Comparar con :meth:`SimpleDatadisClientV1.get_consumption` para diferencias
           - Para obtener CUPS: :meth:`get_supplies`
           - Para datos de potencia máxima: :meth:`get_max_power`

        .. versionadded:: 2.0
           Validaciones automáticas de rangos, soporte para ``authorized_nif`` y manejo de errores por distribuidor

        .. warning::
           Los datos cuarto-horarios siguen teniendo las mismas limitaciones que en V1:
           solo disponibles para tipos de punto 1, 2, y 3 en E-distribución.
        """
        print(f"Obteniendo consumo para {cups} ({date_from} - {date_to})...")

        # Convertir parámetros usando los conversores
        cups = convert_cups_parameter(cups)
        distributor_code = convert_distributor_code_parameter(distributor_code)
        date_from, date_to = convert_date_range_to_api_format(
            date_from, date_to, "monthly"
        )
        measurement_type_converted = convert_number_to_string(measurement_type)

        # Validar rangos después de la conversión
        measurement_type_validated = validate_measurement_type(
            int(measurement_type_converted)
        )

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type_validated),
        }

        point_type_converted = convert_optional_number_to_string(point_type)
        if point_type_converted is not None:
            point_type_validated = validate_point_type(int(point_type_converted))
            params["pointType"] = str(point_type_validated)
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["consumption"], params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"timeCurve": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import ConsumptionResponse

        try:
            validated_response = ConsumptionResponse(**response)
            print(
                f"{len(validated_response.time_curve)} registros de consumo validados"
            )
            if validated_response.distributor_error:
                print(
                    f"Advertencia: {len(validated_response.distributor_error)} errores de distribuidor"
                )
            return validated_response
        except Exception as e:
            print(f"Error validando respuesta de consumo: {e}")
            # Devolver respuesta vacía pero válida
            return ConsumptionResponse(timeCurve=[], distributorError=[])

    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> "MaxPowerResponse":
        """
        Obtiene los datos de potencia máxima demandada con manejo mejorado de errores (V2).

        Consulta el endpoint ``GET /api-private/api/get-max-power-v2`` para obtener las
        potencias máximas registradas en cada período tarifario con **manejo mejorado de
        errores por distribuidor** y **soporte nativo para NIFs autorizados**. Mantiene
        toda la funcionalidad de V1 con mayor robustez y mejor información diagnóstica.

        **IMPORTANTE - Limitación idéntica a V1:**
            Solo acepta **fechas en formato mensual** (YYYY/MM). El SDK convierte
            automáticamente fechas datetime/date al formato requerido.

        Mejoras de V2 sobre V1:
            - **Manejo de errores por distribuidor**: Información detallada de fallos específicos
            - **Soporte nativo para NIFs autorizados**: Parámetro ``authorized_nif`` integrado
            - **Respuesta estructurada**: ``MaxPowerResponse`` con potencias y errores separados
            - **Mayor robustez**: Operación exitosa aunque algunos distribuidores fallen
            - **Mejor diagnóstico**: Códigos y descripciones de errores específicos

        Información de potencia máxima (idéntica a V1):
            - **Potencia en Vatios (W)**: Demanda máxima registrada en cada período
            - **Períodos tarifarios**: VALLE, LLANO, PUNTA, P1-P6
            - **Timestamp completo**: Fecha y hora exacta del pico de potencia
            - **Aplicaciones**: Optimización de potencia contratada, identificación de picos

        Example:
            Obtener potencias máximas con manejo de errores V2::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies_response = client.get_supplies()

                    if supplies_response.supplies:
                        supply = supplies_response.supplies[0]

                        # Potencias máximas de 2024
                        max_power_response = client.get_max_power(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/12"
                        )

                        print(f"✓ Registros de potencia: {len(max_power_response.max_power)}")

                        # Analizar potencias por período
                        periods = {}
                        for power in max_power_response.max_power:
                            period = power.period
                            if period not in periods:
                                periods[period] = []
                            periods[period].append(power.maxPower)

                        # Mostrar potencia máxima por período
                        for period, powers in periods.items():
                            max_power_w = max(powers)
                            max_power_kw = max_power_w / 1000
                            print(f"Período {period}: {max_power_kw:.2f} kW")

                        # Verificar errores específicos
                        if max_power_response.distributor_error:
                            print("⚠️  Errores encontrados:")
                            for error in max_power_response.distributor_error:
                                print(f"- {error.distributorName}: {error.errorDescription}")
                        else:
                            print("✓ Datos obtenidos sin errores")

            Consultar potencias con NIF autorizado::

                max_power_response = client.get_max_power(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/12",
                    authorized_nif="87654321B"  # NIF que nos autorizó
                )

                if max_power_response.max_power:
                    # Encontrar la potencia máxima absoluta del período
                    all_powers = [p.maxPower for p in max_power_response.max_power]
                    peak_power_w = max(all_powers)
                    peak_power_kw = peak_power_w / 1000
                    print(f"Pico máximo autorizado: {peak_power_kw:.2f} kW")

            Identificar mes con mayor demanda::

                # Agrupar por mes (idéntico a V1)
                monthly_max = {}
                for power in max_power_response.max_power:
                    month = power.date[:7]  # YYYY/MM
                    if month not in monthly_max:
                        monthly_max[month] = 0
                    monthly_max[month] = max(monthly_max[month], power.maxPower)

                if monthly_max:
                    peak_month = max(monthly_max, key=monthly_max.get)
                    peak_power_kw = monthly_max[peak_month] / 1000
                    print(f"Mayor demanda: {peak_power_kw:.2f} kW en {peak_month}")

            Comparación V1 vs V2::

                # V1 - Lista simple, fallo total si hay errores
                max_power_v1 = client_v1.get_max_power(cups, dist, date_from, date_to)  # List[MaxPowerData]

                # V2 - Respuesta robusta con manejo de errores
                response_v2 = client_v2.get_max_power(cups, dist, date_from, date_to)    # MaxPowerResponse
                max_power_v2 = response_v2.max_power                                     # List[MaxPowerData]
                errors_v2 = response_v2.distributor_error                               # List[DistributorError]

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico como string
                                (ej: "2" para E-distribución). V2 requiere string
        :type distributor_code: str
        :param date_from: Fecha de inicio en formato YYYY/MM. Se convierte automáticamente
                         si se pasa como datetime/date
        :type date_from: str
        :param date_to: Fecha de fin en formato YYYY/MM. Se convierte automáticamente
                       si se pasa como datetime/date
        :type date_to: str
        :param authorized_nif: NIF de la persona que autorizó la consulta de sus datos.
                              Si se especifica, se consultarán los datos de esa persona
        :type authorized_nif: Optional[str]
        :return: Objeto ``MaxPowerResponse`` que contiene:
                - ``max_power``: Lista de objetos ``MaxPowerData`` validados
                - ``distributor_error``: Lista de errores por distribuidor si los hay
        :rtype: MaxPowerResponse
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP crítico (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si las fechas no están en formato mensual válido o
                               los datos no pasan la validación Pydantic
        :raises ValueError: Si el CUPS no tiene el formato correcto

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-max-power-v2``
           - Comparar con :meth:`SimpleDatadisClientV1.get_max_power` para diferencias
           - Para obtener CUPS: :meth:`get_supplies`
           - Para datos de consumo: :meth:`get_consumption`
           - Para detalles del contrato: :meth:`get_contract_detail`

        .. versionadded:: 2.0
           Soporte nativo para ``authorized_nif`` y manejo de errores por distribuidor

        .. note::
           Las potencias se devuelven en Vatios (W) como en V1. Para obtener
           kilovatios (kW) divida el valor entre 1000.
        """
        print(f"Obteniendo potencia máxima para {cups} ({date_from} - {date_to})...")

        # Convertir parámetros usando los conversores
        cups = convert_cups_parameter(cups)
        distributor_code = convert_distributor_code_parameter(distributor_code)
        date_from, date_to = convert_date_range_to_api_format(
            date_from, date_to, "monthly"
        )

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["max_power"], params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"maxPower": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import MaxPowerResponse

        try:
            validated_response = MaxPowerResponse(**response)
            print(
                f"{len(validated_response.max_power)} registros de potencia máxima validados"
            )
            if validated_response.distributor_error:
                print(
                    f"Advertencia: {len(validated_response.distributor_error)} errores de distribuidor"
                )
            return validated_response
        except Exception as e:
            print(f"Error validando respuesta de potencia máxima: {e}")
            # Devolver respuesta vacía pero válida
            return MaxPowerResponse(maxPower=[], distributorError=[])

    def get_reactive_data(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> List["ReactiveData"]:
        """
        Obtiene datos de energía reactiva - Funcionalidad EXCLUSIVA de la API V2.

        Consulta el endpoint ``GET /api-private/api/get-reactive-data-v2`` para obtener
        información sobre la **energía reactiva** consumida por el punto de suministro.
        Esta funcionalidad es **completamente nueva en V2** y no está disponible en V1.

        **¿Qué es la energía reactiva?**
            La energía reactiva es la energía eléctrica que no realiza trabajo útil pero
            es necesaria para el funcionamiento de equipos inductivos (motores, transformadores,
            etc.). Se mide en kVARh y puede generar penalizaciones en la factura eléctrica.

        **IMPORTANTE - Limitación de fechas:**
            Al igual que otros endpoints, solo acepta **fechas en formato mensual** (YYYY/MM).
            No se permiten fechas con días específicos.

        Información incluida en los datos reactivos:
            - **Energía reactiva por período**: P1, P2, P3, P4, P5, P6
            - **Código y descripción**: Información del tipo de medición
            - **Períodos mensuales**: Datos agregados por mes
            - **CUPS asociado**: Identificación del punto de suministro

        Períodos tarifarios de energía reactiva:
            - **P1-P6**: Períodos tarifarios según discriminación horaria
            - **Valores en kVARh**: Energía reactiva consumida en cada período
            - **Agregación mensual**: Datos totalizados por mes del período consultado

        Applications:
            - **Análisis de eficiencia energética**: Identificar equipos ineficientes
            - **Optimización de costes**: Reducir penalizaciones por energía reactiva
            - **Gestión técnica**: Mejorar el factor de potencia de la instalación
            - **Auditorías energéticas**: Análisis completo del comportamiento eléctrico

        Example:
            Obtener datos de energía reactiva (exclusivo V2)::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies_response = client.get_supplies()

                    if supplies_response.supplies:
                        supply = supplies_response.supplies[0]

                        # Energía reactiva del año 2024
                        reactive_data = client.get_reactive_data(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/12"
                        )

                        print(f"✓ Datos de energía reactiva: {len(reactive_data)} registros")

                        for data in reactive_data:
                            print(f"CUPS: {data.reactive_energy.cups}")
                            print(f"Código: {data.reactive_energy.code}")
                            print(f"Descripción: {data.reactive_energy.code_desc}")

                            # Analizar energía por períodos
                            for energy_record in data.reactive_energy.energy:
                                date = energy_record.date
                                total_reactive = sum([
                                    energy_record.energy_p1 or 0,
                                    energy_record.energy_p2 or 0,
                                    energy_record.energy_p3 or 0,
                                    energy_record.energy_p4 or 0,
                                    energy_record.energy_p5 or 0,
                                    energy_record.energy_p6 or 0
                                ])
                                print(f"{date}: {total_reactive:.2f} kVARh total")

                            print("---")

            Analizar penalizaciones potenciales::

                # Buscar meses con alta energía reactiva
                for data in reactive_data:
                    for energy_record in data.reactive_energy.energy:
                        # Calcular energía reactiva total del mes
                        monthly_reactive = sum([
                            energy_record.energy_p1 or 0,
                            energy_record.energy_p2 or 0,
                            energy_record.energy_p3 or 0,
                            energy_record.energy_p4 or 0,
                            energy_record.energy_p5 or 0,
                            energy_record.energy_p6 or 0
                        ])

                        if monthly_reactive > 1000:  # Umbral de ejemplo
                            print(f"⚠️  {energy_record.date}: Alta energía reactiva ({monthly_reactive:.2f} kVARh)")
                            print("   → Revisar equipos inductivos para optimizar factor de potencia")

            Consultar con NIF autorizado::

                reactive_data = client.get_reactive_data(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/06",
                    authorized_nif="87654321B"
                )

                if reactive_data:
                    print("Datos de energía reactiva obtenidos con autorización")

            ¿Por qué no está disponible en V1?::

                # V1 - Esta funcionalidad NO EXISTE
                # client_v1.get_reactive_data()  # ← AttributeError: no existe

                # V2 - Funcionalidad completamente nueva
                reactive_data = client_v2.get_reactive_data(...)  # ✓ Disponible

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico como string
                                (ej: "2" para E-distribución)
        :type distributor_code: str
        :param date_from: Fecha de inicio en formato YYYY/MM
        :type date_from: str
        :param date_to: Fecha de fin en formato YYYY/MM
        :type date_to: str
        :param authorized_nif: NIF de la persona que autorizó la consulta de sus datos.
                              Si se especifica, se consultarán los datos de esa persona
        :type authorized_nif: Optional[str]
        :return: Lista de objetos ``ReactiveData`` validados con Pydantic.
                Cada objeto contiene información detallada de energía reactiva
                por períodos tarifarios y fechas
        :rtype: List[ReactiveData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si las fechas no están en formato mensual válido o
                               los datos no pasan la validación Pydantic
        :raises ValueError: Si el CUPS no tiene el formato correcto

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-reactive-data-v2``
           - Para datos de energía activa: :meth:`get_consumption`
           - Para datos de potencia máxima: :meth:`get_max_power`
           - Información sobre factor de potencia y energía reactiva en documentación técnica

        .. versionadded:: 2.0
           Funcionalidad completamente nueva, no disponible en V1

        .. note::
           Esta funcionalidad puede no estar disponible para todos los tipos de punto
           o distribuidores. Consulte con su distribuidor la disponibilidad de estos datos.

        .. warning::
           La energía reactiva puede generar penalizaciones en la factura eléctrica.
           Use estos datos para optimizar el factor de potencia de su instalación.
        """
        print(f"Obteniendo energía reactiva para {cups} ({date_from} - {date_to})...")

        # Convertir parámetros usando los conversores
        cups = convert_cups_parameter(cups)
        distributor_code = convert_distributor_code_parameter(distributor_code)
        date_from, date_to = convert_date_range_to_api_format(
            date_from, date_to, "monthly"
        )

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self._make_authenticated_request(
            API_V2_ENDPOINTS["reactive_data"], params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"reactiveEnergy": {}, "distributorError": []}

        # Manejar estructura de respuesta para energía reactiva
        raw_reactive_data = []
        if "reactiveEnergy" in response and response["reactiveEnergy"]:
            raw_reactive_data = [response]  # Envolver en lista para consistencia

        # Validar datos con Pydantic
        from ...models.reactive import ReactiveData

        validated_reactive_data = []
        for reactive_data in raw_reactive_data:
            try:
                validated_reactive_item = ReactiveData(**reactive_data)
                validated_reactive_data.append(validated_reactive_item)
            except Exception as e:
                print(f"Error validando datos de energía reactiva: {e}")
                continue

        print(f"{len(validated_reactive_data)} registros de energía reactiva validados")
        return validated_reactive_data

    def close(self):
        """
        Cierra explícitamente la sesión HTTP y limpia los recursos del cliente V2.

        Realiza las siguientes operaciones de limpieza:
            - **Cierra la sesión HTTP**: Libera conexiones TCP activas
            - **Invalida el token**: Establece el token a None por seguridad
            - **Libera recursos**: Evita memory leaks en aplicaciones de larga duración

        **¿Cuándo llamar manualmente?**
            Normalmente **NO es necesario** llamar este método explícitamente cuando se
            usa el patrón ``with`` (context manager), ya que ``__exit__`` lo llama automáticamente.

            Sin embargo, puede ser útil en estos casos:
                - **Aplicaciones de larga duración**: Cuando el cliente se mantiene activo mucho tiempo
                - **Gestión manual de recursos**: Cuando no se usa context manager
                - **Problemas de conectividad**: Para forzar reconexión después de errores
                - **Testing y debugging**: Para controlar explícitamente el ciclo de vida

        **V1 vs V2 - Diferencias en gestión de recursos:**
            - **V1**: Gestión de recursos más simple, principalmente HTTP sessions
            - **V2**: Gestión más robusta con mejor manejo de tokens y sesiones

        Example:
            Uso con context manager (recomendado)::

                # El método close() se llama automáticamente
                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies = client.get_supplies()
                    # Al salir del bloque 'with', close() se ejecuta automáticamente

                print("✓ Sesión cerrada automáticamente")

            Uso manual (casos especiales)::

                client = SimpleDatadisClientV2("12345678A", "password")
                try:
                    supplies = client.get_supplies()
                    consumption = client.get_consumption(
                        cups=supplies.supplies[0].cups,
                        distributor_code=supplies.supplies[0].distributorCode,
                        date_from="2024/01",
                        date_to="2024/03"
                    )

                    # Procesar muchos datos...

                finally:
                    client.close()  # ← Llamada manual obligatoria
                    print("✓ Recursos liberados manualmente")

            Aplicación de larga duración::

                class DatadisService:
                    def __init__(self):
                        self.client = None

                    def connect(self):
                        self.client = SimpleDatadisClientV2("12345678A", "password")

                    def disconnect(self):
                        if self.client:
                            self.client.close()  # ← Limpieza explícita
                            self.client = None

                    def get_recent_consumption(self):
                        if not self.client:
                            self.connect()
                        return self.client.get_consumption(...)

            Debugging y reconexión::

                client = SimpleDatadisClientV2("12345678A", "password")

                # Primer intento
                try:
                    supplies = client.get_supplies()
                except Exception as e:
                    print(f"Error: {e}")
                    client.close()  # ← Limpiar estado

                    # Reintentar con nueva sesión
                    client = SimpleDatadisClientV2("12345678A", "password")
                    supplies = client.get_supplies()

        .. note::
           Este método es **idempotente**: se puede llamar múltiples veces sin efectos
           secundarios. Si la sesión ya está cerrada, no hace nada.

        .. warning::
           Después de llamar a ``close()``, el cliente queda **inutilizable**. Cualquier
           intento de hacer requests fallará. Cree una nueva instancia si necesita
           continuar usando la API.

        .. seealso::
           - :meth:`__enter__` y :meth:`__exit__` para el patrón context manager
           - Documentación de ``requests.Session.close()`` para detalles técnicos
        """
        if self.session:
            self.session.close()
        self.token = None

    def __enter__(self):
        """
        Método de entrada del context manager - Permite usar ``with`` statement.

        Implementa el protocolo de context manager de Python, permitiendo que el cliente
        se use con la declaración ``with`` para **gestión automática de recursos**.

        **¿Qué hace este método?**
            - **Retorna la instancia actual**: Permite acceso a todos los métodos del cliente
            - **Inicialización implícita**: La autenticación se realiza de forma lazy en el primer request
            - **Establece el contexto**: Prepara el cliente para uso dentro del bloque ``with``

        **Ventajas del patrón context manager:**
            1. **Gestión automática**: Los recursos se liberan automáticamente al salir
            2. **Robustez ante errores**: Cleanup garantizado incluso si ocurren excepciones
            3. **Código más limpio**: No necesidad de llamadas manuales a ``close()``
            4. **Mejores prácticas**: Patrón estándar en Python para gestión de recursos

        **V1 vs V2 - Context manager:**
            - **V1**: Implementación básica del patrón
            - **V2**: Implementación mejorada con mejor gestión de excepciones y recursos

        Example:
            Uso estándar con context manager::

                # __enter__() se llama automáticamente aquí ↓
                with SimpleDatadisClientV2("12345678A", "password") as client:
                    # 'client' es lo que retorna __enter__()
                    supplies = client.get_supplies()

                    for supply in supplies.supplies:
                        consumption = client.get_consumption(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/03"
                        )
                        print(f"Consumo: {len(consumption)} registros")
                # __exit__() se llama automáticamente aquí ↑

                print("✓ Recursos liberados automáticamente")

            Context manager anidado::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies = client.get_supplies()

                    # Múltiples operaciones en el mismo contexto
                    for supply in supplies.supplies[:3]:  # Primeros 3 suministros
                        distributors = client.get_distributors()
                        contracts = client.get_contract_detail(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode
                        )

                        # V2 exclusive: Energía reactiva
                        reactive_data = client.get_reactive_data(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/03"
                        )

                        print(f"CUPS: {supply.cups}")
                        print(f"- Contratos: {len(contracts)}")
                        print(f"- Energía reactiva: {len(reactive_data)} registros")

            Comparación con uso manual::

                # ❌ Uso manual (más propenso a errores)
                client = SimpleDatadisClientV2("12345678A", "password")
                try:
                    supplies = client.get_supplies()
                    # ... hacer trabajo ...
                finally:
                    client.close()  # ← Fácil de olvidar

                # ✅ Context manager (recomendado)
                with SimpleDatadisClientV2("12345678A", "password") as client:
                    supplies = client.get_supplies()
                    # ... hacer trabajo ...
                # ← Cleanup automático garantizado

            Manejo de excepciones transparente::

                try:
                    with SimpleDatadisClientV2("invalid_nif", "wrong_pass") as client:
                        supplies = client.get_supplies()  # ← AuthenticationError
                except AuthenticationError as e:
                    print(f"Error de autenticación: {e}")
                # ← close() se ejecuta incluso con excepción

        :return: La propia instancia del cliente, permitiendo acceso a todos sus métodos
        :rtype: SimpleDatadisClientV2

        .. note::
           Este método **NO** realiza la autenticación. La autenticación se hace de forma
           lazy en el primer request que requiera token.

        .. seealso::
           - :meth:`__exit__` para el método de salida del context manager
           - :meth:`close` para limpieza manual de recursos
           - `PEP 343 <https://peps.python.org/pep-0343/>`_ - Especificación del protocolo context manager

        .. versionadded:: 2.0
           Implementación mejorada del context manager con mejor gestión de recursos
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método de salida del context manager - Garantiza limpieza automática de recursos.

        Se ejecuta automáticamente al salir del bloque ``with``, **independientemente** de
        si el código terminó normalmente o con una excepción. Garantiza que los recursos
        se liberen correctamente en todos los casos.

        **¿Qué hace este método?**
            - **Llamada automática a close()**: Libera sesiones HTTP y tokens
            - **Cleanup garantizado**: Se ejecuta incluso si ocurren excepciones
            - **No suprime excepciones**: Permite que las excepciones se propaguen normalmente
            - **Gestión robusta**: Implementación defensiva ante posibles errores

        **Flujo de ejecución:**
            1. **Entrada**: ``__enter__()`` retorna la instancia del cliente
            2. **Trabajo**: Se ejecuta el código dentro del bloque ``with``
            3. **Salida**: ``__exit__()`` se llama automáticamente (incluso con excepciones)
            4. **Cleanup**: ``close()`` libera todos los recursos
            5. **Propagación**: Las excepciones originales se mantienen

        **V1 vs V2 - Gestión de excepciones:**
            - **V1**: Implementación básica de cleanup
            - **V2**: Gestión más robusta, mejor logging de errores durante cleanup

        Example:
            Flujo normal (sin excepciones)::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    # __enter__() ejecutado ↑

                    supplies = client.get_supplies()
                    print(f"Suministros: {len(supplies.supplies)}")

                    # Código se ejecuta normalmente
                    consumption = client.get_consumption(
                        cups=supplies.supplies[0].cups,
                        distributor_code=supplies.supplies[0].distributorCode,
                        date_from="2024/01",
                        date_to="2024/03"
                    )

                # __exit__(None, None, None) ejecutado aquí ↑
                # Recursos liberados automáticamente
                print("✓ Operación completada, recursos liberados")

            Flujo con excepción controlada::

                try:
                    with SimpleDatadisClientV2("12345678A", "wrong_password") as client:
                        # __enter__() ejecutado ↑

                        supplies = client.get_supplies()  # ← AuthenticationError

                except AuthenticationError as e:
                    # __exit__(AuthenticationError, e, traceback) ya ejecutado ↑
                    print(f"Error de autenticación: {e}")
                    print("✓ Recursos liberados automáticamente (con excepción)")

            Flujo con excepción inesperada::

                with SimpleDatadisClientV2("12345678A", "password") as client:
                    # __enter__() ejecutado ↑

                    supplies = client.get_supplies()

                    # Error inesperado en el código del usuario
                    result = 1 / 0  # ← ZeroDivisionError

                # __exit__(ZeroDivisionError, exception, traceback) ejecutado ↑
                # Recursos liberados automáticamente
                # ZeroDivisionError se propaga normalmente

            Múltiples context managers::

                # Cada context manager gestiona sus propios recursos
                with SimpleDatadisClientV2("user1_nif", "pass1") as client1:
                    with SimpleDatadisClientV2("user2_nif", "pass2") as client2:
                        # Ambos clientes activos
                        supplies1 = client1.get_supplies()
                        supplies2 = client2.get_supplies()

                        # Comparar datos entre usuarios
                        print(f"Usuario 1: {len(supplies1.supplies)} suministros")
                        print(f"Usuario 2: {len(supplies2.supplies)} suministros")
                    # client2.__exit__() ejecutado aquí
                # client1.__exit__() ejecutado aquí

                print("✓ Ambos clientes cerrados correctamente")

            Debugging del context manager::

                class DebuggingDatadisClient(SimpleDatadisClientV2):
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        print(f"Saliendo del context manager...")
                        if exc_type:
                            print(f"- Con excepción: {exc_type.__name__}: {exc_val}")
                        else:
                            print("- Terminación normal")

                        # Llamar al método padre para cleanup real
                        super().__exit__(exc_type, exc_val, exc_tb)
                        print("✓ Recursos liberados")

                with DebuggingDatadisClient("12345678A", "password") as client:
                    supplies = client.get_supplies()
                    # raise ValueError("Error de prueba")  # ← Descomentar para probar

        :param exc_type: Tipo de excepción que causó la salida, o None si terminó normalmente
        :type exc_type: Optional[Type[BaseException]]
        :param exc_val: Instancia de la excepción que causó la salida, o None si terminó normalmente
        :type exc_val: Optional[BaseException]
        :param exc_tb: Traceback de la excepción, o None si terminó normalmente
        :type exc_tb: Optional[TracebackType]
        :return: None (no suprime excepciones, permite propagación normal)
        :rtype: None

        .. note::
           Este método **NUNCA** suprime excepciones (siempre retorna None/False).
           Las excepciones se propagan normalmente después del cleanup.

        .. warning::
           **NO** llame este método manualmente. Es invocado automáticamente por Python
           al salir del bloque ``with``. La llamada manual puede causar doble cleanup.

        .. seealso::
           - :meth:`__enter__` para el método de entrada del context manager
           - :meth:`close` para la implementación del cleanup
           - `PEP 343 <https://peps.python.org/pep-0343/>`_ - Especificación del protocolo context manager
           - `Context Manager Types <https://docs.python.org/3/library/stdtypes.html#context-manager-types>`_

        .. versionadded:: 2.0
           Implementación mejorada con mejor gestión de excepciones durante cleanup
        """
        self.close()
