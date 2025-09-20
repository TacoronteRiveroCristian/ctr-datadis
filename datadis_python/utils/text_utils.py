"""
Utilidades para normalización de texto y manejo de caracteres especiales.

Este módulo contiene funciones para procesar y normalizar texto, eliminando caracteres especiales y tildes.
"""

import unicodedata
from typing import Any, Dict, List, Union


def normalize_text(text: str) -> str:
    """
    Normaliza texto removiendo tildes y caracteres especiales.

    :param text: Texto a normalizar.
    :type text: str
    :return: Texto normalizado sin tildes ni caracteres especiales.
    :rtype: str

    :Example:
        >>> normalize_text("EDISTRIBUCIÓN")
        'EDISTRIBUCION'
        >>> normalize_text("Málaga")
        'Malaga'
    """
    if not isinstance(text, str):
        return text

    # Intentar corregir problemas de doble codificación UTF-8
    try:
        # Si el texto tiene secuencias como Ã\x93 (que debería ser Ó)
        if "Ã" in text:
            # Codificar como latin-1 y decodificar como UTF-8 para corregir la codificación
            corrected_text = text.encode("latin-1").decode("utf-8")
            text = corrected_text
    except (UnicodeError, UnicodeDecodeError):
        # Si hay error, continuar con el texto original
        pass

    # Normalizar unicode y remover acentos
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # Conversiones específicas adicionales
    replacements = {"Ñ": "N", "ñ": "n", "Ç": "C", "ç": "c"}

    for char, replacement in replacements.items():
        ascii_text = ascii_text.replace(char, replacement)

    return ascii_text


def normalize_dict_strings(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza todas las cadenas de texto en un diccionario.

    :param data: Diccionario con datos a normalizar.
    :type data: dict
    :return: Diccionario con strings normalizados.
    :rtype: dict
    """
    if not isinstance(data, dict):
        return data

    normalized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            normalized[key] = normalize_text(value)
        elif isinstance(value, dict):
            normalized[key] = normalize_dict_strings(value)
        elif isinstance(value, list):
            normalized[key] = normalize_list_strings(value)
        else:
            normalized[key] = value

    return normalized


def normalize_list_strings(data: List[Any]) -> List[Any]:
    """
    Normaliza todas las cadenas de texto en una lista.

    :param data: Lista con datos a normalizar.
    :type data: list
    :return: Lista con strings normalizados.
    :rtype: list
    """
    if not isinstance(data, list):
        return data

    normalized: List[Any] = []
    for item in data:
        if isinstance(item, str):
            normalized.append(normalize_text(item))
        elif isinstance(item, dict):
            normalized.append(normalize_dict_strings(item))
        elif isinstance(item, list):
            normalized.append(normalize_list_strings(item))
        else:
            normalized.append(item)

    return normalized


def normalize_api_response(
    response: Union[Dict[str, Any], List[Any]]
) -> Union[Dict[str, Any], List[Any]]:
    """
    Normaliza respuesta de API completa (puede ser dict o list).

    :param response: Respuesta de la API de Datadis.
    :type response: Union[Dict[str, Any], List[Any]]
    :return: Respuesta normalizada sin caracteres especiales.
    :rtype: Union[Dict[str, Any], List[Any]]
    """
    if isinstance(response, dict):
        return normalize_dict_strings(response)
    elif isinstance(response, list):
        return normalize_list_strings(response)
    else:
        return response
