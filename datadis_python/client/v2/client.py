"""
Cliente Datadis API v2 - Devuelve datos raw exactamente como los proporciona la API
"""

from typing import Optional

from ...utils.constants import API_V2_ENDPOINTS
from ...utils.validators import (
    validate_cups,
    validate_date_range,
    validate_distributor_code,
    validate_measurement_type,
    validate_point_type,
)
from ..base import BaseDatadisClient


class DatadisClientV2(BaseDatadisClient):
    """
    Cliente para API v2 de Datadis

    Características:
    - Devuelve datos raw exactamente como los proporciona la API
    - Endpoints v2 con estructura de respuesta actualizada
    - Validación de parámetros de entrada
    - Manejo de errores de distribuidor en formato v2
    """

    def get_supplies(self, distributor_code: Optional[str] = None) -> dict:
        """
        Obtiene la lista de puntos de suministro disponibles

        Args:
            distributor_code: Código del distribuidor (opcional)

        Returns:
            Dict con estructura: {"supplies": [...], "distributorError": [...]}
        """
        params = {}
        if distributor_code:
            params["distributorCode"] = validate_distributor_code(distributor_code)

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["supplies"], params=params
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"supplies": [], "distributorError": []}
        )

    def get_distributors(self) -> dict:
        """
        Obtiene la lista de códigos de distribuidores disponibles

        Returns:
            Dict con estructura: {"distExistenceUser": {"distributorCodes": [...]}, "distributorError": [...]}
        """
        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["distributors"]
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"distExistenceUser": {"distributorCodes": []}, "distributorError": []}
        )

    def get_contract_detail(self, cups: str, distributor_code: str) -> dict:
        """
        Obtiene el detalle del contrato para un CUPS específico

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor

        Returns:
            Dict con estructura: {"contract": [...], "distributorError": [...]}
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)

        params = {"cups": cups, "distributorCode": distributor_code}

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["contracts"], params=params
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"contract": [], "distributorError": []}
        )

    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
    ) -> dict:
        """
        Obtiene datos de consumo para un CUPS y rango de fechas

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            measurement_type: Tipo de medida (0=hora, 1=cuarto hora)
            point_type: Tipo de punto (obtenido de supplies)

        Returns:
            Dict con estructura: {"timeCurve": [...], "distributorError": [...]}
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")
        measurement_type = validate_measurement_type(measurement_type)

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type),
        }

        if point_type is not None:
            params["pointType"] = str(validate_point_type(point_type))

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["consumption"], params=params
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"timeCurve": [], "distributorError": []}
        )

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> dict:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)

        Returns:
            Dict con estructura: {"maxPower": [...], "distributorError": [...]}
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["max_power"], params=params
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"maxPower": [], "distributorError": []}
        )

    def get_reactive_data(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> dict:
        """
        Obtiene datos de energía reactiva (solo disponible en v2)

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)

        Returns:
            Dict con estructura: {"reactiveEnergy": {...}, "distributorError": [...]}
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["reactive_data"], params=params
        )

        # Devolver respuesta raw tal como viene de la API v2
        return (
            response
            if isinstance(response, dict)
            else {"reactiveEnergy": {}, "distributorError": []}
        )
