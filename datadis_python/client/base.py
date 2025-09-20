"""
Cliente base para Datadis con funcionalidad común.

Este módulo define una clase abstracta que sirve como base para los clientes de Datadis.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from ..exceptions import APIError, AuthenticationError, DatadisError
from ..utils.constants import (
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    TOKEN_EXPIRY_HOURS,
)
from ..utils.http import HTTPClient


class BaseDatadisClient(ABC):
    """
    Cliente base abstracto con funcionalidad común para todas las versiones.

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
        Inicializa el cliente base.

        :param username: NIF del usuario registrado en Datadis.
        :param password: Contraseña de acceso a Datadis.
        :param timeout: Timeout para requests en segundos.
        :param retries: Número de reintentos automáticos.
        """
        self.username = username
        self.password = password
        self.base_url = DATADIS_BASE_URL
        self.api_base = DATADIS_API_BASE

        # Cliente HTTP reutilizable
        self.http_client = HTTPClient(timeout=timeout, retries=retries)

        # Estado de autenticación
        self.token: Optional[str] = None
        self.token_expiry: Optional[float] = None

    def authenticate(self) -> None:
        """
        Autentica con la API y obtiene token de acceso.

        :raises AuthenticationError: Si las credenciales son inválidas
        :raises APIError: Si ocurre un error en la comunicación con la API
        """
        login_data = {"username": self.username, "password": self.password}

        try:
            # Headers específicos para autenticación
            auth_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "datadis-python-sdk/0.1.0",
            }

            # La API de Datadis requiere form data, no JSON
            token = self.http_client.make_request(
                method="POST",
                url=f"{self.base_url}{AUTH_ENDPOINTS['login']}",
                data=login_data,
                headers=auth_headers,
                use_form_data=True,
            )

            # La respuesta es directamente el token JWT como texto
            if isinstance(token, str) and token:
                self.token = token
                self.http_client.set_auth_header(self.token)
                # Asumir que el token expira en las horas configuradas
                self.token_expiry = time.time() + (TOKEN_EXPIRY_HOURS * 3600)
            else:
                raise AuthenticationError("No se recibió token válido en la respuesta")

        except APIError as e:
            if e.status_code == 401 or e.status_code == 500:
                raise AuthenticationError("Credenciales inválidas")
            raise

    def ensure_authenticated(self) -> None:
        """
        Asegura que el cliente está autenticado con un token válido.

        Renueva automáticamente el token si ha expirado o está próximo a expirar.
        """
        if not self.token or (
            self.token_expiry and time.time() >= self.token_expiry - 300
        ):  # Renovar 5 min antes
            self.authenticate()

    def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], str, list]:
        """
        Realiza una petición autenticada a la API.

        :param method: Método HTTP (GET, POST)
        :type method: str
        :param endpoint: Endpoint de la API
        :type endpoint: str
        :param data: Datos para el body de la petición
        :type data: Optional[Dict[str, Any]]
        :param params: Parámetros de query string
        :type params: Optional[Dict[str, Any]]
        :return: Respuesta de la API
        :rtype: Union[Dict[str, Any], str, list]
        :raises AuthenticationError: Si fallan las credenciales
        :raises APIError: Si ocurre un error en la API
        """
        self.ensure_authenticated()

        # Construir URL completa
        if endpoint.startswith("/nikola-auth"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.api_base}{endpoint}"

        try:
            return self.http_client.make_request(
                method=method, url=url, data=data, params=params
            )
        except AuthenticationError:
            # Token expirado, intentar renovar una vez
            self.token = None
            self.ensure_authenticated()
            return self.http_client.make_request(
                method=method, url=url, data=data, params=params
            )

    def close(self) -> None:
        """
        Cierra la sesión y libera recursos.

        Limpia el token de autenticación y cierra las conexiones HTTP.
        """
        if self.http_client:
            self.http_client.close()
        self.token = None
        self.token_expiry = None

    def __enter__(self):
        """
        Entrada del context manager.

        :return: Instancia del cliente
        :rtype: BaseDatadisClient
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Salida del context manager.

        :param exc_type: Tipo de excepción
        :type exc_type: Optional[type]
        :param exc_val: Valor de la excepción
        :type exc_val: Optional[BaseException]
        :param exc_tb: Traceback de la excepción
        :type exc_tb: Optional[TracebackType]
        """
        self.close()

    # Métodos abstractos que deben implementar las versiones específicas

    @abstractmethod
    def get_supplies(
        self,
        authorized_nif: Optional[str] = None,
        distributor_code: Optional[str] = None,
    ) -> Any:
        """
        Obtiene puntos de suministro.

        :param authorized_nif: NIF autorizado para la consulta
        :type authorized_nif: Optional[str]
        :param distributor_code: Código de la distribuidora
        :type distributor_code: Optional[str]
        :return: Lista de puntos de suministro
        :rtype: Any
        """
        pass

    @abstractmethod
    def get_distributors(self, authorized_nif: Optional[str] = None) -> Any:
        """
        Obtiene distribuidores.

        :param authorized_nif: NIF autorizado para la consulta
        :type authorized_nif: Optional[str]
        :return: Lista de distribuidores
        :rtype: Any
        """
        pass

    @abstractmethod
    def get_contract_detail(
        self, cups: str, distributor_code: str, authorized_nif: Optional[str] = None
    ) -> Any:
        """
        Obtiene detalle del contrato.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param authorized_nif: NIF autorizado para la consulta
        :type authorized_nif: Optional[str]
        :return: Detalle del contrato
        :rtype: Any
        """
        pass

    @abstractmethod
    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
        authorized_nif: Optional[str] = None,
    ) -> Any:
        """
        Obtiene datos de consumo.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param date_from: Fecha de inicio (YYYY-MM-DD)
        :type date_from: str
        :param date_to: Fecha de fin (YYYY-MM-DD)
        :type date_to: str
        :param measurement_type: Tipo de medida
        :type measurement_type: int
        :param point_type: Tipo de punto
        :type point_type: Optional[int]
        :param authorized_nif: NIF autorizado para la consulta
        :type authorized_nif: Optional[str]
        :return: Datos de consumo
        :rtype: Any
        """
        pass

    @abstractmethod
    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> Any:
        """
        Obtiene datos de potencia máxima.

        :param cups: Código CUPS del punto de suministro
        :type cups: str
        :param distributor_code: Código de la distribuidora
        :type distributor_code: str
        :param date_from: Fecha de inicio (YYYY-MM-DD)
        :type date_from: str
        :param date_to: Fecha de fin (YYYY-MM-DD)
        :type date_to: str
        :param authorized_nif: NIF autorizado para la consulta
        :type authorized_nif: Optional[str]
        :return: Datos de potencia máxima
        :rtype: Any
        """
        pass
