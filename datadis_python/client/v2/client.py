"""
Cliente Datadis API v2 - Devuelve datos raw exactamente como los proporciona la API
"""

from typing import TYPE_CHECKING, List, Optional

from ...utils.constants import API_V2_ENDPOINTS
from ...utils.validators import (
    validate_cups,
    validate_date_range,
    validate_distributor_code,
    validate_measurement_type,
    validate_point_type,
)
from ..base import BaseDatadisClient

if TYPE_CHECKING:
    from ...models.consumption import ConsumptionData
    from ...models.contract import ContractData
    from ...models.distributor import DistributorData
    from ...models.max_power import MaxPowerData
    from ...models.reactive import ReactiveData
    from ...models.responses import (
        ConsumptionResponse,
        ContractResponse,
        DistributorsResponse,
        MaxPowerResponse,
        SuppliesResponse,
    )
    from ...models.supply import SupplyData


class DatadisClientV2(BaseDatadisClient):
    """
    Cliente para API v2 de Datadis

    Características:
    - Devuelve datos raw exactamente como los proporciona la API
    - Endpoints v2 con estructura de respuesta actualizada
    - Validación de parámetros de entrada
    - Manejo de errores de distribuidor en formato v2
    """

    def get_supplies(
        self, distributor_code: Optional[str] = None
    ) -> "SuppliesResponse":
        """
        Obtiene la lista de puntos de suministro disponibles validados con Pydantic

        Args:
            distributor_code: Código del distribuidor (opcional)

        Returns:
            SuppliesResponse con suministros validados y errores de distribuidora
        """
        params = {}
        if distributor_code:
            params["distributorCode"] = validate_distributor_code(distributor_code)

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["supplies"], params=params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"supplies": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import SuppliesResponse

        try:
            validated_response = SuppliesResponse(**response)
            return validated_response
        except Exception as e:
            print(f"⚠️ Error validando respuesta de suministros: {e}")
            # Devolver respuesta vacía pero válida
            return SuppliesResponse(supplies=[], distributorError=[])

    def get_distributors(self) -> "DistributorsResponse":
        """
        Obtiene la lista de códigos de distribuidores disponibles validados con Pydantic

        Returns:
            DistributorsResponse con códigos de distribuidores validados y errores
        """
        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["distributors"]
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {
                "distExistenceUser": {"distributorCodes": []},
                "distributorError": [],
            }

        # Validar respuesta completa con Pydantic
        from ...models.responses import DistributorsResponse

        try:
            validated_response = DistributorsResponse(**response)
            return validated_response
        except Exception as e:
            print(f"⚠️ Error validando respuesta de distribuidores: {e}")
            # Devolver respuesta vacía pero válida
            return DistributorsResponse(
                distExistenceUser={"distributorCodes": []}, distributorError=[]
            )

    def get_contract_detail(
        self, cups: str, distributor_code: str
    ) -> "ContractResponse":
        """
        Obtiene el detalle del contrato para un CUPS específico validado con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor

        Returns:
            ContractResponse con datos de contrato validados y errores de distribuidora
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)

        params = {"cups": cups, "distributorCode": distributor_code}

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["contracts"], params=params
        )

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"contract": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import ContractResponse

        try:
            validated_response = ContractResponse(**response)
            return validated_response
        except Exception as e:
            print(f"⚠️ Error validando respuesta de contrato: {e}")
            # Devolver respuesta vacía pero válida
            return ContractResponse(contract=[], distributorError=[])

    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None,
    ) -> "ConsumptionResponse":
        """
        Obtiene datos de consumo para un CUPS y rango de fechas validados con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            measurement_type: Tipo de medida (0=hora, 1=cuarto hora)
            point_type: Tipo de punto (obtenido de supplies)

        Returns:
            ConsumptionResponse con datos de consumo validados y errores de distribuidora
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

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"timeCurve": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import ConsumptionResponse

        try:
            validated_response = ConsumptionResponse(**response)
            return validated_response
        except Exception as e:
            print(f"⚠️ Error validando respuesta de consumo: {e}")
            # Devolver respuesta vacía pero válida
            return ConsumptionResponse(timeCurve=[], distributorError=[])

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> "MaxPowerResponse":
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas validados con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)

        Returns:
            MaxPowerResponse con datos de potencia máxima validados y errores de distribuidora
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

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"maxPower": [], "distributorError": []}

        # Validar respuesta completa con Pydantic
        from ...models.responses import MaxPowerResponse

        try:
            validated_response = MaxPowerResponse(**response)
            return validated_response
        except Exception as e:
            print(f"⚠️ Error validando respuesta de potencia máxima: {e}")
            # Devolver respuesta vacía pero válida
            return MaxPowerResponse(maxPower=[], distributorError=[])

    def get_reactive_data(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List["ReactiveData"]:
        """
        Obtiene datos de energía reactiva validados con Pydantic (solo disponible en v2)

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)

        Returns:
            Lista de objetos ReactiveData validados
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

        # Asegurar estructura de respuesta válida
        if not isinstance(response, dict):
            response = {"reactiveEnergy": {}, "distributorError": []}

        # Manejar estructura de respuesta para energía reactiva
        raw_reactive_data = []
        if "reactiveEnergy" in response and response["reactiveEnergy"]:
            raw_reactive_data = [response]  # Envolver en lista para consistencia

        # Validar datos con Pydantic
        from ...models.reactive import ReactiveData

        validated_reactive_data = []
        for reactive_data in raw_reactive_data:
            try:
                validated_reactive_item = ReactiveData(**reactive_data)
                validated_reactive_data.append(validated_reactive_item)
            except Exception as e:
                print(f"⚠️ Error validando datos de energía reactiva: {e}")
                continue

        return validated_reactive_data
