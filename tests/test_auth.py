"""
Tests para autenticación y manejo de sesiones en el SDK de Datadis.

Estos tests validan:
- Autenticación exitosa y fallida
- Manejo de tokens y expiración
- Renovación automática de tokens
- Context manager support
- Timeout y reintentos en autenticación
"""

import time
from unittest.mock import Mock, patch

import pytest
import requests
import responses
from freezegun import freeze_time

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.client.v2.client import DatadisClientV2
from datadis_python.exceptions import AuthenticationError, APIError, DatadisError
from datadis_python.utils.constants import (
    AUTH_ENDPOINTS,
    DATADIS_BASE_URL,
    TOKEN_EXPIRY_HOURS,
)


class TestV1Authentication:
    """Tests de autenticación para cliente V1."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_successful_authentication(self, v1_client, mock_auth_success, test_token):
        """Test autenticación exitosa."""
        result = v1_client.authenticate()

        assert result is True
        assert v1_client.token == test_token
        assert v1_client.session.headers["Authorization"] == f"Bearer {test_token}"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_failure_401(self, v1_client):
        """Test fallo de autenticación con credenciales inválidas."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Invalid credentials"},
                status=401,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            assert "Error de autenticación: 401" in str(exc_info.value)
            assert v1_client.token is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_failure_500(self, v1_client):
        """Test fallo de autenticación con error del servidor."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Server error"},
                status=500,
            )

            with pytest.raises(AuthenticationError):
                v1_client.authenticate()

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_timeout(self, v1_client):
        """Test timeout en autenticación."""
        with responses.RequestsMock() as rsps:
            # Simular timeout
            def request_callback(request):
                raise requests.exceptions.Timeout("Request timed out")

            rsps.add_callback(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                callback=request_callback,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            assert "Timeout en autenticación" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_network_error(self, v1_client):
        """Test error de red en autenticación."""
        with responses.RequestsMock() as rsps:

            def request_callback(request):
                raise requests.exceptions.ConnectionError("Network error")

            rsps.add_callback(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                callback=request_callback,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            assert "Error en autenticación" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_empty_response(self, v1_client):
        """Test respuesta vacía en autenticación."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body="",  # Respuesta vacía
                status=200,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                v1_client.authenticate()

            assert "Error de autenticación" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.auth
    def test_token_renewal_on_401(self, v1_client, test_token):
        """Test renovación automática de token en error 401."""
        with responses.RequestsMock() as rsps:
            # Autenticación inicial exitosa
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Primera request falla con 401
            rsps.add(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies",
                json={"error": "Unauthorized"},
                status=401,
            )

            # Segunda autenticación exitosa
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_renewed",
                status=200,
            )

            # Segunda request exitosa después de renovar token
            rsps.add(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies",
                json=[],
                status=200,
            )

            # Autenticar inicialmente
            v1_client.authenticate()
            original_token = v1_client.token

            # Hacer request que triggera renovación
            result = v1_client._make_authenticated_request("/get-supplies")

            # Verificar que el token se renovó
            assert v1_client.token != original_token
            assert v1_client.token == f"{test_token}_renewed"
            assert result == []

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_retry_mechanism(self, v1_client, test_token):
        """Test mecanismo de reintentos en requests autenticados."""
        with responses.RequestsMock() as rsps:
            # Autenticación exitosa
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Primera request falla con timeout
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Request timed out")

            rsps.add_callback(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies",
                callback=timeout_callback,
            )

            # Segunda request falla con timeout (supera límite de reintentos de 1)
            rsps.add_callback(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies",
                callback=timeout_callback,
            )

            v1_client.authenticate()

            # Debería fallar después de agotar reintentos
            with pytest.raises(DatadisError) as exc_info:
                v1_client._make_authenticated_request("/get-supplies")

            assert "Timeout después de" in str(exc_info.value)


class TestV2Authentication:
    """Tests de autenticación para cliente V2 (hereda de BaseDatadisClient)."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_successful_authentication(self, v2_client, mock_auth_success, test_token):
        """Test autenticación exitosa en cliente V2."""
        v2_client.authenticate()

        assert v2_client.token == test_token
        assert v2_client.token_expiry is not None
        assert v2_client.token_expiry > time.time()

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_authentication_failure(self, v2_client, mock_auth_failure):
        """Test fallo de autenticación en cliente V2."""
        with pytest.raises(AuthenticationError) as exc_info:
            v2_client.authenticate()

        assert "Credenciales inválidas" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_ensure_authenticated_fresh_token(self, v2_client, mock_auth_success):
        """Test ensure_authenticated con token fresco."""
        v2_client.authenticate()
        original_token = v2_client.token

        # Token es fresco, no debería renovarse
        v2_client.ensure_authenticated()

        assert v2_client.token == original_token

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_ensure_authenticated_expired_token(self, v2_client, test_token):
        """Test ensure_authenticated con token expirado."""
        with responses.RequestsMock() as rsps:
            # Primera autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Segunda autenticación (renovación)
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_renewed",
                status=200,
            )

            # Autenticar con token que expira inmediatamente
            v2_client.authenticate()
            original_token = v2_client.token

            # Simular token expirado
            v2_client.token_expiry = time.time() - 3600  # 1 hora atrás

            # Debería renovar automáticamente
            v2_client.ensure_authenticated()

            assert v2_client.token != original_token
            assert v2_client.token == f"{test_token}_renewed"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_token_expiry_calculation(self, v2_client, mock_auth_success, frozen_time):
        """Test cálculo correcto de expiración de token."""
        v2_client.authenticate()

        # Token debería expirar en TOKEN_EXPIRY_HOURS horas
        expected_expiry = time.time() + (TOKEN_EXPIRY_HOURS * 3600)
        assert abs(v2_client.token_expiry - expected_expiry) < 60  # Margen de 1 minuto

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_ensure_authenticated_near_expiry(self, v2_client, test_token):
        """Test ensure_authenticated cerca de la expiración (5 min antes)."""
        with responses.RequestsMock() as rsps:
            # Primera autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Segunda autenticación (renovación)
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_renewed",
                status=200,
            )

            v2_client.authenticate()
            original_token = v2_client.token

            # Simular token que expira en 4 minutos (debería renovarse)
            v2_client.token_expiry = time.time() + 240  # 4 minutos

            v2_client.ensure_authenticated()

            # Debería haberse renovado
            assert v2_client.token != original_token

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_make_authenticated_request_with_retry(self, v2_client, test_token):
        """Test make_authenticated_request con renovación automática."""
        with responses.RequestsMock() as rsps:
            # Primera autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Request falla con 401 (token expirado)
            rsps.add(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies-v2",
                json={"error": "Unauthorized"},
                status=401,
            )

            # Segunda autenticación (automática)
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_renewed",
                status=200,
            )

            # Request exitoso después de renovar
            rsps.add(
                responses.GET,
                "https://datadis.es/api-private/api/get-supplies-v2",
                json={"supplies": [], "distributorError": []},
                status=200,
            )

            v2_client.authenticate()

            # Hacer request que debe renovar token automáticamente
            result = v2_client.make_authenticated_request(
                "GET", "/get-supplies-v2"
            )

            assert v2_client.token == f"{test_token}_renewed"
            assert result == {"supplies": [], "distributorError": []}


class TestContextManager:
    """Tests para uso como context manager."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v1_context_manager_success(self, test_credentials, mock_auth_success):
        """Test uso exitoso del cliente V1 como context manager."""
        with SimpleDatadisClientV1(**test_credentials) as client:
            assert client is not None
            client.authenticate()
            assert client.token is not None

        # Después del context manager, la sesión debería estar cerrada
        assert client.token is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_context_manager_success(self, test_credentials, mock_auth_success):
        """Test uso exitoso del cliente V2 como context manager."""
        with DatadisClientV2(**test_credentials) as client:
            assert client is not None
            client.authenticate()
            assert client.token is not None

        # Después del context manager, recursos deberían estar liberados
        assert client.token is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_context_manager_exception_handling(self, test_credentials):
        """Test manejo de excepciones en context manager."""
        try:
            with SimpleDatadisClientV1(**test_credentials) as client:
                # Simular excepción dentro del context manager
                raise ValueError("Test exception")
        except ValueError:
            # La excepción se propaga correctamente
            pass

        # El cliente debería haberse cerrado correctamente
        assert client.token is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_context_manager_resource_cleanup(self, test_credentials, mock_auth_success):
        """Test limpieza de recursos en context manager."""
        client = None

        with SimpleDatadisClientV1(**test_credentials) as ctx_client:
            client = ctx_client
            client.authenticate()

            # Verificar recursos activos
            assert client.session is not None
            assert client.token is not None

        # Verificar limpieza después del context
        assert client.token is None


class TestSessionManagement:
    """Tests para manejo de sesiones HTTP."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v1_session_headers_configuration(self, v1_client):
        """Test configuración correcta de headers de sesión en V1."""
        headers = v1_client.session.headers

        assert "User-Agent" in headers
        assert "datadis-python-sdk" in headers["User-Agent"]
        assert headers["Accept"] == "application/json"
        assert headers["Accept-Encoding"] == "identity"  # Desactivar gzip

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v1_session_timeout_configuration(self, test_credentials):
        """Test configuración de timeout en cliente V1."""
        custom_timeout = 60
        client = SimpleDatadisClientV1(
            **test_credentials,
            timeout=custom_timeout
        )

        assert client.timeout == custom_timeout

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v1_session_retries_configuration(self, test_credentials):
        """Test configuración de reintentos en cliente V1."""
        custom_retries = 5
        client = SimpleDatadisClientV1(
            **test_credentials,
            retries=custom_retries
        )

        assert client.retries == custom_retries

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_http_client_configuration(self, v2_client):
        """Test configuración del HTTPClient en V2."""
        assert v2_client.http_client is not None
        assert hasattr(v2_client.http_client, "make_request")

    @pytest.mark.unit
    @pytest.mark.auth
    def test_session_cleanup_on_close(self, v1_client, mock_auth_success):
        """Test limpieza correcta de sesión al cerrar."""
        v1_client.authenticate()
        assert v1_client.token is not None

        v1_client.close()

        assert v1_client.token is None

    @pytest.mark.unit
    @pytest.mark.auth
    def test_v2_session_cleanup_on_close(self, v2_client, mock_auth_success):
        """Test limpieza correcta de sesión V2 al cerrar."""
        v2_client.authenticate()
        assert v2_client.token is not None
        assert v2_client.token_expiry is not None

        v2_client.close()

        assert v2_client.token is None
        assert v2_client.token_expiry is None


class TestAuthenticationEdgeCases:
    """Tests para casos extremos de autenticación."""

    @pytest.mark.unit
    @pytest.mark.auth
    def test_multiple_authentication_calls(self, v1_client, test_token):
        """Test múltiples llamadas a authenticate()."""
        with responses.RequestsMock() as rsps:
            # Dos autenticaciones exitosas
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_new",
                status=200,
            )

            # Primera autenticación
            result1 = v1_client.authenticate()
            assert result1 is True
            assert v1_client.token == test_token

            # Segunda autenticación (debería sobrescribir)
            result2 = v1_client.authenticate()
            assert result2 is True
            assert v1_client.token == f"{test_token}_new"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_with_empty_credentials(self):
        """Test autenticación con credenciales vacías."""
        client = SimpleDatadisClientV1(username="", password="")

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Empty credentials"},
                status=400,
            )

            with pytest.raises(AuthenticationError):
                client.authenticate()

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_with_malformed_response(self, v1_client):
        """Test autenticación con respuesta malformada."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body="not_valid_json",
                status=200,
                content_type="application/json",  # Dice JSON pero no lo es
            )

            # El cliente V1 espera texto plano como token
            result = v1_client.authenticate()
            assert result is True
            assert v1_client.token == "not_valid_json"

    @pytest.mark.unit
    @pytest.mark.auth
    def test_concurrent_authentication_calls(self, v1_client, test_token):
        """Test llamadas concurrentes a authenticate() - conceptual."""
        # Este test es más conceptual ya que el cliente no es thread-safe
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            result = v1_client.authenticate()
            assert result is True
            assert v1_client.token == test_token

    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_state_persistence(self, v1_client, mock_auth_success):
        """Test persistencia del estado de autenticación."""
        # Verificar estado inicial
        assert v1_client.token is None

        # Autenticar
        v1_client.authenticate()
        token_after_auth = v1_client.token

        assert token_after_auth is not None

        # El token debería persistir hasta que se cierre la sesión
        assert v1_client.token == token_after_auth

        # Cerrar sesión
        v1_client.close()
        assert v1_client.token is None