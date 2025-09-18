"""
Tests para el cliente V1 de Datadis (SimpleDatadisClientV1).

Estos tests validan:
- Inicialización del cliente
- Métodos de API (get_supplies, get_consumption, etc.)
- Manejo de requests autenticados
- Validación de parámetros
- Serialización de respuestas con Pydantic
- Manejo de errores específicos del cliente
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests
import responses

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.exceptions import APIError, AuthenticationError, DatadisError
from datadis_python.models.consumption import ConsumptionData
from datadis_python.models.contract import ContractData
from datadis_python.models.distributor import DistributorData
from datadis_python.models.max_power import MaxPowerData
from datadis_python.models.supply import SupplyData
from datadis_python.utils.constants import (
    API_V1_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)


class TestV1ClientInitialization:
    """Tests de inicialización del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_client_initialization_minimal(self, test_credentials):
        """Test inicialización con parámetros mínimos."""
        client = SimpleDatadisClientV1(
            username=test_credentials["username"],
            password=test_credentials["password"]
        )

        assert client.username == test_credentials["username"]
        assert client.password == test_credentials["password"]
        assert client.timeout == 120  # Default timeout
        assert client.retries == 3  # Default retries
        assert client.token is None
        assert client.session is not None

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_client_initialization_full_params(self, test_credentials):
        """Test inicialización con todos los parámetros."""
        custom_timeout = 60
        custom_retries = 5

        client = SimpleDatadisClientV1(
            username=test_credentials["username"],
            password=test_credentials["password"],
            timeout=custom_timeout,
            retries=custom_retries
        )

        assert client.timeout == custom_timeout
        assert client.retries == custom_retries

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_client_session_headers(self, v1_client):
        """Test configuración correcta de headers de sesión."""
        headers = v1_client.session.headers

        assert "User-Agent" in headers
        assert "datadis-python-sdk/0.2.0" in headers["User-Agent"]
        assert headers["Accept"] == "application/json"
        assert headers["Accept-Encoding"] == "identity"


class TestV1ClientSupplies:
    """Tests para el método get_supplies del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_supplies_success(self, authenticated_v1_client, sample_supplies_response):
        """Test obtención exitosa de suministros."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            supplies = authenticated_v1_client.get_supplies()

            assert isinstance(supplies, list)
            assert len(supplies) == 1
            assert isinstance(supplies[0], SupplyData)
            assert supplies[0].cups == sample_supplies_response[0]["cups"]
            assert supplies[0].distributor == sample_supplies_response[0]["distributor"]

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_supplies_empty_response(self, authenticated_v1_client):
        """Test respuesta vacía de suministros."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=[],
                status=200,
            )

            supplies = authenticated_v1_client.get_supplies()

            assert isinstance(supplies, list)
            assert len(supplies) == 0

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_supplies_nested_response(self, authenticated_v1_client, sample_supply_data):
        """Test respuesta anidada de suministros."""
        nested_response = {
            "supplies": [sample_supply_data]
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=nested_response,
                status=200,
            )

            supplies = authenticated_v1_client.get_supplies()

            assert len(supplies) == 1
            assert isinstance(supplies[0], SupplyData)

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_supplies_validation_error(self, authenticated_v1_client):
        """Test manejo de errores de validación en suministros."""
        invalid_supply = {
            "cups": "INVALID_CUPS",  # CUPS inválido
            "address": "Test Address",
            # Faltan campos requeridos
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=[invalid_supply],
                status=200,
            )

            supplies = authenticated_v1_client.get_supplies()

            # Debería devolver lista vacía si los datos no son válidos
            assert isinstance(supplies, list)
            assert len(supplies) == 0

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_supplies_unexpected_response_format(self, authenticated_v1_client):
        """Test respuesta con formato inesperado."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"unexpected": "format"},
                status=200,
            )

            supplies = authenticated_v1_client.get_supplies()

            assert isinstance(supplies, list)
            assert len(supplies) == 0


class TestV1ClientDistributors:
    """Tests para el método get_distributors del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_distributors_success(self, authenticated_v1_client, sample_distributors_response):
        """Test obtención exitosa de distribuidores."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['distributors']}",
                json=sample_distributors_response,
                status=200,
            )

            distributors = authenticated_v1_client.get_distributors()

            assert isinstance(distributors, list)
            assert len(distributors) == 1
            assert isinstance(distributors[0], DistributorData)
            assert distributors[0].distributor_codes == sample_distributors_response[0]["distributorCodes"]

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_distributors_single_dict_response(self, authenticated_v1_client, sample_distributor_data):
        """Test respuesta como diccionario único."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['distributors']}",
                json=sample_distributor_data,
                status=200,
            )

            distributors = authenticated_v1_client.get_distributors()

            assert isinstance(distributors, list)
            assert len(distributors) == 1
            assert isinstance(distributors[0], DistributorData)

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_distributors_empty_response(self, authenticated_v1_client):
        """Test respuesta vacía de distribuidores."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['distributors']}",
                json=[],
                status=200,
            )

            distributors = authenticated_v1_client.get_distributors()

            assert isinstance(distributors, list)
            assert len(distributors) == 0


class TestV1ClientContracts:
    """Tests para el método get_contract_detail del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_contract_detail_success(
        self,
        authenticated_v1_client,
        sample_contract_response,
        cups_code,
        distributor_code
    ):
        """Test obtención exitosa de detalle de contrato."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['contracts']}",
                json=sample_contract_response,
                status=200,
            )

            contracts = authenticated_v1_client.get_contract_detail(
                cups=cups_code,
                distributor_code=distributor_code
            )

            assert isinstance(contracts, list)
            assert len(contracts) == 1
            assert isinstance(contracts[0], ContractData)
            assert contracts[0].cups == cups_code
            assert contracts[0].distributor is not None

            # Verificar que se enviaron los parámetros correctos
            request = rsps.calls[0].request
            assert f"cups={cups_code}" in request.url
            assert f"distributorCode={distributor_code}" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_contract_detail_single_dict_response(
        self,
        authenticated_v1_client,
        sample_contract_data,
        cups_code,
        distributor_code
    ):
        """Test respuesta de contrato como diccionario único."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['contracts']}",
                json=sample_contract_data,
                status=200,
            )

            contracts = authenticated_v1_client.get_contract_detail(
                cups=cups_code,
                distributor_code=distributor_code
            )

            assert isinstance(contracts, list)
            assert len(contracts) == 1
            assert isinstance(contracts[0], ContractData)

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_contract_detail_not_found(
        self,
        authenticated_v1_client,
        cups_code,
        distributor_code
    ):
        """Test contrato no encontrado."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['contracts']}",
                json=[],
                status=200,
            )

            contracts = authenticated_v1_client.get_contract_detail(
                cups=cups_code,
                distributor_code=distributor_code
            )

            assert isinstance(contracts, list)
            assert len(contracts) == 0


class TestV1ClientConsumption:
    """Tests para el método get_consumption del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_consumption_success(
        self,
        authenticated_v1_client,
        sample_consumption_response,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test obtención exitosa de datos de consumo."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=sample_consumption_response,
                status=200,
            )

            consumption = authenticated_v1_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(consumption, list)
            assert len(consumption) == 24  # 24 horas de datos
            assert all(isinstance(item, ConsumptionData) for item in consumption)
            assert consumption[0].cups == cups_code

            # Verificar parámetros de la request
            request = rsps.calls[0].request
            assert f"cups={cups_code}" in request.url
            assert f"distributorCode={distributor_code}" in request.url
            assert f"startDate={date_range['date_from'].replace('/', '%2F')}" in request.url
            assert f"endDate={date_range['date_to'].replace('/', '%2F')}" in request.url
            assert "measurementType=0" in request.url  # Default value

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_consumption_with_optional_params(
        self,
        authenticated_v1_client,
        sample_consumption_response,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test obtención de consumo con parámetros opcionales."""
        measurement_type = 1
        point_type = 2

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=sample_consumption_response,
                status=200,
            )

            consumption = authenticated_v1_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"],
                measurement_type=measurement_type,
                point_type=point_type
            )

            assert isinstance(consumption, list)

            # Verificar parámetros opcionales en la request
            request = rsps.calls[0].request
            assert f"measurementType={measurement_type}" in request.url
            assert f"pointType={point_type}" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_consumption_nested_response(
        self,
        authenticated_v1_client,
        sample_consumption_response,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test respuesta de consumo anidada."""
        nested_response = {
            "timeCurve": sample_consumption_response
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=nested_response,
                status=200,
            )

            consumption = authenticated_v1_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(consumption, list)
            assert len(consumption) == 24

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_consumption_no_data(
        self,
        authenticated_v1_client,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test obtención de consumo sin datos."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=[],
                status=200,
            )

            consumption = authenticated_v1_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(consumption, list)
            assert len(consumption) == 0


class TestV1ClientMaxPower:
    """Tests para el método get_max_power del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_max_power_success(
        self,
        authenticated_v1_client,
        sample_max_power_response,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test obtención exitosa de datos de potencia máxima."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['max_power']}",
                json=sample_max_power_response,
                status=200,
            )

            max_power = authenticated_v1_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(max_power, list)
            assert len(max_power) == 1
            assert isinstance(max_power[0], MaxPowerData)
            assert max_power[0].cups == cups_code

            # Verificar parámetros de la request
            request = rsps.calls[0].request
            assert f"cups={cups_code}" in request.url
            assert f"distributorCode={distributor_code}" in request.url
            assert f"startDate={date_range['date_from'].replace('/', '%2F')}" in request.url
            assert f"endDate={date_range['date_to'].replace('/', '%2F')}" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_max_power_nested_response(
        self,
        authenticated_v1_client,
        sample_max_power_response,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test respuesta de potencia máxima anidada."""
        nested_response = {
            "maxPower": sample_max_power_response
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['max_power']}",
                json=nested_response,
                status=200,
            )

            max_power = authenticated_v1_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(max_power, list)
            assert len(max_power) == 1

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_get_max_power_empty_response(
        self,
        authenticated_v1_client,
        cups_code,
        distributor_code,
        date_range
    ):
        """Test respuesta vacía de potencia máxima."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['max_power']}",
                json=[],
                status=200,
            )

            max_power = authenticated_v1_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_range["date_from"],
                date_to=date_range["date_to"]
            )

            assert isinstance(max_power, list)
            assert len(max_power) == 0


class TestV1ClientAuthenticatedRequests:
    """Tests para el método _make_authenticated_request del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_success(self, authenticated_v1_client):
        """Test request autenticado exitoso."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"success": True},
                status=200,
            )

            result = authenticated_v1_client._make_authenticated_request("/test-endpoint")

            assert result == {"success": True}

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_with_params(self, authenticated_v1_client):
        """Test request autenticado con parámetros."""
        params = {"param1": "value1", "param2": "value2"}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"success": True},
                status=200,
            )

            result = authenticated_v1_client._make_authenticated_request(
                "/test-endpoint",
                params=params
            )

            assert result == {"success": True}

            # Verificar parámetros en la URL
            request = rsps.calls[0].request
            assert "param1=value1" in request.url
            assert "param2=value2" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_not_authenticated(self, v1_client, test_token):
        """Test request sin autenticación previa."""
        with responses.RequestsMock() as rsps:
            # Auth automático
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Request real
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"success": True},
                status=200,
            )

            result = v1_client._make_authenticated_request("/test-endpoint")

            assert result == {"success": True}
            assert v1_client.token == test_token

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_http_error(self, authenticated_v1_client):
        """Test request con error HTTP."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"error": "Not found"},
                status=404,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/test-endpoint")

            assert exc_info.value.status_code == 404
            assert "Error HTTP 404" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_timeout_retry(self, authenticated_v1_client):
        """Test reintentos en caso de timeout."""
        with responses.RequestsMock() as rsps:
            # Primera request falla con timeout
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Request timed out")

            rsps.add_callback(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                callback=timeout_callback,
            )

            # Segunda request exitosa
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"success": True},
                status=200,
            )

            result = authenticated_v1_client._make_authenticated_request("/test-endpoint")

            assert result == {"success": True}
            assert len(rsps.calls) == 2  # Dos intentos

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_make_authenticated_request_exhausted_retries(self, v1_client, test_token):
        """Test agotamiento de reintentos."""
        # Cliente con solo 1 reintento para acelerar el test
        v1_client.retries = 1

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Todas las requests fallan con timeout
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Request timed out")

            for _ in range(2):  # Para retries=1, son 2 intentos totales
                rsps.add_callback(
                    responses.GET,
                    f"{DATADIS_API_BASE}/test-endpoint",
                    callback=timeout_callback,
                )

            with pytest.raises(DatadisError) as exc_info:
                v1_client._make_authenticated_request("/test-endpoint")

            assert "Timeout después de" in str(exc_info.value)


class TestV1ClientErrorHandling:
    """Tests para manejo de errores específicos del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_api_error_propagation(self, authenticated_v1_client):
        """Test propagación correcta de errores de API."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                json={"error": "Server error"},
                status=500,
            )

            with pytest.raises(APIError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/test-endpoint")

            assert exc_info.value.status_code == 500

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_network_error_handling(self, authenticated_v1_client):
        """Test manejo de errores de red."""
        with responses.RequestsMock() as rsps:

            def network_error_callback(request):
                raise requests.exceptions.ConnectionError("Network error")

            rsps.add_callback(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                callback=network_error_callback,
            )

            with pytest.raises(DatadisError) as exc_info:
                authenticated_v1_client._make_authenticated_request("/test-endpoint")

            assert "Error después de" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_malformed_json_response(self, authenticated_v1_client):
        """Test manejo de respuesta JSON malformada."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}/test-endpoint",
                body="not valid json",
                status=200,
                content_type="application/json",
            )

            with pytest.raises((DatadisError, ValueError)):
                authenticated_v1_client._make_authenticated_request("/test-endpoint")


class TestV1ClientResourceManagement:
    """Tests para manejo de recursos del cliente V1."""

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_close_method(self, v1_client, mock_auth_success):
        """Test método close()."""
        v1_client.authenticate()
        assert v1_client.token is not None
        assert v1_client.session is not None

        v1_client.close()

        assert v1_client.token is None

    @pytest.mark.unit
    @pytest.mark.client_v1
    def test_context_manager_resource_cleanup(self, test_credentials, mock_auth_success):
        """Test limpieza de recursos con context manager."""
        with SimpleDatadisClientV1(**test_credentials) as client:
            client.authenticate()
            assert client.token is not None

        assert client.token is None