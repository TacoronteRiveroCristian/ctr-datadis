"""
Cliente actualizado para la API de Datadis (versión corregida).

Este módulo proporciona un cliente para interactuar con la API de Datadis.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests

from ..exceptions import APIError, AuthenticationError, DatadisError
from ..models import (
    ConsumptionData,
    ConsumptionResponse,
    ContractData,
    ContractResponse,
    DistributorsResponse,
    MaxPowerData,
    MaxPowerResponse,
    SuppliesResponse,
    SupplyData,
)
from ..utils.constants import (
    API_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
)
from ..utils.validators import (
    validate_date_range,
    validate_distributor_code,
    validate_measurement_type,
    validate_point_type,
)


class DatadisClient:
    """
    Cliente actualizado para interactuar con la API de Datadis.

    :param username: NIF del usuario registrado en Datadis.
    :type username: str
    :param password: Contraseña de acceso a Datadis.
    :type password: str
    :param timeout: Timeout para requests en segundos.
    :type timeout: int
    :param retries: Número de reintentos automáticos.
    :type retries: int
    """

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = MAX_RETRIES,
    ):
        """
        Inicializa el cliente.

        :param username: NIF del usuario registrado en Datadis.
        :param password: Contraseña de acceso a Datadis.
        :param timeout: Timeout para requests en segundos.
        :param retries: Número de reintentos automáticos.
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.base_url = DATADIS_BASE_URL
        self.api_base = DATADIS_API_BASE
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.token_expiry: Optional[float] = None

        # Headers por defecto
        self.session.headers.update(
            {
                "User-Agent": "datadis-python-sdk/0.1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = True,
        use_form_data: bool = False,
    ) -> Union[Dict[str, Any], str]:
        """
        Realiza una petición HTTP a la API.

        :param method: Método HTTP (GET, POST)
        :param endpoint: Endpoint de la API
        :param data: Datos para el body de la petición
        :param params: Parámetros de query string
        :param authenticated: Si requiere autenticación
        :param use_form_data: Si usar form data en lugar de JSON

        :return: Respuesta JSON de la API o texto plano
        """
        if authenticated:
            self._ensure_authenticated()

        # Usar URL base apropiada según el endpoint
        if endpoint.startswith("/nikola-auth"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.api_base}{endpoint}"

        # Agregar delay entre peticiones para evitar rate limiting
        # (excepto para autenticación)
        if not endpoint.startswith("/nikola-auth"):
            time.sleep(0.5)  # 500ms entre peticiones normales

        # Reintentos automáticos
        for attempt in range(self.retries + 1):
            try:
                # Configurar la petición según el tipo de datos
                if use_form_data and data:
                    # Para autenticación usar form data con headers específicos
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                        "User-Agent": "datadis-python-sdk/0.1.0",
                    }
                    response = requests.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                    )
                else:
                    # Para peticiones normales usar la sesión con JSON
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        params=params,
                        timeout=self.timeout,
                    )

                # Manejar respuestas de la API
                if response.status_code == 200:
                    # Para autenticación, la respuesta es texto plano (JWT)
                    if endpoint.startswith("/nikola-auth"):
                        return response.text.strip()

                    # Para otras peticiones, esperamos JSON
                    try:
                        return response.json()
                    except ValueError:
                        # Si no es JSON válido, devolver como texto
                        return response.text

                elif response.status_code == 401:
                    # Token expirado, intentar renovar
                    self.token = None
                    if authenticated:
                        self._authenticate()
                        continue
                    else:
                        raise AuthenticationError("Credenciales inválidas")
                elif response.status_code == 429:
                    # Rate limiting - esperar más tiempo progresivamente
                    if attempt < self.retries:
                        wait_time = min(30, (2**attempt) * 2)  # Máximo 30 segundos
                        print(
                            f"Rate limit alcanzado. Esperando {wait_time} segundos..."
                        )
                        time.sleep(wait_time)
                        continue
                    raise APIError(
                        "Límite de peticiones excedido después de varios reintentos",
                        429,
                    )
                else:
                    # Otros errores HTTP
                    error_msg = f"Error HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_msg = error_data["message"]
                        elif "error" in error_data:
                            error_msg = error_data["error"]
                    except ValueError:
                        # Si no es JSON, usar el texto de la respuesta
                        if response.text:
                            error_msg = response.text

                    raise APIError(error_msg, response.status_code)

            except requests.RequestException as e:
                if attempt == self.retries:
                    raise DatadisError(f"Error de conexión: {str(e)}")
                time.sleep(1)

        # Este punto nunca debería alcanzarse, pero MyPy requiere retorno explícito
        raise DatadisError("Error inesperado: se agotaron todos los reintentos")

    def _authenticate(self) -> None:
        """Autentica con la API y obtiene token de acceso."""
        login_data = {"username": self.username, "password": self.password}

        try:
            # La API de Datadis requiere form data, no JSON
            token = self._make_request(
                "POST",
                API_ENDPOINTS["login"],
                data=login_data,
                authenticated=False,
                use_form_data=True,
            )

            # La respuesta es directamente el token JWT como texto
            if isinstance(token, str) and token:
                self.token = token
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                # Asumir que el token expira en 24 horas (valor típico para JWT)
                self.token_expiry = time.time() + (24 * 3600)
            else:
                raise AuthenticationError("No se recibió token válido en la respuesta")

        except APIError as e:
            if e.status_code == 401 or e.status_code == 500:
                raise AuthenticationError("Credenciales inválidas")
            raise

    def _ensure_authenticated(self) -> None:
        """Asegura que el cliente está autenticado con un token válido."""
        if not self.token or (
            self.token_expiry and time.time() >= self.token_expiry - 300
        ):  # Renovar 5 min antes
            self._authenticate()

    def get_distributors(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de distribuidores disponibles usando API v1.

        :return: Lista de distribuidores (raw response de la API)
        """
        response = self._make_request("GET", API_ENDPOINTS["distributors"])

        # Devolver la respuesta directa de la API v1
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return [response] if response else []

        return []

    def get_supplies(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de puntos de suministro disponibles usando API v1.

        :return: Lista de datos de suministros (raw response de la API)
        """
        response = self._make_request("GET", API_ENDPOINTS["supplies"])

        # Devolver la respuesta directa de la API v1
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "supplies" in response:
            return response["supplies"]

        return []

    def get_contract_detail(self, cups: str, distributor_code: str) -> Dict[str, Any]:
        """Obtiene el detalle del contrato para un CUPS específico usando API v1.

        :param cups: Código CUPS del punto de suministro
        :param distributor_code: Código del distribuidor

        :return: Datos del contrato (raw response de la API)
        """
        params = {"cups": cups, "distributorCode": distributor_code}

        response = self._make_request("GET", API_ENDPOINTS["contracts"], params=params)

        # Devolver la respuesta directa de la API v1
        return response if isinstance(response, dict) else {}

    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene datos de consumo para un CUPS y rango de fechas usando API v1.

        :param cups: Código CUPS del punto de suministro
        :param distributor_code: Código del distribuidor
        :param date_from: Fecha inicial (YYYY/MM)
        :param date_to: Fecha final (YYYY/MM)
        :param measurement_type: Tipo de medida (0=hora, 1=cuarto hora)
        :param point_type: Tipo de punto (obtenido de supplies)

        :return: Lista de datos de consumo (raw response de la API)
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type),
        }

        if point_type is not None:
            params["pointType"] = str(point_type)

        response = self._make_request(
            "GET", API_ENDPOINTS["consumption"], params=params
        )

        # Devolver la respuesta directa de la API v1
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "timeCurve" in response:
            return response["timeCurve"]

        return []

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List[Dict[str, Any]]:
        """Obtiene datos de potencia máxima para un CUPS y rango de fechas usando API v1.

        :param cups: Código CUPS del punto de suministro
        :param distributor_code: Código del distribuidor
        :param date_from: Fecha inicial (YYYY/MM)
        :param date_to: Fecha final (YYYY/MM)

        :return: Lista de datos de potencia máxima (raw response de la API)
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }

        response = self._make_request("GET", API_ENDPOINTS["max_power"], params=params)

        # Devolver la respuesta directa de la API v1
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "maxPower" in response:
            return response["maxPower"]

        return []

    def close(self) -> None:
        """Cierra la sesión y libera recursos."""
        if self.session:
            self.session.close()
        self.token = None
        self.token_expiry = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
