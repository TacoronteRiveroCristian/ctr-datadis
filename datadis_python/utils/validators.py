"""
Validadores para parámetros de la API de Datadis.

Este módulo contiene funciones para validar los parámetros utilizados en las solicitudes a la API de Datadis.
"""

import re
from datetime import datetime
from typing import Optional, Tuple

from ..exceptions import ValidationError


def validate_date_range(
    date_from: str, date_to: str, format_type: str = "monthly"
) -> Tuple[str, str]:
    """
    Valida un rango de fechas según el tipo de formato requerido por Datadis.

    :param date_from: Fecha de inicio.
    :type date_from: str
    :param date_to: Fecha de fin.
    :type date_to: str
    :param format_type: Tipo de formato ("monthly" para YYYY/MM).
    :type format_type: str
    :return: Tupla con las fechas validadas.
    :rtype: tuple[str, str]
    """
    if format_type == "monthly":
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
        raise ValidationError(
            "fecha_desde no puede ser anterior a hace 2 años (limitación de Datadis)"
        )

    # Validar que no sea futura
    max_date = datetime.now()
    if end_date > max_date:
        raise ValidationError("fecha_hasta no puede ser futura")

    return date_from, date_to


def validate_distributor_code(distributor_code: str) -> str:
    """
    Valida código de distribuidor.

    :param distributor_code: Código de distribuidor a validar
    :type distributor_code: str
    :return: Código validado
    :rtype: str
    :raises ValidationError: Si el código no es válido
    """
    return distributor_code


def validate_measurement_type(measurement_type: Optional[int]) -> int:
    """
    Valida tipo de medida.

    Tipos válidos:
    0 = Consumo, 1 = Generación

    :param measurement_type: Tipo de medida (0 o 1), None para usar por defecto (0)
    :type measurement_type: Optional[int]
    :return: Tipo de medida validado
    :rtype: int
    :raises ValidationError: Si el tipo no es válido
    """
    if measurement_type is None:
        return 0  # Por defecto consumo

    if measurement_type not in [0, 1]:
        raise ValidationError("measurement_type debe ser 0 (consumo) o 1 (generación)")

    return measurement_type


def validate_point_type(point_type: Optional[int]) -> int:
    """
    Valida tipo de punto.

    :param point_type: Tipo de punto, None para usar por defecto (1)
    :type point_type: Optional[int]
    :return: Tipo de punto validado
    :rtype: int
    :raises ValidationError: Si el tipo no es válido
    """
    if point_type is None:
        return 1  # Por defecto frontera
    return point_type