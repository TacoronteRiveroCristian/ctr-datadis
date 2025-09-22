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
    Cliente V2 simplificado que maneja mejor los timeouts de Datadis.

    :param username: NIF del usuario registrado en Datadis.
    :type username: str
    :param password: Contraseña de acceso a Datadis.
    :type password: str
    :param timeout: Timeout para requests en segundos (120s por defecto para Datadis).
    :type timeout: int
    :param retries: Número de reintentos automáticos.
    :type retries: int
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
        Autentica con la API de Datadis.

        :return: True si la autenticación fue exitosa
        :rtype: bool
        :raises AuthenticationError: Si las credenciales son inválidas
        :raises DatadisError: Si ocurre un error de conexión
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
        Realiza una petición autenticada con manejo robusto de timeouts.

        :param endpoint: Endpoint de la API (ej: '/get-supplies-v2')
        :type endpoint: str
        :param params: Parámetros de query
        :type params: Optional[dict]
        :return: Respuesta de la API
        :rtype: dict
        :raises AuthenticationError: Si no se puede autenticar
        :raises DatadisError: Si se agotan los reintentos
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
        Obtiene la lista de puntos de suministro validados con Pydantic.

        :param authorized_nif: NIF de la persona autorizada para buscar sus suministros
        :type authorized_nif: Optional[str]
        :param distributor_code: Código del distribuidor para filtrar suministros
        :type distributor_code: Optional[str]
        :return: Respuesta con suministros validados y errores de distribuidora
        :rtype: SuppliesResponse
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
        Obtiene distribuidores validados con Pydantic.

        :param authorized_nif: NIF autorizado para obtener distribuidoras del NIF autorizado
        :type authorized_nif: Optional[str]
        :return: Respuesta con códigos de distribuidores validados y errores
        :rtype: DistributorsResponse
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
        Obtiene detalle del contrato validado con Pydantic.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param authorized_nif: NIF autorizado para obtener el detalle del contrato
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de contrato validados y errores de distribuidora
        :rtype: ContractResponse
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
        Obtiene datos de consumo validados con Pydantic.

        IMPORTANTE: La API de Datadis solo acepta fechas en formato mensual (YYYY/MM).
        NO se permiten fechas con días específicos.

        Acepta tipos flexibles para mayor comodidad:
        - Fechas: strings (YYYY/MM), datetime objects, o date objects (se convertirán al primer día del mes)
        - Números: int, float, o string
        - Distributor code: string o int

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: Union[str, int]
        :param date_from: Fecha de inicio (YYYY/MM o datetime/date object)
        :type date_from: Union[str, datetime, date]
        :param date_to: Fecha de fin (YYYY/MM o datetime/date object)
        :type date_to: Union[str, datetime, date]
        :param measurement_type: Tipo de medición (default: 0)
        :type measurement_type: Union[int, float, str]
        :param point_type: Tipo de punto de medida (opcional)
        :type point_type: Optional[Union[int, float, str]]
        :param authorized_nif: NIF autorizado para obtener datos de consumo
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de consumo validados y errores de distribuidora
        :rtype: ConsumptionResponse
        :raises ValidationError: Si las fechas no están en formato mensual válido
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
        Obtiene datos de potencia máxima validados con Pydantic.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param date_from: Fecha de inicio (YYYY/MM)
        :type date_from: str
        :param date_to: Fecha de fin (YYYY/MM)
        :type date_to: str
        :param authorized_nif: NIF autorizado para obtener potencia máxima
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de potencia máxima validados y errores de distribuidora
        :rtype: MaxPowerResponse
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
        Obtiene datos de energía reactiva validados con Pydantic.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param date_from: Fecha de inicio (YYYY/MM)
        :type date_from: str
        :param date_to: Fecha de fin (YYYY/MM)
        :type date_to: str
        :param authorized_nif: NIF autorizado para obtener datos de energía reactiva
        :type authorized_nif: Optional[str]
        :return: Lista de objetos ReactiveData validados
        :rtype: List[ReactiveData]
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
        """Cierra la sesión."""
        if self.session:
            self.session.close()
        self.token = None

    def __enter__(self):
        """
        Context manager entry.

        :return: Instancia del cliente
        :rtype: SimpleDatadisClientV2
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.

        :param exc_type: Tipo de excepción
        :type exc_type: Optional[type]
        :param exc_val: Valor de la excepción
        :type exc_val: Optional[BaseException]
        :param exc_tb: Traceback de la excepción
        :type exc_tb: Optional[TracebackType]
        """
        self.close()
