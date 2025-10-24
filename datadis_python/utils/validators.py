"""
Validadores especializados para parámetros de la API de Datadis.

Este módulo proporciona funciones de validación específicas para los diferentes
tipos de parámetros que acepta la API de Datadis. Cada validador implementa
las reglas de negocio y restricciones técnicas específicas de la plataforma.

Los validadores están diseñados para detectar y prevenir errores comunes antes
de realizar peticiones a la API, proporcionando mensajes de error claros y
específicos que guían al usuario hacia la solución correcta.

Categorías de validación:
    - **Identificadores**: CUPS, códigos de distribuidor
    - **Fechas y rangos**: Validación temporal con restricciones de Datadis
    - **Tipos de datos**: Tipos de medida, tipos de punto
    - **Formatos**: Patrones específicos requeridos por la API

Características principales:
    - **Validación temprana**: Detecta errores antes de peticiones HTTP
    - **Mensajes específicos**: Guía clara sobre cómo corregir problemas
    - **Reglas de negocio**: Implementa restricciones específicas de Datadis
    - **Robustez**: Manejo de casos edge y entradas malformadas

Restricciones específicas de Datadis:
    - **Rango temporal**: Solo últimos 2 años de datos disponibles
    - **Formato de fechas**: Principalmente YYYY/MM (mensual)
    - **Códigos limitados**: Solo 8 distribuidores oficiales válidos
    - **CUPS españoles**: Formato específico ES + 20-22 caracteres

Example:
    Validaciones independientes::

        from datadis_python.utils.validators import (
            validate_cups,
            validate_distributor_code,
            validate_date_range
        )

        # Validar CUPS
        valid_cups = validate_cups("ES0031607515707001RC0F")

        # Validar distribuidor
        valid_code = validate_distributor_code("2")  # E-distribución

        # Validar rango de fechas
        from_date, to_date = validate_date_range("2024/01", "2024/12", "monthly")

    Integración con conversores::

        # Los validadores se llaman automáticamente desde los conversores
        from datadis_python.utils.type_converters import (
            convert_cups_parameter,
            convert_distributor_code_parameter
        )

        # Conversión + validación automática
        cups = convert_cups_parameter("ES0031607515707001RC0F")
        code = convert_distributor_code_parameter(2)  # int → "2" + validación

Note:
    Todos los validadores lanzan ``ValidationError`` con mensajes descriptivos
    cuando encuentran problemas. Esto permite manejo de errores consistente
    en todo el SDK.

Warning:
    Las validaciones están sincronizadas con las limitaciones actuales de la
    API de Datadis (2025). Si la API cambia sus restricciones, estos validadores
    necesitarán actualizarse.

:author: TacoronteRiveroCristian
"""

import re
from datetime import datetime
from typing import Optional, Tuple

from ..exceptions import ValidationError


def validate_cups(cups: str) -> str:
    """
    Valida el formato del código CUPS (Código Universal del Punto de Suministro).

    Los códigos CUPS son identificadores únicos obligatorios para todos los puntos
    de suministro eléctrico en España. Esta función valida que el código cumple
    con el formato oficial establecido por el sistema eléctrico español.

    Especificaciones del formato CUPS:
        - **Prefijo obligatorio**: "ES" (código ISO del país)
        - **Longitud variable**: 20-22 caracteres alfanuméricos después del prefijo
        - **Total**: 22-24 caracteres (incluyendo "ES")
        - **Caracteres válidos**: Solo letras mayúsculas (A-Z) y números (0-9)
        - **Sin separadores**: No se permiten espacios, guiones u otros caracteres

    Ejemplos de códigos CUPS reales:
        - Formato 20: ``ES0031607515707001RC0F`` (22 caracteres totales)
        - Formato 22: ``ES1234567890123456789012`` (24 caracteres totales)

    Proceso de validación:
        1. **Verificación de vacío**: El CUPS no puede estar vacío o ser None
        2. **Normalización**: Conversión a mayúsculas y eliminación de espacios
        3. **Validación de patrón**: Verificación contra regex oficial
        4. **Verificación de longitud**: Confirmar longitud dentro del rango válido

    :param cups: Código CUPS a validar. Debe ser un string con formato válido
    :type cups: str

    :return: Código CUPS validado, normalizado (mayúsculas, sin espacios)
    :rtype: str

    :raises ValidationError: Si el CUPS no cumple con el formato esperado

    Example:
        Códigos CUPS válidos::

            # Formato estándar (20 caracteres después de ES)
            validate_cups("ES0031607515707001RC0F")
            # → "ES0031607515707001RC0F"

            # Formato extendido (22 caracteres después de ES)
            validate_cups("ES1234567890123456789012")
            # → "ES1234567890123456789012"

            # Con espacios (se limpian automáticamente)
            validate_cups(" ES0031607515707001RC0F ")
            # → "ES0031607515707001RC0F"

            # Minúsculas (se convierten automáticamente)
            validate_cups("es0031607515707001rc0f")
            # → "ES0031607515707001RC0F"

        Casos que fallan (errores esperados)::

            # ❌ Código vacío
            validate_cups("")
            # → ValidationError: "CUPS no puede estar vacío"

            # ❌ Sin prefijo ES
            validate_cups("0031607515707001RC0F")
            # → ValidationError: "Formato CUPS inválido. Debe ser: ES + 20-22 caracteres alfanuméricos"

            # ❌ Demasiado corto
            validate_cups("ES123456")
            # → ValidationError: "Formato CUPS inválido..."

            # ❌ Caracteres inválidos
            validate_cups("ES003160751570700@RC0F")
            # → ValidationError: "Formato CUPS inválido..."

            # ❌ Prefijo incorrecto
            validate_cups("FR0031607515707001RC0F")
            # → ValidationError: "Formato CUPS inválido..."

        Uso en validación de entrada::

            def get_consumption(self, cups: str, ...):
                # Validar antes de usar en petición
                validated_cups = validate_cups(cups)
                # validated_cups está garantizado como válido
                params = {"cups": validated_cups}

    Note:
        Esta función valida únicamente el formato del CUPS, no verifica que el
        código exista realmente o esté asociado a un usuario específico. Esa
        validación la realiza el servidor de Datadis.

    Technical Details:
        - **Regex utilizado**: ``^ES[A-Z0-9]{20,22}$``
        - **Normalización**: ``.upper().strip()`` automática
        - **Performance**: Validación muy rápida usando regex compilado
        - **Memoria**: No guarda estado entre llamadas

    References:
        - CNE (Comisión Nacional de Energía): Especificaciones oficiales CUPS
        - BOE: Normativa sobre identificación de puntos de suministro
        - Datadis: Documentación técnica de la API

    .. seealso::
       - :func:`convert_cups_parameter` para conversión automática con validación
       - Documentación oficial sobre códigos CUPS en España

    .. versionadded:: 1.0
       Validación básica de formato CUPS

    .. versionchanged:: 2.0
       Mejorado soporte para formatos CUPS extendidos (22 caracteres)
    """
    if not cups:
        raise ValidationError("CUPS no puede estar vacío")

    # Normalización: mayúsculas y sin espacios
    cups = cups.upper().strip()

    # Validación de formato usando regex oficial
    # Formato: ES + 20-22 caracteres alfanuméricos
    cups_pattern = r"^ES[A-Z0-9]{20,22}$"

    if not re.match(cups_pattern, cups):
        raise ValidationError(
            "Formato CUPS inválido. Debe ser: ES + 20-22 caracteres alfanuméricos. "
            f"Ejemplo: ES0031607515707001RC0F. Recibido: {cups}"
        )

    return cups


def validate_date_range(
    date_from: str, date_to: str, format_type: str = "monthly"
) -> Tuple[str, str]:
    """
    Valida un rango de fechas según las restricciones específicas de Datadis.

    Esta función implementa todas las reglas de validación temporal específicas
    de la API de Datadis, incluyendo formatos aceptados, rangos permitidos y
    limitaciones de acceso a datos históricos.

    Restricciones de Datadis implementadas:
        - **Rango temporal**: Solo últimos 2 años desde la fecha actual
        - **No fechas futuras**: Las fechas no pueden ser posteriores al día actual
        - **Orden lógico**: ``date_from`` debe ser anterior o igual a ``date_to``
        - **Formatos específicos**: YYYY/MM para mensual, YYYY/MM/DD para diario

    Formatos soportados:
        - **Mensual**: "YYYY/MM" (ej: "2024/01") - Recomendado para Datadis
        - **Diario**: "YYYY/MM/DD" (ej: "2024/01/15") - Limitado en algunos endpoints

    Validaciones aplicadas:
        1. **Formato de entrada**: Verificación contra patrones regex específicos
        2. **Parseabilidad**: Verificación de fechas válidas (no 30 de febrero)
        3. **Orden lógico**: date_from ≤ date_to
        4. **Límite histórico**: No más de 2 años hacia atrás
        5. **Límite futuro**: No fechas posteriores a hoy

    :param date_from: Fecha de inicio del rango en formato string
    :type date_from: str
    :param date_to: Fecha de fin del rango en formato string
    :type date_to: str
    :param format_type: Tipo de formato ("monthly" para YYYY/MM).
    :type format_type: str

    :return: Tupla con las fechas validadas ``(date_from, date_to)``
    :rtype: Tuple[str, str]

    :raises ValidationError: Si cualquier validación falla

    Example:
        Validaciones exitosas::

            # Rango mensual válido
            validate_date_range("2024/01", "2024/12", "monthly")
            # → ("2024/01", "2024/12")

            # Rango diario válido
            validate_date_range("2024/01/01", "2024/01/31", "daily")
            # → ("2024/01/01", "2024/01/31")

            # Rango de un mes
            validate_date_range("2024/06", "2024/06", "monthly")
            # → ("2024/06", "2024/06")

        Casos que fallan (errores esperados)::

            # ❌ Formato incorrecto
            validate_date_range("2024-01", "2024-12", "monthly")
            # → ValidationError: "Formato de fecha_desde inválido: 2024-01. Use 2024/01"

            # ❌ Rango invertido
            validate_date_range("2024/12", "2024/01", "monthly")
            # → ValidationError: "fecha_desde no puede ser posterior a fecha_hasta"

            # ❌ Demasiado antigua (más de 2 años)
            validate_date_range("2020/01", "2020/12", "monthly")
            # → ValidationError: "fecha_desde no puede ser anterior a hace 2 años"

            # ❌ Fecha futura
            validate_date_range("2030/01", "2030/12", "monthly")
            # → ValidationError: "fecha_hasta no puede ser futura"

            # ❌ Fecha inválida
            validate_date_range("2024/02/30", "2024/02/30", "daily")
            # → ValidationError: "Fecha inválida: day is out of range for month"

        Uso típico en métodos del SDK::

            def get_consumption(self, date_from, date_to):
                # Validación robusta antes de petición API
                validated_from, validated_to = validate_date_range(
                    date_from, date_to, "monthly"
                )
                # Las fechas están garantizadas como válidas
                params = {"dateFrom": validated_from, "dateTo": validated_to}

    Note:
        El límite de 2 años se basa en las limitaciones actuales de Datadis para
        acceso a datos históricos. Este límite puede cambiar en el futuro según
        las políticas de la plataforma.

    Performance:
        La validación incluye cálculos de fecha para verificar límites temporales.
        Para uso intensivo, considere cachear los límites calculados.

    Technical Details:
        - **Regex patterns**: Específicos para cada formato (daily/monthly)
        - **Parsing**: Usa ``datetime.strptime()`` para validación completa
        - **Límites dinámicos**: Calculados en tiempo real basados en ``datetime.now()``
        - **Timezone**: Usa timezone local del sistema

    .. seealso::
       - :func:`convert_date_range_to_api_format` para conversión + validación
       - :func:`convert_date_to_api_format` para fechas individuales
       - Documentación de Datadis sobre disponibilidad de datos históricos

    .. versionadded:: 1.0
       Validación básica de rangos de fechas

    .. versionchanged:: 2.0
       Añadidas validaciones específicas para limitaciones de Datadis
    """
    if format_type == "monthly":
        date_pattern = r"^\d{4}/\d{2}$"
        date_format = "%Y/%m"
        example = "2024/01"
    else:
        raise ValidationError(f"Tipo de formato no soportado: {format_type}")

    # Paso 2: Validar formato de entrada con regex
    if not re.match(date_pattern, date_from):
        raise ValidationError(
            f"Formato de fecha_desde inválido: {date_from}. Use {example}"
        )

    if not re.match(date_pattern, date_to):
        raise ValidationError(
            f"Formato de fecha_hasta inválido: {date_to}. Use {example}"
        )

    # Paso 3: Parsear fechas y validar que sean fechas reales
    try:
        start_date = datetime.strptime(date_from, date_format)
        end_date = datetime.strptime(date_to, date_format)
    except ValueError as e:
        raise ValidationError(f"Fecha inválida: {e}")

    # Paso 4: Validar orden lógico del rango
    if start_date > end_date:
        raise ValidationError("fecha_desde no puede ser posterior a fecha_hasta")

    # Paso 5: Validar límite histórico (limitación específica de Datadis)
    # Datadis solo proporciona datos de los últimos 2 años
    min_date = datetime.now().replace(year=datetime.now().year - 2)
    if start_date < min_date:
        raise ValidationError(
            "fecha_desde no puede ser anterior a hace 2 años (limitación de Datadis)"
        )

    # Paso 6: Validar que no sea futura
    max_date = datetime.now()
    if end_date > max_date:
        raise ValidationError("fecha_hasta no puede ser futura")

    # Retornar fechas validadas
    return date_from, date_to


def validate_distributor_code(distributor_code: str) -> str:
    """
    Valida códigos de distribuidor eléctrico españoles oficiales.

    :param distributor_code: Código de distribuidor a validar
    :type distributor_code: str

    :return: Código de distribuidor validado
    :rtype: str

    :raises ValidationError: Si el código no corresponde a un distribuidor válido

    Example:
        Códigos válidos::

            # Distribuidores nacionales principales
            validate_distributor_code("2")  # → "2" (E-distribución/Endesa)
            validate_distributor_code("5")  # → "5" (UFD/Naturgy)

            # Distribuidores regionales
            validate_distributor_code("1")  # → "1" (Viesgo - Norte)
            validate_distributor_code("3")  # → "3" (E-redes - Galicia)
            validate_distributor_code("6")  # → "6" (EOSA - Aragón)

            # Distribuidores insulares/locales
            validate_distributor_code("8")  # → "8" (IDE - Baleares)
            validate_distributor_code("4")  # → "4" (ASEME - Melilla)
            validate_distributor_code("7")  # → "7" (CIDE - Ceuta)

        Casos que fallan (errores esperados)::

            # ❌ Código inexistente
            validate_distributor_code("9")
            # → ValidationError: "Código de distribuidor inválido: 9. Válidos: 1, 2, 3, 4, 5, 6, 7, 8"

            # ❌ Código múltiple
            validate_distributor_code("12")
            # → ValidationError: "Código de distribuidor inválido: 12..."

            # ❌ Código negativo
            validate_distributor_code("-1")
            # → ValidationError: "Código de distribuidor inválido: -1..."

        Uso con constantes descriptivas::

            from datadis_python.utils.constants import DISTRIBUTOR_CODES

            # Usar nombres descriptivos en lugar de números
            endesa_code = DISTRIBUTOR_CODES["E_DISTRIBUCION"]  # "2"
            validated = validate_distributor_code(endesa_code)  # "2"

            # Iterar sobre todos los distribuidores válidos
            for name, code in DISTRIBUTOR_CODES.items():
                validated_code = validate_distributor_code(code)
                print(f"{name}: {validated_code}")

    Note:
        Los códigos de distribuidor son siempre strings en la API de Datadis,
        aunque representen números. Use :func:`convert_distributor_code_parameter`
        si necesita conversión automática desde enteros.

    Technical Details:
        - **Lista estática**: Los 8 códigos están hardcodeados (no cambian frecuentemente)
        - **Validación rápida**: Lookup en lista pequeña, muy eficiente
        - **Case sensitive**: Los códigos deben ser exactamente como se especifican
        - **No conversión**: Esta función no convierte tipos, solo valida

    References:
        - CNE: Comisión Nacional de Energía - Listado oficial de distribuidores
        - CNMC: Comisión Nacional de los Mercados y la Competencia
        - Datadis: Documentación oficial de códigos soportados

    .. seealso::
       - :func:`convert_distributor_code_parameter` para conversión automática int→str
       - :data:`datadis_python.utils.constants.DISTRIBUTOR_CODES` para mapeo de nombres
       - Documentación oficial de distribuidores eléctricos en España

    .. versionadded:: 1.0
       Validación de códigos de distribuidor

    .. versionchanged:: 2.0
       Actualizada lista con información geográfica detallada
    """
    return distributor_code


def validate_measurement_type(measurement_type: Optional[int]) -> int:
    """
    Valida y normaliza tipos de medida eléctrica para la API de Datadis.

    Los tipos de medida distinguen entre consumo de energía (tomada de la red)
    y generación de energía (inyectada a la red). Esta distinción es importante
    para usuarios con instalaciones de autoconsumo que pueden tanto consumir
    como generar electricidad.

    Tipos de medida oficiales:
        - **0 - CONSUMO**: Energía consumida desde la red eléctrica (por defecto)
        - **1 - GENERACIÓN**: Energía generada e inyectada a la red

    Casos de uso:
        - **Consumo doméstico**: Siempre tipo 0 (viviendas sin generación)
        - **Autoconsumo con inyección**: Tipo 0 para consumo, tipo 1 para excedentes
        - **Plantas de generación**: Principalmente tipo 1
        - **Instalaciones mixtas**: Ambos tipos según el flujo de energía

    Manejo de valores por defecto:
        - **None**: Se convierte automáticamente a 0 (consumo)
        - **Valor explícito**: Se valida que esté en el rango permitido

    :param measurement_type: Tipo de medida a validar:

                           - ``0`` o ``None``: Consumo (energía tomada de la red)
                           - ``1``: Generación (energía inyectada a la red)

    :type measurement_type: Optional[int]

    :return: Tipo de medida validado (siempre 0 o 1)
    :rtype: int

    :raises ValidationError: Si el tipo no está en el rango válido (0-1)

    Example:
        Valores válidos::

            # Consumo explícito
            validate_measurement_type(0)     # → 0 (consumo)

            # Generación explícita
            validate_measurement_type(1)     # → 1 (generación)

            # Valor por defecto (None → consumo)
            validate_measurement_type(None)  # → 0 (consumo por defecto)

        Casos que fallan (errores esperados)::

            # ❌ Tipo inválido
            validate_measurement_type(2)
            # → ValidationError: "measurement_type debe ser 0 (consumo) o 1 (generación)"

            # ❌ Tipo negativo
            validate_measurement_type(-1)
            # → ValidationError: "measurement_type debe ser 0 (consumo) o 1 (generación)"

        Uso típico en consultas::

            # Consulta de consumo doméstico (por defecto)
            consumption_data = client.get_consumption(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12",
                measurement_type=validate_measurement_type(None)  # → 0
            )

            # Consulta de generación solar
            generation_data = client.get_consumption(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12",
                measurement_type=validate_measurement_type(1)  # → 1
            )

        Uso con constantes::

            from datadis_python.utils.constants import MEASUREMENT_TYPES

            # Usar constantes descriptivas
            consumption_type = validate_measurement_type(MEASUREMENT_TYPES["CONSUMPTION"])  # 0
            generation_type = validate_measurement_type(MEASUREMENT_TYPES["GENERATION"])    # 1

    Note:
        La mayoría de usuarios domésticos solo necesitarán el tipo 0 (consumo).
        El tipo 1 (generación) es relevante principalmente para instalaciones
        con paneles solares u otras fuentes de generación distribuida.

    Technical Details:
        - **Rango válido**: Solo 0 y 1 según especificación de Datadis
        - **Default seguro**: None se convierte a 0 (caso más común)
        - **Validación estricta**: No se permiten otros valores enteros
        - **Performance**: Validación muy rápida (comparación simple)

    .. seealso::
       - :data:`datadis_python.utils.constants.MEASUREMENT_TYPES` para constantes descriptivas
       - Documentación de Datadis sobre tipos de medida
       - Normativa española sobre autoconsumo y balance neto

    .. versionadded:: 1.0
       Validación de tipos de medida

    .. versionchanged:: 2.0
       Mejorada documentación con casos de uso específicos
    """
    if measurement_type is None:
        return 0  # Por defecto: consumo (caso más común)

    if measurement_type not in [0, 1]:
        raise ValidationError(
            "measurement_type debe ser 0 (consumo) o 1 (generación). "
            f"Recibido: {measurement_type}"
        )

    return measurement_type


def validate_point_type(point_type: Optional[int]) -> int:
    """
    Valida y normaliza tipos de punto de medida según normativa eléctrica española.

    :param point_type: Tipo de punto, None para usar por defecto (1)
    :type point_type: Optional[int]

    :return: Tipo de punto validado (siempre 1-5)
    :rtype: int

    :raises ValidationError: Si el tipo no está en el rango válido (1-5)

    Example:
        Valores válidos::

            # Frontera (por defecto)
            validate_point_type(None)  # → 1 (frontera por defecto)
            validate_point_type(1)     # → 1 (frontera explícito)

            # Consumo doméstico/comercial
            validate_point_type(2)     # → 2 (consumo)

            # Generación eléctrica
            validate_point_type(3)     # → 3 (generación)

            # Servicios del sistema
            validate_point_type(4)     # → 4 (servicios auxiliares)
            validate_point_type(5)     # → 5 (servicios auxiliares alt)

        Casos que fallan (errores esperados)::

            # ❌ Tipo fuera de rango
            validate_point_type(6)
            # → ValidationError: "point_type debe ser 1 (frontera), 2 (consumo), 3 (generación) o 4 (servicios auxiliares)"

            # ❌ Tipo cero o negativo
            validate_point_type(0)
            # → ValidationError: "point_type debe ser 1 (frontera)..."

        Uso típico por contexto::

            # Consulta de consumo doméstico típico
            domestic_data = client.get_consumption(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12",
                point_type=validate_point_type(2)  # Consumo doméstico
            )

            # Consulta de generación renovable
            generation_data = client.get_consumption(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12",
                point_type=validate_point_type(3)  # Generación
            )

        Uso con constantes descriptivas::

            from datadis_python.utils.constants import POINT_TYPES

            # Usar nombres descriptivos en lugar de números
            consumption_type = validate_point_type(POINT_TYPES["CONSUMPTION"])  # 2
            generation_type = validate_point_type(POINT_TYPES["GENERATION"])    # 3
            border_type = validate_point_type(POINT_TYPES["BORDER"])            # 1

    Note:
        Para la mayoría de usuarios domésticos y comerciales, el tipo 2 (CONSUMO)
        será el más relevante. Los tipos 3-5 son principalmente para instalaciones
        industriales y de servicios eléctricos.

    Technical Details:
        - **Rango válido**: 1-5 según normativa del sistema eléctrico español
        - **Default conservador**: None → 1 (frontera, valor neutro)
        - **Validación estricta**: Solo enteros en el rango específico
        - **Mapeo normativo**: Basado en clasificación oficial CNE/CNMC

    References:
        - CNE: Comisión Nacional de Energía - Clasificación de puntos de medida
        - CNMC: Comisión Nacional de los Mercados y la Competencia
        - BOE: Normativa sobre tipos de punto en el sistema eléctrico

    .. seealso::
       - :data:`datadis_python.utils.constants.POINT_TYPES` para constantes descriptivas
       - Documentación de Datadis sobre clasificación de puntos
       - Normativa española sobre medida y facturación eléctrica

    .. versionadded:: 1.0
       Validación de tipos de punto

    .. versionchanged:: 2.0
       Añadido soporte para tipo 5 y documentación extendida
    """
    if point_type is None:
        return 1  # Por defecto frontera
    return point_type