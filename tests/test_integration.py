"""
Tests de integración para flujos completos del SDK de Datadis.

Estos tests validan:
- Flujos end-to-end completos
- Integración entre componentes
- Escenarios de uso real
- Compatibilidad V1 vs V2
- Workflows de múltiples pasos
"""

import pytest
import responses

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.client.v2.client import DatadisClientV2
from datadis_python.exceptions import AuthenticationError, DatadisError
from datadis_python.models.consumption import ConsumptionData
from datadis_python.models.contract import ContractData
from datadis_python.models.max_power import MaxPowerData
from datadis_python.models.supply import SupplyData
from datadis_python.utils.constants import (
    API_V1_ENDPOINTS,
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)


class TestCompleteV1Workflow:
    """Tests para flujo completo con cliente V1."""

    @pytest.mark.integration
    def test_complete_data_retrieval_workflow_v1(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
        sample_consumption_response,
        sample_contract_response,
        sample_max_power_response,
        sample_distributors_response,
    ):
        """Test flujo completo: autenticación → supplies → consumption → contract → max_power."""
        with responses.RequestsMock() as rsps:
            # 1. Autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # 2. Get distributors
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['distributors']}",
                json=sample_distributors_response,
                status=200,
            )

            # 3. Get supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            # 4. Get contract detail
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['contracts']}",
                json=sample_contract_response,
                status=200,
            )

            # 5. Get consumption
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=sample_consumption_response,
                status=200,
            )

            # 6. Get max power
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['max_power']}",
                json=sample_max_power_response,
                status=200,
            )

            # Ejecutar flujo completo
            with SimpleDatadisClientV1(**test_credentials) as client:
                # Paso 1: Autenticar
                auth_success = client.authenticate()
                assert auth_success is True
                assert client.token == test_token

                # Paso 2: Obtener distribuidores disponibles
                distributors = client.get_distributors()
                assert len(distributors) >= 1
                distributor_code = distributors[0].distributor_codes[0]

                # Paso 3: Obtener suministros
                supplies = client.get_supplies()
                assert len(supplies) >= 1
                assert isinstance(supplies[0], SupplyData)

                first_supply = supplies[0]
                cups = first_supply.cups
                assert cups.startswith("ES")

                # Paso 4: Obtener detalle de contrato
                contracts = client.get_contract_detail(
                    cups=cups, distributor_code=distributor_code
                )
                assert len(contracts) >= 1
                assert isinstance(contracts[0], ContractData)

                # Paso 5: Obtener datos de consumo
                consumption = client.get_consumption(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )
                assert len(consumption) >= 1
                assert isinstance(consumption[0], ConsumptionData)

                # Paso 6: Obtener potencia máxima
                max_power = client.get_max_power(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )
                assert len(max_power) >= 1
                assert isinstance(max_power[0], MaxPowerData)

                # Verificar que todos los requests se hicieron
                assert len(rsps.calls) == 6

    @pytest.mark.integration
    def test_v1_workflow_with_multiple_supplies(
        self,
        test_credentials,
        test_token,
    ):
        """Test flujo con múltiples suministros."""
        multiple_supplies = [
            {
                "address": "CALLE EJEMPLO 123",
                "cups": "ES0031607515707001RC0F",
                "postalCode": "28001",
                "province": "MADRID",
                "municipality": "MADRID",
                "distributor": "E-DISTRIBUCIÓN",
                "validDateFrom": "2023/01/01",
                "validDateTo": None,
                "pointType": 2,
                "distributorCode": "2",
            },
            {
                "address": "AVENIDA LIBERTAD 456",
                "cups": "ES987654321098765432109A",
                "postalCode": "41001",
                "province": "SEVILLA",
                "municipality": "SEVILLA",
                "distributor": "E-DISTRIBUCIÓN",
                "validDateFrom": "2023/01/01",
                "validDateTo": None,
                "pointType": 2,
                "distributorCode": "2",
            },
        ]

        consumption_response = [
            {
                "cups": "ES0031607515707001RC0F",
                "date": "2024/01/15",
                "time": "01:00",
                "consumptionKWh": 0.125,
                "obtainMethod": "Real",
            }
        ]

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=multiple_supplies,
                status=200,
            )

            # Consumption para cada CUPS
            for supply in multiple_supplies:
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                    json=consumption_response,
                    status=200,
                )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()

                supplies = client.get_supplies()
                assert len(supplies) == 2

                # Obtener consumo para cada suministro
                all_consumption = []
                for supply in supplies:
                    consumption = client.get_consumption(
                        cups=supply.cups,
                        distributor_code=supply.distributor_code,
                        date_from="2024/01",
                        date_to="2024/01",
                    )
                    all_consumption.extend(consumption)

                assert len(all_consumption) == 2  # Uno por cada CUPS

    @pytest.mark.integration
    def test_v1_workflow_error_recovery(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
    ):
        """Test recuperación de errores en flujo V1."""
        with responses.RequestsMock() as rsps:
            # Auth exitoso
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Primera request de supplies falla
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Temporary error"},
                status=503,
            )

            # Segunda request de supplies exitosa
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()

                # Primera intención falla
                with pytest.raises(Exception):  # APIError o DatadisError
                    client.get_supplies()

                # Segunda intención exitosa
                supplies = client.get_supplies()
                assert len(supplies) >= 1


class TestCompleteV2Workflow:
    """Tests para flujo completo con cliente V2."""

    @pytest.mark.integration
    def test_complete_data_retrieval_workflow_v2(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
        sample_consumption_response,
        sample_contract_response,
        sample_max_power_response,
    ):
        """Test flujo completo V2 con respuestas estructuradas."""
        # Respuestas V2 estructuradas
        supplies_v2_response = {
            "supplies": sample_supplies_response,
            "distributorError": [],
        }

        distributors_v2_response = {
            "distExistenceUser": {"distributorCodes": ["2"]},
            "distributorError": [],
        }

        contracts_v2_response = {
            "contract": sample_contract_response,
            "distributorError": [],
        }

        consumption_v2_response = {
            "timeCurve": sample_consumption_response,
            "distributorError": [],
        }

        max_power_v2_response = {
            "maxPower": sample_max_power_response,
            "distributorError": [],
        }

        reactive_data_response = {
            "reactiveEnergy": {
                "cups": "ES0031607515707001RC0F",
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
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # V2 endpoints
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['distributors']}",
                json=distributors_v2_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=supplies_v2_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['contracts']}",
                json=contracts_v2_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=consumption_v2_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['max_power']}",
                json=max_power_v2_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=reactive_data_response,
                status=200,
            )

            with DatadisClientV2(**test_credentials) as client:
                # Autenticar
                client.authenticate()

                # Obtener distribuidores
                distributors_response = client.get_distributors()
                assert (
                    len(distributors_response.dist_existence_user["distributorCodes"])
                    >= 1
                )
                distributor_code = distributors_response.dist_existence_user[
                    "distributorCodes"
                ][0]

                # Obtener suministros
                supplies_response = client.get_supplies()
                assert len(supplies_response.supplies) >= 1
                cups = supplies_response.supplies[0].cups

                # Obtener contrato
                contract_response = client.get_contract_detail(
                    cups=cups, distributor_code=distributor_code
                )
                assert len(contract_response.contract) >= 1

                # Obtener consumo (fechas mensuales para V2)
                consumption_response = client.get_consumption(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )
                assert len(consumption_response.time_curve) >= 1

                # Obtener potencia máxima
                max_power_response = client.get_max_power(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )
                assert len(max_power_response.max_power) >= 1

                # Obtener datos reactivos (específico de V2)
                reactive_data = client.get_reactive_data(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )
                assert len(reactive_data) >= 1

    @pytest.mark.integration
    def test_v2_workflow_with_distributor_errors(
        self,
        test_credentials,
        test_token,
    ):
        """Test flujo V2 con errores de distribuidor."""
        supplies_with_errors = {
            "supplies": [],
            "distributorError": [
                {
                    "distributorCode": "2",
                    "distributorName": "E-DISTRIBUCIÓN",
                    "errorCode": "404",
                    "errorDescription": "No data found for this period",
                }
            ],
        }

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Supplies con errores
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json=supplies_with_errors,
                status=200,
            )

            with DatadisClientV2(**test_credentials) as client:
                client.authenticate()

                supplies_response = client.get_supplies()

                # No hay suministros debido al error
                assert len(supplies_response.supplies) == 0

                # Pero hay información del error
                assert len(supplies_response.distributor_error) == 1
                assert supplies_response.distributor_error[0].error_code == "404"


class TestV1vsV2Compatibility:
    """Tests de compatibilidad entre V1 y V2."""

    @pytest.mark.integration
    def test_v1_v2_same_data_different_format(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
        sample_consumption_response,
    ):
        """Test que V1 y V2 devuelven los mismos datos en diferentes formatos."""
        # Respuesta V2 estructurada
        consumption_v2_response = {
            "timeCurve": sample_consumption_response,
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            # Auth para ambos
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # V1 supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            # V2 supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json={"supplies": sample_supplies_response, "distributorError": []},
                status=200,
            )

            # V1 consumption
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=sample_consumption_response,
                status=200,
            )

            # V2 consumption
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=consumption_v2_response,
                status=200,
            )

            # Comparar V1 vs V2
            with SimpleDatadisClientV1(**test_credentials) as v1_client:
                v1_client.authenticate()
                v1_supplies = v1_client.get_supplies()
                v1_consumption = v1_client.get_consumption(
                    cups=v1_supplies[0].cups,
                    distributor_code=v1_supplies[0].distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )

            with DatadisClientV2(**test_credentials) as v2_client:
                v2_client.authenticate()
                v2_supplies_response = v2_client.get_supplies()
                v2_consumption_response = v2_client.get_consumption(
                    cups=v2_supplies_response.supplies[0].cups,
                    distributor_code=v2_supplies_response.supplies[0].distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )

            # Comparar datos de suministros
            assert len(v1_supplies) == len(v2_supplies_response.supplies)
            assert v1_supplies[0].cups == v2_supplies_response.supplies[0].cups

            # Comparar datos de consumo
            assert len(v1_consumption) == len(v2_consumption_response.time_curve)
            assert v1_consumption[0].cups == v2_consumption_response.time_curve[0].cups

    @pytest.mark.integration
    def test_v2_has_additional_features(
        self,
        test_credentials,
        test_token,
    ):
        """Test que V2 tiene funcionalidades adicionales que V1 no tiene."""
        reactive_data_response = {
            "reactiveEnergy": {
                "cups": "ES0031607515707001RC0F",
                "energy": [{"date": "2024/01", "energy_p1": 10.5}],
            },
            "distributorError": [],
        }

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Reactive data (solo V2)
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['reactive_data']}",
                json=reactive_data_response,
                status=200,
            )

            with DatadisClientV2(**test_credentials) as v2_client:
                v2_client.authenticate()

                # V2 tiene get_reactive_data
                assert hasattr(v2_client, "get_reactive_data")

                reactive_data = v2_client.get_reactive_data(
                    cups="ES0031607515707001RC0F",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/01",
                )

                assert len(reactive_data) >= 1

            # V1 no tiene get_reactive_data
            with SimpleDatadisClientV1(**test_credentials) as v1_client:
                assert not hasattr(v1_client, "get_reactive_data")


class TestErrorRecoveryWorkflows:
    """Tests para flujos de recuperación de errores."""

    @pytest.mark.integration
    def test_authentication_token_renewal_workflow(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
    ):
        """Test renovación automática de token durante workflow."""
        with responses.RequestsMock() as rsps:
            # Primera auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Request falla con 401 (token expirado)
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json={"error": "Token expired"},
                status=401,
            )

            # Segunda auth (renovación automática)
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=f"{test_token}_renewed",
                status=200,
            )

            # Request exitoso con nuevo token
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()
                original_token = client.token

                # Esta request debería renovar el token automáticamente
                supplies = client.get_supplies()

                # Verificar que el token se renovó
                assert client.token != original_token
                assert client.token == f"{test_token}_renewed"
                assert len(supplies) >= 1

    @pytest.mark.integration
    def test_partial_failure_workflow(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
    ):
        """Test workflow con fallos parciales en algunos endpoints."""
        consumption_error_response = {
            "timeCurve": [],
            "distributorError": [
                {
                    "distributorCode": "2",
                    "distributorName": "E-DISTRIBUCIÓN",
                    "errorCode": "503",
                    "errorDescription": "Service temporarily unavailable",
                }
            ],
        }

        with responses.RequestsMock() as rsps:
            # Auth exitoso
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Supplies exitoso
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json={"supplies": sample_supplies_response, "distributorError": []},
                status=200,
            )

            # Consumption falla parcialmente
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                json=consumption_error_response,
                status=200,
            )

            with DatadisClientV2(**test_credentials) as client:
                client.authenticate()

                # Supplies funciona
                supplies_response = client.get_supplies()
                assert len(supplies_response.supplies) >= 1

                # Consumption falla pero no lanza excepción
                consumption_response = client.get_consumption(
                    cups=supplies_response.supplies[0].cups,
                    distributor_code=supplies_response.supplies[0].distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )

                # No hay datos pero hay información del error
                assert len(consumption_response.time_curve) == 0
                assert len(consumption_response.distributor_error) == 1
                assert consumption_response.distributor_error[0].error_code == "503"


class TestLongRunningWorkflows:
    """Tests para workflows de larga duración."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_months_data_retrieval(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
    ):
        """Test obtención de datos para múltiples meses."""
        months = ["2024/01", "2024/02", "2024/03"]

        consumption_responses = []
        for month in months:
            consumption_responses.append(
                {
                    "timeCurve": [
                        {
                            "cups": "ES0031607515707001RC0F",
                            "date": f"{month}/15",
                            "time": "12:00",
                            "consumptionKWh": 1.5,
                            "obtainMethod": "Real",
                        }
                    ],
                    "distributorError": [],
                }
            )

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['supplies']}",
                json={"supplies": sample_supplies_response, "distributorError": []},
                status=200,
            )

            # Consumption para cada mes
            for response in consumption_responses:
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V2_ENDPOINTS['consumption']}",
                    json=response,
                    status=200,
                )

            with DatadisClientV2(**test_credentials) as client:
                client.authenticate()

                supplies_response = client.get_supplies()
                cups = supplies_response.supplies[0].cups
                distributor_code = supplies_response.supplies[0].distributor_code

                # Obtener datos para múltiples meses
                all_consumption = []
                for month in months:
                    consumption_response = client.get_consumption(
                        cups=cups,
                        distributor_code=distributor_code,
                        date_from=month,
                        date_to=month,
                    )
                    all_consumption.extend(consumption_response.time_curve)

                assert len(all_consumption) == 3  # Uno por mes

                # Verificar que se hicieron todas las requests
                assert len(rsps.calls) == 5  # Auth + supplies + 3 consumption

    @pytest.mark.integration
    def test_session_persistence_across_multiple_requests(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
        sample_consumption_response,
    ):
        """Test persistencia de sesión a través de múltiples requests."""
        with responses.RequestsMock() as rsps:
            # Una sola autenticación
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Múltiples requests de datos
            for _ in range(5):
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                    json=sample_supplies_response,
                    status=200,
                )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()

                # Hacer múltiples requests sin re-autenticar
                for i in range(5):
                    supplies = client.get_supplies()
                    assert len(supplies) >= 1

                # Solo debería haber una autenticación
                auth_calls = [
                    call for call in rsps.calls if "nikola-auth" in call.request.url
                ]
                assert len(auth_calls) == 1


class TestRealWorldScenarios:
    """Tests para escenarios del mundo real."""

    @pytest.mark.integration
    def test_daily_energy_monitoring_scenario(
        self,
        test_credentials,
        test_token,
        sample_supplies_response,
    ):
        """Test escenario de monitoreo diario de energía."""
        # Simular datos de consumo horario para un día
        hourly_consumption = []
        for hour in range(24):
            hourly_consumption.append(
                {
                    "cups": "ES0031607515707001RC0F",
                    "date": "2024/01/15",
                    "time": f"{hour:02d}:00",
                    "consumptionKWh": 0.5 + (hour * 0.05),  # Consumo variable
                    "obtainMethod": "Real",
                }
            )

        with responses.RequestsMock() as rsps:
            # Setup
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=sample_supplies_response,
                status=200,
            )

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                json=hourly_consumption,
                status=200,
            )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()

                supplies = client.get_supplies()
                primary_supply = supplies[0]

                consumption = client.get_consumption(
                    cups=primary_supply.cups,
                    distributor_code=primary_supply.distributor_code,
                    date_from="2024/01",
                    date_to="2024/01",
                )

                # Análisis de datos
                total_consumption = sum(item.consumption_kwh for item in consumption)
                peak_hour = max(consumption, key=lambda x: x.consumption_kwh)
                off_peak_hours = [
                    item for item in consumption if item.consumption_kwh < 0.75
                ]

                # Verificaciones
                assert len(consumption) == 24  # 24 horas
                assert total_consumption > 0
                assert peak_hour.consumption_kwh >= 1.0  # Pico de consumo
                assert len(off_peak_hours) > 0  # Horas de bajo consumo

    @pytest.mark.integration
    def test_multi_property_management_scenario(
        self,
        test_credentials,
        test_token,
    ):
        """Test escenario de gestión de múltiples propiedades."""
        # Múltiples propiedades con diferentes distribuidores
        multi_supplies = [
            {
                "address": "PROPIEDAD 1",
                "cups": "ES0031607515707001RC0F",
                "postalCode": "28001",
                "province": "MADRID",
                "municipality": "MADRID",
                "distributor": "E-DISTRIBUCIÓN",
                "validDateFrom": "2023/01/01",
                "pointType": 2,
                "distributorCode": "2",
            },
            {
                "address": "PROPIEDAD 2",
                "cups": "ES987654321098765432109B",
                "postalCode": "48001",
                "province": "BIZKAIA",
                "municipality": "BILBAO",
                "distributor": "VIESGO",
                "validDateFrom": "2023/01/01",
                "pointType": 2,
                "distributorCode": "1",
            },
        ]

        with responses.RequestsMock() as rsps:
            # Auth
            rsps.add(
                responses.POST,
                f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                body=test_token,
                status=200,
            )

            # Supplies
            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
                json=multi_supplies,
                status=200,
            )

            # Consumption para cada propiedad
            for supply in multi_supplies:
                rsps.add(
                    responses.GET,
                    f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
                    json=[
                        {
                            "cups": supply["cups"],
                            "date": "2024/01/15",
                            "time": "12:00",
                            "consumptionKWh": 2.5,
                            "obtainMethod": "Real",
                        }
                    ],
                    status=200,
                )

            with SimpleDatadisClientV1(**test_credentials) as client:
                client.authenticate()

                supplies = client.get_supplies()
                assert len(supplies) == 2

                # Agrupar por distribuidor
                by_distributor = {}
                for supply in supplies:
                    dist_code = supply.distributor_code
                    if dist_code not in by_distributor:
                        by_distributor[dist_code] = []
                    by_distributor[dist_code].append(supply)

                # Obtener consumo por distribuidor
                total_consumption_by_distributor = {}
                for dist_code, dist_supplies in by_distributor.items():
                    total_consumption = 0
                    for supply in dist_supplies:
                        consumption = client.get_consumption(
                            cups=supply.cups,
                            distributor_code=supply.distributor_code,
                            date_from="2024/01",
                            date_to="2024/01",
                        )
                        total_consumption += sum(
                            item.consumption_kwh for item in consumption
                        )

                    total_consumption_by_distributor[dist_code] = total_consumption

                # Verificaciones
                assert len(by_distributor) == 2  # Dos distribuidores
                assert "1" in by_distributor  # Viesgo
                assert "2" in by_distributor  # E-Distribución
                assert all(
                    consumption > 0
                    for consumption in total_consumption_by_distributor.values()
                )
