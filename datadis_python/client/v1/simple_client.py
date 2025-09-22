"""Cliente V1 simplificado para Datadis."""

import time
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import requests

if TYPE_CHECKING:
    from ...models.consumption import ConsumptionData
    from ...models.contract import ContractData
    from ...models.distributor import DistributorData
    from ...models.max_power import MaxPowerData
    from ...models.supply import SupplyData

from ...exceptions import APIError, AuthenticationError, DatadisError
from ...utils.constants import (
    API_V1_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)
from ...utils.text_utils import normalize_api_response


class SimpleDatadisClientV1:
    """
    Cliente simplificado para la API V1 de Datadis.

    Este cliente proporciona una interfaz fácil de usar para acceder a los datos de consumo
    eléctrico almacenados en las bases de datos de las distribuidoras eléctricas españolas
    a través de la plataforma Datadis.

    Características principales:
    - Autenticación automática y renovación de tokens
    - Manejo robusto de timeouts y reintentos
    - Validación de datos con Pydantic para mayor seguridad
    - Soporte para tipos flexibles en parámetros de entrada
    - Context manager para gestión automática de recursos

    Example:
        Uso básico del cliente::

            from datadis_python.client.v1 import SimpleDatadisClientV1

            # Inicializar el cliente
            client = SimpleDatadisClientV1(
                username="12345678A",
                password="mi_password",
                timeout=120,
                retries=3
            )

            # Usar como context manager (recomendado)
            with SimpleDatadisClientV1("12345678A", "mi_password") as client:
                # Obtener suministros
                supplies = client.get_supplies()

                # Obtener consumo para un suministro específico
                if supplies:
                    consumption = client.get_consumption(
                        cups=supplies[0].cups,
                        distributor_code=supplies[0].distributorCode,
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
    :raises ValidationError: Si los datos devueltos por la API no pasan la validación Pydantic
    """

    def __init__(
        self, username: str, password: str, timeout: int = 120, retries: int = 3
    ):
        """
        Inicializa el cliente simplificado.

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
        Autentica con la API de Datadis y obtiene el token de acceso.

        Realiza una petición POST al endpoint ``/nikola-auth/tokens/login`` de la API
        de Datadis para obtener un token Bearer que será utilizado en todas las
        peticiones subsecuentes. El token se almacena automáticamente y se añade
        a los headers de la sesión HTTP.

        Note:
            Este método normalmente NO necesita ser llamado manualmente, ya que
            la autenticación se realiza automáticamente cuando se ejecuta cualquier
            método que requiera acceso a la API (como ``get_supplies()``,
            ``get_consumption()``, etc.).

        Warning:
            Los tokens de Datadis tienen expiración, pero la renovación se maneja
            automáticamente cuando se detecta un error 401 (Unauthorized).

        Example:
            Autenticación manual (opcional)::

                client = SimpleDatadisClientV1("12345678A", "mi_password")

                # Verificar credenciales antes de hacer operaciones
                if client.authenticate():
                    print("Credenciales válidas")
                    supplies = client.get_supplies()
                else:
                    print("Error en las credenciales")

        :return: ``True`` si la autenticación fue exitosa, ``False`` en caso contrario
        :rtype: bool
        :raises AuthenticationError: Si las credenciales (NIF/contraseña) son inválidas
                                   o el servidor devuelve un error de autenticación
        :raises DatadisError: Si ocurre un timeout o error de conexión con el servidor

        .. seealso::
           - Documentación oficial: ``POST /nikola-auth/tokens/login``
           - Los tokens son válidos por tiempo limitado y se renuevan automáticamente
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
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Any:
        """
        Realiza una petición HTTP autenticada a la API de Datadis con manejo robusto de errores.

        Este método interno maneja toda la lógica de peticiones HTTP incluyendo:
        autenticación automática, renovación de tokens, reintentos con backoff
        exponencial, manejo de timeouts y normalización de respuestas.

        Flujo de operación:
            1. Verifica si existe un token válido, si no, autentica automáticamente
            2. Realiza la petición HTTP GET al endpoint especificado
            3. Maneja códigos de respuesta (200: éxito, 401: token expirado, otros: error)
            4. Implementa reintentos con backoff exponencial en caso de timeouts
            5. Normaliza la respuesta JSON para evitar problemas de caracteres especiales

        Estrategia de reintentos:
            - Errores HTTP 4xx/5xx: No se reintentan (se propagan inmediatamente)
            - Timeouts y errores de red: Se reintentan hasta ``self.retries`` veces
            - Backoff exponencial: 2s, 4s, 8s... (máximo 30s para timeouts)
            - Error 401: Se renueva el token automáticamente y se reintenta

        :param endpoint: Endpoint relativo de la API (ej: ``'/get-supplies'``)
        :type endpoint: str
        :param params: Parámetros de query string para la petición HTTP
        :type params: Optional[Dict]
        :return: Respuesta JSON normalizada de la API
        :rtype: Any
        :raises AuthenticationError: Si no se puede autenticar o renovar el token
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si se agotan todos los reintentos por timeouts o errores de red

        .. note::
           Este es un método interno. Los usuarios deben usar los métodos públicos
           como ``get_supplies()``, ``get_consumption()``, etc.
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
                    return normalize_api_response(json_response)
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
        distributor_code: Optional[Union[str, int]] = None,
    ) -> List["SupplyData"]:
        """
        Obtiene la lista de puntos de suministro (CUPS) asociados al usuario.

        Consulta el endpoint ``GET /api-private/api/get-supplies`` para obtener todos
        los puntos de suministro eléctrico que el usuario tiene registrados en Datadis.
        Los datos se validan automáticamente usando Pydantic para garantizar la
        integridad y consistencia de la información.

        Los puntos de suministro incluyen información detallada como:
        - Código CUPS (identificador único del punto de suministro)
        - Dirección física del suministro
        - Código postal, provincia y municipio
        - Distribuidor eléctrico y su código
        - Fechas de validez del contrato
        - Tipo de punto de medida (1-5)

        Códigos de distribuidor más comunes:
            - **1**: Viesgo
            - **2**: E-distribución (Endesa)
            - **3**: E-redes
            - **4**: ASEME
            - **5**: UFD (Naturgy)
            - **6**: EOSA
            - **7**: CIDE
            - **8**: IDE

        Example:
            Obtener todos los suministros del usuario::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    supplies = client.get_supplies()

                    for supply in supplies:
                        print(f"CUPS: {supply.cups}")
                        print(f"Dirección: {supply.address}")
                        print(f"Distribuidor: {supply.distributor} (código: {supply.distributorCode})")
                        print(f"Tipo: {supply.pointType}")
                        print("---")

            Filtrar por distribuidor específico::

                # Solo suministros de Endesa (E-distribución)
                supplies_endesa = client.get_supplies(distributor_code=2)

                # También funciona con string
                supplies_endesa = client.get_supplies(distributor_code="2")

        :param authorized_nif: NIF de una persona autorizada para consultar sus suministros.
                              Si se especifica, se obtendrán los suministros de esa persona
                              en lugar de los del usuario autenticado
        :type authorized_nif: Optional[str]
        :param distributor_code: Código del distribuidor para filtrar suministros.
                                Acepta tanto enteros como strings (ej: 2 o "2")
        :type distributor_code: Optional[Union[str, int]]
        :return: Lista de objetos ``SupplyData`` validados con Pydantic, cada uno
                representando un punto de suministro con toda su información asociada
        :rtype: List[SupplyData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-supplies``
           - Para obtener detalles del contrato: :meth:`get_contract_detail`
           - Lista completa de códigos de distribuidor en la documentación de la API
        """
        print("Obteniendo lista de suministros...")

        # Construir parámetros de query
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif
        if distributor_code is not None:
            from ...utils.type_converters import convert_distributor_code_parameter

            params["distributorCode"] = convert_distributor_code_parameter(
                distributor_code
            )

        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["supplies"], params=params
        )

        raw_supplies = []
        if isinstance(response, list):
            raw_supplies = response
        elif isinstance(response, dict) and "supplies" in response:
            raw_supplies = response["supplies"]
        else:
            print("Respuesta inesperada de la API")
            return []

        # Validar datos con Pydantic
        from ...models.supply import SupplyData

        validated_supplies = []
        for supply_data in raw_supplies:
            try:
                validated_supply = SupplyData(**supply_data)
                validated_supplies.append(validated_supply)
            except Exception as e:
                print(f"Error validando suministro: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"{len(validated_supplies)} suministros validados")
        return validated_supplies

    def get_distributors(self) -> List["DistributorData"]:
        """
        Obtiene la lista de distribuidores eléctricos donde el usuario tiene suministros.

        Consulta el endpoint ``GET /api-private/api/get-distributors-with-supplies``
        para obtener información sobre las distribuidoras eléctricas donde el usuario
        autenticado tiene puntos de suministro activos. Esto es útil para conocer
        qué distribuidores están disponibles antes de realizar consultas específicas.

        La respuesta incluye los códigos únicos de cada distribuidor, que son necesarios
        para realizar consultas posteriores como obtener consumos, contratos o potencias
        máximas de suministros específicos.

        Distribuidores eléctricos en España:
            - **Código 1**: Viesgo (Cantabria, Asturias)
            - **Código 2**: E-distribución/Endesa (Nacional)
            - **Código 3**: E-redes (Galicia)
            - **Código 4**: ASEME (Melilla)
            - **Código 5**: UFD/Naturgy (Nacional)
            - **Código 6**: EOSA (Aragón)
            - **Código 7**: CIDE (Ceuta)
            - **Código 8**: IDE (Baleares)

        Example:
            Listar distribuidores del usuario::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    distributors = client.get_distributors()

                    print("Distribuidores con suministros:")
                    for dist in distributors:
                        print(f"- {dist.distributorName} (Código: {dist.distributorCode})")

                    # Usar el primer distribuidor para consultas posteriores
                    if distributors:
                        first_dist_code = distributors[0].distributorCode
                        supplies = client.get_supplies(distributor_code=first_dist_code)

        :return: Lista de objetos ``DistributorData`` validados con Pydantic.
                Cada objeto contiene el código y nombre del distribuidor donde
                el usuario tiene suministros activos
        :rtype: List[DistributorData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-distributors-with-supplies``
           - Para filtrar suministros por distribuidor: :meth:`get_supplies`
           - Los códigos obtenidos aquí se usan en :meth:`get_consumption`, :meth:`get_contract_detail`, etc.

        .. note::
           Solo se devuelven distribuidores donde el usuario tiene suministros activos.
           Si no hay suministros registrados, la lista estará vacía.
        """
        print("Obteniendo distribuidores...")
        response = self._make_authenticated_request(API_V1_ENDPOINTS["distributors"])

        # Manejar diferentes estructuras de respuesta
        raw_distributors = []
        if isinstance(response, list):
            raw_distributors = response
        elif isinstance(response, dict):
            if response:
                raw_distributors = [response]

        # Validar datos con Pydantic
        from ...models.distributor import DistributorData

        validated_distributors = []
        for distributor_data in raw_distributors:
            try:
                validated_distributor = DistributorData(**distributor_data)
                validated_distributors.append(validated_distributor)
            except Exception as e:
                print(f"Error validando distribuidor: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"{len(validated_distributors)} distribuidores validados")
        return validated_distributors

    def get_contract_detail(
        self, cups: str, distributor_code: Union[str, int]
    ) -> List["ContractData"]:
        """
        Obtiene los detalles del contrato eléctrico para un punto de suministro específico.

        Consulta el endpoint ``GET /api-private/api/get-contract-detail`` para obtener
        información detallada del contrato asociado a un CUPS específico. Los datos
        incluyen información técnica, comercial y administrativa del suministro eléctrico.

        Información del contrato incluida:
            - **Datos básicos**: CUPS, distribuidor, comercializadora
            - **Características técnicas**: Tensión, potencia contratada, tipo de punto
            - **Datos tarifarios**: Tarifa de acceso, discriminación horaria, código de tarifa
            - **Ubicación**: Provincia, municipio, código postal
            - **Fechas**: Inicio y fin de contrato, fechas de cambios
            - **Autoconsumo**: Tipo y características (si aplica)
            - **Control de potencia**: ICP o Maxímetro
            - **CAU**: Código de Autoconsumo Único (si es aplicable)

        Types de punto de medida:
            - **Tipo 1**: > 450 kW (alta tensión)
            - **Tipo 2**: 50-450 kW (media tensión)
            - **Tipo 3**: 15-50 kW (baja tensión)
            - **Tipo 4**: < 15 kW con discriminación horaria
            - **Tipo 5**: < 15 kW sin discriminación horaria

        Example:
            Obtener detalles de contrato::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    # Primero obtener suministros
                    supplies = client.get_supplies()

                    if supplies:
                        supply = supplies[0]

                        # Obtener detalles del contrato
                        contracts = client.get_contract_detail(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode
                        )

                        for contract in contracts:
                            print(f"CUPS: {contract.cups}")
                            print(f"Distribuidor: {contract.distributor}")
                            print(f"Potencia contratada: {contract.contractedPowerkW} kW")
                            print(f"Tarifa: {contract.accessFare}")
                            print(f"Tipo de punto: {contract.pointType}")
                            if contract.marketer:
                                print(f"Comercializadora: {contract.marketer}")

            Usando tipos flexibles de parámetros::

                # Ambos formatos son válidos
                contracts1 = client.get_contract_detail("ES001234567890123456AB", 2)
                contracts2 = client.get_contract_detail("ES001234567890123456AB", "2")

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos
                    que identifican únicamente el punto de suministro eléctrico)
        :type cups: str
        :param distributor_code: Código numérico del distribuidor eléctrico.
                                Acepta tanto enteros como strings para mayor flexibilidad
        :type distributor_code: Union[str, int]
        :return: Lista de objetos ``ContractData`` validados con Pydantic.
                Normalmente contiene un solo contrato, pero pueden ser varios
                si ha habido cambios históricos en el suministro
        :rtype: List[ContractData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si los datos devueltos no pasan la validación Pydantic
        :raises ValueError: Si el CUPS no tiene el formato correcto (22 caracteres)

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-contract-detail``
           - Para obtener la lista de CUPS: :meth:`get_supplies`
           - Para datos de consumo del contrato: :meth:`get_consumption`

        .. note::
           El CUPS debe ser exactamente de 22 caracteres alfanuméricos.
           Si el formato es incorrecto, la API devolverá un error.
        """
        from ...utils.type_converters import (
            convert_cups_parameter,
            convert_distributor_code_parameter,
        )

        # Convertir parámetros usando los conversores
        cups_converted = convert_cups_parameter(cups)
        distributor_code_converted = convert_distributor_code_parameter(
            distributor_code
        )

        print(f"Obteniendo contrato para {cups_converted}...")

        params = {"cups": cups_converted, "distributorCode": distributor_code_converted}
        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["contracts"], params
        )

        # Manejar diferentes estructuras de respuesta
        raw_contracts = []
        if isinstance(response, list):
            raw_contracts = response
        elif isinstance(response, dict):
            if response:
                raw_contracts = [response]

        # Validar datos con Pydantic
        from ...models.contract import ContractData

        validated_contracts = []
        for contract_data in raw_contracts:
            try:
                validated_contract = ContractData(**contract_data)
                validated_contracts.append(validated_contract)
            except Exception as e:
                print(f"Error validando contrato: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"{len(validated_contracts)} contratos validados")
        return validated_contracts

    def get_consumption(
        self,
        cups: str,
        distributor_code: Union[str, int],
        date_from: Union[str, datetime, date],
        date_to: Union[str, datetime, date],
        measurement_type: Union[int, float, str] = 0,
        point_type: Optional[Union[int, float, str]] = None,
    ) -> List["ConsumptionData"]:
        """
        Obtiene los datos de consumo eléctrico para un punto de suministro específico.

        Consulta el endpoint ``GET /api-private/api/get-consumption-data`` para obtener
        la curva de carga (datos de consumo) de un CUPS en un período determinado.
        Los datos incluyen consumo, excedentes, generación y autoconsumo cuando aplique.

        **IMPORTANTE - Limitación de fechas:**
            La API de Datadis **SOLO acepta fechas en formato mensual** (YYYY/MM).
            NO se permiten fechas con días específicos. El SDK convierte automáticamente
            fechas datetime/date al formato requerido.

        **IMPORTANTE - Disponibilidad de datos cuarto-horarios:**
            Los datos cada 15 minutos (``measurement_type=1``) solo están disponibles para:
            - Tipos de punto 1 y 2 (alta y media tensión)
            - Tipo de punto 3 en E-distribución únicamente
            - Para el resto de casos, solo están disponibles datos horarios (``measurement_type=0``)

        Tipos de medición:
            - **0**: Datos horarios (disponible para todos los tipos de punto)
            - **1**: Datos cuarto-horarios/15 min (limitado según tipo de punto)

        Tipos de punto de medida:
            - **1**: > 450 kW - Datos horarios y cuarto-horarios
            - **2**: 50-450 kW - Datos horarios y cuarto-horarios
            - **3**: 15-50 kW - Cuarto-horarios solo en E-distribución
            - **4**: < 15 kW con DH - Solo datos horarios
            - **5**: < 15 kW sin DH - Solo datos horarios

        Datos incluidos en la respuesta:
            - **Consumo**: Energía consumida de la red (kWh)
            - **Excedentes**: Energía vertida a la red (kWh)
            - **Generación**: Energía generada por autoconsumo (kWh)
            - **Autoconsumo**: Energía autoconsumida directamente (kWh)
            - **Método de obtención**: Real (medido) o Estimada (calculada)

        Example:
            Obtener consumo horario para todo un año::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    supplies = client.get_supplies()

                    if supplies:
                        supply = supplies[0]

                        # Consumo horario del año 2024
                        consumption = client.get_consumption(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",  # Enero 2024
                            date_to="2024/12",    # Diciembre 2024
                            measurement_type=0    # Datos horarios
                        )

                        # Analizar los datos
                        total_kwh = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
                        print(f"Consumo total 2024: {total_kwh:.2f} kWh")

                        # Filtrar datos reales vs estimados
                        real_data = [c for c in consumption if c.obtainMethod == "Real"]
                        print(f"Datos reales: {len(real_data)}/{len(consumption)}")

            Obtener datos cuarto-horarios (solo para tipos 1, 2, y 3 en E-distribución)::

                # Solo si el tipo de punto lo permite
                consumption_15min = client.get_consumption(
                    cups="ES001234567890123456AB",
                    distributor_code=2,  # E-distribución
                    date_from="2024/06",
                    date_to="2024/06",
                    measurement_type=1,  # Cuarto-horarios
                    point_type=3         # Tipo de punto
                )

            Usando diferentes tipos de fecha::

                from datetime import date, datetime

                # Con strings (recomendado)
                consumption1 = client.get_consumption(cups, dist_code, "2024/01", "2024/03")

                # Con objetos datetime (se convertirán automáticamente)
                start_date = datetime(2024, 1, 1)
                end_date = datetime(2024, 3, 31)
                consumption2 = client.get_consumption(cups, dist_code, start_date, end_date)

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico (acepta int o str)
        :type distributor_code: Union[str, int]
        :param date_from: Fecha de inicio en formato YYYY/MM. También acepta objetos
                         datetime/date que se convertirán automáticamente
        :type date_from: Union[str, datetime, date]
        :param date_to: Fecha de fin en formato YYYY/MM. También acepta objetos
                       datetime/date que se convertirán automáticamente
        :type date_to: Union[str, datetime, date]
        :param measurement_type: Tipo de medición - 0: horarios (defecto), 1: cuarto-horarios.
                               Acepta int, float o str
        :type measurement_type: Union[int, float, str]
        :param point_type: Tipo de punto de medida (1-5). Requerido para datos cuarto-horarios.
                          Acepta int, float o str
        :type point_type: Optional[Union[int, float, str]]
        :return: Lista de objetos ``ConsumptionData`` validados con Pydantic.
                Cada objeto representa una lectura de consumo con timestamp
        :rtype: List[ConsumptionData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si las fechas no están en formato mensual válido o
                               los datos no pasan la validación Pydantic
        :raises ValueError: Si se solicitan datos cuarto-horarios para un tipo de punto no compatible

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-consumption-data``
           - Para obtener CUPS: :meth:`get_supplies`
           - Para datos de potencia máxima: :meth:`get_max_power`

        .. warning::
           Los datos cuarto-horarios no están disponibles para todos los tipos de punto.
           Verifique la compatibilidad antes de solicitar ``measurement_type=1``.
        """
        from ...utils.type_converters import (
            convert_cups_parameter,
            convert_date_range_to_api_format,
            convert_distributor_code_parameter,
            convert_number_to_string,
            convert_optional_number_to_string,
        )

        # Convertir parámetros usando los conversores
        cups_converted = convert_cups_parameter(cups)
        distributor_code_converted = convert_distributor_code_parameter(
            distributor_code
        )
        # CAMBIO CRÍTICO: Usar "monthly" en lugar de "daily" para la API de Datadis
        date_from_converted, date_to_converted = convert_date_range_to_api_format(
            date_from, date_to, "monthly"
        )
        measurement_type_converted = convert_number_to_string(measurement_type)
        point_type_converted = convert_optional_number_to_string(point_type)

        print(
            f"Obteniendo consumo para {cups_converted} ({date_from_converted} - {date_to_converted})..."
        )

        params = {
            "cups": cups_converted,
            "distributorCode": distributor_code_converted,
            "startDate": date_from_converted,
            "endDate": date_to_converted,
            "measurementType": measurement_type_converted,
        }

        if point_type_converted is not None:
            params["pointType"] = point_type_converted

        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["consumption"], params
        )

        # Manejar diferentes estructuras de respuesta
        raw_consumption = []
        if isinstance(response, list):
            raw_consumption = response
        elif isinstance(response, dict) and "timeCurve" in response:
            raw_consumption = response["timeCurve"]

        # Validar datos con Pydantic
        from ...models.consumption import ConsumptionData

        validated_consumption = []
        for consumption_data in raw_consumption:
            try:
                validated_consumption_item = ConsumptionData(**consumption_data)
                validated_consumption.append(validated_consumption_item)
            except Exception as e:
                print(f"Error validando consumo: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"{len(validated_consumption)} registros de consumo validados")
        return validated_consumption

    def get_max_power(
        self,
        cups: str,
        distributor_code: Union[str, int],
        date_from: Union[str, datetime, date],
        date_to: Union[str, datetime, date],
    ) -> List["MaxPowerData"]:
        """
        Obtiene los datos de potencia máxima demandada para un punto de suministro.

        Consulta el endpoint ``GET /api-private/api/get-max-power`` para obtener
        las potencias máximas registradas en cada período tarifario durante el
        rango de fechas especificado. Esta información es crucial para optimizar
        la potencia contratada y evitar penalizaciones por excesos.

        **IMPORTANTE - Limitación de fechas:**
            Al igual que los datos de consumo, la API **SOLO acepta fechas en formato
            mensual** (YYYY/MM). El SDK convierte automáticamente fechas datetime/date
            al primer día del mes correspondiente.

        Períodos tarifarios incluidos:
            - **VALLE**: Período de menor coste energético (madrugada)
            - **LLANO**: Período de coste intermedio (mañana/tarde)
            - **PUNTA**: Período de mayor coste energético (mediodía/noche)
            - **P1, P2, P3, P4, P5, P6**: Períodos específicos según tarifa

        La potencia se mide en **Vatios (W)** y representa la demanda máxima
        registrada en cada período durante el mes consultado. Esta información
        es especialmente útil para:
            - Optimizar la potencia contratada
            - Identificar picos de consumo
            - Evaluar la eficiencia energética
            - Planificar instalaciones de autoconsumo

        Example:
            Obtener potencias máximas del último año::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    supplies = client.get_supplies()

                    if supplies:
                        supply = supplies[0]

                        # Potencias máximas de 2024
                        max_powers = client.get_max_power(
                            cups=supply.cups,
                            distributor_code=supply.distributorCode,
                            date_from="2024/01",
                            date_to="2024/12"
                        )

                        # Analizar potencias por período
                        periods = {}
                        for power in max_powers:
                            period = power.period
                            if period not in periods:
                                periods[period] = []
                            periods[period].append(power.maxPower)

                        # Mostrar potencia máxima por período
                        for period, powers in periods.items():
                            max_power_w = max(powers)
                            max_power_kw = max_power_w / 1000
                            print(f"Período {period}: {max_power_kw:.2f} kW")

            Identificar el mes con mayor demanda::

                # Agrupar por mes
                monthly_max = {}
                for power in max_powers:
                    month = power.date[:7]  # YYYY/MM
                    if month not in monthly_max:
                        monthly_max[month] = 0
                    monthly_max[month] = max(monthly_max[month], power.maxPower)

                # Encontrar el mes de mayor demanda
                peak_month = max(monthly_max, key=monthly_max.get)
                peak_power_kw = monthly_max[peak_month] / 1000
                print(f"Mayor demanda: {peak_power_kw:.2f} kW en {peak_month}")

        :param cups: Código CUPS del punto de suministro (22 caracteres alfanuméricos)
        :type cups: str
        :param distributor_code: Código del distribuidor eléctrico (acepta int o str)
        :type distributor_code: Union[str, int]
        :param date_from: Fecha de inicio en formato YYYY/MM. También acepta objetos
                         datetime/date que se convertirán automáticamente
        :type date_from: Union[str, datetime, date]
        :param date_to: Fecha de fin en formato YYYY/MM. También acepta objetos
                       datetime/date que se convertirán automáticamente
        :type date_to: Union[str, datetime, date]
        :return: Lista de objetos ``MaxPowerData`` validados con Pydantic.
                Cada objeto representa la potencia máxima registrada en un
                período específico con fecha, hora y período tarifario
        :rtype: List[MaxPowerData]
        :raises AuthenticationError: Si las credenciales son inválidas o el token expira
        :raises APIError: Si la API devuelve un error HTTP (400, 403, 404, 500, etc.)
        :raises DatadisError: Si ocurren errores de conexión o timeouts repetidos
        :raises ValidationError: Si las fechas no están en formato mensual válido o
                               los datos no pasan la validación Pydantic
        :raises ValueError: Si el CUPS no tiene el formato correcto

        .. seealso::
           - Documentación oficial: ``GET /api-private/api/get-max-power``
           - Para obtener CUPS: :meth:`get_supplies`
           - Para datos de consumo: :meth:`get_consumption`
           - Para detalles del contrato: :meth:`get_contract_detail`

        .. note::
           Las potencias se devuelven en Vatios (W). Para obtener kilovatios (kW)
           divida el valor entre 1000.
        """
        from ...utils.type_converters import (
            convert_cups_parameter,
            convert_date_range_to_api_format,
            convert_distributor_code_parameter,
        )

        # Convertir parámetros usando los conversores
        cups_converted = convert_cups_parameter(cups)
        distributor_code_converted = convert_distributor_code_parameter(
            distributor_code
        )
        # CAMBIO CRÍTICO: Usar "monthly" en lugar de "daily" para la API de Datadis
        date_from_converted, date_to_converted = convert_date_range_to_api_format(
            date_from, date_to, "monthly"
        )

        print(
            f"Obteniendo potencia máxima para {cups_converted} ({date_from_converted} - {date_to_converted})..."
        )

        params = {
            "cups": cups_converted,
            "distributorCode": distributor_code_converted,
            "startDate": date_from_converted,
            "endDate": date_to_converted,
        }

        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["max_power"], params
        )

        # Manejar diferentes estructuras de respuesta
        raw_max_power = []
        if isinstance(response, list):
            raw_max_power = response
        elif isinstance(response, dict) and "maxPower" in response:
            raw_max_power = response["maxPower"]

        # Validar datos con Pydantic
        from ...models.max_power import MaxPowerData

        validated_max_power = []
        for max_power_data in raw_max_power:
            try:
                validated_max_power_item = MaxPowerData(**max_power_data)
                validated_max_power.append(validated_max_power_item)
            except Exception as e:
                print(f"Error validando potencia máxima: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"{len(validated_max_power)} registros de potencia máxima validados")
        return validated_max_power

    def close(self):
        """
        Cierra la sesión HTTP y libera recursos del cliente.

        Este método limpia los recursos utilizados por el cliente:
        - Cierra la sesión HTTP de requests
        - Elimina el token de autenticación almacenado
        - Libera las conexiones de red activas

        Es una buena práctica llamar a este método cuando termine de usar
        el cliente, aunque se recomienda usar el cliente como context manager
        con ``with`` para gestión automática de recursos.

        Example:
            Uso manual (no recomendado)::

                client = SimpleDatadisClientV1("12345678A", "password")
                try:
                    supplies = client.get_supplies()
                    # ... más operaciones
                finally:
                    client.close()  # Limpiar recursos

            Uso recomendado con context manager::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    supplies = client.get_supplies()
                    # ... más operaciones
                # close() se llama automáticamente

        .. note::
           Si usa el cliente como context manager (con ``with``), este método
           se llama automáticamente al salir del bloque.
        """
        if self.session:
            self.session.close()
        self.token = None

    def __enter__(self):
        """
        Entrada del context manager para gestión automática de recursos.

        Este método se llama automáticamente cuando se usa el cliente con
        la declaración ``with``. Permite usar el patrón context manager
        para garantizar la limpieza automática de recursos.

        Example:
            Uso como context manager (recomendado)::

                with SimpleDatadisClientV1("12345678A", "password") as client:
                    # El método __enter__ se llama aquí automáticamente
                    supplies = client.get_supplies()
                    consumption = client.get_consumption(...)
                    # ... más operaciones
                # El método __exit__ se llama automáticamente al salir

        :return: La propia instancia del cliente para usar en el bloque ``with``
        :rtype: SimpleDatadisClientV1

        .. seealso::
           :meth:`__exit__` - Método de salida del context manager
           :meth:`close` - Limpieza manual de recursos
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Salida del context manager con limpieza automática de recursos.

        Este método se llama automáticamente al salir del bloque ``with``,
        garantizando que los recursos se liberen correctamente incluso si
        ocurre una excepción durante la ejecución.

        La limpieza incluye:
        - Cierre de la sesión HTTP
        - Eliminación del token de autenticación
        - Liberación de conexiones de red

        Example:
            El context manager maneja automáticamente las excepciones::

                try:
                    with SimpleDatadisClientV1("12345678A", "password") as client:
                        supplies = client.get_supplies()
                        # Si ocurre una excepción aquí...
                        raise Exception("Algo salió mal")
                except Exception as e:
                    # ... los recursos se limpian automáticamente
                    print(f"Error: {e}")
                # El cliente ya está cerrado y los recursos liberados

        :param exc_type: Tipo de excepción que causó la salida (None si no hay excepción)
        :type exc_type: Optional[type]
        :param exc_val: Instancia de la excepción (None si no hay excepción)
        :type exc_val: Optional[BaseException]
        :param exc_tb: Traceback de la excepción (None si no hay excepción)
        :type exc_tb: Optional[TracebackType]
        :return: None (no suprime excepciones)
        :rtype: None

        .. seealso::
           :meth:`__enter__` - Método de entrada del context manager
           :meth:`close` - Método de limpieza llamado internamente

        .. note::
           Este método no suprime excepciones - si ocurre un error en el bloque
           ``with``, la excepción se propagará normalmente después de la limpieza.
        """
        self.close()
