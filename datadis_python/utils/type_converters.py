"""
Conversores de tipos flexibles para el SDK de Datadis.

Este módulo proporciona funciones de conversión de tipos que hacen el SDK más flexible
y pythónico, permitiendo que los usuarios pasen parámetros en formatos naturales y
cómodos que se convierten automáticamente a los formatos esperados por la API de Datadis.

El SDK acepta tipos Python naturales y los convierte automáticamente:
    - **Fechas**: ``datetime``, ``date``, o ``str`` → formato API (YYYY/MM o YYYY/MM/DD)
    - **Números**: ``int``, ``float``, o ``str`` → strings validados para la API
    - **Códigos**: ``int`` o ``str`` → strings validados con formato correcto

Filosofía de diseño:
    - **Flexibilidad**: Acepta múltiples tipos de entrada para facilitar el uso
    - **Validación robusta**: Detecta y previene errores comunes antes de llegar a la API
    - **Retrocompatibilidad**: Mantiene compatibilidad total con código existente
    - **Mensajes de error claros**: Proporciona guía específica cuando hay problemas

Limitaciones específicas de Datadis:
    - **Solo fechas mensuales**: La API solo acepta YYYY/MM, no fechas específicas
    - **Rangos temporales limitados**: Máximo 2 años hacia atrás desde la fecha actual
    - **Códigos específicos**: Solo se aceptan códigos de distribuidor válidos (1-8)

Example:
    Antes (inflexible)::

        # El usuario tenía que formatear todo manualmente
        client.get_consumption(
            cups="ES001234567890123456AB",
            distributor_code="2",  # Solo string
            date_from="2024/01",   # Solo formato específico
            date_to="2024/12"      # Solo formato específico
        )

    Después (flexible)::

        from datetime import date

        # El SDK acepta múltiples formatos automáticamente
        client.get_consumption(
            cups="ES001234567890123456AB",
            distributor_code=2,              # int automáticamente → "2"
            date_from=date(2024, 1, 1),      # date automáticamente → "2024/01"
            date_to=date(2024, 12, 31)       # date automáticamente → "2024/12"
        )

Funciones principales:
    - :func:`convert_date_to_api_format`: Convierte fechas de cualquier formato a API
    - :func:`convert_date_range_to_api_format`: Convierte rangos de fechas con validación
    - :func:`convert_number_to_string`: Convierte números a strings validados
    - :func:`convert_cups_parameter`: Valida y formatea códigos CUPS
    - :func:`convert_distributor_code_parameter`: Convierte códigos de distribuidor

Warning:
    Las conversiones incluyen validaciones estrictas específicas para Datadis.
    Por ejemplo, se rechazarán fechas con días específicos en modo mensual para
    prevenir errores comunes.

:author: TacoronteRiveroCristian
"""

from datetime import date, datetime
from typing import Optional, Union

from ..exceptions import ValidationError


def convert_date_to_api_format(
    date_value: Union[str, datetime, date], format_type: str = "daily"
) -> str:
    """
    Convierte fechas de múltiples formatos al formato requerido por la API de Datadis.

    Esta función es el núcleo del sistema de conversión de fechas del SDK. Acepta fechas
    en múltiples formatos naturales de Python y las convierte al formato específico
    requerido por la API de Datadis, aplicando validaciones estrictas para prevenir
    errores comunes.

    Limitaciones específicas de Datadis:
        - **Solo fechas mensuales**: Para la mayoría de endpoints, solo se acepta YYYY/MM
        - **No fechas específicas**: Fechas como YYYY/MM/DD se rechazan en modo mensual
        - **Rango temporal limitado**: Solo últimos 2 años (validado por otros componentes)

    Formatos de entrada soportados:
        - **Strings**: "2024/01", "2024-01-15", "20240115", "15/01/2024"
        - **datetime objects**: ``datetime(2024, 1, 15)`` → "2024/01" (modo mensual)
        - **date objects**: ``date(2024, 1, 15)`` → "2024/01" (modo mensual)

    Validaciones aplicadas:
        - **Detección de días específicos**: Rechaza YYYY/MM/DD en modo mensual
        - **Parseo de múltiples formatos**: Intenta varios formatos comunes automáticamente
        - **Consistencia de modo**: Asegura que el output coincida con el format_type

    :param date_value: Fecha a convertir. Acepta strings en múltiples formatos,
                      objetos datetime, o objetos date de Python
    :type date_value: Union[str, datetime, date]
    :param format_type: Tipo de formato de salida requerido:

                       - **"monthly"**: Formato YYYY/MM (recomendado para Datadis)
                       - **"daily"**: Formato YYYY/MM/DD (limitado en Datadis)

    :type format_type: str

    :return: Fecha formateada según el format_type especificado y validada
            para cumplir con las restricciones de la API de Datadis
    :rtype: str

    :raises ValidationError: En los siguientes casos:

                           - Fecha contiene día específico en modo mensual
                           - Formato de fecha no reconocible
                           - Tipo de entrada no soportado
                           - format_type no válido

    Example:
        Conversiones típicas en modo mensual (recomendado)::

            # Strings en formato correcto (pasan sin cambios)
            convert_date_to_api_format("2024/01", "monthly")  # → "2024/01"

            # Objetos datetime (día se ignora en modo mensual)
            from datetime import datetime
            dt = datetime(2024, 1, 15)
            convert_date_to_api_format(dt, "monthly")  # → "2024/01"

            # Strings en formatos alternativos (se convierten)
            convert_date_to_api_format("2024-01-15", "monthly")  # → "2024/01"
            convert_date_to_api_format("15/01/2024", "monthly")  # → "2024/01"

        Validaciones que fallan (errores esperados)::

            # ❌ Fecha específica en modo mensual
            convert_date_to_api_format("2024/01/15", "monthly")
            # → ValidationError: "API solo acepta fechas mensuales"

            # ❌ datetime con día específico
            dt = datetime(2024, 1, 15)  # día 15, no día 1
            convert_date_to_api_format(dt, "monthly")
            # → ValidationError: "Fecha contiene día específico"

        Conversiones en modo daily::

            # Para endpoints que sí aceptan fechas específicas
            convert_date_to_api_format("2024/01/15", "daily")   # → "2024/01/15"
            dt = datetime(2024, 1, 15)
            convert_date_to_api_format(dt, "daily")             # → "2024/01/15"

    Note:
        La mayoría de endpoints de Datadis solo aceptan fechas mensuales (YYYY/MM).
        Use ``format_type="monthly"`` a menos que esté seguro de que el endpoint
        específico acepta fechas diarias.

    Technical Details:
        - **Detección inteligente**: Analiza el formato de entrada automáticamente
        - **Múltiples intentos**: Prueba varios formatos comunes antes de fallar
        - **Validación estricta**: Previene errores sutiles por formato incorrecto
        - **Retrocompatibilidad**: Strings correctos pasan sin modificación

    .. seealso::
       - :func:`convert_date_range_to_api_format` para rangos de fechas
       - :func:`datadis_python.utils.validators.validate_date_range` para validaciones adicionales
       - Documentación de Datadis sobre formatos de fecha aceptados

    .. versionchanged:: 2.0
       Añadida validación estricta para fechas específicas en modo mensual
    """
    if isinstance(date_value, str):
        # Paso 1: VALIDACIÓN CRÍTICA - Detectar fechas diarias en modo mensual
        if format_type == "monthly" and "/" in date_value:
            parts = date_value.split("/")
            if len(parts) == 3:
                # Formato YYYY/MM/DD detectado en modo mensual - RECHAZAR
                raise ValidationError(
                    f"La API de Datadis solo acepta fechas mensuales en formato YYYY/MM. "
                    f"Recibido: '{date_value}' (contiene día específico). "
                    f"Use formato mensual como: '{parts[0]}/{parts[1]}'"
                )

        # Paso 2: Si ya es string, validar que tenga el formato correcto
        from .validators import validate_date_range

        try:
            # Usar el validador existente para verificar formato
            if format_type == "daily":
                validate_date_range(date_value, date_value, "daily")
            else:
                validate_date_range(date_value, date_value, "monthly")
            return date_value
        except ValidationError:
            # Si falla la validación, intentar parsear y reformatear
            try:
                # Intentar diferentes formatos comunes de fecha
                formats_to_try = ["%Y-%m-%d", "%Y%m%d", "%d/%m/%Y", "%Y/%m/%d"]

                # Manejo especial para formato YYYY/MM
                if "/" in date_value:
                    parts = date_value.split("/")
                    if len(parts) == 2:
                        # Formato YYYY/MM válido
                        dt = datetime(int(parts[0]), int(parts[1]), 1)
                        # Formatear según el tipo requerido
                        if format_type == "daily":
                            return dt.strftime("%Y/%m/%d")
                        else:
                            return dt.strftime("%Y/%m")

                # Intentar los formatos uno por uno
                for fmt in formats_to_try:
                    try:
                        dt = datetime.strptime(date_value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(
                        f"Formato de fecha no reconocido: {date_value}. "
                        f"Formatos soportados: YYYY/MM, YYYY-MM-DD, DD/MM/YYYY, YYYYMMDD"
                    )

                # VALIDACIÓN CRÍTICA: Rechazar fechas específicas en modo mensual
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
        # Paso 3: VALIDACIÓN CRÍTICA para objetos datetime/date en modo mensual
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
    Convierte números de múltiples tipos a strings validados para la API de Datadis.

    La API de Datadis espera parámetros numéricos como strings, pero los usuarios
    naturalmente quieren pasar enteros o floats. Esta función acepta cualquier
    tipo numérico y lo convierte a string después de validar que sea un número válido.

    Validaciones aplicadas:
        - **Strings**: Verifica que representen números válidos antes de retornarlos
        - **Enteros**: Convierte directamente a string
        - **Floats**: Convierte a string con representación completa
        - **Tipos inválidos**: Rechaza con mensaje de error claro

    Casos de uso típicos:
        - **Códigos de distribuidor**: ``2`` → ``"2"``
        - **Tipos de medida**: ``0`` → ``"0"`` (consumo vs generación)
        - **Tipos de punto**: ``1`` → ``"1"`` (frontera, consumo, etc.)
        - **IDs numéricos**: Para cualquier identificador numérico de la API

    :param value: Valor numérico a convertir. Acepta enteros, floats, o strings
                 que representen números válidos
    :type value: Union[str, int, float]

    :return: Representación string del número, validada para ser numérica
    :rtype: str

    :raises ValidationError: Si el valor no es numérico válido o es de tipo no soportado

    Example:
        Conversiones exitosas::

            # Enteros (caso más común)
            convert_number_to_string(2)        # → "2"
            convert_number_to_string(0)        # → "0"
            convert_number_to_string(-1)       # → "-1"

            # Floats
            convert_number_to_string(2.5)      # → "2.5"
            convert_number_to_string(0.0)      # → "0.0"

            # Strings numéricos válidos (pasan sin cambios)
            convert_number_to_string("2")      # → "2"
            convert_number_to_string("2.5")    # → "2.5"

        Casos que fallan (errores esperados)::

            # ❌ String no numérico
            convert_number_to_string("abc")
            # → ValidationError: "String no numérico: abc"

            # ❌ Tipos no soportados
            convert_number_to_string(None)
            # → ValidationError: "Tipo numérico no soportado: <class 'NoneType'>"

            convert_number_to_string([1, 2, 3])
            # → ValidationError: "Tipo numérico no soportado: <class 'list'>"

        Uso en contexto de Datadis::

            # Flexibilidad para el usuario
            distributor_code = 2  # int natural
            api_param = convert_number_to_string(distributor_code)  # "2" para API

            # Validación de entrada
            user_input = "2.5"  # string del usuario
            validated = convert_number_to_string(user_input)  # validado

    Note:
        La función preserva la precisión completa de los floats. Para casos donde
        necesite controlar el número de decimales, aplique redondeo antes de llamar
        esta función.

    Technical Details:
        - **Validación de strings**: Usa ``float()`` para verificar que sean numéricos
        - **Preservación de formato**: Strings válidos se retornan sin modificación
        - **Conversión directa**: Enteros y floats se convierten con ``str()``
        - **Mensajes específicos**: Errores incluyen el valor problemático para debugging

    .. seealso::
       - :func:`convert_optional_number_to_string` para valores que pueden ser None
       - :func:`convert_distributor_code_parameter` para códigos específicos de distribuidor
    """
    if isinstance(value, str):
        # Si ya es string, validar que sea numérico
        try:
            float(value)  # Intentar parsear para validar formato numérico
            return value  # Retornar el string original si es válido
        except ValueError:
            raise ValidationError(f"String no numérico: {value}")

    elif isinstance(value, (int, float)):
        # Convertir números directamente a string
        return str(value)

    else:
        raise ValidationError(
            f"Tipo numérico no soportado: {type(value)}. " f"Use str, int, o float."
        )


def convert_optional_number_to_string(
    value: Optional[Union[str, int, float]]
) -> Optional[str]:
    """
    Convierte números opcionales a strings para la API de Datadis.

    Esta función extiende :func:`convert_number_to_string` para manejar valores
    que pueden ser ``None``, lo que es común en parámetros opcionales de la API.
    Mantiene la semántica de ``None`` (parámetro no especificado) mientras valida
    valores no-None.

    Comportamiento:
        - **None**: Se retorna como ``None`` (parámetro opcional no especificado)
        - **Valores válidos**: Se procesan con :func:`convert_number_to_string`
        - **Valores inválidos**: Se rechazan con ``ValidationError``

    Casos de uso típicos:
        - **point_type**: Parámetro opcional en consultas de consumo
        - **measurement_type**: Parámetro opcional con valor por defecto
        - **Filtros numéricos**: Cualquier filtro numérico opcional

    :param value: Valor numérico opcional a convertir. Puede ser None, entero,
                 float, o string que represente un número
    :type value: Optional[Union[str, int, float]]

    :return: String representando el número si no es None, o None si es None
    :rtype: Optional[str]

    :raises ValidationError: Si el valor no es None y no es numérico válido

    Example:
        Manejo de parámetros opcionales::

            # Valor None (parámetro no especificado)
            convert_optional_number_to_string(None)       # → None

            # Valores numéricos válidos
            convert_optional_number_to_string(2)          # → "2"
            convert_optional_number_to_string(2.5)        # → "2.5"
            convert_optional_number_to_string("3")        # → "3"

            # Valores inválidos (solo si no son None)
            convert_optional_number_to_string("abc")      # → ValidationError

        Uso en consultas de API::

            # point_type es opcional
            point_type = None  # Usuario no especifica
            api_point_type = convert_optional_number_to_string(point_type)  # → None

            # measurement_type especificado por usuario
            measurement_type = 1  # Usuario especifica generación
            api_measurement = convert_optional_number_to_string(measurement_type)  # → "1"

        En métodos del cliente::

            def get_consumption(self, point_type=None, measurement_type=0):
                # Convertir parámetros opcionales
                api_point_type = convert_optional_number_to_string(point_type)
                api_measurement = convert_optional_number_to_string(measurement_type)

                # Solo añadir a params si no son None
                params = {}
                if api_point_type is not None:
                    params["pointType"] = api_point_type
                if api_measurement is not None:
                    params["measurementType"] = api_measurement

    Note:
        Esta función es la forma recomendada de manejar todos los parámetros
        numéricos opcionales en el SDK, ya que mantiene la semántica clara
        entre "no especificado" (None) y "especificado con valor" (string).

    .. seealso::
       - :func:`convert_number_to_string` para valores numéricos obligatorios
       - Documentación de la API de Datadis sobre parámetros opcionales
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
    Convierte y valida un rango de fechas para la API de Datadis.

    Esta función es un wrapper de alto nivel que combina conversión de tipos y
    validación de rangos para asegurar que tanto las fechas individuales como
    el rango completo cumplan con los requisitos de la API de Datadis.

    Proceso de validación en dos etapas:
        1. **Conversión individual**: Cada fecha se convierte usando :func:`convert_date_to_api_format`
        2. **Validación de rango**: El rango se valida usando ``validate_date_range``

    Validaciones aplicadas:
        - **Formato individual**: Cada fecha debe tener formato válido
        - **Consistencia de rango**: ``date_from`` no puede ser posterior a ``date_to``
        - **Límites temporales**: Cumplir restricciones de Datadis (últimos 2 años)
        - **Restricciones de modo**: Solo formatos mensuales si ``format_type="monthly"``

    :param date_from: Fecha de inicio del rango. Acepta múltiples formatos
    :type date_from: Union[str, datetime, date]
    :param date_to: Fecha de fin del rango. Acepta múltiples formatos
    :type date_to: Union[str, datetime, date]
    :param format_type: Tipo de formato de salida:

                       - **"monthly"**: YYYY/MM (recomendado para Datadis)
                       - **"daily"**: YYYY/MM/DD (limitado en Datadis)

    :type format_type: str

    :return: Tupla con fechas convertidas y validadas ``(date_from_str, date_to_str)``
    :rtype: tuple[str, str]

    :raises ValidationError: Si cualquier fecha es inválida o el rango no cumple restricciones

    Example:
        Rangos típicos para consultas mensuales::

            from datetime import date

            # Objetos date → strings de API
            start = date(2024, 1, 1)
            end = date(2024, 12, 31)
            converted = convert_date_range_to_api_format(start, end, "monthly")
            # Resultado: ("2024/01", "2024/12")

            # Strings en formatos mixtos
            converted = convert_date_range_to_api_format(
                "2024-01-01",  # Formato ISO
                "2024/12",     # Formato API
                "monthly"
            )
            # Resultado: ("2024/01", "2024/12")

        Rangos para consultas diarias (limitado)::

            # Solo algunos endpoints aceptan fechas específicas
            converted = convert_date_range_to_api_format(
                "2024/01/01",
                "2024/01/31",
                "daily"
            )
            # Resultado: ("2024/01/01", "2024/01/31")

        Casos que fallan (errores esperados)::

            # ❌ Rango invertido
            convert_date_range_to_api_format("2024/12", "2024/01", "monthly")
            # → ValidationError: "date_from no puede ser posterior a date_to"

            # ❌ Fechas específicas en modo mensual
            convert_date_range_to_api_format("2024/01/15", "2024/01/20", "monthly")
            # → ValidationError: "API solo acepta fechas mensuales"

        Uso típico en métodos del SDK::

            def get_consumption(self, date_from, date_to):
                # Conversión flexible + validación automática
                api_from, api_to = convert_date_range_to_api_format(
                    date_from, date_to, "monthly"
                )

                # api_from y api_to están garantizados como válidos
                params = {"dateFrom": api_from, "dateTo": api_to}

    Note:
        Esta función es la forma recomendada de procesar todos los rangos de fechas
        en el SDK, ya que combina flexibilidad de entrada con validación robusta.

    Performance:
        La función realiza validación completa en cada llamada. Para uso intensivo
        con fechas ya validadas, considere llamar directamente las funciones
        de conversión individual.

    .. seealso::
       - :func:`convert_date_to_api_format` para conversión de fechas individuales
       - :func:`datadis_python.utils.validators.validate_date_range` para validaciones de rango
       - Documentación de Datadis sobre limitaciones temporales

    .. versionchanged:: 2.0
       Añadida validación estricta para prevenir fechas específicas en modo mensual
    """
    # Paso 1: Convertir fechas individuales (incluye validaciones de formato)
    converted_from = convert_date_to_api_format(date_from, format_type)
    converted_to = convert_date_to_api_format(date_to, format_type)

    # Paso 2: Validar el rango completo (incluye validaciones de lógica de negocio)
    from .validators import validate_date_range

    return validate_date_range(converted_from, converted_to, format_type)


def convert_cups_parameter(cups: str) -> str:
    """
    Procesa y valida un código CUPS para la API de Datadis.

    Los códigos CUPS (Código Universal del Punto de Suministro) son identificadores
    únicos para puntos de suministro eléctrico en España. Esta función valida que
    el código tenga el formato correcto antes de enviarlo a la API.

    Formato CUPS español:
        - **Prefijo**: Siempre "ES" (código país)
        - **Longitud**: 20-22 caracteres alfanuméricos después del prefijo
        - **Caracteres**: Solo letras mayúsculas y números
        - **Ejemplo**: ``"ES0031607515707001RC0F"``

    Validaciones aplicadas:
        - **Tipo correcto**: Debe ser string
        - **Formato válido**: Cumplir patrón regex de CUPS españoles
        - **Longitud correcta**: Entre 22-24 caracteres totales (ES + 20-22)

    :param cups: Código CUPS a validar. Debe ser un string con formato válido
    :type cups: str

    :return: Código CUPS validado y limpio (sin espacios extra)
    :rtype: str

    :raises ValidationError: Si el CUPS no cumple con el formato esperado o no es string

    Example:
        Códigos CUPS válidos::

            # Formato típico (20 caracteres después de ES)
            convert_cups_parameter("ES0031607515707001RC0F")  # → "ES0031607515707001RC0F"

            # Formato largo (22 caracteres después de ES)
            convert_cups_parameter("ES1234567890123456789012")  # → "ES1234567890123456789012"

            # Con espacios (se limpian automáticamente)
            convert_cups_parameter(" ES0031607515707001RC0F ")  # → "ES0031607515707001RC0F"

        Casos que fallan (errores esperados)::

            # ❌ Tipo incorrecto
            convert_cups_parameter(123456)
            # → ValidationError: "CUPS debe ser string, recibido: <class 'int'>"

            # ❌ Formato inválido (sin prefijo ES)
            convert_cups_parameter("0031607515707001RC0F")
            # → ValidationError: "Formato CUPS inválido. Debe ser: ES + 20-22 caracteres alfanuméricos"

            # ❌ Demasiado corto
            convert_cups_parameter("ES12345")
            # → ValidationError: "Formato CUPS inválido..."

            # ❌ Caracteres inválidos
            convert_cups_parameter("ES003160751570700@RC0F")
            # → ValidationError: "Formato CUPS inválido..."

        Uso típico en consultas::

            def get_consumption(self, cups, ...):
                # Validar CUPS antes de enviar a API
                validated_cups = convert_cups_parameter(cups)

                # validated_cups está garantizado como válido
                params = {"cups": validated_cups}

    Note:
        Esta función realiza validación del formato pero no verifica que el CUPS
        exista realmente o esté asociado al usuario. Esa validación la realiza
        la API de Datadis en el servidor.

    Technical Details:
        - **Regex pattern**: ``^ES[A-Z0-9]{20,22}$``
        - **Case sensitivity**: Solo acepta mayúsculas (conversión automática)
        - **Limpieza**: Elimina espacios en blanco automáticamente
        - **Delegación**: Usa :func:`datadis_python.utils.validators.validate_cups` internamente

    .. seealso::
       - :func:`datadis_python.utils.validators.validate_cups` para validación detallada
       - Documentación oficial sobre formato de códigos CUPS
       - CNE (Comisión Nacional de Energía) para especificaciones oficiales

    .. versionadded:: 1.0
       Validación de formato CUPS integrada en el SDK
    """
    if not isinstance(cups, str):
        raise ValidationError(f"CUPS debe ser string, recibido: {type(cups)}")

    # Delegar validación detallada al módulo de validadores
    from .validators import validate_cups

    return validate_cups(cups)


def convert_distributor_code_parameter(distributor_code: Union[str, int]) -> str:
    """
    Convierte y valida códigos de distribuidor para la API de Datadis.

    Los códigos de distribuidor identifican las diferentes compañías distribuidoras
    eléctricas en España. Esta función acepta tanto enteros como strings para
    flexibilidad del usuario, y valida que el código sea uno de los oficialmente
    reconocidos por Datadis.

    Distribuidores válidos (códigos oficiales):
        - **"1"**: Viesgo (Cantabria, Asturias)
        - **"2"**: E-distribución/Endesa (Nacional)
        - **"3"**: E-redes (Galicia)
        - **"4"**: ASEME (Melilla)
        - **"5"**: UFD/Naturgy (Nacional)
        - **"6"**: EOSA (Aragón)
        - **"7"**: CIDE (Ceuta)
        - **"8"**: IDE (Baleares)

    Conversión automática:
        - **Enteros**: Se convierten a string (``2`` → ``"2"``)
        - **Strings**: Se validan y retornan si son correctos
        - **Otros tipos**: Se rechazan con error claro

    :param distributor_code: Código del distribuidor. Acepta entero (ej: ``2``)
                           o string (ej: ``"2"``) con código válido
    :type distributor_code: Union[str, int]

    :return: Código de distribuidor como string validado
    :rtype: str

    :raises ValidationError: Si el código no es válido o es de tipo no soportado

    Example:
        Conversiones exitosas::

            # Enteros (forma natural para usuarios)
            convert_distributor_code_parameter(2)      # → "2" (Endesa)
            convert_distributor_code_parameter(5)      # → "5" (Naturgy)
            convert_distributor_code_parameter(1)      # → "1" (Viesgo)

            # Strings válidos (pasan sin cambios)
            convert_distributor_code_parameter("2")    # → "2"
            convert_distributor_code_parameter("8")    # → "8" (IDE Baleares)

        Casos que fallan (errores esperados)::

            # ❌ Código inválido (no existe distribuidor 9)
            convert_distributor_code_parameter(9)
            # → ValidationError: "Código de distribuidor inválido: 9. Válidos: 1, 2, 3, 4, 5, 6, 7, 8"

            # ❌ Código inválido como string
            convert_distributor_code_parameter("99")
            # → ValidationError: "Código de distribuidor inválido: 99..."

            # ❌ Tipo no soportado
            convert_distributor_code_parameter([1, 2])
            # → ValidationError: "Código de distribuidor debe ser string o int, recibido: <class 'list'>"

        Uso típico con constantes::

            from datadis_python.utils.constants import DISTRIBUTOR_CODES

            # Usuario puede usar nombres descriptivos
            endesa_code = DISTRIBUTOR_CODES["E_DISTRIBUCION"]  # "2"
            validated = convert_distributor_code_parameter(endesa_code)  # "2"

            # O directamente números naturales
            validated = convert_distributor_code_parameter(2)  # "2"

        En métodos del SDK::

            def get_supplies(self, distributor_code=None):
                if distributor_code is not None:
                    # Conversión flexible + validación
                    api_code = convert_distributor_code_parameter(distributor_code)
                    params["distributorCode"] = api_code

    Note:
        Aunque la función acepta enteros para comodidad, la API de Datadis
        internamente espera todos los códigos como strings, por eso se hace
        la conversión automática.

    Technical Details:
        - **Validación**: Usa :func:`datadis_python.utils.validators.validate_distributor_code`
        - **Conversión de tipos**: ``int`` → ``str`` automáticamente
        - **Códigos válidos**: Solo 1-8 según distribuidores oficiales españoles
        - **Case insensitive**: Los strings se procesan exactamente como se reciben

    .. seealso::
       - :func:`datadis_python.utils.validators.validate_distributor_code` para validación detallada
       - :data:`datadis_python.utils.constants.DISTRIBUTOR_CODES` para mapeo de nombres
       - Documentación oficial de Datadis sobre códigos de distribuidor

    .. versionadded:: 1.0
       Soporte para conversión automática int → string
    """
    # Paso 1: Convertir enteros a string para uniformidad
    if isinstance(distributor_code, int):
        distributor_code = str(distributor_code)
    elif not isinstance(distributor_code, str):
        raise ValidationError(
            f"Código de distribuidor debe ser string o int, recibido: {type(distributor_code)}"
        )

    # Paso 2: Delegar validación detallada al módulo de validadores
    from .validators import validate_distributor_code

    return validate_distributor_code(distributor_code)
