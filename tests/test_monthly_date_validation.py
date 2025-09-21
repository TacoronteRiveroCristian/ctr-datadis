"""
Tests específicos para validación de fechas mensuales en la API de Datadis.

Este módulo contiene tests para asegurar que la API V1 rechace fechas no mensuales
y solo acepte fechas en formato YYYY/MM según las especificaciones de Datadis.
"""

from datetime import date, datetime

import pytest

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
from datadis_python.exceptions import ValidationError


class TestMonthlyDateValidation:
    """Tests para validar que solo se acepten fechas mensuales."""

    def test_consumption_rejects_daily_dates_string(self, v1_client):
        """Test que fechas diarias como string sean rechazadas en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from="2024/01/15",  # Fecha con día específico - DEBE FALLAR
                date_to="2024/02/20",  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        # Verificar que el mensaje de error menciona el formato mensual
        error_message = str(excinfo.value).lower()
        assert "formato" in error_message or "yyyy/mm" in error_message

    def test_consumption_rejects_daily_dates_datetime(self, v1_client):
        """Test que fechas datetime con días específicos sean rechazadas en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from=datetime(
                    2024, 1, 15
                ),  # Fecha con día específico - DEBE FALLAR
                date_to=datetime(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_consumption_rejects_daily_dates_date_objects(self, v1_client):
        """Test que objetos date con días específicos sean rechazados en get_consumption."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from=date(2024, 1, 15),  # Fecha con día específico - DEBE FALLAR
                date_to=date(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
                measurement_type=0,
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_consumption_accepts_monthly_dates_string(self, v1_client):
        """Test que fechas mensuales como string sean aceptadas en get_consumption."""
        # Este test debería pasar la validación (aunque la request falle por no estar autenticado)
        try:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
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

    def test_consumption_accepts_monthly_dates_datetime_first_day(self, v1_client):
        """Test que fechas datetime del primer día del mes sean aceptadas en get_consumption."""
        try:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
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

    def test_max_power_rejects_daily_dates_string(self, v1_client):
        """Test que fechas diarias como string sean rechazadas en get_max_power."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from="2024/01/15",  # Fecha con día específico - DEBE FALLAR
                date_to="2024/02/20",  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        assert "formato" in error_message or "yyyy/mm" in error_message

    def test_max_power_rejects_daily_dates_datetime(self, v1_client):
        """Test que fechas datetime con días específicos sean rechazadas en get_max_power."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from=datetime(
                    2024, 1, 15
                ),  # Fecha con día específico - DEBE FALLAR
                date_to=datetime(2024, 2, 20),  # Fecha con día específico - DEBE FALLAR
            )

        error_message = str(excinfo.value).lower()
        # Verificar que el mensaje menciona fechas mensuales
        assert "mensual" in error_message or "día específico" in error_message

    def test_max_power_accepts_monthly_dates_string(self, v1_client):
        """Test que fechas mensuales como string sean aceptadas en get_max_power."""
        try:
            v1_client.get_max_power(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
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

    def test_error_message_provides_clear_guidance(self, v1_client):
        """Test que los mensajes de error proporcionen orientación clara sobre el formato correcto."""
        with pytest.raises(ValidationError) as excinfo:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from="2024/01/15",
                date_to="2024/02/20",
                measurement_type=0,
            )

        error_message = str(excinfo.value)
        # El mensaje debería mencionar el formato correcto
        assert "YYYY/MM" in error_message or "yyyy/mm" in error_message.lower()

    def test_conversion_datetime_to_monthly_preserves_year_month(self, v1_client):
        """Test que la conversión de datetime a mensual preserve año y mes correctamente."""
        # Este test verifica que datetime(2024, 3, 15) se convierta a "2024/03"

        # Creamos un mock básico para interceptar la llamada y verificar parámetros
        original_make_request = v1_client._make_authenticated_request
        captured_params = {}

        def mock_request(endpoint, params=None):
            captured_params.update(params or {})
            # Simular un error de autenticación para evitar llamada real
            from datadis_python.exceptions import AuthenticationError

            raise AuthenticationError("Mock error")

        v1_client._make_authenticated_request = mock_request

        # Las fechas con días específicos deben fallar la validación antes de llegar a la request
        with pytest.raises(ValidationError):
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from=datetime(2024, 3, 15),  # Día 15 debe ser rechazado
                date_to=datetime(2024, 4, 22),  # Día 22 debe ser rechazado
                measurement_type=0,
            )

        # Restaurar método original
        v1_client._make_authenticated_request = original_make_request

        # Test con fechas válidas (primer día del mes)
        v1_client._make_authenticated_request = mock_request
        captured_params.clear()

        try:
            v1_client.get_consumption(
                cups="ES1234000000000001JN0F",
                distributor_code=2,
                date_from=datetime(2024, 3, 1),  # Primer día del mes - válido
                date_to=datetime(2024, 4, 1),  # Primer día del mes - válido
                measurement_type=0,
            )
        except Exception:
            pass  # Esperamos el error de auth mock
        finally:
            # Restaurar método original
            v1_client._make_authenticated_request = original_make_request

        # Verificar que las fechas se convirtieron correctamente
        assert captured_params.get("startDate") == "2024/03"
        assert captured_params.get("endDate") == "2024/04"


@pytest.fixture
def v1_client():
    """Cliente V1 para tests sin autenticación."""
    return SimpleDatadisClientV1(username="test", password="test")
