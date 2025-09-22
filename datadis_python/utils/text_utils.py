r"""
Utilidades para normalización y procesamiento de texto de respuestas de Datadis.

Este módulo proporciona funciones especializadas para procesar y normalizar texto
recibido de la API de Datadis, solucionando problemas comunes de encoding y caracteres
especiales que pueden aparecer en las respuestas del servicio.

La API de Datadis frecuentemente devuelve texto con problemas de encoding, especialmente
con caracteres españoles como tildes (á, é, í, ó, ú), eñes (ñ), cedillas (ç) y otros
caracteres especiales. Este módulo proporciona herramientas robustas para detectar y
corregir estos problemas automáticamente.

Problemas comunes solucionados:
    - **Doble codificación UTF-8**: Secuencias como "Ã\x93" en lugar de "Ó"
    - **Caracteres especiales mal codificados**: "EDISTRIBUCIÃ\x93N" → "EDISTRIBUCION"
    - **Inconsistencias de encoding**: Mezcla de encodings en una misma respuesta
    - **Caracteres no ASCII**: Normalización a ASCII para compatibilidad

Funciones principales:
    - :func:`normalize_text`: Normaliza texto individual con corrección de encoding
    - :func:`normalize_dict_strings`: Normaliza recursivamente todas las cadenas en diccionarios
    - :func:`normalize_list_strings`: Normaliza recursivamente todas las cadenas en listas
    - :func:`normalize_api_response`: Función principal para normalizar respuestas completas

Example:
    Uso típico para procesar respuestas de Datadis::

        from datadis_python.utils.text_utils import normalize_api_response

        # Respuesta raw de Datadis con problemas de encoding
        raw_response = {
            "distributor": "EDISTRIBUCIÃ\x93N",
            "address": "CALLE JOSÃπ MARTÃ\xadNEZ"
        }

        # Normalizar respuesta completa
        clean_response = normalize_api_response(raw_response)
        # Resultado: {"distributor": "EDISTRIBUCION", "address": "CALLE JOSE MARTINEZ"}

    Normalización de texto individual::

        from datadis_python.utils.text_utils import normalize_text

        # Texto con problemas típicos de Datadis
        problematic_text = "MÃ¡laga"
        clean_text = normalize_text(problematic_text)
        # Resultado: "Malaga"

Note:
    Todas las funciones de este módulo son seguras de usar con datos ``None`` o de
    tipos incorrectos - retornan el valor original sin modificar si no pueden procesarlo.

Warning:
    La normalización elimina permanentemente caracteres especiales y acentos. Si necesita
    preservar el texto original, haga una copia antes de aplicar estas funciones.

:author: TacoronteRiveroCristian
"""

import unicodedata
from typing import Any, Dict, List, Union


def normalize_text(text: str) -> str:
    r"""
    Normaliza texto removiendo tildes, caracteres especiales y corrigiendo problemas de encoding.

    Esta función es el núcleo del sistema de normalización de texto del SDK. Aplica múltiples
    estrategias para corregir problemas comunes de encoding que aparecen frecuentemente en
    las respuestas de la API de Datadis, especialmente con caracteres españoles.

    Proceso de normalización:
        1. **Detección de doble codificación**: Identifica secuencias como "Ã\x93" (debe ser "Ó")
        2. **Corrección de encoding**: Recodifica usando latin-1 → UTF-8 cuando es necesario
        3. **Normalización Unicode**: Aplica descomposición NFD para separar caracteres base de acentos
        4. **Eliminación de acentos**: Convierte caracteres acentuados a su equivalente ASCII
        5. **Reemplazos específicos**: Maneja caracteres especiales españoles (ñ, ç, etc.)

    Casos de uso típicos:
        - **Nombres de distribuidores**: "EDISTRIBUCIÃ\x93N" → "EDISTRIBUCION"
        - **Direcciones**: "CALLE JOSÃπ MARTÃ\xadNEZ" → "CALLE JOSE MARTINEZ"
        - **Nombres de municipios**: "MÃ¡laga", "CÃ¡diz" → "Malaga", "Cadiz"
        - **Códigos postales**: Normalmente no necesitan normalización pero se procesan igual

    :param text: Texto a normalizar. Puede contener caracteres especiales, acentos,
                o problemas de doble codificación típicos de Datadis
    :type text: str

    :return: Texto normalizado sin tildes, acentos ni caracteres especiales.
            Convertido completamente a caracteres ASCII seguros
    :rtype: str

    Example:
        Problemas típicos de encoding de Datadis::

            # Doble codificación UTF-8
            normalize_text("EDISTRIBUCIÃ\x93N")     # → "EDISTRIBUCION"
            normalize_text("MÃ¡laga")               # → "Malaga"

            # Caracteres españoles normales
            normalize_text("Málaga")                # → "Malaga"
            normalize_text("Coruña")                # → "Coruna"
            normalize_text("Cáceres")               # → "Caceres"

            # Caracteres especiales
            normalize_text("Peñíscola")             # → "Peniscola"
            normalize_text("François")              # → "Francois"

        Casos extremos manejados::

            # Texto ya normalizado - sin cambios
            normalize_text("MADRID")                # → "MADRID"

            # Mezcla de problemas
            normalize_text("CÃ¡diz - AndalucÃ\xada") # → "Cadiz - Andalucia"

    Note:
        La función es segura con datos de entrada inválidos - si recibe algo que no es
        string, retorna el valor original sin modificar. Esto evita errores en cadenas
        de procesamiento de datos.

    Warning:
        La normalización es irreversible. Si necesita preservar el texto original
        con acentos, haga una copia antes de llamar esta función.

    Technical details:
        - Usa ``unicodedata.normalize('NFD', text)`` para descomposición Unicode
        - Aplica ``encode('ascii', 'ignore')`` para eliminar caracteres no-ASCII
        - Maneja específicamente problemas de doble codificación latin-1/UTF-8
        - Incluye tabla de reemplazos para caracteres que ``unicodedata`` no maneja

    .. seealso::
       - :func:`normalize_dict_strings` para normalizar diccionarios completos
       - :func:`normalize_api_response` para procesar respuestas completas de API
       - Documentación de ``unicodedata`` para detalles sobre normalización Unicode
    """
    if not isinstance(text, str):
        return text

    # Paso 1: Intentar corregir problemas de doble codificación UTF-8
    # Este es un problema muy común en Datadis donde el texto se codifica
    # incorrectamente como latin-1 cuando debería ser UTF-8
    try:
        # Detectar secuencias sospechosas que indican doble codificación
        if "Ã" in text:
            # Codificar como latin-1 y decodificar como UTF-8 para corregir
            corrected_text = text.encode("latin-1").decode("utf-8")
            text = corrected_text
    except (UnicodeError, UnicodeDecodeError):
        # Si hay error en la corrección, continuar con el texto original
        # Es mejor procesar texto ligeramente incorrecto que fallar completamente
        pass

    # Paso 2: Normalizar unicode y remover acentos usando descomposición NFD
    # NFD (Canonical Decomposition) separa caracteres base de sus acentos
    normalized = unicodedata.normalize("NFD", text)
    # Convertir a ASCII ignorando caracteres no representables
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # Paso 3: Conversiones específicas para caracteres que NFD no maneja
    # Estos caracteres necesitan reemplazo manual
    replacements = {
        "Ñ": "N",
        "ñ": "n",  # Eñe española
        "Ç": "C",
        "ç": "c",  # Cedilla francesa/catalana
    }

    for char, replacement in replacements.items():
        ascii_text = ascii_text.replace(char, replacement)

    return ascii_text


def normalize_dict_strings(data: Dict[str, Any]) -> Dict[str, Any]:
    r"""
    Normaliza recursivamente todas las cadenas de texto en un diccionario.

    Esta función recorre un diccionario de forma recursiva aplicando normalización
    de texto a todas las cadenas encontradas, manteniendo la estructura original
    del diccionario pero limpiando el contenido textual.

    Procesamiento recursivo:
        - **Strings**: Aplica :func:`normalize_text` para limpiar caracteres especiales
        - **Diccionarios anidados**: Procesa recursivamente con :func:`normalize_dict_strings`
        - **Listas anidadas**: Procesa recursivamente con :func:`normalize_list_strings`
        - **Otros tipos**: Se mantienen sin modificar (números, booleanos, None, etc.)

    Esta función es especialmente útil para procesar respuestas JSON estructuradas
    de la API de Datadis donde los problemas de encoding pueden aparecer en cualquier
    campo de texto dentro de estructuras complejas.

    :param data: Diccionario con datos a normalizar. Puede contener estructuras anidadas
                complejas con strings que necesiten limpieza de caracteres especiales
    :type data: Dict[str, Any]

    :return: Nuevo diccionario con la misma estructura pero con todos los strings normalizados.
            Los valores no-string se mantienen exactamente igual
    :rtype: Dict[str, Any]

    Example:
        Normalizar respuesta estructurada de Datadis::

            raw_supply_data = {
                "cups": "ES001234567890123456AB",
                "address": "CALLE JOSÃπ MARTÃ\xadNEZ",
                "distributor": "EDISTRIBUCIÃ\x93N",
                "postalCode": "28001",
                "province": "MÃ¡drid",
                "details": {
                    "city": "MÃ¡laga",
                    "municipality": "AndalucÃ\xada"
                },
                "contracts": [
                    {"startDate": "2024/01/01", "type": "Normal"}
                ],
                "active": True,
                "pointType": 2
            }

            normalized_data = normalize_dict_strings(raw_supply_data)
            # Resultado:
            # {
            #     "cups": "ES001234567890123456AB",          # Sin cambio
            #     "address": "CALLE JOSE MARTINEZ",          # Normalizado
            #     "distributor": "EDISTRIBUCION",            # Normalizado
            #     "postalCode": "28001",                     # Sin cambio
            #     "province": "Madrid",                      # Normalizado
            #     "details": {
            #         "city": "Malaga",                      # Normalizado (recursivo)
            #         "municipality": "Andalucia"            # Normalizado (recursivo)
            #     },
            #     "contracts": [
            #         {"startDate": "2024/01/01", "type": "Normal"}  # Procesado recursivamente
            #     ],
            #     "active": True,                            # Sin cambio (boolean)
            #     "pointType": 2                             # Sin cambio (int)
            # }

        Casos extremos manejados::

            # Diccionario vacío
            normalize_dict_strings({})  # → {}

            # Diccionario con valores None
            normalize_dict_strings({"key": None})  # → {"key": None}

            # Anidación profunda
            deep_dict = {"level1": {"level2": {"text": "MÃ¡laga"}}}
            normalize_dict_strings(deep_dict)  # → {"level1": {"level2": {"text": "Malaga"}}}

    Note:
        La función es segura con datos de entrada inválidos - si recibe algo que no es
        diccionario, retorna el valor original sin modificar. Esto permite su uso
        seguro en cadenas de procesamiento donde el tipo de dato puede ser incierto.

    Performance:
        La función crea un nuevo diccionario en lugar de modificar el original,
        lo que la hace segura para uso concurrente pero puede consumir más memoria
        con estructuras muy grandes.

    .. seealso::
       - :func:`normalize_text` para normalización de strings individuales
       - :func:`normalize_list_strings` para normalización de listas
       - :func:`normalize_api_response` para entrada principal de normalización
    """
    if not isinstance(data, dict):
        return data

    normalized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Normalizar strings individuales
            normalized[key] = normalize_text(value)
        elif isinstance(value, dict):
            # Procesar diccionarios anidados recursivamente
            normalized[key] = normalize_dict_strings(value)
        elif isinstance(value, list):
            # Procesar listas anidadas recursivamente
            normalized[key] = normalize_list_strings(value)
        else:
            # Mantener otros tipos sin modificar (int, float, bool, None, etc.)
            normalized[key] = value

    return normalized


def normalize_list_strings(data: List[Any]) -> List[Any]:
    r"""
    Normaliza recursivamente todas las cadenas de texto en una lista.

    Esta función procesa listas de forma recursiva aplicando normalización de texto
    a todos los elementos string encontrados, mientras mantiene la estructura y orden
    original de la lista. Es especialmente útil para procesar arrays de datos de Datadis.

    Procesamiento recursivo por tipo:
        - **Strings**: Aplica :func:`normalize_text` para limpiar caracteres especiales
        - **Diccionarios**: Procesa recursivamente con :func:`normalize_dict_strings`
        - **Listas anidadas**: Procesa recursivamente con :func:`normalize_list_strings`
        - **Otros tipos**: Se mantienen sin modificar (números, booleanos, None, etc.)

    Casos de uso típicos en Datadis:
        - **Arrays de suministros**: Lista de objetos SupplyData con addresses problemáticas
        - **Arrays de consumo**: Lista de ConsumptionData con distributors mal codificados
        - **Arrays mixtos**: Listas que combinan strings, números y objetos

    :param data: Lista con datos a normalizar. Puede contener elementos de cualquier tipo,
                incluidas estructuras anidadas complejas
    :type data: List[Any]

    :return: Nueva lista con la misma estructura y orden, pero con todos los strings
            normalizados. Los elementos no-string se mantienen exactamente igual
    :rtype: List[Any]

    Example:
        Normalizar array de respuesta de Datadis::

            raw_supplies_list = [
                "EDISTRIBUCIÃ\x93N",  # String simple problemático
                {
                    "distributor": "MÃ¡laga ElÃ©ctrica",
                    "address": "CALLE JOSÃπ MARTÃ\xadNEZ"
                },
                ["CÃ¡diz", "SevillÃ¡"],  # Lista anidada
                42,  # Número
                None,  # Valor nulo
                True  # Booleano
            ]

            normalized_list = normalize_list_strings(raw_supplies_list)
            # Resultado:
            # [
            #     "EDISTRIBUCION",                    # String normalizado
            #     {
            #         "distributor": "Malaga Electrica",  # Dict normalizado recursivamente
            #         "address": "CALLE JOSE MARTINEZ"
            #     },
            #     ["Cadiz", "Sevilla"],               # Lista normalizada recursivamente
            #     42,                                 # Sin cambio (int)
            #     None,                               # Sin cambio (None)
            #     True                                # Sin cambio (bool)
            # ]

        Array de objetos de consumo::

            consumption_data = [
                {
                    "date": "2024/01/01",
                    "consumptionKWh": 5.2,
                    "distributor": "EDISTRIBUCIÃ\x93N"
                },
                {
                    "date": "2024/01/02",
                    "consumptionKWh": 4.8,
                    "distributor": "MÃ¡laga ElÃ©ctrica"
                }
            ]

            normalized_consumption = normalize_list_strings(consumption_data)
            # Solo los campos "distributor" se normalizan, fechas y números quedan igual

        Casos extremos::

            # Lista vacía
            normalize_list_strings([])  # → []

            # Lista con solo valores no-string
            normalize_list_strings([1, 2, 3, True, None])  # → [1, 2, 3, True, None]

            # Anidación profunda
            deep_list = [[[["MÃ¡laga"]]]]
            normalize_list_strings(deep_list)  # → [[[["Malaga"]]]]

    Note:
        La función es segura con datos de entrada inválidos - si recibe algo que no es
        lista, retorna el valor original sin modificar. Esto permite su uso seguro
        en cadenas de procesamiento de datos heterogéneos.

    Performance:
        Crea una nueva lista en lugar de modificar la original, garantizando inmutabilidad
        pero puede consumir más memoria con listas muy grandes.

    .. seealso::
       - :func:`normalize_text` para normalización de strings individuales
       - :func:`normalize_dict_strings` para normalización de diccionarios
       - :func:`normalize_api_response` para entrada principal de normalización
    """
    if not isinstance(data, list):
        return data

    normalized: List[Any] = []
    for item in data:
        if isinstance(item, str):
            # Normalizar strings individuales
            normalized.append(normalize_text(item))
        elif isinstance(item, dict):
            # Procesar diccionarios anidados recursivamente
            normalized.append(normalize_dict_strings(item))
        elif isinstance(item, list):
            # Procesar listas anidadas recursivamente
            normalized.append(normalize_list_strings(item))
        else:
            # Mantener otros tipos sin modificar (int, float, bool, None, etc.)
            normalized.append(item)

    return normalized


def normalize_api_response(
    response: Union[Dict[str, Any], List[Any]]
) -> Union[Dict[str, Any], List[Any]]:
    r"""
    Función principal para normalizar respuestas completas de la API de Datadis.

    Esta es la función de entrada principal del sistema de normalización del SDK.
    Detecta automáticamente el tipo de respuesta (diccionario o lista) y aplica
    la estrategia de normalización correspondiente para limpiar todos los strings
    de problemas de encoding y caracteres especiales.

    Función de router inteligente:
        - **Dict response**: Usa :func:`normalize_dict_strings` para procesamiento recursivo
        - **List response**: Usa :func:`normalize_list_strings` para procesamiento recursivo
        - **Otros tipos**: Retorna sin modificar (para compatibilidad futura)

    Esta función es llamada automáticamente por el :class:`HTTPClient` del SDK,
    por lo que los usuarios normalmente no necesitan llamarla manualmente.
    Sin embargo, puede ser útil para procesar datos cacheados o respuestas
    guardadas localmente.

    Casos de uso típicos:
        - **Auto-procesamiento**: Llamada automática por HTTPClient en todas las respuestas JSON
        - **Procesamiento manual**: Para limpiar datos guardados localmente o cacheados
        - **Testing**: Para normalizar respuestas mock en tests unitarios
        - **Debugging**: Para limpiar respuestas antes de análisis manual

    :param response: Respuesta completa de la API de Datadis en formato JSON deserializado.
                    Puede ser un diccionario (respuesta de objeto) o lista (respuesta de array)
    :type response: Union[Dict[str, Any], List[Any]]

    :return: Respuesta normalizada con la misma estructura pero con todos los strings
            limpios de problemas de encoding y caracteres especiales
    :rtype: Union[Dict[str, Any], List[Any]]

    Example:
        Respuestas típicas de diferentes endpoints::

            # Respuesta de get_supplies (lista de objetos)
            supplies_response = [
                {"cups": "ES001...", "distributor": "EDISTRIBUCIÃ\x93N"},
                {"cups": "ES002...", "distributor": "MÃ¡laga ElÃ©ctrica"}
            ]
            clean_supplies = normalize_api_response(supplies_response)
            # Resultado: [{"cups": "ES001...", "distributor": "EDISTRIBUCION"}, ...]

            # Respuesta de get_consumption (objeto con arrays)
            consumption_response = {
                "consumption": [
                    {"date": "2024/01/01", "distributor": "EDISTRIBUCIÃ\x93N"}
                ],
                "distributor_error": []
            }
            clean_consumption = normalize_api_response(consumption_response)
            # Resultado: {"consumption": [{"date": "2024/01/01", "distributor": "EDISTRIBUCION"}], ...}

        Procesamiento manual de datos guardados::

            # Datos cacheados que pueden tener problemas de encoding
            cached_data = load_from_cache("datadis_supplies.json")
            clean_data = normalize_api_response(cached_data)
            # Ahora clean_data está libre de problemas de encoding

        Uso en testing::

            # Mock response con problemas simulados de Datadis
            mock_response = {"distributor": "EDISTRIBUCIÃ\x93N"}
            normalized_mock = normalize_api_response(mock_response)
            # Para tests con datos normalizados

    Note:
        Esta función es completamente segura con cualquier tipo de entrada.
        Si recibe datos que no puede procesar, los retorna sin modificar,
        garantizando que nunca cause errores en el pipeline de datos.

    Performance:
        La función crea nuevas estructuras de datos en lugar de modificar las originales,
        lo que la hace segura para uso concurrente pero puede consumir más memoria
        con respuestas muy grandes (miles de registros).

    Integration:
        Esta función está integrada automáticamente en la cadena de procesamiento
        de respuestas del :class:`HTTPClient`, por lo que todos los datos que
        llegan a los usuarios finales ya están normalizados.

    .. seealso::
       - :func:`normalize_text` para normalización básica de strings
       - :func:`normalize_dict_strings` para objetos JSON
       - :func:`normalize_list_strings` para arrays JSON
       - :class:`datadis_python.utils.http.HTTPClient` donde se integra automáticamente

    .. versionadded:: 1.0
       Normalización automática integrada en todo el SDK

    .. versionchanged:: 2.0
       Mejorada detección de problemas de doble codificación UTF-8
    """
    if isinstance(response, dict):
        return normalize_dict_strings(response)
    elif isinstance(response, list):
        return normalize_list_strings(response)
    else:
        # Para otros tipos (str, int, bool, None, etc.) retornar sin modificar
        # Esto garantiza compatibilidad futura si la API cambia formatos
        return response
