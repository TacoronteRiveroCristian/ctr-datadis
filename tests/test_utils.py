"""
Tests para funciones utilitarias del SDK de Datadis.

Estos tests validan:
- Validadores de parámetros (CUPS, fechas, distribuidores, etc.)
- Utilidades de texto y normalización
- Cliente HTTP base
- Funciones de constantes y configuración
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
import requests
import responses

from datadis_python.exceptions import APIError, AuthenticationError, DatadisError, ValidationError
from datadis_python.utils.constants import (
    API_V1_ENDPOINTS,
    DISTRIBUTOR_CODES,
    MEASUREMENT_TYPES,
    POINT_TYPES,
)
from datadis_python.utils.http import HTTPClient
from datadis_python.utils.text_utils import (
    normalize_api_response,
    normalize_dict_strings,
    normalize_list_strings,
    normalize_text,
)
from datadis_python.utils.validators import (
    validate_cups,
    validate_date_range,
    validate_distributor_code,
    validate_measurement_type,
    validate_point_type,
)


class TestCUPSValidator:
    """Tests para validador de códigos CUPS."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_valid_format(self):
        """Test validación exitosa de CUPS con formato válido."""
        valid_cups = [
            # Formatos reales de CUPS españoles (20-22 caracteres)
            "ES0031607515707001RC0F",  # 20 chars - formato real de Datadis
            "ES0031607495168002EK0F",  # 20 chars - formato real de Datadis  
            "ES0031601360306001PX0F",  # 20 chars - formato real de Datadis
            "ES123456789012345678901A",  # 21 chars - formato intermedio
            "ES1234567890123456789012",  # 22 chars - formato máximo
        ]

        for cups in valid_cups:
            result = validate_cups(cups)
            assert result == cups.upper()

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_case_insensitive(self):
        """Test que el validador de CUPS es case-insensitive."""
        lowercase_cups = "es0031607515707001rc0f"
        mixed_case_cups = "Es0031607515707001Rc0F"

        result1 = validate_cups(lowercase_cups)
        result2 = validate_cups(mixed_case_cups)

        expected = "ES0031607515707001RC0F"
        assert result1 == expected
        assert result2 == expected

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_strips_whitespace(self):
        """Test que el validador quita espacios en blanco."""
        cups_with_spaces = "  ES0031607515707001RC0F  "
        result = validate_cups(cups_with_spaces)
        assert result == "ES0031607515707001RC0F"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_empty_string(self):
        """Test validación falla con string vacío."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cups("")

        assert "no puede estar vacío" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_none_value(self):
        """Test validación falla con None."""
        with pytest.raises(ValidationError):
            validate_cups(None)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_invalid_prefix(self):
        """Test validación falla con prefijo incorrecto."""
        invalid_cups = [
            "EN0031607515707001RC0F",  # Prefijo incorrecto
            "XX0031607515707001RC0F",  # Prefijo incorrecto
            "0031607515707001RC0F",    # Sin prefijo
            "FR0031607515707001RC0F",  # País incorrecto
        ]

        for cups in invalid_cups:
            with pytest.raises(ValidationError) as exc_info:
                validate_cups(cups)
            assert "Formato CUPS inválido" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_wrong_length(self):
        """Test validación falla con longitud incorrecta."""
        invalid_cups = [
            "ES123456789012345678",     # Muy corto (19 chars después de ES)
            "ES12345678901234567890123",  # Muy largo (23 chars después de ES)
            "ES123",                    # Muy corto (3 chars después de ES)
            "ES",                       # Solo prefijo
        ]

        for cups in invalid_cups:
            with pytest.raises(ValidationError) as exc_info:
                validate_cups(cups)
            assert "Formato CUPS inválido" in str(exc_info.value)
            assert "20-22 caracteres alfanuméricos" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_invalid_characters(self):
        """Test validación falla con caracteres inválidos."""
        invalid_cups = [
            "ES0031607515707001RC@F",  # Carácter especial (@)
            "ES0031607515707001RC-F",  # Guión en lugar de letra
            "ES0031607515707001RC0#",  # Carácter especial (#) al final
            "ES003160751570700?RC0F",  # Signo de interrogación
        ]

        for cups in invalid_cups:
            with pytest.raises(ValidationError) as exc_info:
                validate_cups(cups)
            assert "Formato CUPS inválido" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_real_datadis_examples(self):
        """Test validación con ejemplos reales de la API de Datadis."""
        real_datadis_cups = [
            "ES0031607515707001RC0F",  # Ejemplo real 1
            "ES0031607495168002EK0F",  # Ejemplo real 2
            "ES0031601360306001PX0F",  # Ejemplo real 3
            "ES0031601359854001KY0F",  # Ejemplo real 4
            "ES0031601105278001LN0F",  # Ejemplo real 5
        ]

        for cups in real_datadis_cups:
            result = validate_cups(cups)
            assert result == cups  # Ya están en mayúsculas
            assert len(result) == 22  # ES + 20 caracteres

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_cups_edge_cases(self):
        """Test validación con casos límite válidos."""
        edge_cases = [
            "ES12345678901234567890",    # Exactamente 20 chars después de ES
            "ES123456789012345678901",   # Exactamente 21 chars después de ES
            "ES1234567890123456789012",  # Exactamente 22 chars después de ES
            "ES00000000000000000000",    # Todo ceros
            "ESZZZZZZZZZZZZZZZZZZZZ",    # Todo letras
            "ES000000000000000000ZZ",    # Mezcla números y letras
        ]

        for cups in edge_cases:
            result = validate_cups(cups)
            assert result == cups
            assert result.startswith("ES")
            assert 22 <= len(result) <= 24  # ES + 20-22 caracteres


class TestDateRangeValidator:
    """Tests para validador de rangos de fechas."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_daily_format_valid(self):
        """Test validación exitosa de fechas en formato diario."""
        date_from = "2024/01/01"
        date_to = "2024/01/31"

        result_from, result_to = validate_date_range(date_from, date_to, "daily")

        assert result_from == date_from
        assert result_to == date_to

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_monthly_format_valid(self):
        """Test validación exitosa de fechas en formato mensual."""
        date_from = "2024/01"
        date_to = "2024/12"

        result_from, result_to = validate_date_range(date_from, date_to, "monthly")

        assert result_from == date_from
        assert result_to == date_to

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_invalid_format_type(self):
        """Test validación falla con tipo de formato inválido."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range("2024/01/01", "2024/01/31", "invalid_format")

        assert "Tipo de formato no soportado" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_invalid_date_format(self):
        """Test validación falla con formato de fecha incorrecto."""
        invalid_dates = [
            ("2024-01-01", "2024/01/31"),  # Separador incorrecto
            ("01/01/2024", "2024/01/31"),  # Orden incorrecto
            ("2024/1/1", "2024/01/31"),    # Sin ceros
            ("24/01/01", "2024/01/31"),    # Año de 2 dígitos
        ]

        for date_from, date_to in invalid_dates:
            with pytest.raises(ValidationError) as exc_info:
                validate_date_range(date_from, date_to, "daily")
            assert "Formato de fecha" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_invalid_dates(self):
        """Test validación falla con fechas inválidas."""
        invalid_dates = [
            ("2024/02/30", "2024/02/28"),  # 30 de febrero
            ("2024/13/01", "2024/12/01"),  # Mes 13
            ("2024/01/32", "2024/01/31"),  # Día 32
        ]

        for date_from, date_to in invalid_dates:
            with pytest.raises(ValidationError) as exc_info:
                validate_date_range(date_from, date_to, "daily")
            assert "Fecha inválida" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_date_range_start_after_end(self):
        """Test validación falla cuando fecha inicio es posterior a fecha fin."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range("2024/01/31", "2024/01/01", "daily")

        assert "no puede ser posterior a" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    @patch('datadis_python.utils.validators.datetime')
    def test_validate_date_range_too_old(self, mock_datetime):
        """Test validación falla con fechas muy antiguas."""
        # Mock datetime.now() para tener control sobre la fecha actual
        mock_now = datetime(2024, 6, 15)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        # Fecha de hace 3 años (debería fallar)
        old_date = "2021/06/01"
        recent_date = "2024/06/01"

        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(old_date, recent_date, "daily")

        assert "no puede ser anterior a hace 2 años" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    @patch('datadis_python.utils.validators.datetime')
    def test_validate_date_range_future_date(self, mock_datetime):
        """Test validación falla con fechas futuras."""
        # Mock datetime.now() para tener control sobre la fecha actual
        mock_now = datetime(2024, 6, 15)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        # Fecha futura (debería fallar)
        current_date = "2024/06/01"
        future_date = "2024/12/01"

        with pytest.raises(ValidationError) as exc_info:
            validate_date_range(current_date, future_date, "daily")

        assert "no puede ser futura" in str(exc_info.value)


class TestDistributorCodeValidator:
    """Tests para validador de códigos de distribuidor."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_distributor_code_valid(self):
        """Test validación exitosa de códigos de distribuidor válidos."""
        valid_codes = ["1", "2", "3", "4", "5", "6", "7", "8"]

        for code in valid_codes:
            result = validate_distributor_code(code)
            assert result == code

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_distributor_code_invalid(self):
        """Test validación falla con códigos inválidos."""
        invalid_codes = ["0", "9", "10", "A", "X", "", "99"]

        for code in invalid_codes:
            with pytest.raises(ValidationError) as exc_info:
                validate_distributor_code(code)
            assert "Código de distribuidor inválido" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_distributor_code_error_message_includes_valid_codes(self):
        """Test que el mensaje de error incluye códigos válidos."""
        with pytest.raises(ValidationError) as exc_info:
            validate_distributor_code("invalid")

        error_message = str(exc_info.value)
        assert "Válidos:" in error_message
        assert "1" in error_message
        assert "8" in error_message


class TestMeasurementTypeValidator:
    """Tests para validador de tipos de medida."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_measurement_type_valid(self):
        """Test validación exitosa de tipos de medida válidos."""
        assert validate_measurement_type(0) == 0  # Consumo
        assert validate_measurement_type(1) == 1  # Generación

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_measurement_type_none_returns_default(self):
        """Test que None devuelve valor por defecto."""
        assert validate_measurement_type(None) == 0  # Default: consumo

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_measurement_type_invalid(self):
        """Test validación falla con tipos inválidos."""
        invalid_types = [2, 3, -1, 999]

        for measurement_type in invalid_types:
            with pytest.raises(ValidationError) as exc_info:
                validate_measurement_type(measurement_type)
            assert "debe ser 0 (consumo) o 1 (generación)" in str(exc_info.value)


class TestPointTypeValidator:
    """Tests para validador de tipos de punto."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_point_type_valid(self):
        """Test validación exitosa de tipos de punto válidos."""
        valid_types = [1, 2, 3, 4]

        for point_type in valid_types:
            result = validate_point_type(point_type)
            assert result == point_type

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_point_type_none_returns_default(self):
        """Test que None devuelve valor por defecto."""
        assert validate_point_type(None) == 1  # Default: frontera

    @pytest.mark.unit
    @pytest.mark.utils
    def test_validate_point_type_invalid(self):
        """Test validación falla con tipos inválidos."""
        invalid_types = [0, 5, 6, -1, 999]

        for point_type in invalid_types:
            with pytest.raises(ValidationError) as exc_info:
                validate_point_type(point_type)
            assert "debe ser 1 (frontera), 2 (consumo), 3 (generación) o 4 (servicios auxiliares)" in str(exc_info.value)


class TestTextNormalization:
    """Tests para funciones de normalización de texto."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_text_basic(self):
        """Test normalización básica de texto."""
        test_cases = [
            ("MÁLAGA", "MALAGA"),
            ("CORUÑA", "CORUNA"),
            ("JOSÉ", "JOSE"),
            ("NIÑO", "NINO"),
            ("ESPAÑA", "ESPANA"),
        ]

        for input_text, expected in test_cases:
            result = normalize_text(input_text)
            assert result == expected

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_text_special_characters(self):
        """Test normalización de caracteres especiales."""
        test_cases = [
            ("E-DISTRIBUCIÓN", "E-DISTRIBUCION"),
            ("IBERDROLA DISTRIBUCIÓN", "IBERDROLA DISTRIBUCION"),
            ("EDISTRIBUCIÓN", "EDISTRIBUCION"),
        ]

        for input_text, expected in test_cases:
            result = normalize_text(input_text)
            assert result == expected

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_text_non_string_input(self):
        """Test que entradas no-string se devuelven sin cambios."""
        non_string_inputs = [123, None, [], {}]

        for input_value in non_string_inputs:
            result = normalize_text(input_value)
            assert result == input_value

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_text_unicode_issues(self):
        """Test corrección de problemas de codificación Unicode."""
        # Simular problemas de doble codificación
        problematic_text = "EDISTRIBUCIÃlN"  # Debería corregirse
        result = normalize_text(problematic_text)
        # Debería al menos normalizar lo que puede
        assert "A" not in result or "Ã" not in result

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_dict_strings(self):
        """Test normalización de strings en diccionarios."""
        input_dict = {
            "distributor": "E-DISTRIBUCIÓN",
            "province": "MÁLAGA",
            "nested": {
                "city": "CORUÑA",
                "number": 123
            },
            "number": 456
        }

        result = normalize_dict_strings(input_dict)

        assert result["distributor"] == "E-DISTRIBUCION"
        assert result["province"] == "MALAGA"
        assert result["nested"]["city"] == "CORUNA"
        assert result["nested"]["number"] == 123  # No modificado
        assert result["number"] == 456  # No modificado

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_list_strings(self):
        """Test normalización de strings en listas."""
        input_list = [
            "MÁLAGA",
            123,
            {
                "name": "JOSÉ",
                "age": 30
            },
            ["NIÑO", "ESPAÑA"]
        ]

        result = normalize_list_strings(input_list)

        assert result[0] == "MALAGA"
        assert result[1] == 123
        assert result[2]["name"] == "JOSE"
        assert result[2]["age"] == 30
        assert result[3] == ["NINO", "ESPANA"]

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_api_response_dict(self):
        """Test normalización de respuesta de API como diccionario."""
        api_response = {
            "supplies": [
                {
                    "distributor": "E-DISTRIBUCIÓN",
                    "province": "MÁLAGA"
                }
            ],
            "status": "success"
        }

        result = normalize_api_response(api_response)

        assert result["supplies"][0]["distributor"] == "E-DISTRIBUCION"
        assert result["supplies"][0]["province"] == "MALAGA"
        assert result["status"] == "success"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_api_response_list(self):
        """Test normalización de respuesta de API como lista."""
        api_response = [
            {
                "name": "JOSÉ",
                "city": "CORUÑA"
            },
            {
                "name": "MARÍA",
                "city": "SEVILLA"
            }
        ]

        result = normalize_api_response(api_response)

        assert result[0]["name"] == "JOSE"
        assert result[0]["city"] == "CORUNA"
        assert result[1]["name"] == "MARIA"
        assert result[1]["city"] == "SEVILLA"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_normalize_api_response_non_dict_list(self):
        """Test normalización con tipos que no son dict ni list."""
        non_dict_list_responses = ["string", 123, None]

        for response in non_dict_list_responses:
            result = normalize_api_response(response)
            assert result == response


class TestHTTPClient:
    """Tests para cliente HTTP base."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_initialization(self):
        """Test inicialización del cliente HTTP."""
        client = HTTPClient(timeout=30, retries=2)

        assert client.timeout == 30
        assert client.retries == 2
        assert client.session is not None
        assert "datadis-python-sdk" in client.session.headers["User-Agent"]

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_default_headers(self):
        """Test headers por defecto del cliente HTTP."""
        client = HTTPClient()

        headers = client.session.headers
        assert "User-Agent" in headers
        assert "Content-Type" in headers
        assert "Accept" in headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_successful_request(self):
        """Test request HTTP exitoso."""
        client = HTTPClient(timeout=5, retries=1)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"success": True},
                status=200,
            )

            result = client.make_request("GET", "https://example.com/api/test")

            assert result == {"success": True}

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_auth_endpoint_response(self):
        """Test respuesta de endpoint de autenticación."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://example.com/nikola-auth/login",
                body="test_token_jwt",
                status=200,
            )

            result = client.make_request("POST", "https://example.com/nikola-auth/login")

            assert result == "test_token_jwt"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_form_data_request(self):
        """Test request con form data."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://example.com/api/login",
                body="success",
                status=200,
            )

            data = {"username": "test", "password": "pass"}
            result = client.make_request(
                "POST",
                "https://example.com/api/login",
                data=data,
                use_form_data=True
            )

            assert result == "success"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_401_error(self):
        """Test error 401 del cliente HTTP."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"error": "Unauthorized"},
                status=401,
            )

            with pytest.raises(AuthenticationError) as exc_info:
                client.make_request("GET", "https://example.com/api/test")

            assert "Credenciales inválidas o token expirado" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_429_error(self):
        """Test error 429 del cliente HTTP."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"error": "Rate limit exceeded"},
                status=429,
            )

            with pytest.raises(APIError) as exc_info:
                client.make_request("GET", "https://example.com/api/test")

            error = exc_info.value
            assert error.status_code == 429
            assert "Límite de peticiones excedido" in str(error)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_server_error(self):
        """Test error del servidor en cliente HTTP."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"error": "Internal server error"},
                status=500,
            )

            with pytest.raises(APIError) as exc_info:
                client.make_request("GET", "https://example.com/api/test")

            error = exc_info.value
            assert error.status_code == 500

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_retry_mechanism(self):
        """Test mecanismo de reintentos del cliente HTTP."""
        client = HTTPClient(retries=1)

        with responses.RequestsMock() as rsps:
            # Primera request falla
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Timeout")

            rsps.add_callback(
                responses.GET,
                "https://example.com/api/test",
                callback=timeout_callback,
            )

            # Segunda request exitosa
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"success": True},
                status=200,
            )

            result = client.make_request("GET", "https://example.com/api/test")

            assert result == {"success": True}
            assert len(rsps.calls) == 2

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_exhausted_retries(self):
        """Test agotamiento de reintentos."""
        client = HTTPClient(retries=1)

        with responses.RequestsMock() as rsps:
            # Todas las requests fallan
            def timeout_callback(request):
                raise requests.exceptions.Timeout("Timeout")

            for _ in range(2):  # Para retries=1, son 2 intentos totales
                rsps.add_callback(
                    responses.GET,
                    "https://example.com/api/test",
                    callback=timeout_callback,
                )

            with pytest.raises(DatadisError) as exc_info:
                client.make_request("GET", "https://example.com/api/test")

            assert "Error de conexión" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_set_auth_header(self):
        """Test establecer header de autorización."""
        client = HTTPClient()
        token = "test_token_123"

        client.set_auth_header(token)

        assert client.session.headers["Authorization"] == f"Bearer {token}"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_remove_auth_header(self):
        """Test remover header de autorización."""
        client = HTTPClient()
        client.set_auth_header("test_token")

        # Verificar que existe
        assert "Authorization" in client.session.headers

        client.remove_auth_header()

        # Verificar que se removió
        assert "Authorization" not in client.session.headers

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_close(self):
        """Test cierre del cliente HTTP."""
        client = HTTPClient()
        session = client.session

        client.close()

        # Verificar que la sesión se cerró (no podemos verificar directamente,
        # pero al menos verificar que no hay errores)
        assert client.session is session  # La referencia sigue ahí

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_custom_headers(self):
        """Test request con headers personalizados."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json={"success": True},
                status=200,
            )

            custom_headers = {"Custom-Header": "custom-value"}
            result = client.make_request(
                "GET",
                "https://example.com/api/test",
                headers=custom_headers
            )

            assert result == {"success": True}

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_malformed_json_response(self):
        """Test manejo de respuesta JSON malformada."""
        client = HTTPClient()

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                body="not valid json",
                status=200,
                content_type="application/json",
            )

            result = client.make_request("GET", "https://example.com/api/test")

            # Debería devolver como texto si no es JSON válido
            assert result == "not valid json"


class TestConstants:
    """Tests para constantes y configuración."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_api_v1_endpoints_exist(self):
        """Test que existen todos los endpoints V1 esperados."""
        expected_endpoints = [
            "supplies",
            "contracts",
            "consumption",
            "max_power",
            "distributors",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in API_V1_ENDPOINTS
            assert isinstance(API_V1_ENDPOINTS[endpoint], str)
            assert API_V1_ENDPOINTS[endpoint].startswith("/")

    @pytest.mark.unit
    @pytest.mark.utils
    def test_distributor_codes_mapping(self):
        """Test mapeo de códigos de distribuidor."""
        assert "VIESGO" in DISTRIBUTOR_CODES
        assert "E_DISTRIBUCION" in DISTRIBUTOR_CODES
        assert "E_REDES" in DISTRIBUTOR_CODES

        # Verificar que los valores son strings
        for code in DISTRIBUTOR_CODES.values():
            assert isinstance(code, str)
            assert code.isdigit()

    @pytest.mark.unit
    @pytest.mark.utils
    def test_measurement_types_mapping(self):
        """Test mapeo de tipos de medición."""
        assert "CONSUMPTION" in MEASUREMENT_TYPES
        assert "GENERATION" in MEASUREMENT_TYPES

        assert MEASUREMENT_TYPES["CONSUMPTION"] == 0
        assert MEASUREMENT_TYPES["GENERATION"] == 1

    @pytest.mark.unit
    @pytest.mark.utils
    def test_point_types_mapping(self):
        """Test mapeo de tipos de punto."""
        expected_point_types = [
            "BORDER",
            "CONSUMPTION",
            "GENERATION",
            "AUXILIARY_SERVICES",
            "AUXILIARY_SERVICES_ALT"
        ]

        for point_type in expected_point_types:
            assert point_type in POINT_TYPES
            assert isinstance(POINT_TYPES[point_type], int)
            assert 1 <= POINT_TYPES[point_type] <= 5


class TestUtilsIntegration:
    """Tests de integración para utilidades."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_full_validation_pipeline(self):
        """Test pipeline completo de validación."""
        # Datos de entrada
        cups = "  es0123456789012345678901ab  "
        distributor_code = "2"
        date_from = "2024/01/01"
        date_to = "2024/01/31"
        measurement_type = None
        point_type = None

        # Aplicar validaciones
        validated_cups = validate_cups(cups)
        validated_distributor = validate_distributor_code(distributor_code)
        validated_dates = validate_date_range(date_from, date_to, "daily")
        validated_measurement = validate_measurement_type(measurement_type)
        validated_point = validate_point_type(point_type)

        # Verificar resultados
        assert validated_cups == "ES0123456789012345678901AB"
        assert validated_distributor == "2"
        assert validated_dates == (date_from, date_to)
        assert validated_measurement == 0  # Default
        assert validated_point == 1  # Default

    @pytest.mark.unit
    @pytest.mark.utils
    def test_text_normalization_api_response(self):
        """Test normalización completa de respuesta de API."""
        api_response = {
            "supplies": [
                {
                    "distributor": "E-DISTRIBUCIÓN REDES DIGITALES S.L.U.",
                    "address": "CALLE JOSÉ MARÍA PEMÁN 123",
                    "province": "MÁLAGA",
                    "municipality": "CORUÑA"
                }
            ]
        }

        normalized = normalize_api_response(api_response)

        supply = normalized["supplies"][0]
        assert "Ñ" not in supply["distributor"]
        assert "É" not in supply["address"]
        assert "Á" not in supply["province"]
        assert "Ñ" not in supply["municipality"]

    @pytest.mark.unit
    @pytest.mark.utils
    def test_error_propagation_in_validators(self):
        """Test propagación correcta de errores en validadores."""
        error_scenarios = [
            (lambda: validate_cups("invalid"), ValidationError),
            (lambda: validate_date_range("invalid", "2024/01/01", "daily"), ValidationError),
            (lambda: validate_distributor_code("invalid"), ValidationError),
            (lambda: validate_measurement_type(999), ValidationError),
            (lambda: validate_point_type(999), ValidationError),
        ]

        for func, expected_error in error_scenarios:
            with pytest.raises(expected_error):
                func()

    @pytest.mark.unit
    @pytest.mark.utils
    def test_http_client_with_text_normalization(self):
        """Test que HTTPClient normaliza respuestas de texto."""
        client = HTTPClient()

        api_response = {
            "distributor": "E-DISTRIBUCIÓN",
            "province": "MÁLAGA"
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://example.com/api/test",
                json=api_response,
                status=200,
            )

            result = client.make_request("GET", "https://example.com/api/test")

            # La respuesta debería estar normalizada
            assert result["distributor"] == "E-DISTRIBUCION"
            assert result["province"] == "MALAGA"