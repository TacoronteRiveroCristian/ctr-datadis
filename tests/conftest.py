"""
Configuración global de pytest para el SDK de Datadis.

Este módulo define fixtures reutilizables y configuración para todos los tests.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest
import responses
from freezegun import freeze_time

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.client.v2.client import DatadisClientV2
from datadis_python.utils.constants import (
    API_V1_ENDPOINTS,
    API_V2_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)


# Test credentials
TEST_USERNAME = "12345678A"
TEST_PASSWORD = "test_password"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"

# Time fixtures
TEST_DATE_STR = "2024-01-15"
TEST_DATE = datetime(2024, 1, 15)


@pytest.fixture
def test_credentials():
    """Credenciales de prueba para autenticación."""
    return {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }


@pytest.fixture
def test_token():
    """Token JWT de prueba."""
    return TEST_TOKEN


@pytest.fixture
def frozen_time():
    """Fixture para tiempo congelado en tests."""
    with freeze_time(TEST_DATE_STR):
        yield TEST_DATE


@pytest.fixture
def mock_auth_success():
    """Mock de autenticación exitosa."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
            body=TEST_TOKEN,
            status=200,
            content_type="text/plain",
        )
        yield rsps


@pytest.fixture
def mock_auth_failure():
    """Mock de autenticación fallida."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
            json={"error": "Invalid credentials"},
            status=401,
        )
        yield rsps


@pytest.fixture
def v1_client(test_credentials):
    """Cliente V1 con credenciales de prueba."""
    return SimpleDatadisClientV1(
        username=test_credentials["username"],
        password=test_credentials["password"],
        timeout=30,
        retries=1,
    )


@pytest.fixture
def v2_client(test_credentials):
    """Cliente V2 con credenciales de prueba."""
    return DatadisClientV2(
        username=test_credentials["username"],
        password=test_credentials["password"],
        timeout=30,
        retries=1,
    )


@pytest.fixture
def authenticated_v1_client(v1_client, mock_auth_success):
    """Cliente V1 ya autenticado."""
    v1_client.authenticate()
    return v1_client


@pytest.fixture
def authenticated_v2_client(v2_client, mock_auth_success):
    """Cliente V2 ya autenticado."""
    v2_client.authenticate()
    return v2_client


# Fixtures de datos de prueba
@pytest.fixture
def sample_supply_data():
    """Datos de ejemplo para un punto de suministro."""
    return {
        "address": "CALLE EJEMPLO 123",
        "cups": "ES0123456789012345678901AB",
        "postalCode": "28001",
        "province": "MADRID",
        "municipality": "MADRID",
        "distributor": "E-DISTRIBUCION REDES DIGITALES S.L.U.",
        "validDateFrom": "2023/01/01",
        "validDateTo": None,
        "pointType": 2,
        "distributorCode": "2",
    }


@pytest.fixture
def sample_supplies_response(sample_supply_data):
    """Respuesta de ejemplo para get-supplies."""
    return [sample_supply_data]


@pytest.fixture
def sample_consumption_data():
    """Datos de ejemplo para consumo."""
    return {
        "cups": "ES0123456789012345678901AB",
        "date": "2024/01/15",
        "time": "01:00",
        "consumptionKWh": 0.125,
        "obtainMethod": "Real",
        "surplusEnergyKWh": None,
        "generationEnergyKWh": None,
        "selfConsumptionEnergyKWh": None,
    }


@pytest.fixture
def sample_consumption_response(sample_consumption_data):
    """Respuesta de ejemplo para get-consumption-data."""
    # Generar 24 horas de datos
    consumption_list = []
    for hour in range(24):
        data = sample_consumption_data.copy()
        data["time"] = f"{hour:02d}:00"
        data["consumptionKWh"] = 0.125 + (hour * 0.001)  # Variación pequeña
        consumption_list.append(data)
    return consumption_list


@pytest.fixture
def sample_contract_data():
    """Datos de ejemplo para contrato."""
    return {
        "cups": "ES0123456789012345678901AB",
        "distributor": "E-DISTRIBUCION REDES DIGITALES S.L.U.",
        "marketer": "ENDESA ENERGÍA XXI S.L.U.",
        "tension": "BT",
        "accessFare": "2.0TD",
        "province": "MADRID",
        "municipality": "MADRID",
        "postalCode": "28001",
        "contractedPowerkW": [3.45, 3.45],
        "timeDiscrimination": None,
        "modePowerControl": "ICP",
        "startDate": "2023/01/01",
        "endDate": None,
        "codeFare": "2.0TD",
    }


@pytest.fixture
def sample_contract_response(sample_contract_data):
    """Respuesta de ejemplo para get-contract-detail."""
    return [sample_contract_data]


@pytest.fixture
def sample_max_power_data():
    """Datos de ejemplo para potencia máxima."""
    return {
        "cups": "ES0123456789012345678901AB",
        "date": "2024/01/15",
        "time": "20:00",
        "maxPower": 2.15,
        "period": "P1",
    }


@pytest.fixture
def sample_max_power_response(sample_max_power_data):
    """Respuesta de ejemplo para get-max-power."""
    return [sample_max_power_data]


@pytest.fixture
def sample_distributor_data():
    """Datos de ejemplo para distribuidor."""
    return {
        "distributorCodes": ["2", "3", "5"]
    }


@pytest.fixture
def sample_distributors_response(sample_distributor_data):
    """Respuesta de ejemplo para get-distributors."""
    return [sample_distributor_data]


@pytest.fixture
def sample_reactive_data():
    """Datos de ejemplo para energía reactiva (V2)."""
    return {
        "cups": "ES0123456789012345678901AB",
        "date": "2024/01/15",
        "time": "01:00",
        "reactiveEnergyQ1": 0.025,
        "reactiveEnergyQ2": 0.000,
        "reactiveEnergyQ3": 0.000,
        "reactiveEnergyQ4": 0.010,
        "obtainMethod": "Real",
    }


@pytest.fixture
def sample_reactive_response(sample_reactive_data):
    """Respuesta de ejemplo para get-reactive-data-v2."""
    return [sample_reactive_data]


# Fixtures para mocking completo de APIs
@pytest.fixture
def mock_v1_api_responses(
    mock_auth_success,
    sample_supplies_response,
    sample_consumption_response,
    sample_contract_response,
    sample_max_power_response,
    sample_distributors_response,
):
    """Mock completo de todas las respuestas V1 de la API."""
    with responses.RequestsMock() as rsps:
        # Auth
        rsps.add(
            responses.POST,
            f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
            body=TEST_TOKEN,
            status=200,
        )

        # Supplies
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['supplies']}",
            json=sample_supplies_response,
            status=200,
        )

        # Consumption
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['consumption']}",
            json=sample_consumption_response,
            status=200,
        )

        # Contracts
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['contracts']}",
            json=sample_contract_response,
            status=200,
        )

        # Max Power
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['max_power']}",
            json=sample_max_power_response,
            status=200,
        )

        # Distributors
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}{API_V1_ENDPOINTS['distributors']}",
            json=sample_distributors_response,
            status=200,
        )

        yield rsps


@pytest.fixture
def mock_v2_api_responses(
    mock_auth_success,
    sample_supplies_response,
    sample_consumption_response,
    sample_contract_response,
    sample_max_power_response,
    sample_distributors_response,
    sample_reactive_response,
):
    """Mock completo de todas las respuestas V2 de la API."""
    with responses.RequestsMock() as rsps:
        # Auth
        rsps.add(
            responses.POST,
            f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
            body=TEST_TOKEN,
            status=200,
        )

        # V2 endpoints (mismo formato de datos pero endpoints diferentes)
        for endpoint_name, endpoint_path in API_V2_ENDPOINTS.items():
            if endpoint_name == "supplies":
                response_data = sample_supplies_response
            elif endpoint_name == "consumption":
                response_data = sample_consumption_response
            elif endpoint_name == "contracts":
                response_data = sample_contract_response
            elif endpoint_name == "max_power":
                response_data = sample_max_power_response
            elif endpoint_name == "distributors":
                response_data = sample_distributors_response
            elif endpoint_name == "reactive_data":
                response_data = sample_reactive_response
            else:
                response_data = {}

            rsps.add(
                responses.GET,
                f"{DATADIS_API_BASE}{endpoint_path}",
                json=response_data,
                status=200,
            )

        yield rsps


# Fixtures para testing de errores
@pytest.fixture
def mock_api_error_responses():
    """Mock de respuestas de error de la API."""
    error_responses = {
        400: {"error": "Bad Request", "message": "Parámetros inválidos"},
        401: {"error": "Unauthorized", "message": "Token inválido o expirado"},
        403: {"error": "Forbidden", "message": "Acceso denegado"},
        404: {"error": "Not Found", "message": "Recurso no encontrado"},
        500: {"error": "Internal Server Error", "message": "Error del servidor"},
        502: {"error": "Bad Gateway", "message": "Gateway error"},
        503: {"error": "Service Unavailable", "message": "Servicio no disponible"},
    }
    return error_responses


@pytest.fixture
def mock_timeout_response():
    """Mock de timeout de request."""
    import requests

    def mock_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Request timed out")

    return mock_timeout


# Utility fixtures
@pytest.fixture
def cups_code():
    """Código CUPS válido para tests."""
    return "ES0123456789012345678901AB"


@pytest.fixture
def distributor_code():
    """Código de distribuidor válido para tests."""
    return "2"


@pytest.fixture
def date_range():
    """Rango de fechas para tests."""
    return {
        "date_from": "2024/01/01",
        "date_to": "2024/01/31",
    }


@pytest.fixture
def measurement_types():
    """Tipos de medición disponibles."""
    return {
        "consumption": 0,
        "generation": 1,
        "reactive": 2,
    }


@pytest.fixture
def point_types():
    """Tipos de punto de medida disponibles."""
    return {
        "border": 1,
        "consumption": 2,
        "generation": 3,
        "auxiliary_services": 4,
        "auxiliary_services_alt": 5,
    }


# Pytest configuration markers
def pytest_configure(config):
    """Configuración de pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "models: Pydantic model tests")
    config.addinivalue_line("markers", "client_v1: V1 client tests")
    config.addinivalue_line("markers", "client_v2: V2 client tests")
    config.addinivalue_line("markers", "utils: Utility function tests")
    config.addinivalue_line("markers", "errors: Error handling tests")


# Helper functions para tests
@pytest.fixture
def assert_valid_cups():
    """Helper para validar códigos CUPS."""

    def _assert_valid_cups(cups: str):
        assert len(cups) == 22, f"CUPS debe tener 22 caracteres, tiene {len(cups)}"
        assert cups.startswith("ES"), "CUPS debe empezar con 'ES'"
        assert cups[2:].replace("AB", "").isdigit(), "CUPS contiene caracteres inválidos"

    return _assert_valid_cups


@pytest.fixture
def assert_valid_date_format():
    """Helper para validar formato de fecha."""

    def _assert_valid_date_format(date_str: str):
        assert len(date_str) == 10, f"Fecha debe tener formato YYYY/MM/DD"
        assert date_str[4] == "/" and date_str[7] == "/", "Fecha debe usar '/' como separador"
        year, month, day = date_str.split("/")
        assert year.isdigit() and len(year) == 4, "Año inválido"
        assert month.isdigit() and 1 <= int(month) <= 12, "Mes inválido"
        assert day.isdigit() and 1 <= int(day) <= 31, "Día inválido"

    return _assert_valid_date_format


@pytest.fixture
def assert_valid_time_format():
    """Helper para validar formato de hora."""

    def _assert_valid_time_format(time_str: str):
        assert len(time_str) == 5, f"Hora debe tener formato HH:MM"
        assert time_str[2] == ":", "Hora debe usar ':' como separador"
        hour, minute = time_str.split(":")
        assert hour.isdigit() and 0 <= int(hour) <= 23, "Hora inválida"
        assert minute.isdigit() and 0 <= int(minute) <= 59, "Minuto inválido"

    return _assert_valid_time_format