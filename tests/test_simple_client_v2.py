"""
Tests para el cliente V2 simplificado de Datadis (SimpleDatadisClientV2).

Estos tests validan:
- Independencia del cliente (no hereda de BaseDatadisClient)
- Funciones de robustez (timeout extendido, reintentos inteligentes, anti-gzip)
- Manejo automático de tokens y renovación en 401
- Validación de entrada con validators
- Todos los métodos API con validación Pydantic
- Context manager y manejo de sesiones
- Tolerancia a fallos y casos extremos
"""

import time
from unittest.mock import MagicMock, patch

import pytest
import requests
import responses
from requests.exceptions import ConnectionError, Timeout

from datadis_python.client.v2.simple_client import SimpleDatadisClientV2
from datadis_python.exceptions import (
    APIError,
    AuthenticationError,
    DatadisError,
    ValidationError,
)
from datadis_python.models.consumption import ConsumptionData
from datadis_python.models.contract import ContractData
from datadis_python.models.max_power import MaxPowerData
from datadis_python.models.reactive import ReactiveData
from datadis_python.models.responses import (
    ConsumptionResponse,
    ContractResponse,
    DistributorError,
    DistributorsResponse,
    MaxPowerResponse,
    SuppliesResponse,
)
from datadis_python.models.supply import SupplyData
from datadis_python.utils.constants import (
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)


class TestSimpleClientV2Initialization:
    """Tests de inicialización y configuración del cliente simplificado."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_initialization_with_default_params(self, test_credentials):
        """Test inicialización con parámetros por defecto."""
        client = SimpleDatadisClientV2(
            username=test_credentials["username"], password=test_credentials["password"]
        )

        assert client.username == test_credentials["username"]
        assert client.password == test_credentials["password"]
        assert client.timeout == 120  # Default para Datadis
        assert client.retries == 3  # Default
        assert client.token is None
        assert client.session is not None
        assert isinstance(client.session, requests.Session)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_initialization_with_custom_params(self, test_credentials):
        """Test inicialización con parámetros personalizados."""
        client = SimpleDatadisClientV2(
            username=test_credentials["username"],
            password=test_credentials["password"],
            timeout=60,
            retries=5,
        )

        assert client.timeout == 60
        assert client.retries == 5

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_session_headers_configuration(self, simple_v2_client):
        """Test configuración de headers de sesión."""
        headers = simple_v2_client.session.headers

        assert headers["User-Agent"] == "datadis-python-sdk/0.2.0"
        assert headers["Accept"] == "application/json"
        assert headers["Accept-Encoding"] == "identity"  # Anti-gzip

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_independence_from_base_client(self, simple_v2_client):
        """Test que SimpleDatadisClientV2 NO hereda de BaseDatadisClient."""
        from datadis_python.client.base import BaseDatadisClient

        # El cliente simplificado es independiente
        assert not isinstance(simple_v2_client, BaseDatadisClient)

        # Pero tiene los métodos esenciales
        assert hasattr(simple_v2_client, "authenticate")
        assert hasattr(simple_v2_client, "close")
        assert hasattr(simple_v2_client, "__enter__")
        assert hasattr(simple_v2_client, "__exit__")

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_has_all_v2_api_methods(self, simple_v2_client):
        """Test que tiene todos los métodos de API V2."""
        api_methods = [
            "get_supplies",
            "get_distributors",
            "get_contract_detail",
            "get_consumption",
            "get_max_power",
            "get_reactive_data",
        ]

        for method_name in api_methods:
            assert hasattr(simple_v2_client, method_name)
            assert callable(getattr(simple_v2_client, method_name))


class TestSimpleClientV2Authentication:
    """Tests de autenticación y manejo de tokens."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.auth
    def test_authenticate_success(self, simple_v2_client, test_token):
        """Test autenticación exitosa."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
                content_type="text/plain",
            )

            result = simple_v2_client.authenticate()

            assert result is True
            assert simple_v2_client.token == test_token
            assert (
                simple_v2_client.session.headers["Authorization"]
                == f"Bearer {test_token}"
            )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.auth
    def test_authenticate_empty_response(self, simple_v2_client):
        """Test autenticación con respuesta vacía."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body="",
                status=200,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                simple_v2_client.authenticate()

            assert "respuesta vacía" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.auth
    def test_authenticate_http_error(self, simple_v2_client):
        """Test autenticación con error HTTP."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                json={"error": "Invalid credentials"},
                status=401,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                simple_v2_client.authenticate()

            assert "401" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.auth
    def test_authenticate_timeout(self, simple_v2_client):
        """Test timeout en autenticación."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Timeout("Timeout")

            with pytest.raises(AuthenticationError) as exc_info:
                simple_v2_client.authenticate()

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.auth
    def test_authenticate_connection_error(self, simple_v2_client):
        """Test error de conexión en autenticación."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = ConnectionError("Connection failed")

            with pytest.raises(AuthenticationError) as exc_info:
                simple_v2_client.authenticate()

            assert "connection failed" in str(exc_info.value).lower()


class TestSimpleClientV2RobustnessFeatures:
    """Tests de funciones de robustez específicas del cliente simplificado."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_timeout_configuration(self, simple_v2_client, sample_v2_supplies_response):
        """Test configuración de timeout extendido."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body="test-token",
                status=200,
            )
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=sample_v2_supplies_response,
                status=200,
            )

            # Verificar que usa el timeout configurado
            assert simple_v2_client.timeout == 30  # Fixture usa 30 para tests

            simple_v2_client.authenticate()
            result = simple_v2_client.get_supplies()

            # Verificar que la llamada incluye el timeout
            assert isinstance(result, SuppliesResponse)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_retry_logic_on_timeout(self, simple_v2_client):
        """Test lógica de reintentos en caso de timeout."""
        # Ajustar cliente para tener más reintentos para este test
        simple_v2_client.retries = 2
        call_count = 0

        def timeout_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Primeros 2 intentos fallan
                raise Timeout("Request timed out")
            # Tercer intento exitoso
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"supplies": [], "distributorError": []}
            mock_response.text = '{"supplies": [], "distributorError": []}'
            return mock_response

        with patch.object(
            simple_v2_client.session, "get", side_effect=timeout_then_success
        ):
            with patch.object(simple_v2_client, "authenticate", return_value=True):
                simple_v2_client.token = "test-token"
                simple_v2_client.session.headers["Authorization"] = "Bearer test-token"

                with patch("time.sleep"):  # Acelerar test
                    result = simple_v2_client.get_supplies()

                assert call_count == 3  # 2 timeouts + 1 éxito
                assert isinstance(result, SuppliesResponse)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_retry_exhaustion(self, simple_v2_client):
        """Test agotamiento de reintentos."""
        with patch.object(
            simple_v2_client.session, "get", side_effect=Timeout("Always timeout")
        ):
            with patch.object(simple_v2_client, "authenticate", return_value=True):
                simple_v2_client.token = "test-token"

                with patch("time.sleep"):  # Acelerar test
                    with pytest.raises(DatadisError) as exc_info:
                        simple_v2_client.get_supplies()

                assert "timeout después de" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_exponential_backoff(self, simple_v2_client):
        """Test backoff exponencial en reintentos."""
        sleep_times = []

        def mock_sleep(seconds):
            sleep_times.append(seconds)

        with patch.object(
            simple_v2_client.session, "get", side_effect=Timeout("Always timeout")
        ):
            with patch.object(simple_v2_client, "authenticate", return_value=True):
                simple_v2_client.token = "test-token"

                with patch("time.sleep", side_effect=mock_sleep):
                    with pytest.raises(DatadisError):
                        simple_v2_client.get_supplies()

        # Verificar que los tiempos aumentan exponencialmente (pero con límite de 30s)
        assert len(sleep_times) == simple_v2_client.retries
        assert sleep_times[0] <= sleep_times[1] if len(sleep_times) > 1 else True

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_token_auto_renewal_on_401(
        self, simple_v2_client, test_token, sample_v2_supplies_response
    ):
        """Test renovación automática de token en error 401."""
        auth_calls = 0
        get_calls = 0

        def mock_get(*args, **kwargs):
            nonlocal get_calls
            get_calls += 1
            if get_calls == 1:  # Primera llamada retorna 401
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.text = "Unauthorized"
                return mock_response
            else:  # Segunda llamada (después de renovar) exitosa
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = sample_v2_supplies_response
                mock_response.text = str(sample_v2_supplies_response)
                return mock_response

        def mock_authenticate():
            nonlocal auth_calls
            auth_calls += 1
            simple_v2_client.token = f"{test_token}-{auth_calls}"
            simple_v2_client.session.headers[
                "Authorization"
            ] = f"Bearer {simple_v2_client.token}"
            return True

        with patch.object(simple_v2_client.session, "get", side_effect=mock_get):
            with patch.object(
                simple_v2_client, "authenticate", side_effect=mock_authenticate
            ):
                # Simular token inicial
                simple_v2_client.token = test_token
                simple_v2_client.session.headers[
                    "Authorization"
                ] = f"Bearer {test_token}"

                result = simple_v2_client.get_supplies()

                assert auth_calls == 1  # Solo la renovación (no llamada inicial)
                assert get_calls == 2  # Primera (401) + segunda (exitosa)
                assert isinstance(result, SuppliesResponse)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_anti_gzip_headers(self, simple_v2_client):
        """Test headers anti-gzip para evitar problemas de compresión."""
        headers = simple_v2_client.session.headers

        # Verificar que la compresión está deshabilitada
        assert headers.get("Accept-Encoding") == "identity"

        # Verificar otros headers básicos
        assert "User-Agent" in headers
        assert "Accept" in headers


class TestSimpleClientV2SuppliesAPI:
    """Tests para el método get_supplies."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_success(
        self, authenticated_simple_v2_client, sample_v2_supplies_response
    ):
        """Test obtención exitosa de suministros."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=sample_v2_supplies_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 1
            assert isinstance(result.supplies[0], SupplyData)
            assert len(result.distributor_error) == 0

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_with_authorized_nif(
        self, authenticated_simple_v2_client, sample_v2_supplies_response
    ):
        """Test get_supplies con NIF autorizado."""
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=sample_v2_supplies_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies(
                authorized_nif=authorized_nif
            )

            assert isinstance(result, SuppliesResponse)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"authorizedNif={authorized_nif}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_with_distributor_code(
        self,
        authenticated_simple_v2_client,
        sample_v2_supplies_response,
        distributor_code,
    ):
        """Test get_supplies con código de distribuidor."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=sample_v2_supplies_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies(
                distributor_code=distributor_code
            )

            assert isinstance(result, SuppliesResponse)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"distributorCode={distributor_code}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_with_distributor_error(self, authenticated_simple_v2_client):
        """Test get_supplies con errores de distribuidor."""
        error_response = {
            "supplies": [],
            "distributorError": [
                {
                    "distributorCode": "2",
                    "distributorName": "E-DISTRIBUCIÓN",
                    "errorCode": "404",
                    "errorDescription": "No data found",
                }
            ],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=error_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 0
            assert len(result.distributor_error) == 1
            assert isinstance(result.distributor_error[0], DistributorError)
            assert result.distributor_error[0].distributor_code == "2"

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_invalid_response_structure(
        self, authenticated_simple_v2_client
    ):
        """Test get_supplies con estructura de respuesta inválida."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json="invalid_response",
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies()

            # Debería devolver respuesta vacía pero válida
            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 0
            assert len(result.distributor_error) == 0

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_supplies_invalid_distributor_code(
        self, authenticated_simple_v2_client
    ):
        """Test get_supplies con código de distribuidor inválido."""
        invalid_distributor = "invalid"

        with pytest.raises(ValidationError):
            authenticated_simple_v2_client.get_supplies(
                distributor_code=invalid_distributor
            )


class TestSimpleClientV2DistributorsAPI:
    """Tests para el método get_distributors."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_distributors_success(
        self, authenticated_simple_v2_client, sample_v2_distributors_response
    ):
        """Test obtención exitosa de distribuidores."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json=sample_v2_distributors_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_distributors()

            assert isinstance(result, DistributorsResponse)
            assert "distributorCodes" in result.dist_existence_user
            assert len(result.distributor_error) == 0

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_distributors_with_authorized_nif(
        self, authenticated_simple_v2_client, sample_v2_distributors_response
    ):
        """Test get_distributors con NIF autorizado."""
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json=sample_v2_distributors_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_distributors(
                authorized_nif=authorized_nif
            )

            assert isinstance(result, DistributorsResponse)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"authorizedNif={authorized_nif}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_distributors_invalid_response(self, authenticated_simple_v2_client):
        """Test get_distributors con respuesta inválida."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json="invalid_response",
                status=200,
            )

            result = authenticated_simple_v2_client.get_distributors()

            # Debería devolver respuesta vacía pero válida
            assert isinstance(result, DistributorsResponse)
            assert result.dist_existence_user == {"distributorCodes": []}
            assert len(result.distributor_error) == 0


class TestSimpleClientV2ContractAPI:
    """Tests para el método get_contract_detail."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_contract_detail_success(
        self,
        authenticated_simple_v2_client,
        sample_v2_contract_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de contrato."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['contracts']}",
                json=sample_v2_contract_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_contract_detail(
                cups=cups_code, distributor_code=distributor_code
            )

            assert isinstance(result, ContractResponse)
            assert len(result.contract) == 1
            assert isinstance(result.contract[0], ContractData)
            assert result.contract[0].cups == cups_code

            # Verificar parámetros en URL
            request = rsps.calls[0].request
            assert f"cups={cups_code}" in request.url
            assert f"distributorCode={distributor_code}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_contract_detail_with_authorized_nif(
        self,
        authenticated_simple_v2_client,
        sample_v2_contract_response,
        cups_code,
        distributor_code,
    ):
        """Test get_contract_detail con NIF autorizado."""
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['contracts']}",
                json=sample_v2_contract_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_contract_detail(
                cups=cups_code,
                distributor_code=distributor_code,
                authorized_nif=authorized_nif,
            )

            assert isinstance(result, ContractResponse)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"authorizedNif={authorized_nif}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_contract_detail_invalid_cups(
        self, authenticated_simple_v2_client, distributor_code
    ):
        """Test get_contract_detail con CUPS inválido."""
        invalid_cups = "INVALID_CUPS"

        with pytest.raises(ValidationError):
            authenticated_simple_v2_client.get_contract_detail(
                cups=invalid_cups, distributor_code=distributor_code
            )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_contract_detail_invalid_distributor(
        self, authenticated_simple_v2_client, cups_code
    ):
        """Test get_contract_detail con código de distribuidor inválido."""
        invalid_distributor = "invalid"

        with pytest.raises(ValidationError):
            authenticated_simple_v2_client.get_contract_detail(
                cups=cups_code, distributor_code=invalid_distributor
            )


class TestSimpleClientV2ConsumptionAPI:
    """Tests para el método get_consumption."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_consumption_success(
        self,
        authenticated_simple_v2_client,
        sample_v2_consumption_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de consumo."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=sample_v2_consumption_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, ConsumptionResponse)
            assert len(result.time_curve) == 24  # 24 horas de datos
            assert all(isinstance(item, ConsumptionData) for item in result.time_curve)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_consumption_with_optional_params(
        self,
        authenticated_simple_v2_client,
        sample_v2_consumption_response,
        cups_code,
        distributor_code,
    ):
        """Test get_consumption con parámetros opcionales."""
        measurement_type = 1
        point_type = 2
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=sample_v2_consumption_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
                measurement_type=measurement_type,
                point_type=point_type,
                authorized_nif=authorized_nif,
            )

            assert isinstance(result, ConsumptionResponse)

            # Verificar parámetros en URL
            request = rsps.calls[0].request
            assert f"measurementType={measurement_type}" in request.url
            assert f"pointType={point_type}" in request.url
            assert f"authorizedNif={authorized_nif}" in request.url

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_consumption_invalid_date_format(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test get_consumption con formato de fecha inválido."""
        invalid_date = "2024-01-15"  # Formato incorrecto

        with pytest.raises(ValidationError):
            authenticated_simple_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=invalid_date,
                date_to="2024/01",
            )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_consumption_invalid_measurement_type(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test get_consumption con tipo de medición inválido."""
        invalid_measurement_type = 999

        with pytest.raises(ValidationError):
            authenticated_simple_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
                measurement_type=invalid_measurement_type,
            )


class TestSimpleClientV2MaxPowerAPI:
    """Tests para el método get_max_power."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_max_power_success(
        self,
        authenticated_simple_v2_client,
        sample_v2_max_power_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de potencia máxima."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['max_power']}",
                json=sample_v2_max_power_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, MaxPowerResponse)
            assert len(result.max_power) == 1
            assert isinstance(result.max_power[0], MaxPowerData)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_max_power_with_authorized_nif(
        self,
        authenticated_simple_v2_client,
        sample_v2_max_power_response,
        cups_code,
        distributor_code,
    ):
        """Test get_max_power con NIF autorizado."""
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['max_power']}",
                json=sample_v2_max_power_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
                authorized_nif=authorized_nif,
            )

            assert isinstance(result, MaxPowerResponse)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"authorizedNif={authorized_nif}" in request.url


class TestSimpleClientV2ReactiveDataAPI:
    """Tests para el método get_reactive_data (específico de V2)."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_reactive_data_success(
        self,
        authenticated_simple_v2_client,
        sample_v2_reactive_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de datos reactivos."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=sample_v2_reactive_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], ReactiveData)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_reactive_data_empty_response(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test get_reactive_data con respuesta vacía."""
        empty_response = {"reactiveEnergy": {}, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=empty_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_get_reactive_data_with_authorized_nif(
        self,
        authenticated_simple_v2_client,
        sample_v2_reactive_response,
        cups_code,
        distributor_code,
    ):
        """Test get_reactive_data con NIF autorizado."""
        authorized_nif = "87654321B"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=sample_v2_reactive_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
                authorized_nif=authorized_nif,
            )

            assert isinstance(result, list)

            # Verificar parámetro en URL
            request = rsps.calls[0].request
            assert f"authorizedNif={authorized_nif}" in request.url


class TestSimpleClientV2ErrorHandling:
    """Tests para manejo de errores y casos extremos."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.errors
    def test_http_error_handling(self, authenticated_simple_v2_client):
        """Test manejo de errores HTTP diversos."""
        error_codes = [400, 403, 404, 500, 502, 503]

        for error_code in error_codes:
            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                    json={"error": f"HTTP {error_code}"},
                    status=error_code,
                )

                with pytest.raises(APIError) as exc_info:
                    authenticated_simple_v2_client.get_supplies()

                assert str(error_code) in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.errors
    def test_malformed_json_response(self, authenticated_simple_v2_client):
        """Test respuestas con JSON malformado."""
        with patch.object(authenticated_simple_v2_client.session, "get") as mock_get:
            # Mock response con JSON inválido
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "invalid json content"
            mock_response.json.side_effect = ValueError(
                "No JSON object could be decoded"
            )
            mock_get.return_value = mock_response

            # Debería propagar el error como DatadisError
            with pytest.raises(DatadisError) as exc_info:
                authenticated_simple_v2_client.get_supplies()

            assert "error después de" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.errors
    def test_network_connection_error(self, authenticated_simple_v2_client):
        """Test errores de conexión de red."""
        with patch.object(
            authenticated_simple_v2_client.session,
            "get",
            side_effect=ConnectionError("Network error"),
        ):
            with patch("time.sleep"):  # Acelerar test
                with pytest.raises(DatadisError) as exc_info:
                    authenticated_simple_v2_client.get_supplies()

                assert "error después de" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_unauthenticated_request_triggers_auth(
        self, simple_v2_client, sample_v2_supplies_response, test_token
    ):
        """Test que una petición sin autenticar dispara la autenticación automática."""
        with responses.RequestsMock() as rsps:
            # Mock autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )
            # Mock API call
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=sample_v2_supplies_response,
                status=200,
            )

            # Cliente sin token
            assert simple_v2_client.token is None

            result = simple_v2_client.get_supplies()

            # Debería haberse autenticado automáticamente
            assert simple_v2_client.token == test_token
            assert isinstance(result, SuppliesResponse)


class TestSimpleClientV2ContextManager:
    """Tests para context manager y manejo de sesiones."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_context_manager_entry_exit(self, test_credentials):
        """Test entrada y salida del context manager."""
        with SimpleDatadisClientV2(**test_credentials) as client:
            assert client.session is not None
            assert isinstance(client, SimpleDatadisClientV2)

        # Después del exit, la sesión debería estar cerrada
        assert client.token is None

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_context_manager_with_exception(self, test_credentials):
        """Test context manager cuando ocurre una excepción."""
        try:
            with SimpleDatadisClientV2(**test_credentials) as client:
                assert client.session is not None
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Incluso con excepción, debería cerrar la sesión
        assert client.token is None

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_manual_close(self, simple_v2_client):
        """Test cierre manual de la sesión."""
        # Verificar estado inicial
        assert simple_v2_client.session is not None
        assert simple_v2_client.token is None

        # Simular token establecido
        simple_v2_client.token = "test-token"

        # Cerrar manualmente
        simple_v2_client.close()

        # Verificar que se limpió el estado
        assert simple_v2_client.token is None

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_session_reuse(
        self, simple_v2_client, test_token, sample_v2_supplies_response
    ):
        """Test reutilización de sesión para múltiples llamadas."""
        with responses.RequestsMock() as rsps:
            # Mock autenticación una vez
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )
            # Mock múltiples llamadas API
            for _ in range(3):
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                    json=sample_v2_supplies_response,
                    status=200,
                )

            # Hacer múltiples llamadas
            result1 = simple_v2_client.get_supplies()
            result2 = simple_v2_client.get_supplies()
            result3 = simple_v2_client.get_supplies()

            # Todas deberían ser exitosas
            assert isinstance(result1, SuppliesResponse)
            assert isinstance(result2, SuppliesResponse)
            assert isinstance(result3, SuppliesResponse)

            # Solo debería haber autenticado una vez
            auth_calls = [call for call in rsps.calls if "login" in call.request.url]
            assert len(auth_calls) == 1


class TestSimpleClientV2InputValidation:
    """Tests específicos para validación de entrada."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_cups_validation(self, authenticated_simple_v2_client, distributor_code):
        """Test validación de códigos CUPS."""
        invalid_cups_cases = [
            "",  # Vacío
            "INVALID",  # Muy corto
            "ES0123456789012345678901234567",  # Muy largo (26 chars después de ES)
            "XX0123456789012345678901AB",  # Prefijo inválido
            "ES0123456789012345678",  # Muy corto (19 chars después de ES)
            "ES01234567890123456789ABC",  # Muy largo (23 chars después de ES)
            "ES012345678901234567890123456",  # Muy largo (27 chars después de ES)
        ]

        for invalid_cups in invalid_cups_cases:
            with pytest.raises(ValidationError):
                authenticated_simple_v2_client.get_contract_detail(
                    cups=invalid_cups, distributor_code=distributor_code
                )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_distributor_code_validation(
        self, authenticated_simple_v2_client, cups_code
    ):
        """Test validación de códigos de distribuidor."""
        invalid_distributors = [
            "0",  # No válido
            "9",  # Fuera de rango
            "abc",  # No numérico
            "",  # Vacío
        ]

        for invalid_distributor in invalid_distributors:
            with pytest.raises(ValidationError):
                authenticated_simple_v2_client.get_contract_detail(
                    cups=cups_code, distributor_code=invalid_distributor
                )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_date_format_validation(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test validación de formatos de fecha."""
        # Fechas que deberían fallar validación estricta
        truly_invalid_dates = [
            "2024-01-15",  # Formato ISO con día específico - debe fallar por día específico
            "2024/13",  # Mes inválido
            "2024/00",  # Mes cero
            "",  # Vacío
            "invalid",  # No fecha
        ]

        for invalid_date in truly_invalid_dates:
            with pytest.raises(ValidationError):
                authenticated_simple_v2_client.get_consumption(
                    cups=cups_code,
                    distributor_code=distributor_code,
                    date_from=invalid_date,
                    date_to="2024/01",
                )

        # Fechas que ahora son auto-convertidas correctamente (no deberían fallar)
        auto_converted_dates = [
            "2024/1",  # Sin ceros padding pero convertible a 2024/01
        ]

        for convertible_date in auto_converted_dates:
            try:
                authenticated_simple_v2_client.get_consumption(
                    cups=cups_code,
                    distributor_code=distributor_code,
                    date_from=convertible_date,
                    date_to="2024/01",
                )
            except ValidationError:
                pytest.fail(
                    f"La fecha {convertible_date} debería ser auto-convertida correctamente"
                )
            except Exception:
                # Otros errores (auth, red, etc.) son esperados en tests unitarios
                pass

        # Fechas que siguen fallando pero que antes pensé que serían convertidas
        still_invalid_dates = [
            "01/2024",  # Orden incorrecto - no se puede convertir automáticamente
        ]

        for invalid_date in still_invalid_dates:
            with pytest.raises(ValidationError):
                authenticated_simple_v2_client.get_consumption(
                    cups=cups_code,
                    distributor_code=distributor_code,
                    date_from=invalid_date,
                    date_to="2024/01",
                )

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_point_type_validation(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test validación de tipos de punto."""
        invalid_point_types = [
            0,  # Fuera de rango
            6,  # Fuera de rango
            -1,  # Negativo
        ]

        for invalid_point_type in invalid_point_types:
            with pytest.raises(ValidationError):
                authenticated_simple_v2_client.get_consumption(
                    cups=cups_code,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                    point_type=invalid_point_type,
                )


class TestSimpleClientV2PydanticValidation:
    """Tests para validación de modelos Pydantic."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.models
    def test_supplies_response_validation(self, authenticated_simple_v2_client):
        """Test validación del modelo SuppliesResponse."""
        valid_response = {
            "supplies": [
                {
                    "address": "CALLE EJEMPLO 123",
                    "cups": "ES0031607515707001RC0F",
                    "postalCode": "28001",
                    "province": "MADRID",
                    "municipality": "MADRID",
                    "distributor": "E-DISTRIBUCION",
                    "validDateFrom": "2023/01/01",
                    "validDateTo": None,
                    "pointType": 2,
                    "distributorCode": "2",
                }
            ],
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=valid_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies()

            # Verificar que el modelo Pydantic se validó correctamente
            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 1

            # Verificar que se puede serializar de vuelta
            json_data = result.model_dump_json(by_alias=True)
            assert "supplies" in json_data
            assert "distributorError" in json_data

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.models
    def test_consumption_response_validation(
        self, authenticated_simple_v2_client, cups_code, distributor_code
    ):
        """Test validación del modelo ConsumptionResponse."""
        valid_response = {
            "timeCurve": [
                {
                    "cups": cups_code,
                    "date": "2024/01/15",
                    "time": "01:00",
                    "consumptionKWh": 0.125,
                    "obtainMethod": "Real",
                    "surplusEnergyKWh": None,
                    "generationEnergyKWh": None,
                    "selfConsumptionEnergyKWh": None,
                }
            ],
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=valid_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, ConsumptionResponse)
            assert len(result.time_curve) == 1
            assert isinstance(result.time_curve[0], ConsumptionData)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.models
    def test_model_schema_compliance(self, authenticated_simple_v2_client):
        """Test cumplimiento de esquemas de modelos."""
        # Verificar que los modelos de respuesta tienen esquemas válidos
        response_models = [
            SuppliesResponse,
            DistributorsResponse,
            ContractResponse,
            ConsumptionResponse,
            MaxPowerResponse,
        ]

        for model_class in response_models:
            schema = model_class.model_json_schema()

            # Verificar estructura básica del esquema
            assert "properties" in schema
            assert "type" in schema
            assert schema["type"] == "object"

            # Verificar que tiene campos requeridos para V2
            properties = schema["properties"]
            assert any("error" in prop.lower() for prop in properties.keys())


class TestSimpleClientV2PerformanceAndLimits:
    """Tests para rendimiento y límites del cliente."""

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    @pytest.mark.slow
    def test_large_response_handling(self, authenticated_simple_v2_client):
        """Test manejo de respuestas grandes."""
        # Simular respuesta grande con muchos datos
        large_supplies = []
        for i in range(100):  # 100 suministros
            large_supplies.append(
                {
                    "address": f"CALLE EJEMPLO {i}",
                    "cups": f"ES00316075157070{i:02d}RC0F",
                    "postalCode": "28001",
                    "province": "MADRID",
                    "municipality": "MADRID",
                    "distributor": "E-DISTRIBUCION",
                    "validDateFrom": "2023/01/01",
                    "validDateTo": None,
                    "pointType": 2,
                    "distributorCode": "2",
                }
            )

        large_response = {"supplies": large_supplies, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=large_response,
                status=200,
            )

            result = authenticated_simple_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 100

            # Verificar que todos los elementos son válidos
            for supply in result.supplies:
                assert isinstance(supply, SupplyData)

    @pytest.mark.unit
    @pytest.mark.simple_client_v2
    def test_concurrent_requests_simulation(
        self, authenticated_simple_v2_client, sample_v2_supplies_response
    ):
        """Test simulación de peticiones concurrentes (sesión reutilizada)."""
        with responses.RequestsMock() as rsps:
            # Mock múltiples respuestas
            for _ in range(10):
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                    json=sample_v2_supplies_response,
                    status=200,
                )

            # Hacer múltiples llamadas rápidas
            results = []
            for _ in range(10):
                result = authenticated_simple_v2_client.get_supplies()
                results.append(result)

            # Todas deberían ser exitosas
            assert len(results) == 10
            assert all(isinstance(r, SuppliesResponse) for r in results)
