"""
Utilidades HTTP comunes para clientes Datadis.

Este módulo proporciona una clase HTTPClient para realizar solicitudes HTTP con funcionalidades comunes.
"""

import time
from typing import Any, Dict, Optional, Union

import requests

from ..exceptions import APIError, AuthenticationError, DatadisError


class HTTPClient:
    """
    Cliente HTTP base con funcionalidades comunes.

    :param timeout: Timeout para requests en segundos.
    :type timeout: int
    :param retries: Número de reintentos automáticos.
    :type retries: int
    """

    def __init__(self, timeout: int = 60, retries: int = 3):
        """
        Inicializa el cliente HTTP.

        :param timeout: Timeout para requests en segundos.
        :type timeout: int
        :param retries: Número de reintentos automáticos.
        :type retries: int
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

        # Headers por defecto
        self.session.headers.update(
            {
                "User-Agent": "datadis-python-sdk/0.1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_form_data: bool = False,
    ) -> Union[Dict[str, Any], str, list]:
        """
        Realiza una petición HTTP con reintentos automáticos.

        :param method: Método HTTP (GET, POST, etc.).
        :type method: str
        :param url: URL de la solicitud.
        :type url: str
        :param data: Datos a enviar en el cuerpo de la solicitud (opcional).
        :type data: dict, opcional
        :param params: Parámetros de consulta para la URL (opcional).
        :type params: dict, opcional
        :param headers: Encabezados HTTP adicionales (opcional).
        :type headers: dict, opcional
        :param use_form_data: Indica si se deben enviar los datos como formulario.
        :type use_form_data: bool
        :return: Respuesta de la solicitud HTTP.
        :rtype: dict, str o list
        """
        # Delay para evitar rate limiting (excepto para auth)
        if "/nikola-auth" not in url:
            time.sleep(0.1)  # Reducir delay de 0.5s a 0.1s

        # Reintentos automáticos
        for attempt in range(self.retries + 1):
            try:
                # Configurar headers específicos si se necesitan
                if headers:
                    request_headers = {**self.session.headers, **headers}
                else:
                    request_headers = dict(self.session.headers)

                # Configurar la petición según el tipo de datos
                if use_form_data and data:
                    # Para autenticación usar form data
                    response = requests.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        headers=request_headers,
                        timeout=self.timeout,
                    )
                else:
                    # Para peticiones normales usar JSON
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        params=params,
                        timeout=self.timeout,
                    )

                return self._handle_response(response, url)

            except requests.RequestException as e:
                if attempt == self.retries:
                    raise DatadisError(f"Error de conexión: {str(e)}")
                # Esperar más tiempo antes del siguiente intento
                wait_time = min(10, (2**attempt) * 2)  # Backoff exponencial
                print(
                    f"Reintento {attempt + 1}/{self.retries + 1} después de {wait_time}s..."
                )
                time.sleep(wait_time)

        # Este punto nunca debería alcanzarse, pero MyPy requiere retorno explícito
        raise DatadisError("Error inesperado: se agotaron todos los reintentos")

    def _handle_response(
        self, response: requests.Response, url: str
    ) -> Union[Dict[str, Any], str, list]:
        """
        Maneja la respuesta HTTP.

        :param response: Respuesta HTTP
        :type response: requests.Response
        :param url: URL de la petición
        :type url: str
        :return: Respuesta procesada
        :rtype: Union[Dict[str, Any], str, list]
        :raises AuthenticationError: Si las credenciales son inválidas
        :raises APIError: Si hay errores en la API
        """
        if response.status_code == 200:
            # Para autenticación, la respuesta es texto plano (JWT)
            if "/nikola-auth" in url:
                return response.text.strip()

            # Para otras peticiones, esperamos JSON
            try:
                json_response = response.json()
                # Normalizar texto para evitar problemas de caracteres especiales
                from ..utils.text_utils import normalize_api_response

                return normalize_api_response(json_response)
            except ValueError:
                # Si no es JSON válido, devolver como texto
                return response.text

        elif response.status_code == 401:
            raise AuthenticationError("Credenciales inválidas o token expirado")
        elif response.status_code == 429:
            raise APIError("Límite de peticiones excedido", 429)
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

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        if self.session:
            self.session.close()

    def set_auth_header(self, token: str) -> None:
        """
        Establece el header de autorización.

        :param token: Token de autorización
        :type token: str
        """
        self.session.headers["Authorization"] = f"Bearer {token}"

    def remove_auth_header(self) -> None:
        """Remueve el header de autorización."""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
