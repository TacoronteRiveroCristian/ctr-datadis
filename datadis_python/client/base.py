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
        self.token = None
        self.token_expiry = None

    def authenticate(self) -> None:
        """
        Autentica con la API y obtiene token de acceso
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
        Asegura que el cliente está autenticado con un token válido
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
        Realiza una petición autenticada a la API

        :param method: Método HTTP (GET, POST)
        :param endpoint: Endpoint de la API
        :param data: Datos para el body de la petición
        :param params: Parámetros de query string

        :return: Respuesta de la API
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
        Cierra la sesión y libera recursos
        """
        if self.http_client:
            self.http_client.close()
        self.token = None
        self.token_expiry = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    # Métodos abstractos que deben implementar las versiones específicas

    @abstractmethod
    def get_supplies(self, **kwargs):
        """Obtiene puntos de suministro"""
        pass

    @abstractmethod
    def get_distributors(self, **kwargs):
        """Obtiene distribuidores"""
        pass

    @abstractmethod
    def get_contract_detail(self, cups: str, distributor_code: str, **kwargs):
        """Obtiene detalle del contrato"""
        pass

    @abstractmethod
    def get_consumption(
        self, cups: str, distributor_code: str, date_from: str, date_to: str, **kwargs
    ):
        """Obtiene datos de consumo"""
        pass

    @abstractmethod
    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str, **kwargs
    ):
        """Obtiene datos de potencia máxima"""
        pass
