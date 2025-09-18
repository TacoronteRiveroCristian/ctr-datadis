"""
Cliente Datadis API v1 - Respuestas raw para máxima compatibilidad.

Este módulo proporciona un cliente para interactuar con la versión 1 de la API de Datadis.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ...utils.constants import API_V1_ENDPOINTS
from ..base import BaseDatadisClient

if TYPE_CHECKING:
    from ...models.consumption import ConsumptionData
    from ...models.contract import ContractData
    from ...models.distributor import DistributorData
    from ...models.max_power import MaxPowerData
    from ...models.supply import SupplyData


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

    def get_supplies(self) -> List["SupplyData"]:
        """
        Obtiene la lista de puntos de suministro disponibles validados con Pydantic.

        :return: Lista de suministros como objetos SupplyData validados.
        :rtype: List[SupplyData]

        :Example:
            [
                SupplyData(
                    address="CAMINO DEL HIERRO 2",
                    cups="ES0031607515707001RC0F",
                    postal_code="38009",
                    province="Santa Cruz de Tenerife",
                    municipality="SANTA CRUZ DE TENERIFE",
                    distributor="EDISTRIBUCIÓN",
                    valid_date_from="2024/11/01",
                    valid_date_to="",
                    point_type=3,
                    distributor_code="2"
                )
            ]
        """
        response = self.make_authenticated_request("GET", API_V1_ENDPOINTS["supplies"])

        # API v1 devuelve directamente una lista
        raw_supplies = []
        if isinstance(response, list):
            raw_supplies = response
        elif isinstance(response, dict) and "supplies" in response:
            raw_supplies = response["supplies"]

        # Validar datos con Pydantic
        from ...models.supply import SupplyData

        validated_supplies = []
        for supply_data in raw_supplies:
            try:
                validated_supply = SupplyData(**supply_data)
                validated_supplies.append(validated_supply)
            except Exception as e:
                # Log del error pero continúa procesando
                print(f"Error validando suministro: {e}")
                continue

        return validated_supplies

    def get_distributors(self) -> List["DistributorData"]:
        """
        Obtiene la lista de distribuidores disponibles validados con Pydantic.

        :return: Lista de distribuidores como objetos DistributorData validados.
        :rtype: List[DistributorData]
        """
        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["distributors"]
        )

        # Manejar diferentes formatos de respuesta
        raw_distributors = []
        if isinstance(response, list):
            raw_distributors = response
        elif isinstance(response, dict):
            if response:
                raw_distributors = [response]

        # Validar datos con Pydantic
        from ...models.distributor import DistributorData

        validated_distributors = []
        for distributor_data in raw_distributors:
            try:
                validated_distributor = DistributorData(**distributor_data)
                validated_distributors.append(validated_distributor)
            except Exception as e:
                # Log del error pero continúa procesando
                print(f"Error validando distribuidor: {e}")
                continue

        return validated_distributors

    def get_contract_detail(
        self, cups: str, distributor_code: str
    ) -> List["ContractData"]:
        """
        Obtiene el detalle del contrato para un CUPS específico validado con Pydantic.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).

        :return: Lista de datos del contrato como objetos ContractData validados.
        :rtype: List[ContractData]
        """
        params = {"cups": cups, "distributorCode": distributor_code}

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["contracts"], params=params
        )

        # Manejar diferentes estructuras de respuesta
        raw_contracts = []
        if isinstance(response, list):
            raw_contracts = response
        elif isinstance(response, dict):
            if response:
                raw_contracts = [response]

        # Validar datos con Pydantic
        from ...models.contract import ContractData

        validated_contracts = []
        for contract_data in raw_contracts:
            try:
                validated_contract = ContractData(**contract_data)
                validated_contracts.append(validated_contract)
            except Exception as e:
                # Log del error pero continúa procesando
                print(f"Error validando contrato: {e}")
                continue

        return validated_contracts

    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
    ) -> List["ConsumptionData"]:
        """
        Obtiene datos de consumo para un CUPS y rango de fechas validados con Pydantic.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).
        :param date_from: Fecha inicial (YYYY/MM).
        :param date_to: Fecha final (YYYY/MM).
        :param measurement_type: Tipo de medida (0=hora, 1=cuarto hora).
        :param point_type: Tipo de punto (1-5, opcional).

        :return: Lista de datos de consumo como objetos ConsumptionData validados.
        :rtype: List[ConsumptionData]
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
        raw_consumption = []
        if isinstance(response, list):
            raw_consumption = response
        elif isinstance(response, dict) and "timeCurve" in response:
            raw_consumption = response["timeCurve"]

        # Validar datos con Pydantic
        from ...models.consumption import ConsumptionData

        validated_consumption = []
        for consumption_data in raw_consumption:
            try:
                validated_consumption_item = ConsumptionData(**consumption_data)
                validated_consumption.append(validated_consumption_item)
            except Exception as e:
                # Log del error pero continúa procesando
                print(f"Error validando consumo: {e}")
                continue

        return validated_consumption

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List["MaxPowerData"]:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas validados con Pydantic.

        :param cups: Código CUPS del punto de suministro.
        :param distributor_code: Código del distribuidor (1-8).
        :param date_from: Fecha inicial (YYYY/MM).
        :param date_to: Fecha final (YYYY/MM).

        :return: Lista de datos de potencia máxima como objetos MaxPowerData validados.
        :rtype: List[MaxPowerData]
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
        raw_max_power = []
        if isinstance(response, list):
            raw_max_power = response
        elif isinstance(response, dict) and "maxPower" in response:
            raw_max_power = response["maxPower"]

        # Validar datos con Pydantic
        from ...models.max_power import MaxPowerData

        validated_max_power = []
        for max_power_data in raw_max_power:
            try:
                validated_max_power_item = MaxPowerData(**max_power_data)
                validated_max_power.append(validated_max_power_item)
            except Exception as e:
                # Log del error pero continúa procesando
                print(f"Error validando potencia máxima: {e}")
                continue

        return validated_max_power

    # Métodos de conveniencia para acceso rápido

    def get_cups_list(self) -> List[str]:
        """
        Obtiene solo la lista de códigos CUPS disponibles.

        :return: Lista de códigos CUPS.
        :rtype: List[str]
        """
        supplies = self.get_supplies()
        return [supply.cups for supply in supplies if supply.cups]

    def get_distributor_codes(self) -> List[str]:
        """
        Obtiene solo los códigos de distribuidores disponibles.

        :return: Lista de códigos de distribuidores.
        :rtype: List[str]
        """
        supplies = self.get_supplies()
        codes = set()
        for supply in supplies:
            if supply.distributor_code:
                codes.add(supply.distributor_code)
        return list(codes)
