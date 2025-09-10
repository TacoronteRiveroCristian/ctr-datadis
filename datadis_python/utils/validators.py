"""
Validadores para parámetros de la API de Datadis
"""

import re
from datetime import datetime
from typing import Optional

from ..exceptions import ValidationError


def validate_cups(cups: str) -> str:
    """
    Valida formato CUPS (Código Universal del Punto de Suministro)
    
    Formato real: ES + 16 dígitos + 4 caracteres alfanuméricos (ej: ES0031607515707001RC0F)
    """
    if not cups:
        raise ValidationError("CUPS no puede estar vacío")
    
    cups = cups.upper().strip()
    
    # Formato real observado: ES + 16 dígitos + 4 caracteres alfanuméricos
    cups_pattern = r"^ES\d{16}[A-Z0-9]{4}$"
    
    if not re.match(cups_pattern, cups):
        raise ValidationError(
            "Formato CUPS inválido. Debe ser: ES + 16 dígitos + 4 caracteres alfanuméricos"
        )
    
    return cups


def validate_date_range(date_from: str, date_to: str, format_type: str = "daily") -> tuple[str, str]:
    """
    Valida rango de fechas según el tipo de formato requerido por Datadis
    
    Args:
        date_from: Fecha de inicio
        date_to: Fecha de fin  
        format_type: Tipo de formato ("daily" para YYYY/MM/DD, "monthly" para YYYY/MM)
    """
    if format_type == "daily":
        date_pattern = r"^\d{4}/\d{2}/\d{2}$"
        date_format = "%Y/%m/%d"
        example = "2024/01/31"
    elif format_type == "monthly":
        date_pattern = r"^\d{4}/\d{2}$" 
        date_format = "%Y/%m"
        example = "2024/01"
    else:
        raise ValidationError(f"Tipo de formato no soportado: {format_type}")
    
    if not re.match(date_pattern, date_from):
        raise ValidationError(
            f"Formato de fecha_desde inválido: {date_from}. Use {example}"
        )
    
    if not re.match(date_pattern, date_to):
        raise ValidationError(
            f"Formato de fecha_hasta inválido: {date_to}. Use {example}"
        )
    
    try:
        start_date = datetime.strptime(date_from, date_format)
        end_date = datetime.strptime(date_to, date_format)
    except ValueError as e:
        raise ValidationError(f"Fecha inválida: {e}")
    
    if start_date > end_date:
        raise ValidationError("fecha_desde no puede ser posterior a fecha_hasta")
    
    # Validar que no sea muy antigua (límite de la API - solo últimos 2 años)
    min_date = datetime.now().replace(year=datetime.now().year - 2)
    if start_date < min_date:
        raise ValidationError("fecha_desde no puede ser anterior a hace 2 años (limitación de Datadis)")
    
    # Validar que no sea futura
    max_date = datetime.now()
    if end_date > max_date:
        raise ValidationError("fecha_hasta no puede ser futura")
    
    return date_from, date_to


def validate_distributor_code(distributor_code: str) -> str:
    """
    Valida código de distribuidor
    1: Viesgo, 2: E-distribución, 3: E-redes, 4: ASEME, 5: UFD, 6: EOSA, 7: CIDE, 8: IDE
    """
    valid_codes = ["1", "2", "3", "4", "5", "6", "7", "8"]
    
    if distributor_code not in valid_codes:
        raise ValidationError(
            f"Código de distribuidor inválido: {distributor_code}. "
            f"Válidos: {', '.join(valid_codes)}"
        )
    
    return distributor_code


def validate_measurement_type(measurement_type: Optional[int]) -> int:
    """
    Valida tipo de medida
    0 = Consumo, 1 = Generación
    """
    if measurement_type is None:
        return 0  # Por defecto consumo
    
    if measurement_type not in [0, 1]:
        raise ValidationError("measurement_type debe ser 0 (consumo) o 1 (generación)")
    
    return measurement_type


def validate_point_type(point_type: Optional[int]) -> int:
    """
    Valida tipo de punto
    1 = Frontera, 2 = Consumo, 3 = Generación, 4 = Servicios auxiliares
    """
    if point_type is None:
        return 1  # Por defecto frontera
    
    if point_type not in [1, 2, 3, 4]:
        raise ValidationError(
            "point_type debe ser 1 (frontera), 2 (consumo), 3 (generación) o 4 (servicios auxiliares)"
        )
    
    return point_type