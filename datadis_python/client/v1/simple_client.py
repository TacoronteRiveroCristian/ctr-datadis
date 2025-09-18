"""
Cliente V1 simplificado y robusto para Datadis
"""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests

if TYPE_CHECKING:
    from ...models.consumption import ConsumptionData
    from ...models.contract import ContractData
    from ...models.distributor import DistributorData
    from ...models.max_power import MaxPowerData
    from ...models.supply import SupplyData

from ...exceptions import APIError, AuthenticationError, DatadisError
from ...utils.constants import (
    API_V1_ENDPOINTS,
    AUTH_ENDPOINTS,
    DATADIS_API_BASE,
    DATADIS_BASE_URL,
)
from ...utils.text_utils import normalize_api_response


class SimpleDatadisClientV1:
    """
    Cliente V1 simplificado que maneja mejor los timeouts de Datadis
    """

    def __init__(
        self, username: str, password: str, timeout: int = 120, retries: int = 3
    ):
        """
        Inicializa el cliente simplificado

        Args:
            username: NIF del usuario
            password: Contraseña
            timeout: Timeout en segundos (120s por defecto para Datadis)
            retries: Número de reintentos
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.token = None
        self.session = requests.Session()

        # Headers básicos (desactivar compresión para evitar problemas de gzip)
        self.session.headers.update(
            {
                "User-Agent": "datadis-python-sdk/0.2.0",
                "Accept": "application/json",
                "Accept-Encoding": "identity",  # Desactivar compresión gzip
            }
        )

    def authenticate(self) -> bool:
        """
        Autentica con la API de Datadis

        Returns:
            True si la autenticación fue exitosa
        """
        print("🔐 Autenticando con Datadis...")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "datadis-python-sdk/0.2.0",
        }

        data = {"username": self.username, "password": self.password}

        try:
            response = requests.post(
                url=f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                data=data,
                headers=headers,
                timeout=30,  # Auth timeout más corto
            )

            if response.status_code == 200:
                self.token = response.text.strip()
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Autenticación exitosa")
                return True
            else:
                raise AuthenticationError(
                    f"Error de autenticación: {response.status_code}"
                )

        except requests.Timeout:
            raise AuthenticationError("Timeout en autenticación")
        except Exception as e:
            raise AuthenticationError(f"Error en autenticación: {e}")

    def _make_authenticated_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Any:
        """
        Realiza una petición autenticada con manejo robusto de timeouts

        Args:
            endpoint: Endpoint de la API (ej: '/get-supplies')
            params: Parámetros de query

        Returns:
            Respuesta de la API
        """
        if not self.token:
            if not self.authenticate():
                raise AuthenticationError("No se pudo autenticar")

        url = f"{DATADIS_API_BASE}{endpoint}"

        for attempt in range(self.retries + 1):
            try:
                print(
                    f"📡 Petición a {endpoint} (intento {attempt + 1}/{self.retries + 1})..."
                )

                response = self.session.get(
                    url=url, params=params, timeout=self.timeout
                )

                if response.status_code == 200:
                    print(f"✅ Respuesta exitosa ({len(response.text)} chars)")
                    json_response = response.json()
                    # Normalizar texto para evitar problemas de caracteres especiales
                    return normalize_api_response(json_response)
                elif response.status_code == 401:
                    # Token expirado, renovar
                    print("🔄 Token expirado, renovando...")
                    self.token = None
                    if self.authenticate():
                        continue
                    else:
                        raise AuthenticationError("No se pudo renovar el token")
                else:
                    raise APIError(
                        f"Error HTTP {response.status_code}: {response.text}",
                        response.status_code,
                    )

            except requests.Timeout:
                if attempt < self.retries:
                    wait_time = min(30, (2**attempt) * 5)
                    print(
                        f"⏰ Timeout. Esperando {wait_time}s antes del siguiente intento..."
                    )
                    time.sleep(wait_time)
                else:
                    raise DatadisError(
                        f"Timeout después de {self.retries + 1} intentos. La API de Datadis puede estar lenta."
                    )
            except Exception as e:
                if attempt < self.retries:
                    wait_time = (2**attempt) * 2
                    print(f"❌ Error: {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise DatadisError(
                        f"Error después de {self.retries + 1} intentos: {e}"
                    )

        raise DatadisError("Se agotaron todos los reintentos")

    def get_supplies(self) -> List["SupplyData"]:
        """
        Obtiene la lista de puntos de suministro validados con Pydantic

        Returns:
            Lista de suministros como objetos SupplyData validados
        """
        print("🏠 Obteniendo lista de suministros...")
        response = self._make_authenticated_request(API_V1_ENDPOINTS["supplies"])

        raw_supplies = []
        if isinstance(response, list):
            raw_supplies = response
        elif isinstance(response, dict) and "supplies" in response:
            raw_supplies = response["supplies"]
        else:
            print("⚠️ Respuesta inesperada de la API")
            return []

        # Validar datos con Pydantic
        from ...models.supply import SupplyData

        validated_supplies = []
        for supply_data in raw_supplies:
            try:
                validated_supply = SupplyData(**supply_data)
                validated_supplies.append(validated_supply)
            except Exception as e:
                print(f"⚠️ Error validando suministro: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"✅ {len(validated_supplies)} suministros validados")
        return validated_supplies

    def get_distributors(self) -> List["DistributorData"]:
        """
        Obtiene distribuidores validados con Pydantic

        Returns:
            Lista de distribuidores como objetos DistributorData validados
        """
        print("🔌 Obteniendo distribuidores...")
        response = self._make_authenticated_request(API_V1_ENDPOINTS["distributors"])

        # Manejar diferentes estructuras de respuesta
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
                print(f"⚠️ Error validando distribuidor: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"✅ {len(validated_distributors)} distribuidores validados")
        return validated_distributors

    def get_contract_detail(
        self, cups: str, distributor_code: str
    ) -> List["ContractData"]:
        """
        Obtiene detalle del contrato validado con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código de la distribuidora

        Returns:
            Lista de contratos como objetos ContractData validados
        """
        print(f"📋 Obteniendo contrato para {cups}...")
        params = {"cups": cups, "distributorCode": distributor_code}
        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["contracts"], params
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
                print(f"⚠️ Error validando contrato: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"✅ {len(validated_contracts)} contratos validados")
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
        Obtiene datos de consumo validados con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código de la distribuidora
            date_from: Fecha de inicio (YYYY/MM/DD)
            date_to: Fecha de fin (YYYY/MM/DD)
            measurement_type: Tipo de medición (default: 0)
            point_type: Tipo de punto de medida (opcional)

        Returns:
            Lista de datos de consumo como objetos ConsumptionData validados
        """
        print(f"⚡ Obteniendo consumo para {cups} ({date_from} - {date_to})...")
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type),
        }

        if point_type is not None:
            params["pointType"] = str(point_type)

        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["consumption"], params
        )

        # Manejar diferentes estructuras de respuesta
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
                print(f"⚠️ Error validando consumo: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"✅ {len(validated_consumption)} registros de consumo validados")
        return validated_consumption

    def get_max_power(
        self, cups: str, distributor_code: str, date_from: str, date_to: str
    ) -> List["MaxPowerData"]:
        """
        Obtiene datos de potencia máxima validados con Pydantic

        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código de la distribuidora
            date_from: Fecha de inicio (YYYY/MM/DD)
            date_to: Fecha de fin (YYYY/MM/DD)

        Returns:
            Lista de datos de potencia máxima como objetos MaxPowerData validados
        """
        print(f"🔋 Obteniendo potencia máxima para {cups} ({date_from} - {date_to})...")
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
        }

        response = self._make_authenticated_request(
            API_V1_ENDPOINTS["max_power"], params
        )

        # Manejar diferentes estructuras de respuesta
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
                print(f"⚠️ Error validando potencia máxima: {e}")
                # Continúa con el siguiente sin fallar completamente
                continue

        print(f"✅ {len(validated_max_power)} registros de potencia máxima validados")
        return validated_max_power

    def close(self):
        """Cierra la sesión"""
        if self.session:
            self.session.close()
        self.token = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
