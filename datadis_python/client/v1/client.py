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

    def get_supplies(
        self,
        authorized_nif: Optional[str] = None,
        distributor_code: Optional[str] = None,
    ) -> List["SupplyData"]:
        """
        Buscar todos los suministros.

        :param authorized_nif: NIF de la persona autorizada para buscar sus suministros
        :type authorized_nif: Optional[str]
        :param distributor_code: Código del distribuidor para filtrar suministros de una distribuidora específica
        :type distributor_code: Optional[str]
        :return: Lista de suministros como objetos SupplyData validados
        :rtype: List[SupplyData]
        """
        # Construir parámetros de query
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif
        if distributor_code is not None:
            params["distributorCode"] = distributor_code

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["supplies"], params=params
        )

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

    def get_distributors(
        self, authorized_nif: Optional[str] = None
    ) -> List["DistributorData"]:
        """
        Obtiene una lista de códigos de distribuidores en los que el usuario tiene suministros.

        :param authorized_nif: NIF autorizado para obtener distribuidoras del NIF autorizado
        :type authorized_nif: Optional[str]
        :return: Lista de distribuidores como objetos DistributorData validados
        :rtype: List[DistributorData]
        :note: Códigos de distribuidora: (1: Viesgo, 2: E-distribución, 3: E-redes, 4: ASEME, 5: UFD, 6: EOSA, 7:CIDE, 8: IDE)
        """
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self.make_authenticated_request(
            "GET", API_V1_ENDPOINTS["distributors"], params=params
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
        self, cups: str, distributor_code: str, authorized_nif: Optional[str] = None
    ) -> List["ContractData"]:
        """
        Buscar el detalle del contrato.

        :param cups: Código CUPS del punto de suministro para obtener detalles del contrato
        :type cups: str
        :param distributor_code: Código del distribuidor obtenido de la solicitud de suministros
        :type distributor_code: str
        :param authorized_nif: NIF autorizado para obtener el detalle del contrato del NIF autorizado
        :type authorized_nif: Optional[str]
        :return: Lista de datos del contrato como objetos ContractData validados
        :rtype: List[ContractData]
        """
        params = {"cups": cups, "distributorCode": distributor_code}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
        authorized_nif: Optional[str] = None,
    ) -> List["ConsumptionData"]:
        """
        Buscar los datos de consumo.

        :param cups: Código CUPS del punto de suministro para obtener datos de consumo
        :type cups: str
        :param distributor_code: Código del distribuidor obtenido de la solicitud de suministros
        :type distributor_code: str
        :param date_from: Fecha de inicio en formato AAAA/MM (ejemplo: 2020/02)
        :type date_from: str
        :param date_to: Fecha de finalización en formato AAAA/MM (ejemplo: 2020/02)
        :type date_to: str
        :param measurement_type: Tipo de medida: 0 para consumo horario, 1 para consumo por cuarto de hora
        :type measurement_type: int
        :param point_type: Código de tipo de punto obtenido de la solicitud de suministros
        :type point_type: Optional[int]
        :param authorized_nif: NIF autorizado para obtener datos de consumo del NIF autorizado
        :type authorized_nif: Optional[str]
        :return: Lista de datos de consumo como objetos ConsumptionData validados
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
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> List["MaxPowerData"]:
        """
        Busca la potencia máxima y devuelve el resultado en kW.

        :param cups: Código CUPS del punto de suministro para obtener potencia máxima
        :type cups: str
        :param distributor_code: Código del distribuidor obtenido de la solicitud de suministros
        :type distributor_code: str
        :param date_from: Fecha de inicio en formato AAAA/MM (ejemplo: 2020/02)
        :type date_from: str
        :param date_to: Fecha de finalización en formato AAAA/MM (ejemplo: 2020/02)
        :type date_to: str
        :param authorized_nif: NIF autorizado para obtener potencia máxima del NIF autorizado
        :type authorized_nif: Optional[str]
        :return: Lista de datos de potencia máxima como objetos MaxPowerData validados
        :rtype: List[MaxPowerData]
        """
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
