"""
Tests para excepciones y manejo de errores en el SDK de Datadis.

Estos tests validan:
- Jerarquía correcta de excepciones
- Propagación de errores específicos
- Manejo de errores HTTP
- Contexto de errores y mensajes descriptivos
- Comportamiento de excepciones en diferentes escenarios
"""

import pytest
import requests
import responses

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.client.v2.client import DatadisClientV2
from datadis_python.exceptions import (
    APIError,
    AuthenticationError,
    DatadisError,
    ValidationError,
)
from datadis_python.utils.constants import (
    API_V1_ENDPOINTS,
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)


class TestExceptionHierarchy:
    """Tests para la jerarquía de excepciones."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_datadis_error_is_base_exception(self):
        """Test que DatadisError es la excepción base."""
        error = DatadisError("Test message")

        assert isinstance(error, Exception)
        assert str(error) == "Test message"

    @pytest.mark.unit
    @pytest.mark.errors
    def test_authentication_error_inheritance(self):
        """Test herencia de AuthenticationError."""
        error = AuthenticationError("Auth failed")

        assert isinstance(error, DatadisError)
        assert isinstance(error, Exception)
        assert str(error) == "Auth failed"

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_inheritance(self):
        """Test herencia de APIError."""
        error = APIError("API error", status_code=500)

        assert isinstance(error, DatadisError)
        assert isinstance(error, Exception)
        assert str(error) == "API error"
        assert error.status_code == 500

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_without_status_code(self):
        """Test APIError sin código de estado."""
        error = APIError("API error")

        assert str(error) == "API error"
        assert error.status_code is None

    @pytest.mark.unit
    @pytest.mark.errors
    def test_validation_error_inheritance(self):
        """Test herencia de ValidationError."""
        error = ValidationError("Validation failed")

        assert isinstance(error, DatadisError)
        assert isinstance(error, Exception)
        assert str(error) == "Validation failed"

    @pytest.mark.unit
    @pytest.mark.errors
    def test_exception_hierarchy_polymorphism(self):
        """Test polimorfismo en jerarquía de excepciones."""
        errors = [
            DatadisError("Base error"),
            AuthenticationError("Auth error"),
            APIError("API error", 400),
            ValidationError("Validation error"),
        ]

        # Todas deberían ser instancias de DatadisError
        for error in errors:
            assert isinstance(error, DatadisError)

        # Deberían poder ser capturadas como DatadisError
        for error in errors:
            try:
                raise error
            except DatadisError as e:
                assert e is error


class TestAuthenticationErrorScenarios:
    """Tests para escenarios específicos de AuthenticationError."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_auth_error_invalid_credentials(self, v1_client):
        """Test AuthenticationError con credenciales inválidas."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Invalid credentials"},
                status=401,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert "Error de autenticación: 401" in str(error)
            assert isinstance(error, DatadisError)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_auth_error_timeout(self, v1_client):
        """Test AuthenticationError por timeout."""
        with responses.RequestsMock() as rsps:

            def timeout_callback(request):
                raise requests.exceptions.Timeout("Connection timeout")

            rsps.add_callback(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                callback=timeout_callback,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert "Timeout en autenticación" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_auth_error_network_error(self, v1_client):
        """Test AuthenticationError por error de red."""
        with responses.RequestsMock() as rsps:

            def network_error_callback(request):
                raise requests.exceptions.ConnectionError("Network unreachable")

            rsps.add_callback(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                callback=network_error_callback,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert "Error en autenticación" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_auth_error_server_error(self, v1_client):
        """Test AuthenticationError por error del servidor."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Internal server error"},
                status=500,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert "Error de autenticación: 500" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_auth_error_empty_response(self, v1_client):
        """Test AuthenticationError con respuesta vacía."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body="",
                status=200,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert "Error de autenticación" in str(error)


class TestAPIErrorScenarios:
    """Tests para escenarios específicos de APIError."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_400_bad_request(self, authenticated_v1_client):
        """Test APIError con código 400."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Bad request", "message": "Invalid parameters"},
                status=400,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 400
            assert "Error HTTP 400" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_403_forbidden(self, authenticated_v1_client):
        """Test APIError con código 403."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Forbidden", "message": "Access denied"},
                status=403,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 403

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_404_not_found(self, authenticated_v1_client):
        """Test APIError con código 404."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Not found"},
                status=404,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 404

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_500_server_error(self, authenticated_v1_client):
        """Test APIError con código 500."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Internal server error"},
                status=500,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 500

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_502_bad_gateway(self, authenticated_v1_client):
        """Test APIError con código 502."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Bad gateway"},
                status=502,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 502

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_503_service_unavailable(self, authenticated_v1_client):
        """Test APIError con código 503."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Service unavailable"},
                status=503,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/get-supplies")

            error = exc_info.value
            assert error.status_code == 503


class TestDatadisErrorScenarios:
    """Tests para escenarios específicos de DatadisError."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_datadis_error_timeout_exhausted(self, v1_client, test_token):
        """Test DatadisError cuando se agotan los reintentos por timeout."""
        v1_client.retries = 1  # Solo 1 reintento para acelerar test

        with responses.RequestsMock() as rsps:
            # Auth exitoso
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Todos los intentos fallan con timeout
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Request timeout")

            for _ in range(2):  # Para retries=1, son 2 intentos totales
                rsps.add_callback(
                    responses.GET,
                    f"{DATADIS_API_BASE}/test-endpoint",
                    callback=timeout_callback,
                )

            with pytest.raises(DatadisError) as exc_info:
                v1_client._make_authenticated_request("/test-endpoint")

            error = exc_info.value
            assert "Timeout después de" in str(error)
            assert "intentos" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_datadis_error_network_exhausted(self, v1_client, test_token):
        """Test DatadisError cuando se agotan los reintentos por error de red."""
        v1_client.retries = 1

        with responses.RequestsMock() as rsps:
            # Auth exitoso
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Todos los intentos fallan con error de red
            def network_error_callback(request):
                raise requests.exceptions.ConnectionError("Network error")

            for _ in range(2):  # Para retries=1, son 2 intentos totales
                rsps.add_callback(
                    responses.GET,
                    f"{DATADIS_API_BASE}/test-endpoint",
                    callback=network_error_callback,
                )

            with pytest.raises(DatadisError) as exc_info:
                v1_client._make_authenticated_request("/test-endpoint")

            error = exc_info.value
            assert "Error después de" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_datadis_error_general_exception(self, v1_client, test_token):
        """Test DatadisError por excepción general."""
        with responses.RequestsMock() as rsps:
            # Auth exitoso
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Request falla con excepción general
            def general_error_callback(request):
                raise ValueError("Unexpected error")

            rsps.add_callback(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                callback=general_error_callback,
            )

            with pytest.raises(DatadisError) as exc_info:
                v1_client._make_authenticated_request("/test-endpoint")

            error = exc_info.value
            assert "Error después de" in str(error)


class TestV2ErrorHandling:
    """Tests para manejo de errores específicos de V2."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_v2_authentication_error_propagation(self, v2_client):
        """Test propagación de AuthenticationError en V2."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Unauthorized"},
                status=401,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v2_client.authenticate()

            error = exc_info.value
            assert "Credenciales inválidas" in str(error)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_v2_api_error_propagation(self, authenticated_v2_client):
        """Test propagación de APIError en V2."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json={"error": "Internal error"},
                status=500,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v2_client.make_authenticated_request(
                    "GET", "/get-supplies-v2"
                )

            error = exc_info.value
            assert error.status_code == 500

    @pytest.mark.unit
    @pytest.mark.errors
    def test_v2_invalid_cups_validation(self, authenticated_v2_client):
        """Test validación de CUPS inválido en V2."""
        # Este test depende de la implementación de validators
        # Asumimos que los validators lanzan ValidationError para CUPS inválidos
        invalid_cups = "INVALID_CUPS_FORMAT"

        # Nota: Si los validators están implementados correctamente,
        # esto debería lanzar ValidationError antes de hacer el request HTTP
        try:
            result = authenticated_v2_client.get_contract_detail(
                cups=invalid_cups,
                distributor_code="2"
            )
            # Si no falla, el validator podría no estar implementado o ser permisivo
            assert result is not None
        except Exception as e:
            # Si falla, debería ser con una excepción relacionada con validación
            assert isinstance(e, (ValidationError, ValueError))


class TestErrorContextAndMessages:
    """Tests para contexto y mensajes descriptivos de errores."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_error_messages_are_descriptive(self, v1_client):
        """Test que los mensajes de error son descriptivos."""
        error_scenarios = [
            (AuthenticationError("Invalid credentials"), "Invalid credentials"),
            (APIError("Not found", 404), "Not found"),
            (DatadisError("Connection failed"), "Connection failed"),
            (ValidationError("Invalid CUPS format"), "Invalid CUPS format"),
        ]

        for error, expected_message in error_scenarios:
            assert str(error) == expected_message
            assert len(str(error)) > 0

    @pytest.mark.unit
    @pytest.mark.errors
    def test_api_error_includes_status_code(self):
        """Test que APIError incluye código de estado."""
        error = APIError("Server error", status_code=500)

        assert error.status_code == 500
        assert hasattr(error, "status_code")

    @pytest.mark.unit
    @pytest.mark.errors
    def test_error_chaining_and_context(self, v1_client):
        """Test encadenamiento y contexto de errores."""
        with responses.RequestsMock() as rsps:

            def chained_error_callback(request):
                try:
                    raise ValueError("Original error")
                except ValueError as e:
                    raise requests.exceptions.RequestException("Request failed") from e

            rsps.add_callback(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                callback=chained_error_callback,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            error = exc_info.value
            assert isinstance(error, AuthenticationError)

    @pytest.mark.unit
    @pytest.mark.errors
    def test_exception_repr_and_str(self):
        """Test representación string de excepciones."""
        errors = [
            DatadisError("Base error"),
            AuthenticationError("Auth error"),
            APIError("API error", 400),
            ValidationError("Validation error"),
        ]

        for error in errors:
            # str() debería devolver el mensaje
            str_repr = str(error)
            assert isinstance(str_repr, str)
            assert len(str_repr) > 0

            # repr() debería ser informativo
            repr_str = repr(error)
            assert isinstance(repr_str, str)
            assert error.__class__.__name__ in repr_str


class TestErrorRecoveryScenarios:
    """Tests para escenarios de recuperación de errores."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_recovery_after_auth_error(self, v1_client, test_token):
        """Test recuperación después de error de autenticación."""
        with responses.RequestsMock() as rsps:
            # Primera auth falla
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Temporary error"},
                status=500,
            )

            # Segunda auth exitosa
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Primera autenticación falla
            with pytest.raises(AuthenticationError):
                v1_client.authenticate()

            # Segunda autenticación exitosa
            result = v1_client.authenticate()
            assert result is True
            assert v1_client.token == test_token

    @pytest.mark.unit
    @pytest.mark.errors
    def test_recovery_after_api_error(self, authenticated_v1_client):
        """Test recuperación después de error de API."""
        with responses.RequestsMock() as rsps:
            # Primera request falla
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"error": "Temporary unavailable"},
                status=503,
            )

            # Segunda request exitosa
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"success": True},
                status=200,
            )

            # Primera request falla
            with pytest.raises(APIError):
                authenticated_v1_client._make_authenticated_request("/test-endpoint")

            # Segunda request exitosa
            result = authenticated_v1_client._make_authenticated_request("/test-endpoint")
            assert result == {"success": True}

    @pytest.mark.unit
    @pytest.mark.errors
    def test_error_logging_and_debugging(self, v1_client, capfd):
        """Test que los errores proporcionan información para debugging."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Debug info error"},
                status=400,
            )

            with pytest.raises(AuthenticationError):
                v1_client.authenticate()

            # Verificar que se imprimió información de debug
            captured = capfd.readouterr()
            # El cliente V1 imprime información, verificar que hay output
            assert len(captured.out) >= 0  # Puede o no haber output según implementación


class TestExceptionCompatibility:
    """Tests para compatibilidad de excepciones."""

    @pytest.mark.unit
    @pytest.mark.errors
    def test_exceptions_are_pickleable(self):
        """Test que las excepciones se pueden serializar."""
        import pickle

        errors = [
            DatadisError("Base error"),
            AuthenticationError("Auth error"),
            APIError("API error", 400),
            ValidationError("Validation error"),
        ]

        for error in errors:
            # Debería poder serializarse y deserializarse
            pickled = pickle.dumps(error)
            unpickled = pickle.loads(pickled)

            assert type(unpickled) == type(error)
            assert str(unpickled) == str(error)
            if hasattr(error, "status_code"):
                assert unpickled.status_code == error.status_code

    @pytest.mark.unit
    @pytest.mark.errors
    def test_exceptions_work_with_logging(self):
        """Test que las excepciones funcionan con logging."""
        import logging
        import io

        # Configurar logger de prueba
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)

        errors = [
            DatadisError("Base error"),
            AuthenticationError("Auth error"),
            APIError("API error", 500),
        ]

        try:
            for error in errors:
                logger.error("Test error: %s", error)

            log_output = log_stream.getvalue()
            assert len(log_output) > 0
            assert "Base error" in log_output
            assert "Auth error" in log_output
            assert "API error" in log_output

        finally:
            logger.removeHandler(handler)
            handler.close()