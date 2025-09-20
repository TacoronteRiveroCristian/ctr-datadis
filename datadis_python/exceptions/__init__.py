"""
Excepciones personalizadas para el SDK de Datadis.

:author: TacoronteRiveroCristian
"""


class DatadisError(Exception):
    """
    Base exception for Datadis SDK.

    Esta es la excepción base de la cual heredan todas las demás excepciones del SDK.
    """

    pass


class AuthenticationError(DatadisError):
    """
    Authentication related errors.

    Se lanza cuando hay problemas con la autenticación del usuario.
    """

    pass


class APIError(DatadisError):
    """
    API response errors.

    Se lanza cuando la API de Datadis devuelve errores HTTP.

    :param message: Mensaje de error
    :type message: str
    :param status_code: Código de estado HTTP (opcional)
    :type status_code: int
    """

    def __init__(self, message: str, status_code: int = None):
        """
        Inicializa una excepción de error de API.

        :param message: Mensaje de error
        :type message: str
        :param status_code: Código de estado HTTP (opcional)
        :type status_code: int
        """
        super().__init__(message)
        self.status_code = status_code


class ValidationError(DatadisError):
    """
    Parameter validation errors.

    Se lanza cuando los parámetros proporcionados no son válidos.
    """

    pass


__all__ = ["DatadisError", "AuthenticationError", "APIError", "ValidationError"]
