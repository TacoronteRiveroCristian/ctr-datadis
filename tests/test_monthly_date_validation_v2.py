"""
Tests específicos para validación de fechas mensuales en SimpleDatadisClientV2.

Este módulo contiene tests para asegurar que la API V2 rechace fechas no mensuales
y solo acepte fechas en formato YYYY/MM según las especificaciones de Datadis.
"""

from datetime import date, datetime

import pytest

from datadis_python.client.v2.simple_client import SimpleDatadisClientV2
from datadis_python.exceptions import ValidationError


class TestMonthlyDateValidationV2:
    """Tests para validar que solo se acepten fechas mensuales en V2."""

    def test_consumption_rejects_daily_dates_string(self, v2_client):
        """Test que fechas diarias como string sean rechazadas en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01/15",  # Fecha con día específico - DEBE FALLAR
                date_to="2024/02/20",  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        # Verificar que el mensaje de error menciona el formato mensual
        error_message = str(excinfo.value).lower()
        assert "formato" in error_message or "yyyy/mm" in error_message

    def test_consumption_rejects_daily_dates_datetime(self, v2_client):
        """Test que fechas datetime con días específicos sean rechazadas en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(
                    2024, 1, 15
                ),  # Fecha con día específico - DEBE FALLAR
                date_to=datetime(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_consumption_rejects_daily_dates_date_objects(self, v2_client):
        """Test que objetos date con días específicos sean rechazados en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=date(2024, 1, 15),  # Fecha con día específico - DEBE FALLAR
                date_to=date(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_consumption_accepts_monthly_dates_string(self, v2_client):
        """Test que fechas mensuales como string sean aceptadas en get_consumption."""
        # Este test debería pasar la validación (aunque la request falle por no estar autenticado)
        try:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01",  # Formato mensual correcto
                date_to="2024/02",  # Formato mensual correcto
                measurement_type=0,
            )
        except ValidationError:
            pytest.fail(
                "Las fechas mensuales válidas no deberían lanzar ValidationError"
            )
        except Exception:
            # Otros errores (auth, red, etc.) son esperados en tests unitarios
            pass

    def test_consumption_accepts_monthly_dates_datetime_first_day(self, v2_client):
        """Test que fechas datetime del primer día del mes sean aceptadas en get_consumption."""
        try:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(
                    2024, 1, 1
                ),  # Primer día del mes - debe convertirse a mensual
                date_to=datetime(
                    2024, 2, 1
                ),  # Primer día del mes - debe convertirse a mensual
                measurement_type=0,
            )
        except ValidationError:
            pytest.fail("Las fechas del primer día del mes deberían ser aceptadas")
        except Exception:
            # Otros errores son esperados
            pass

    def test_max_power_rejects_daily_dates_string(self, v2_client):
        """Test que fechas diarias como string sean rechazadas en get_max_power."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01/15",  # Fecha con día específico - DEBE FALLAR
                date_to="2024/02/20",  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        assert "formato" in error_message or "yyyy/mm" in error_message

    def test_max_power_rejects_daily_dates_datetime(self, v2_client):
        """Test que fechas datetime con días específicos sean rechazadas en get_max_power."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(
                    2024, 1, 15
                ),  # Fecha con día específico - DEBE FALLAR
                date_to=datetime(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_max_power_accepts_monthly_dates_string(self, v2_client):
        """Test que fechas mensuales como string sean aceptadas en get_max_power."""
        try:
            v2_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01",  # Formato mensual correcto
                date_to="2024/02",  # Formato mensual correcto
            )
        except ValidationError:
            pytest.fail(
                "Las fechas mensuales válidas no deberían lanzar ValidationError"
            )
        except Exception:
            # Otros errores son esperados
            pass

    def test_reactive_data_rejects_daily_dates_string(self, v2_client):
        """Test que fechas diarias como string sean rechazadas en get_reactive_data."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_reactive_data(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01/15",  # Fecha con día específico - DEBE FALLAR
                date_to="2024/02/20",  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        assert "formato" in error_message or "yyyy/mm" in error_message

    def test_reactive_data_rejects_daily_dates_datetime(self, v2_client):
        """Test que fechas datetime con días específicos sean rechazadas en get_reactive_data."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_reactive_data(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(
                    2024, 1, 15
                ),  # Fecha con día específico - DEBE FALLAR
                date_to=datetime(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_reactive_data_accepts_monthly_dates_string(self, v2_client):
        """Test que fechas mensuales como string sean aceptadas en get_reactive_data."""
        try:
            v2_client.get_reactive_data(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01",  # Formato mensual correcto
                date_to="2024/02",  # Formato mensual correcto
            )
        except ValidationError:
            pytest.fail(
                "Las fechas mensuales válidas no deberían lanzar ValidationError"
            )
        except Exception:
            # Otros errores son esperados
            pass

    def test_error_message_provides_clear_guidance(self, v2_client):
        """Test que los mensajes de error proporcionen orientación clara sobre el formato correcto."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/01/15",
                date_to="2024/02/20",
                measurement_type=0,
            )

        error_message = str(excinfo.value)
        # El mensaje debería mencionar el formato correcto
        assert "YYYY/MM" in error_message or "yyyy/mm" in error_message.lower()

    def test_conversion_datetime_to_monthly_preserves_year_month(self, v2_client):
        """Test que la conversión de datetime a mensual preserve año y mes correctamente."""
        # Este test verifica que datetime(2024, 3, 15) se convierta a "2024/03"

        # Creamos un mock básico para interceptar la llamada y verificar parámetros
        original_make_request = v2_client._make_authenticated_request
        captured_params = {}

        def mock_request(endpoint, params=None):
            captured_params.update(params or {})
            # Simular un error de autenticación para evitar llamada real
            from datadis_python.exceptions import AuthenticationError

            raise AuthenticationError("Mock error")

        v2_client._make_authenticated_request = mock_request

        # Las fechas con días específicos deben fallar la validación antes de llegar a la request
        with pytest.raises(ValidationError):
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(2024, 3, 15),  # Día 15 debe ser rechazado
                date_to=datetime(2024, 4, 22),  # Día 22 debe ser rechazado
                measurement_type=0,
            )

        # Restaurar método original
        v2_client._make_authenticated_request = original_make_request

        # Test con fechas válidas (primer día del mes)
        v2_client._make_authenticated_request = mock_request
        captured_params.clear()

        try:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from=datetime(2024, 3, 1),  # Primer día del mes - válido
                date_to=datetime(2024, 4, 1),  # Primer día del mes - válido
                measurement_type=0,
            )
        except Exception:
            pass  # Esperamos el error de auth mock
        finally:
            # Restaurar método original
            v2_client._make_authenticated_request = original_make_request

        # Verificar que las fechas se convirtieron correctamente
        assert captured_params.get("startDate") == "2024/03"
        assert captured_params.get("endDate") == "2024/04"

    def test_multiple_invalid_date_formats(self, v2_client):
        """Test múltiples formatos de fecha inválidos."""
        invalid_dates = [
            "2024-01-15",  # Formato ISO
            "01/15/2024",  # Formato americano
            "15/01/2024",  # Formato europeo
            "2024.01.15",  # Puntos
            "20240115",  # Sin separadores
            "2024/1/15",  # Sin padding
            "24/01/15",  # Año corto
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(ValidationError) as excinfo:
                v2_client.get_consumption(
                    cups="ES1234000000000001JN0F",
                    distributor_code="2",
                    date_from=invalid_date,
                    date_to="2024/02",
                    measurement_type=0,
                )

            # Verificar que cada formato inválido produce un error informativo
            error_message = str(excinfo.value).lower()
            assert "formato" in error_message or "yyyy/mm" in error_message

    def test_edge_case_february_leap_year(self, v2_client):
        """Test casos edge con febrero en año bisiesto."""
        # Estas fechas deberían fallar por tener días específicos
        with pytest.raises(ValidationError):
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/02/29",  # 29 de febrero (año bisiesto) - DEBE FALLAR
                date_to="2024/03/01",  # 1 de marzo - DEBE FALLAR
                measurement_type=0,
            )

        # Formato mensual correcto debe pasar validación
        try:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/02",  # Formato mensual correcto
                date_to="2024/03",  # Formato mensual correcto
                measurement_type=0,
            )
        except ValidationError:
            pytest.fail(
                "Las fechas mensuales válidas no deberían lanzar ValidationError"
            )
        except Exception:
            pass  # Otros errores son esperados

    def test_date_range_validation_start_after_end(self, v2_client):
        """Test validación cuando fecha inicio es posterior a fecha fin."""
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code="2",
                date_from="2024/03",  # Marzo
                date_to="2024/01",  # Enero (anterior) - DEBE FALLAR
                measurement_type=0,
            )

        error_message = str(excinfo.value).lower()
        assert "posterior" in error_message or "mayor" in error_message

    def test_extreme_date_values(self, v2_client):
        """Test fechas extremas que deberían fallar validación."""
        extreme_cases = [
            ("2024/00", "2024/01"),  # Mes 0
            ("2024/13", "2024/12"),  # Mes 13
            ("2024/99", "2024/01"),  # Mes inválido
            ("1900/01", "1900/02"),  # Año muy antiguo
            ("2050/01", "2050/02"),  # Año futuro
        ]

        for date_from, date_to in extreme_cases:
            with pytest.raises(ValidationError):
                v2_client.get_consumption(
                    cups="ES1234000000000001JN0F",
                    distributor_code="2",
                    date_from=date_from,
                    date_to=date_to,
                    measurement_type=0,
                )

    def test_mixed_valid_invalid_parameters(self, v2_client):
        """Test combinación de parámetros válidos e inválidos."""
        # Fecha válida pero CUPS inválido - debería fallar por CUPS primero
        with pytest.raises(ValidationError) as excinfo:
            v2_client.get_consumption(
                cups="INVALID_CUPS",  # CUPS inválido
                distributor_code="2",
                date_from="2024/01/15",  # Fecha también inválida
                date_to="2024/02",
                measurement_type=0,
            )

        # El error podría ser por CUPS o por fecha, ambos son válidos
        error_message = str(excinfo.value).lower()
        assert "cups" in error_message or "formato" in error_message

    def test_all_v2_date_methods_consistency(self, v2_client):
        """Test que todos los métodos V2 con fechas tengan validación consistente."""
        invalid_date = "2024/01/15"  # Fecha con día específico

        methods_to_test = [
            (
                "get_consumption",
                {
                    "cups": "ES1234000000000001JN0F",
                    "distributor_code": "2",
                    "date_from": invalid_date,
                    "date_to": "2024/02",
                    "measurement_type": 0,
                },
            ),
            (
                "get_max_power",
                {
                    "cups": "ES1234000000000001JN0F",
                    "distributor_code": "2",
                    "date_from": invalid_date,
                    "date_to": "2024/02",
                },
            ),
            (
                "get_reactive_data",
                {
                    "cups": "ES1234000000000001JN0F",
                    "distributor_code": "2",
                    "date_from": invalid_date,
                    "date_to": "2024/02",
                },
            ),
        ]

        for method_name, kwargs in methods_to_test:
            method = getattr(v2_client, method_name)
            with pytest.raises(ValidationError) as excinfo:
                method(**kwargs)

            # Todos deberían producir errores similares sobre formato de fecha
            error_message = str(excinfo.value).lower()
            assert "formato" in error_message or "mensual" in error_message


@pytest.fixture
def v2_client():
    """Cliente V2 para tests sin autenticación."""
    return SimpleDatadisClientV2(username="test", password="test")
