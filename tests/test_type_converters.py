"""
Tests para conversores de tipos flexibles del SDK de Datadis.

Este módulo contiene tests específicos para los conversores de tipos que permiten
que el SDK acepte parámetros en formatos más pythónicos (datetime, int, float)
además de strings.
"""

from datetime import date, datetime

import pytest

from datadis_python.exceptions import ValidationError
from datadis_python.utils.type_converters import (
    convert_cups_parameter,
    convert_date_range_to_api_format,
    convert_date_to_api_format,
    convert_distributor_code_parameter,
    convert_number_to_string,
    convert_optional_number_to_string,
)


class TestTypeConverters:
    """Tests para conversores de tipos flexibles."""

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_string_valid_daily(self):
        """Test conversión de fecha string válida formato diario."""
        result = convert_date_to_api_format("2024/01/15", "daily")
        assert result == "2024/01/15"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_string_valid_monthly(self):
        """Test conversión de fecha string válida formato mensual."""
        result = convert_date_to_api_format("2024/01", "monthly")
        assert result == "2024/01"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_datetime_to_daily(self):
        """Test conversión de datetime object a formato diario."""
        dt = datetime(2024, 1, 15, 14, 30)
        result = convert_date_to_api_format(dt, "daily")
        assert result == "2024/01/15"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_datetime_to_monthly(self):
        """Test conversión de datetime object a formato mensual."""
        dt = datetime(2024, 1, 1, 14, 30)  # Primer día del mes
        result = convert_date_to_api_format(dt, "monthly")
        assert result == "2024/01"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_object_to_daily(self):
        """Test conversión de date object a formato diario."""
        d = date(2024, 1, 15)
        result = convert_date_to_api_format(d, "daily")
        assert result == "2024/01/15"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_object_to_monthly(self):
        """Test conversión de date object a formato mensual."""
        d = date(2024, 1, 1)  # Primer día del mes
        result = convert_date_to_api_format(d, "monthly")
        assert result == "2024/01"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_alternative_formats(self):
        """Test conversión de fechas en formatos alternativos."""
        # Formato ISO
        result = convert_date_to_api_format("2024-01-15", "daily")
        assert result == "2024/01/15"

        # Formato compacto
        result = convert_date_to_api_format("20240115", "daily")
        assert result == "2024/01/15"

        # Formato español
        result = convert_date_to_api_format("15/01/2024", "daily")
        assert result == "2024/01/15"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_invalid_format(self):
        """Test error con formato de fecha inválido."""
        with pytest.raises(ValidationError) as exc_info:
            convert_date_to_api_format("invalid-date", "daily")
        assert "Formato de fecha no reconocido" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_invalid_type(self):
        """Test error con tipo de fecha inválido."""
        with pytest.raises(ValidationError) as exc_info:
            convert_date_to_api_format(123, "daily")
        assert "Tipo de fecha no soportado" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_number_string_valid(self):
        """Test conversión de número string válido."""
        assert convert_number_to_string("123") == "123"
        assert convert_number_to_string("45.67") == "45.67"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_number_int(self):
        """Test conversión de entero."""
        assert convert_number_to_string(123) == "123"
        assert convert_number_to_string(0) == "0"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_number_float(self):
        """Test conversión de float."""
        assert convert_number_to_string(45.67) == "45.67"
        assert convert_number_to_string(0.0) == "0.0"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_number_string_invalid(self):
        """Test error con string no numérico."""
        with pytest.raises(ValidationError) as exc_info:
            convert_number_to_string("not-a-number")
        assert "String no numérico" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_number_invalid_type(self):
        """Test error con tipo numérico inválido."""
        with pytest.raises(ValidationError) as exc_info:
            convert_number_to_string(["list"])
        assert "Tipo numérico no soportado" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_optional_number_none(self):
        """Test conversión de número opcional None."""
        assert convert_optional_number_to_string(None) is None

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_optional_number_valid(self):
        """Test conversión de número opcional válido."""
        assert convert_optional_number_to_string(123) == "123"
        assert convert_optional_number_to_string("456") == "456"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_range_mixed_types(self):
        """Test conversión de rango de fechas con tipos mixtos."""
        dt_from = datetime(2024, 1, 1)
        date_to = "2024/01/31"

        result = convert_date_range_to_api_format(dt_from, date_to, "daily")
        assert result == ("2024/01/01", "2024/01/31")

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_date_range_validation_error(self):
        """Test error en validación de rango de fechas."""
        # Fecha from posterior a fecha to
        with pytest.raises(ValidationError):
            convert_date_range_to_api_format("2024/01/31", "2024/01/01", "daily")

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_cups_parameter_valid(self):
        """Test conversión de parámetro CUPS válido."""
        result = convert_cups_parameter("  es0031607515707001rc0f  ")
        assert result == "ES0031607515707001RC0F"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_cups_parameter_invalid_type(self):
        """Test error con tipo CUPS inválido."""
        with pytest.raises(ValidationError) as exc_info:
            convert_cups_parameter(123)
        assert "CUPS debe ser string" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_distributor_code_string(self):
        """Test conversión de código distribuidor string."""
        result = convert_distributor_code_parameter("2")
        assert result == "2"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_distributor_code_int(self):
        """Test conversión de código distribuidor int."""
        result = convert_distributor_code_parameter(2)
        assert result == "2"

    @pytest.mark.unit
    @pytest.mark.utils
    def test_convert_distributor_code_invalid_type(self):
        """Test error con tipo código distribuidor inválido."""
        with pytest.raises(ValidationError) as exc_info:
            convert_distributor_code_parameter(["list"])
        assert "Código de distribuidor debe ser string o int" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.utils
    def test_type_converters_integration_example(self):
        """Test integración completa de conversores."""
        # Simular llamada con tipos flexibles
        cups = "  es0031607515707001rc0f  "
        distributor_code = 2
        date_from = datetime(2024, 1, 1)
        date_to = date(2024, 1, 31)
        measurement_type = 0
        point_type = None

        # Aplicar conversores
        cups_conv = convert_cups_parameter(cups)
        dist_conv = convert_distributor_code_parameter(distributor_code)
        from_conv, to_conv = convert_date_range_to_api_format(
            date_from, date_to, "daily"
        )
        measurement_conv = convert_number_to_string(measurement_type)
        point_conv = convert_optional_number_to_string(point_type)

        # Verificar resultados
        assert cups_conv == "ES0031607515707001RC0F"
        assert dist_conv == "2"
        assert from_conv == "2024/01/01"
        assert to_conv == "2024/01/31"
        assert measurement_conv == "0"
        assert point_conv is None
