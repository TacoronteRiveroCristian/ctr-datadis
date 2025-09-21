"""
Tests para el cliente V2 de Datadis (DatadisClientV2).

Estos tests validan:
- Herencia correcta de BaseDatadisClient
- Métodos específicos de V2 con respuestas estructuradas
- Validación de parámetros con validators
- Respuestas con formato DistributorError
- Método específico get_reactive_data
- Endpoints V2 y diferencias con V1
"""

import pytest
import responses

from datadis_python.client.v2.client import DatadisClientV2
from datadis_python.exceptions import ValidationError
from datadis_python.models.consumption import ConsumptionData
from datadis_python.models.contract import ContractData
from datadis_python.models.max_power import MaxPowerData
from datadis_python.models.reactive import ReactiveData, ReactiveEnergyData
from datadis_python.models.responses import (
    ConsumptionResponse,
    ContractResponse,
    DistributorError,
    DistributorsResponse,
    MaxPowerResponse,
    SuppliesResponse,
)
from datadis_python.models.supply import SupplyData
from datadis_python.utils.constants import API_V2_ENDPOINTS, DATADIS_API_BASE


class TestV2ClientInheritance:
    """Tests de herencia y funcionalidad base."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_inherits_from_base(self, v2_client):
        """Test que V2 hereda correctamente de BaseDatadisClient."""
        # Verificar que hereda métodos de la clase base
        assert hasattr(v2_client, "authenticate")
        assert hasattr(v2_client, "ensure_authenticated")
        assert hasattr(v2_client, "make_authenticated_request")
        assert hasattr(v2_client, "close")
        assert hasattr(v2_client, "__enter__")
        assert hasattr(v2_client, "__exit__")

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_has_specific_methods(self, v2_client):
        """Test que V2 tiene métodos específicos."""
        assert hasattr(v2_client, "get_supplies")
        assert hasattr(v2_client, "get_distributors")
        assert hasattr(v2_client, "get_contract_detail")
        assert hasattr(v2_client, "get_consumption")
        assert hasattr(v2_client, "get_max_power")
        assert hasattr(v2_client, "get_reactive_data")  # Específico de V2

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_initialization(self, test_credentials):
        """Test inicialización del cliente V2."""
        client = DatadisClientV2(**test_credentials)

        assert client.username == test_credentials["username"]
        assert client.password == test_credentials["password"]
        assert client.http_client is not None
        assert client.token is None


class TestV2ClientSupplies:
    """Tests para get_supplies en V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_supplies_success(
        self, authenticated_v2_client, sample_supplies_response
    ):
        """Test obtención exitosa de suministros en V2."""
        v2_response = {"supplies": sample_supplies_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 1
            assert isinstance(result.supplies[0], SupplyData)
            assert len(result.distributor_error) == 0

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_supplies_with_distributor_filter(
        self, authenticated_v2_client, sample_supplies_response, distributor_code
    ):
        """Test get_supplies con filtro de distribuidor."""
        v2_response = {"supplies": sample_supplies_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies(
                distributor_code=distributor_code
            )

            assert isinstance(result, SuppliesResponse)

            # Verificar que se envió el parámetro
            request = rsps.calls[0].request
            assert f"distributorCode={distributor_code}" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_supplies_with_distributor_error(self, authenticated_v2_client):
        """Test get_supplies con errores de distribuidor."""
        v2_response = {
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
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 0
            assert len(result.distributor_error) == 1
            assert isinstance(result.distributor_error[0], DistributorError)
            assert result.distributor_error[0].distributor_code == "2"

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_supplies_invalid_response(self, authenticated_v2_client):
        """Test get_supplies con respuesta inválida."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json="invalid_response",
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            # Debería devolver respuesta vacía válida
            assert isinstance(result, SuppliesResponse)
            assert len(result.supplies) == 0
            assert len(result.distributor_error) == 0


class TestV2ClientDistributors:
    """Tests para get_distributors en V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_distributors_success(self, authenticated_v2_client):
        """Test obtención exitosa de distribuidores en V2."""
        v2_response = {
            "distExistenceUser": {"distributorCodes": ["1", "2", "3"]},
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_distributors()

            assert isinstance(result, DistributorsResponse)
            assert "distributorCodes" in result.dist_existence_user
            assert len(result.dist_existence_user["distributorCodes"]) == 3
            assert len(result.distributor_error) == 0

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_distributors_with_error(self, authenticated_v2_client):
        """Test get_distributors con errores."""
        v2_response = {
            "distExistenceUser": {"distributorCodes": []},
            "distributorError": [
                {
                    "distributorCode": "999",
                    "distributorName": "UNKNOWN",
                    "errorCode": "404",
                    "errorDescription": "Distributor not found",
                }
            ],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_distributors()

            assert isinstance(result, DistributorsResponse)
            assert len(result.distributor_error) == 1
            assert result.distributor_error[0].error_code == "404"


class TestV2ClientContracts:
    """Tests para get_contract_detail en V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_contract_detail_success(
        self,
        authenticated_v2_client,
        sample_contract_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de contrato en V2."""
        v2_response = {"contract": sample_contract_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['contracts']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_contract_detail(
                cups=cups_code, distributor_code=distributor_code
            )

            assert isinstance(result, ContractResponse)
            assert len(result.contract) == 1
            assert isinstance(result.contract[0], ContractData)
            assert result.contract[0].cups == cups_code

            # Verificar parámetros
            request = rsps.calls[0].request
            assert f"cups={cups_code}" in request.url
            assert f"distributorCode={distributor_code}" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_contract_detail_validation(self, authenticated_v2_client):
        """Test validación de parámetros en get_contract_detail."""
        # Test con CUPS inválido - debería fallar validación sin hacer HTTP request
        invalid_cups = "INVALID_CUPS"
        valid_distributor = "2"

        # No configuramos mock porque esperamos que falle validación antes de HTTP
        with pytest.raises(ValidationError):
            authenticated_v2_client.get_contract_detail(
                cups=invalid_cups, distributor_code=valid_distributor
            )


class TestV2ClientConsumption:
    """Tests para get_consumption en V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_consumption_success(
        self,
        authenticated_v2_client,
        sample_consumption_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de consumo en V2."""
        v2_response = {"timeCurve": sample_consumption_response, "distributorError": []}

        # Fechas mensuales para V2
        date_from = "2024/01"
        date_to = "2024/01"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from=date_from,
                date_to=date_to,
            )

            assert isinstance(result, ConsumptionResponse)
            assert len(result.time_curve) == 24  # 24 horas de datos
            assert all(isinstance(item, ConsumptionData) for item in result.time_curve)

            # Verificar parámetros (considerando URL encoding)
            request = rsps.calls[0].request
            import urllib.parse

            assert f"startDate={urllib.parse.quote(date_from, safe='')}" in request.url
            assert f"endDate={urllib.parse.quote(date_to, safe='')}" in request.url
            assert "measurementType=0" in request.url  # Default

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_consumption_with_optional_params(
        self,
        authenticated_v2_client,
        sample_consumption_response,
        cups_code,
        distributor_code,
    ):
        """Test get_consumption con parámetros opcionales."""
        v2_response = {"timeCurve": sample_consumption_response, "distributorError": []}

        measurement_type = 1
        point_type = 2

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_consumption(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
                measurement_type=measurement_type,
                point_type=point_type,
            )

            assert isinstance(result, ConsumptionResponse)

            # Verificar parámetros opcionales
            request = rsps.calls[0].request
            assert f"measurementType={measurement_type}" in request.url
            assert f"pointType={point_type}" in request.url


class TestV2ClientMaxPower:
    """Tests para get_max_power en V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_max_power_success(
        self,
        authenticated_v2_client,
        sample_max_power_response,
        cups_code,
        distributor_code,
    ):
        """Test obtención exitosa de potencia máxima en V2."""
        v2_response = {"maxPower": sample_max_power_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['max_power']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_max_power(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, MaxPowerResponse)
            assert len(result.max_power) == 1
            assert isinstance(result.max_power[0], MaxPowerData)


class TestV2ClientReactiveData:
    """Tests para get_reactive_data (específico de V2)."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_reactive_data_success(
        self, authenticated_v2_client, cups_code, distributor_code
    ):
        """Test obtención exitosa de datos reactivos."""
        reactive_response = {
            "reactiveEnergy": {
                "cups": cups_code,
                "energy": [
                    {
                        "date": "2024/01",
                        "energy_p1": 10.5,
                        "energy_p2": 8.2,
                        "energy_p3": None,
                        "energy_p4": None,
                        "energy_p5": None,
                        "energy_p6": None,
                    }
                ],
            },
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=reactive_response,
                status=200,
            )

            result = authenticated_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], ReactiveData)
            assert result[0].reactive_energy.cups == cups_code

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_reactive_data_empty_response(
        self, authenticated_v2_client, cups_code, distributor_code
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

            result = authenticated_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_get_reactive_data_validation_error(
        self, authenticated_v2_client, cups_code, distributor_code
    ):
        """Test get_reactive_data con datos inválidos."""
        invalid_response = {
            "reactiveEnergy": {
                "cups": cups_code,
                "energy": [
                    {
                        "date": "invalid_date",
                        "energy_p1": "not_a_number",
                    }
                ],
            },
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=invalid_response,
                status=200,
            )

            result = authenticated_v2_client.get_reactive_data(
                cups=cups_code,
                distributor_code=distributor_code,
                date_from="2024/01",
                date_to="2024/01",
            )

            # Debería devolver lista vacía si hay errores de validación
            assert isinstance(result, list)
            assert len(result) == 0


class TestV2ClientErrorHandling:
    """Tests para manejo de errores específico de V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_invalid_response_handling(self, authenticated_v2_client):
        """Test manejo de respuestas inválidas en todos los métodos."""
        methods_and_args = [
            ("get_supplies", {}),
            ("get_distributors", {}),
            (
                "get_contract_detail",
                {"cups": "ES0031607515707001RC0F", "distributor_code": "2"},
            ),
            (
                "get_consumption",
                {
                    "cups": "ES0031607515707001RC0F",
                    "distributor_code": "2",
                    "date_from": "2024/01",
                    "date_to": "2024/01",
                },
            ),
            (
                "get_max_power",
                {
                    "cups": "ES0031607515707001RC0F",
                    "distributor_code": "2",
                    "date_from": "2024/01",
                    "date_to": "2024/01",
                },
            ),
        ]

        # Mapeo de métodos a endpoints
        method_to_endpoint = {
            "get_supplies": "supplies",
            "get_distributors": "distributors",
            "get_contract_detail": "contracts",
            "get_consumption": "consumption",
            "get_max_power": "max_power",
        }

        for method_name, kwargs in methods_and_args:
            endpoint = API_V2_ENDPOINTS[method_to_endpoint[method_name]]

            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{endpoint}",
                    json="invalid_response_format",
                    status=200,
                )

                method = getattr(authenticated_v2_client, method_name)
                result = method(**kwargs)

                # Todos los métodos deberían devolver respuestas válidas aunque vacías
                assert result is not None

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_distributor_error_parsing(
        self, authenticated_v2_client, cups_code, distributor_code
    ):
        """Test parseo correcto de errores de distribuidor."""
        error_response = {
            "supplies": [],
            "distributorError": [
                {
                    "distributorCode": "2",
                    "distributorName": "E-DISTRIBUCIÓN",
                    "errorCode": "500",
                    "errorDescription": "Internal server error",
                },
                {
                    "distributorCode": "3",
                    "distributorName": "E-REDES",
                    "errorCode": "404",
                    "errorDescription": "Data not found",
                },
            ],
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=error_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            assert isinstance(result, SuppliesResponse)
            assert len(result.distributor_error) == 2
            assert result.distributor_error[0].error_code == "500"
            assert result.distributor_error[1].error_code == "404"


class TestV2ClientResponseValidation:
    """Tests para validación de respuestas V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_response_model_validation(
        self, authenticated_v2_client, sample_supply_data
    ):
        """Test validación completa de modelos de respuesta."""
        v2_response = {"supplies": [sample_supply_data], "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            # Verificar que la respuesta es un modelo Pydantic válido
            assert isinstance(result, SuppliesResponse)

            # Verificar que se puede serializar/deserializar
            json_str = result.model_dump_json(by_alias=True)
            restored = SuppliesResponse.model_validate_json(json_str)

            assert len(restored.supplies) == len(result.supplies)
            assert restored.supplies[0].cups == result.supplies[0].cups

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_response_schema_compliance(self, authenticated_v2_client):
        """Test cumplimiento de esquemas de respuesta."""
        response_classes = [
            SuppliesResponse,
            DistributorsResponse,
            ContractResponse,
            ConsumptionResponse,
            MaxPowerResponse,
        ]

        for response_class in response_classes:
            schema = response_class.model_json_schema()

            # Verificar estructura básica del esquema
            assert "properties" in schema
            assert "type" in schema
            assert schema["type"] == "object"

            # Verificar que tiene campos esperados
            properties = schema["properties"]
            assert "distributorError" in properties or "distributor_error" in properties


class TestV2vs1Compatibility:
    """Tests de compatibilidad entre V1 y V2."""

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_uses_different_endpoints(
        self, authenticated_v2_client, sample_supplies_response
    ):
        """Test que V2 usa endpoints diferentes a V1."""
        v2_response = {"supplies": sample_supplies_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            # Endpoint V2
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=v2_response,
                status=200,
            )

            authenticated_v2_client.get_supplies()

            # Verificar que se usó el endpoint V2
            request = rsps.calls[0].request
            assert "/get-supplies-v2" in request.url

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_structured_responses(
        self, authenticated_v2_client, sample_supplies_response
    ):
        """Test que V2 devuelve respuestas estructuradas."""
        v2_response = {"supplies": sample_supplies_response, "distributorError": []}

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=v2_response,
                status=200,
            )

            result = authenticated_v2_client.get_supplies()

            # V2 devuelve objetos Response estructurados, no listas simples
            assert isinstance(result, SuppliesResponse)
            assert hasattr(result, "supplies")
            assert hasattr(result, "distributor_error")

    @pytest.mark.unit
    @pytest.mark.client_v2
    def test_v2_has_reactive_data_method(self, authenticated_v2_client):
        """Test que V2 tiene método get_reactive_data que V1 no tiene."""
        # Verificar que el método existe
        assert hasattr(authenticated_v2_client, "get_reactive_data")
        assert callable(getattr(authenticated_v2_client, "get_reactive_data"))

        # Verificar que es específico de V2 (no está en la clase base abstracta)
        from datadis_python.client.base import BaseDatadisClient

        assert not hasattr(BaseDatadisClient, "get_reactive_data")
