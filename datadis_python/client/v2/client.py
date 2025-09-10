"""
Cliente Datadis API v2 - Respuestas tipadas con validación
"""

from typing import List, Optional

from ..base import BaseDatadisClient
from ...utils.constants import API_V2_ENDPOINTS
from ...utils.validators import (
    validate_cups, 
    validate_date_range, 
    validate_measurement_type,
    validate_point_type,
    validate_distributor_code
)
from ...models import (
    ConsumptionData, ContractData, SupplyData, MaxPowerData
)


class DatadisClientV2(BaseDatadisClient):
    """
    Cliente para API v2 de Datadis
    
    Características:
    - Respuestas tipadas con Pydantic models
    - Validación automática de parámetros
    - Endpoints modernos v2
    - Type hints completos para IDE
    """
    
    def get_supplies(self, distributor_code: Optional[str] = None) -> List[SupplyData]:
        """
        Obtiene la lista de puntos de suministro disponibles
        
        Args:
            distributor_code: Código del distribuidor (opcional)
            
        Returns:
            Lista de objetos SupplyData tipados
        """
        params = {}
        if distributor_code:
            params["distributorCode"] = validate_distributor_code(distributor_code)
            
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["supplies"], params=params)
        
        supplies = []
        if isinstance(response, dict) and "supplies" in response:
            for supply_data in response["supplies"]:
                supplies.append(SupplyData(**supply_data))
        elif isinstance(response, list):
            for supply_data in response:
                supplies.append(SupplyData(**supply_data))
        
        return supplies
    
    def get_distributors(self) -> List[str]:
        """
        Obtiene la lista de códigos de distribuidores disponibles
        
        Returns:
            Lista de códigos de distribuidoras
        """
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["distributors"])
        
        if isinstance(response, dict) and "distExistenceUser" in response:
            distributor_codes = response["distExistenceUser"].get("distributorCodes", [])
            return distributor_codes
        
        return []
    
    def get_contract_detail(
        self,
        cups: str,
        distributor_code: str
    ) -> Optional[ContractData]:
        """
        Obtiene el detalle del contrato para un CUPS específico
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            
        Returns:
            Objeto ContractData tipado o None si no se encuentra
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code
        }
        
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["contracts"], params=params)
        
        if isinstance(response, dict) and "contract" in response:
            contracts = response["contract"]
            if contracts:
                return ContractData(**contracts[0])
        
        return None
    
    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None
    ) -> List[ConsumptionData]:
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
            Lista de objetos ConsumptionData tipados
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
            "measurementType": str(measurement_type)
        }
        
        if point_type is not None:
            params["pointType"] = str(validate_point_type(point_type))
        
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["consumption"], params=params)
        
        consumptions = []
        if isinstance(response, dict) and "timeCurve" in response:
            for consumption_data in response["timeCurve"]:
                consumptions.append(ConsumptionData(**consumption_data))
        
        return consumptions
    
    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str
    ) -> List[MaxPowerData]:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            
        Returns:
            Lista de objetos MaxPowerData tipados
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to
        }
        
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["max_power"], params=params)
        
        max_powers = []
        if isinstance(response, dict) and "maxPower" in response:
            for power_data in response["maxPower"]:
                max_powers.append(MaxPowerData(**power_data))
        
        return max_powers
    
    def get_reactive_data(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str
    ) -> List[dict]:
        """
        Obtiene datos de energía reactiva (solo disponible en v2)
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            
        Returns:
            Lista de datos de energía reactiva
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to
        }
        
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["reactive_data"], params=params)
        
        # Devolver datos raw ya que no tenemos modelo específico aún
        if isinstance(response, dict) and "reactiveData" in response:
            return response["reactiveData"]
        elif isinstance(response, list):
            return response
        
        return []
    
    # Métodos de conveniencia con validación adicional
    
    def get_consumption_summary(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str
    ) -> dict:
        """
        Obtiene un resumen de consumo con estadísticas básicas
        
        Returns:
            Diccionario con total, promedio, min y max de consumo
        """
        consumption_data = self.get_consumption(cups, distributor_code, date_from, date_to)
        
        if not consumption_data:
            return {"total": 0, "average": 0, "min": 0, "max": 0, "count": 0}
        
        values = [float(item.obtainedMeasure or 0) for item in consumption_data]
        
        return {
            "total": sum(values),
            "average": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "count": len(values)
        }