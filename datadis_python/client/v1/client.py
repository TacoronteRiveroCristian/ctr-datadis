"""
Cliente Datadis API v1 - Respuestas raw para máxima compatibilidad.

Este módulo proporciona un cliente para interactuar con la versión 1 de la API de Datadis.
"""

from typing import Any, Dict, List, Optional

from ...utils.constants import API_V1_ENDPOINTS
from ..base import BaseDatadisClient


class DatadisClientV1(BaseDatadisClient):
    """
    Cliente para API v1 de Datadis.

    :param username: NIF del usuario registrado en Datadis.
    :type username: str
    :param password: Contraseña de acceso a Datadis.
    :type password: str
    :param timeout: Timeout para requests en segundos.
    :type timeout: int
    :param retries: Número de reintentos automáticos.
    :type retries: int
    """

    def get_supplies(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de puntos de suministro disponibles.

        :return: Lista de suministros como diccionarios raw.
        :rtype: List[Dict[str, Any]]

        :Example:
            [
                {
                    "address": "CAMINO DEL HIERRO 2",
                    "cups": "ES0031607515707001RC0F",
                    "postalCode": "38009",
                    "province": "Santa Cruz de Tenerife",
                    "municipality": "SANTA CRUZ DE TENERIFE",
                    "distributor": "EDISTRIBUCIÓN",
                    "validDateFrom": "2024/11/01",
                    "validDateTo": "",
                    "pointType": 3,
                    "distributorCode": "2"
                }
            ]
        """
        response = self.make_authenticated_request("GET", API_V1_ENDPOINTS["supplies"])

        # API v1 devuelve directamente una lista
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "supplies" in response:
            return response["supplies"]

        return []

    def get_distributors(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de distribuidores disponibles.

        :return: Lista de distribuidores como diccionarios raw.
        :rtype: List[Dict[str, Any]]
        """
        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["distributors"]
        )

        # Manejar diferentes formatos de respuesta
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return [response] if response else []

        return []

    def get_contract_detail(
        self, cups: str, distributor_code: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el detalle del contrato para un CUPS específico.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).

        :return: Lista de datos del contrato como diccionarios raw (según API spec).
        :rtype: List[Dict[str, Any]]
        """
        params = {"cups": cups, "distributorCode": distributor_code}

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["contracts"], params=params
        )

        # Según la documentación de la API, siempre debe devolver una lista de diccionarios
        if isinstance(response, list):
            # Ya es una lista, devolverla directamente
            return response
        elif isinstance(response, dict):
            # Si viene un objeto, envolverlo en una lista
            if response:  # Solo si tiene contenido
                return [response]

        # Si no hay datos válidos, devolver lista vacía
        return []

    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene datos de consumo para un CUPS y rango de fechas.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).
        :param date_from: Fecha inicial (YYYY/MM).
        :param date_to: Fecha final (YYYY/MM).
        :param measurement_type: Tipo de medida (0=hora, 1=cuarto hora).
        :param point_type: Tipo de punto (1-5, opcional).

        :return: Lista de datos de consumo como diccionarios raw.
        :rtype: List[Dict[str, Any]]
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type),
        }

        if point_type is not None:
            params["pointType"] = str(point_type)

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["consumption"], params=params
        )

        # Manejar diferentes formatos de respuesta
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "timeCurve" in response:
            return response["timeCurve"]

        return []

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).
        :param date_from: Fecha inicial (YYYY/MM).
        :param date_to: Fecha final (YYYY/MM).

        :return: Lista de datos de potencia máxima como diccionarios raw.
        :rtype: List[Dict[str, Any]]
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["max_power"], params=params
        )

        # Manejar diferentes formatos de respuesta
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "maxPower" in response:
            return response["maxPower"]

        return []

    # Métodos de conveniencia para acceso rápido

    def get_cups_list(self) -> List[str]:
        """
        Obtiene solo la lista de códigos CUPS disponibles.

        :return: Lista de códigos CUPS.
        :rtype: List[str]
        """
        supplies = self.get_supplies()
        return [supply.get("cups", "") for supply in supplies if supply.get("cups")]

    def get_distributor_codes(self) -> List[str]:
        """
        Obtiene solo los códigos de distribuidores disponibles.

        :return: Lista de códigos de distribuidores.
        :rtype: List[str]
        """
        supplies = self.get_supplies()
        codes = set()
        for supply in supplies:
            if supply.get("distributorCode"):
                codes.add(supply["distributorCode"])
        return list(codes)
