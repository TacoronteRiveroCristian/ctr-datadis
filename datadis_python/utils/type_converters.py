"""
Conversores de tipos para hacer el SDK más flexible y pythónico.

Este módulo permite que los métodos del cliente acepten tipos más naturales:
- datetime objects para fechas (además de strings)
- int/float para números (además de strings)
- Mantiene compatibilidad total con la API existente
"""

from datetime import date, datetime
from typing import Optional, Union

from ..exceptions import ValidationError


def convert_date_to_api_format(
    date_value: Union[str, datetime, date], format_type: str = "daily"
) -> str:
    """
    Convierte una fecha a formato de la API de Datadis.

    :param date_value: Fecha como string, datetime, o date
    :type date_value: Union[str, datetime, date]
    :param format_type: Tipo de formato ("daily" para YYYY/MM/DD, "monthly" para YYYY/MM)
    :type format_type: str
    :return: Fecha formateada para la API
    :rtype: str
    :raises ValidationError: Si el formato no es válido
    """
    if isinstance(date_value, str):
        # NUEVA VALIDACIÓN: Verificar que no se envíen fechas diarias en modo mensual
        if format_type == "monthly" and "/" in date_value:
            parts = date_value.split("/")
            if len(parts) == 3:
                # Formato YYYY/MM/DD detectado en modo mensual - rechazar
                raise ValidationError(
                    f"La API de Datadis solo acepta fechas mensuales en formato YYYY/MM. "
                    f"Recibido: '{date_value}' (contiene día específico). "
                    f"Use formato mensual como: '{parts[0]}/{parts[1]}'"
                )

        # Si ya es string, validamos que tenga el formato correcto
        from .validators import validate_date_range

        try:
            # Usamos el validador existente para verificar formato
            if format_type == "daily":
                validate_date_range(date_value, date_value, "daily")
            else:
                validate_date_range(date_value, date_value, "monthly")
            return date_value
        except ValidationError:
            # Si falla la validación, intentamos parsear y reformatear
            try:
                # Intentar diferentes formatos comunes
                formats_to_try = ["%Y-%m-%d", "%Y%m%d", "%d/%m/%Y", "%Y/%m/%d"]

                # Si contiene "/", también manejar formato YYYY/MM
                if "/" in date_value:
                    parts = date_value.split("/")
                    if len(parts) == 2:
                        # Para formato YYYY/MM
                        dt = datetime(int(parts[0]), int(parts[1]), 1)
                        # Formatear según el tipo requerido
                        if format_type == "daily":
                            return dt.strftime("%Y/%m/%d")
                        else:
                            return dt.strftime("%Y/%m")

                # Intentar los formatos en orden
                for fmt in formats_to_try:
                    try:
                        dt = datetime.strptime(date_value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(
                        f"Formato de fecha no reconocido: {date_value}"
                    )

                # NUEVA VALIDACIÓN: Si parseamos una fecha con día específico en modo mensual, rechazar
                if format_type == "monthly" and dt.day != 1:
                    raise ValidationError(
                        f"La API de Datadis solo acepta fechas mensuales. "
                        f"Fecha '{date_value}' contiene día específico ({dt.day}). "
                        f"Use formato mensual como: '{dt.strftime('%Y/%m')}'"
                    )

                # Formatear según el tipo requerido
                if format_type == "daily":
                    return dt.strftime("%Y/%m/%d")
                else:
                    return dt.strftime("%Y/%m")

            except (ValueError, IndexError) as e:
                raise ValidationError(
                    f"No se pudo parsear la fecha: {date_value}. Error: {e}"
                )

    elif isinstance(date_value, (datetime, date)):
        # NUEVA VALIDACIÓN: Verificar que no se envíen días específicos en modo mensual
        if format_type == "monthly" and date_value.day != 1:
            raise ValidationError(
                f"La API de Datadis solo acepta fechas mensuales. "
                f"Fecha {date_value} contiene día específico ({date_value.day}). "
                f"Use el primer día del mes: {date_value.replace(day=1).strftime('%Y/%m')}"
            )

        # Convertir datetime/date a string en formato API
        if format_type == "daily":
            return date_value.strftime("%Y/%m/%d")
        elif format_type == "monthly":
            return date_value.strftime("%Y/%m")
        else:
            raise ValidationError(f"Tipo de formato no soportado: {format_type}")

    else:
        raise ValidationError(
            f"Tipo de fecha no soportado: {type(date_value)}. "
            f"Use str, datetime, o date."
        )


def convert_number_to_string(value: Union[str, int, float]) -> str:
    """
    Convierte un número a string para la API.

    :param value: Valor numérico como string, int, o float
    :type value: Union[str, int, float]
    :return: Valor como string
    :rtype: str
    :raises ValidationError: Si el tipo no es válido
    """
    if isinstance(value, str):
        # Si ya es string, validamos que sea numérico
        try:
            float(value)  # Intenta parsearlo para validar
            return value
        except ValueError:
            raise ValidationError(f"String no numérico: {value}")

    elif isinstance(value, (int, float)):
        return str(value)

    else:
        raise ValidationError(
            f"Tipo numérico no soportado: {type(value)}. " f"Use str, int, o float."
        )


def convert_optional_number_to_string(
    value: Optional[Union[str, int, float]]
) -> Optional[str]:
    """
    Convierte un número opcional a string para la API.

    :param value: Valor numérico opcional como string, int, float, o None
    :type value: Optional[Union[str, int, float]]
    :return: Valor como string o None
    :rtype: Optional[str]
    """
    if value is None:
        return None
    return convert_number_to_string(value)


def convert_date_range_to_api_format(
    date_from: Union[str, datetime, date],
    date_to: Union[str, datetime, date],
    format_type: str = "daily",
) -> tuple[str, str]:
    """
    Convierte un rango de fechas a formato de la API.

    :param date_from: Fecha de inicio
    :type date_from: Union[str, datetime, date]
    :param date_to: Fecha de fin
    :type date_to: Union[str, datetime, date]
    :param format_type: Tipo de formato ("daily" o "monthly")
    :type format_type: str
    :return: Tupla con fechas formateadas
    :rtype: tuple[str, str]
    """
    converted_from = convert_date_to_api_format(date_from, format_type)
    converted_to = convert_date_to_api_format(date_to, format_type)

    # Usar el validador existente para verificar el rango
    from .validators import validate_date_range

    return validate_date_range(converted_from, converted_to, format_type)


def convert_cups_parameter(cups: str) -> str:
    """
    Procesa un código CUPS sin validación de formato.

    :param cups: Código CUPS
    :type cups: str
    :return: CUPS procesado
    :rtype: str
    """
    if not isinstance(cups, str):
        raise ValidationError(f"CUPS debe ser string, recibido: {type(cups)}")

    return cups.upper().strip()


def convert_distributor_code_parameter(distributor_code: Union[str, int]) -> str:
    """
    Convierte y valida un código de distribuidor.

    :param distributor_code: Código del distribuidor como string o int
    :type distributor_code: Union[str, int]
    :return: Código de distribuidor como string validado
    :rtype: str
    """
    if isinstance(distributor_code, int):
        distributor_code = str(distributor_code)
    elif not isinstance(distributor_code, str):
        raise ValidationError(
            f"Código de distribuidor debe ser string o int, recibido: {type(distributor_code)}"
        )

    from .validators import validate_distributor_code

    return validate_distributor_code(distributor_code)
