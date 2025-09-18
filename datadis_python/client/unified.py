"""
Cliente unificado que expone ambas versiones de la API de Datadis.

Este módulo proporciona un cliente que permite interactuar con ambas versiones de la API de Datadis.
"""

from typing import TYPE_CHECKING, List, Optional

from ..utils.constants import DEFAULT_TIMEOUT, MAX_RETRIES
from .v1.client import DatadisClientV1
from .v2.client import DatadisClientV2

if TYPE_CHECKING:
    from ..models.reactive import ReactiveData
    from ..models.responses import (
        ConsumptionResponse,
        ContractResponse,
        DistributorsResponse,
        MaxPowerResponse,
        SuppliesResponse,
    )


class DatadisClient:
    """
    Cliente unificado que permite acceso a ambas versiones de la API.

    :param username: NIF del usuario registrado en Datadis.
    :type username: str
    :param password: Contraseña de acceso a Datadis.
    :type password: str
    :param timeout: Timeout para requests en segundos.
    :type timeout: int
    :param retries: Número de reintentos automáticos.
    :type retries: int
    """

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = MAX_RETRIES,
    ):
        """
        Inicializa el cliente unificado.

        :param username: NIF del usuario registrado en Datadis.
        :param password: Contraseña de acceso a Datadis.
        :param timeout: Timeout para requests en segundos.
        :param retries: Número de reintentos automáticos.
        """
        self._username = username
        self._password = password
        self._timeout = timeout
        self._retries = retries

        # Inicialización lazy de los clientes
        self._v1_client = None
        self._v2_client = None

    @property
    def v1(self) -> DatadisClientV1:
        """
        Acceso al cliente API v1 (respuestas raw)

        Returns:
            Cliente v1 inicializado
        """
        if self._v1_client is None:
            self._v1_client = DatadisClientV1(
                self._username, self._password, self._timeout, self._retries
            )
        return self._v1_client

    @property
    def v2(self) -> DatadisClientV2:
        """
        Acceso al cliente API v2 (respuestas tipadas)

        Returns:
            Cliente v2 inicializado
        """
        if self._v2_client is None:
            self._v2_client = DatadisClientV2(
                self._username, self._password, self._timeout, self._retries
            )
        return self._v2_client

    # Métodos de conveniencia que delegan a v2 por defecto

    def get_supplies(
        self, distributor_code: Optional[str] = None
    ) -> "SuppliesResponse":
        """
        Obtiene puntos de suministro (usa API v2)

        Para usar v1: client.v1.get_supplies()
        """
        return self.v2.get_supplies(distributor_code)

    def get_distributors(self) -> "DistributorsResponse":
        """
        Obtiene distribuidores (usa API v2)

        Para usar v1: client.v1.get_distributors()
        """
        return self.v2.get_distributors()

    def get_contract_detail(
        self, cups: str, distributor_code: str
    ) -> "ContractResponse":
        """
        Obtiene detalle del contrato (usa API v2)

        Para usar v1: client.v1.get_contract_detail(cups, distributor_code)
        """
        return self.v2.get_contract_detail(cups, distributor_code)

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
        Obtiene datos de consumo (usa API v2)

        Para usar v1: client.v1.get_consumption(...)
        """
        return self.v2.get_consumption(
            cups, distributor_code, date_from, date_to, measurement_type, point_type
        )

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> "MaxPowerResponse":
        """
        Obtiene datos de potencia máxima (usa API v2)

        Para usar v1: client.v1.get_max_power(...)
        """
        return self.v2.get_max_power(cups, distributor_code, date_from, date_to)

    # Métodos únicos de v2

    def get_reactive_data(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List["ReactiveData"]:
        """
        Obtiene datos de energía reactiva (solo disponible en v2)
        """
        return self.v2.get_reactive_data(cups, distributor_code, date_from, date_to)

    # Métodos únicos de v1

    def get_cups_list(self) -> List[str]:
        """
        Obtiene solo códigos CUPS (método de conveniencia de v1)
        """
        return self.v1.get_cups_list()

    def get_distributor_codes(self) -> List[str]:
        """
        Obtiene solo códigos de distribuidores (método de conveniencia de v1)
        """
        return self.v1.get_distributor_codes()

    # Gestión de recursos

    def close(self) -> None:
        """
        Cierra ambos clientes y libera recursos
        """
        if self._v1_client:
            self._v1_client.close()
        if self._v2_client:
            self._v2_client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    # Información del cliente

    def get_client_info(self) -> dict:
        """
        Obtiene información sobre el estado de los clientes

        Returns:
            Diccionario con información de estado
        """
        return {
            "v1_initialized": self._v1_client is not None,
            "v2_initialized": self._v2_client is not None,
            "v1_authenticated": self._v1_client.token is not None
            if self._v1_client
            else False,
            "v2_authenticated": self._v2_client.token is not None
            if self._v2_client
            else False,
            "timeout": self._timeout,
            "retries": self._retries,
        }
