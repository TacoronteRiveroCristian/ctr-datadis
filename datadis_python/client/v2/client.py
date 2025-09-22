"""
Cliente Datadis API v2 - Devuelve datos raw exactamente como los proporciona la API.

Este módulo proporciona un cliente para la versión 2 de la API de Datadis.
"""

from typing import TYPE_CHECKING, List, Optional

from ...utils.constants import API_V2_ENDPOINTS
from ...utils.validators import (
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
    Cliente para API v2 de Datadis.

    Características:
    - Devuelve datos raw exactamente como los proporciona la API
    - Endpoints v2 con estructura de respuesta actualizada
    - Validación de parámetros de entrada
    - Manejo de errores de distribuidor en formato v2

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
    ) -> "SuppliesResponse":
        """
        Buscar todos los suministros.

        :param authorized_nif: Si queremos buscar suministros de personas que hemos autorizado, podemos buscarlo con el NIF de las personas autorizadas.
        :type authorized_nif: Optional[str]
        :param distributor_code: Código del distribuidor, que se obtiene con la solicitud de distribuidoras con suministros: /get-distributors-with-supplies. Para consultar los suministros de una sola distribuidora.
        :type distributor_code: Optional[str]
        :return: Respuesta con suministros validados y errores de distribuidora en formato v2.
        :rtype: SuppliesResponse
        """
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif
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
            print(f"Error validando respuesta de suministros: {e}")
            # Devolver respuesta vacía pero válida
            return SuppliesResponse(supplies=[], distributorError=[])

    def get_distributors(
        self, authorized_nif: Optional[str] = None
    ) -> "DistributorsResponse":
        """
        Obtiene una lista de códigos de distribuidores en los que el usuario tiene suministros.

        :param authorized_nif: Únicamente en caso de querer obtener el listado de códigos de distribuidoras que disponen de suministros del NIF autorizado.
        :type authorized_nif: Optional[str]
        :return: Respuesta con códigos de distribuidores validados y errores en formato v2.
        :rtype: DistributorsResponse
        :note: Códigos de distribuidora: (1: Viesgo, 2: E-distribución, 3: E-redes, 4: ASEME, 5: UFD, 6: EOSA, 7:CIDE, 8: IDE)
        """
        params = {}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

        response = self.make_authenticated_request(
            "GET", API_V2_ENDPOINTS["distributors"], params=params
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
            print(f"Error validando respuesta de distribuidores: {e}")
            # Devolver respuesta vacía pero válida
            return DistributorsResponse(
                distExistenceUser={"distributorCodes": []}, distributorError=[]
            )

    def get_contract_detail(
        self, cups: str, distributor_code: str, authorized_nif: Optional[str] = None
    ) -> "ContractResponse":
        """
        Buscar el detalle del contrato.

        :param cups: Los CUPS de los que querremos saber los detalles del contrato. Solo puede buscar un CUPS por pedido.
        :type cups: str
        :param distributor_code: Código del distribuidor, que se obtiene con la solicitud de obtención de suministros.
        :type distributor_code: str
        :param authorized_nif: Solo en el caso de que quieras obtener el detalle del contrato del NIF autorizado.
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de contrato validados y errores de distribuidora en formato v2.
        :rtype: ContractResponse
        """
        cups = cups.upper().strip()
        distributor_code = validate_distributor_code(distributor_code)

        params = {"cups": cups, "distributorCode": distributor_code}
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
            print(f"Error validando respuesta de contrato: {e}")
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
        authorized_nif: Optional[str] = None,
    ) -> "ConsumptionResponse":
        """
        Buscar los datos de consumo.

        :param cups: Los CUPS de los que querremos saber los datos de consumo.
        :type cups: str
        :param distributor_code: Código del distribuidor, que se obtiene con la solicitud de obtención de suministros.
        :type distributor_code: str
        :param date_from: Fecha de inicio entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_from: str
        :param date_to: Fecha de finalización entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_to: str
        :param measurement_type: Establézcalo en 0 (Cero) si desea obtener el consumo por hora y en 1 (Uno) si desea obtener el consumo por cuarto de hora. La consulta cuarta horaria solo está disponible para los PointType 1 y 2, y en el caso de la distribuidora E-distribución adicionalmente el PointType 3.
        :type measurement_type: int
        :param point_type: Código de tipo de punto, que se obtiene con la solicitud de obtención de suministros.
        :type point_type: Optional[int]
        :param authorized_nif: Solo en caso que se quiera obtener los datos de consumo de un NIF autorizado.
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de consumo validados y errores de distribuidora en formato v2.
        :rtype: ConsumptionResponse
        """
        cups = cups.upper().strip()
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
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
            print(f"Error validando respuesta de consumo: {e}")
            # Devolver respuesta vacía pero válida
            return ConsumptionResponse(timeCurve=[], distributorError=[])

    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> "MaxPowerResponse":
        """
        Busca la potencia máxima y te aparecerá el resultado en kW.

        :param cups: Las CUPS de las que querremos conocer los detalles del contrato.
        :type cups: str
        :param distributor_code: Código del distribuidor, que se obtiene con la solicitud de obtención de suministros.
        :type distributor_code: str
        :param date_from: Fecha de inicio entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_from: str
        :param date_to: Fecha de finalización entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_to: str
        :param authorized_nif: Solo en el caso de que quieras obtener el detalle del contrato del NIF autorizado.
        :type authorized_nif: Optional[str]
        :return: Respuesta con datos de potencia máxima validados y errores de distribuidora en formato v2.
        :rtype: MaxPowerResponse
        """
        cups = cups.upper().strip()
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
            print(f"Error validando respuesta de potencia máxima: {e}")
            # Devolver respuesta vacía pero válida
            return MaxPowerResponse(maxPower=[], distributorError=[])

    def get_reactive_data(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        authorized_nif: Optional[str] = None,
    ) -> List["ReactiveData"]:
        """
        Buscar datos de energía reactiva (solo disponible en v2).

        :param cups: Los CUPS de los que querremos saber los datos de consumo.
        :type cups: str
        :param distributor_code: Código del distribuidor, que se obtiene con la solicitud de obtención de suministros.
        :type distributor_code: str
        :param date_from: Fecha de inicio entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_from: str
        :param date_to: Fecha de finalización entre los datos de búsqueda. Formato: AAAA/MM. Ejemplo = 2020/02.
        :type date_to: str
        :param authorized_nif: Solo en caso que se quiera obtener los datos de consumo de un NIF autorizado.
        :type authorized_nif: Optional[str]
        :return: Lista de objetos ReactiveData validados.
        :rtype: List[ReactiveData]
        """
        cups = cups.upper().strip()
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")

        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }
        if authorized_nif is not None:
            params["authorizedNif"] = authorized_nif

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
                print(f"Error validando datos de energía reactiva: {e}")
                continue

        return validated_reactive_data
