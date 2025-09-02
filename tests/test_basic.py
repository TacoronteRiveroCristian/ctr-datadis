"""
Tests básicos para el SDK de Datadis
"""

import pytest
from datadis_python import DatadisClient
from datadis_python.exceptions import ValidationError
from datadis_python.utils.validators import validate_cups, validate_date_range


class TestValidators:
    """Tests para validadores"""
    
    def test_validate_cups_valid(self):
        """Test CUPS válido"""
        cups = "ES001234567890123456AB"
        result = validate_cups(cups)
        assert result == cups
    
    def test_validate_cups_invalid_format(self):
        """Test CUPS con formato inválido"""
        with pytest.raises(ValidationError):
            validate_cups("INVALID_CUPS")
    
    def test_validate_cups_empty(self):
        """Test CUPS vacío"""
        with pytest.raises(ValidationError):
            validate_cups("")
    
    def test_validate_date_range_valid_daily(self):
        """Test rango de fechas válido formato diario"""
        date_from, date_to = validate_date_range("2024/01/01", "2024/01/31", "daily")
        assert date_from == "2024/01/01"
        assert date_to == "2024/01/31"
    
    def test_validate_date_range_valid_monthly(self):
        """Test rango de fechas válido formato mensual"""
        date_from, date_to = validate_date_range("2024/01", "2024/02", "monthly")
        assert date_from == "2024/01"
        assert date_to == "2024/02"
    
    def test_validate_date_range_invalid_format(self):
        """Test formato de fecha inválido"""
        with pytest.raises(ValidationError):
            validate_date_range("2024-01-01", "2024-01-31", "daily")
    
    def test_validate_date_range_from_after_to(self):
        """Test fecha desde posterior a fecha hasta"""
        with pytest.raises(ValidationError):
            validate_date_range("2024/02", "2024/01", "monthly")


class TestDatadisClient:
    """Tests para el cliente principal"""
    
    def test_client_initialization(self):
        """Test inicialización del cliente"""
        client = DatadisClient("test_user", "test_pass")
        assert client.username == "test_user"
        assert client.password == "test_pass"
        assert client.timeout == 30
        assert client.retries == 3
    
    def test_client_custom_params(self):
        """Test inicialización con parámetros custom"""
        client = DatadisClient(
            "test_user", 
            "test_pass", 
            timeout=60, 
            retries=5
        )
        assert client.timeout == 60
        assert client.retries == 5