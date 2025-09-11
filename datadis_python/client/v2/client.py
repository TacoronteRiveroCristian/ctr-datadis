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
from ...models.contract import (
    ContractResponse, ConsumptionResponse, SuppliesResponse, 
    MaxPowerResponse, DistributorsResponse
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
    
    def get_supplies(self, distributor_code: Optional[str] = None) -> SuppliesResponse:
        """
        Obtiene la lista de puntos de suministro disponibles
        
        Args:
            distributor_code: Código del distribuidor (opcional)
            
        Returns:
            SuppliesResponse con supplies y errores de distribuidor (datos raw)
        """
        params = {}
        if distributor_code:
            params["distributorCode"] = validate_distributor_code(distributor_code)
            
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["supplies"], params=params)
        
        supplies = []
        distributor_errors = []
        
        if isinstance(response, dict):
            # Procesar supplies
            if "supplies" in response:
                supply_list = response["supplies"]
                if isinstance(supply_list, list):
                    supplies = supply_list  # Raw data sin validación
            
            # Procesar errores de distribuidor
            if "distributorError" in response:
                error_list = response["distributorError"]
                if isinstance(error_list, list):
                    distributor_errors = error_list  # Raw data sin validación
        
        return SuppliesResponse(
            supplies=supplies,
            distributor_errors=distributor_errors
        )
    
    def get_distributors(self) -> DistributorsResponse:
        """
        Obtiene la lista de códigos de distribuidores disponibles
        
        Returns:
            DistributorsResponse con códigos y errores de distribuidor (datos raw)
        """
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["distributors"])
        
        distributor_codes = []
        distributor_errors = []
        
        if isinstance(response, dict):
            # Procesar códigos de distribuidores
            if "distExistenceUser" in response:
                dist_data = response["distExistenceUser"]
                if isinstance(dist_data, dict) and "distributorCodes" in dist_data:
                    codes = dist_data["distributorCodes"]
                    if isinstance(codes, list):
                        distributor_codes = codes
            
            # Procesar errores de distribuidor
            if "distributorError" in response:
                error_list = response["distributorError"]
                if isinstance(error_list, list):
                    distributor_errors = error_list  # Raw data sin validación
        
        return DistributorsResponse(
            distributor_codes=distributor_codes,
            distributor_errors=distributor_errors
        )
    
    def get_contract_detail(
        self,
        cups: str,
        distributor_code: str
    ) -> ContractResponse:
        """
        Obtiene el detalle del contrato para un CUPS específico
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            
        Returns:
            ContractResponse con contratos y errores de distribuidor (datos raw)
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code
        }
        
        response = self.make_authenticated_request("GET", API_V2_ENDPOINTS["contracts"], params=params)
        
        contracts = []
        distributor_errors = []
        
        if isinstance(response, dict):
            # Procesar contratos
            if "contract" in response:
                contract_list = response["contract"]
                if isinstance(contract_list, list):
                    contracts = contract_list  # Raw data sin validación
                elif isinstance(contract_list, dict) and contract_list:
                    contracts = [contract_list]  # Envolver dict en lista
            
            # Procesar errores de distribuidor
            if "distributorError" in response:
                error_list = response["distributorError"]
                if isinstance(error_list, list):
                    distributor_errors = error_list  # Raw data sin validación
        
        return ContractResponse(
            contracts=contracts,
            distributor_errors=distributor_errors
        )
    
    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None
    ) -> ConsumptionResponse:
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
            ConsumptionResponse con datos de consumo y errores de distribuidor (datos raw)
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
        
        consumption_data = []
        distributor_errors = []
        
        if isinstance(response, dict):
            # Procesar datos de consumo
            if "timeCurve" in response:
                time_curve = response["timeCurve"]
                if isinstance(time_curve, list):
                    consumption_data = time_curve  # Raw data sin validación
            
            # Procesar errores de distribuidor
            if "distributorError" in response:
                error_list = response["distributorError"]
                if isinstance(error_list, list):
                    distributor_errors = error_list  # Raw data sin validación
        
        return ConsumptionResponse(
            consumption_data=consumption_data,
            distributor_errors=distributor_errors
        )
    
    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str
    ) -> MaxPowerResponse:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            
        Returns:
            MaxPowerResponse con datos de potencia máxima y errores de distribuidor (datos raw)
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
        
        max_power_data = []
        distributor_errors = []
        
        if isinstance(response, dict):
            # Procesar datos de potencia máxima
            if "maxPower" in response:
                max_power = response["maxPower"]
                if isinstance(max_power, list):
                    max_power_data = max_power  # Raw data sin validación
            
            # Procesar errores de distribuidor
            if "distributorError" in response:
                error_list = response["distributorError"]
                if isinstance(error_list, list):
                    distributor_errors = error_list  # Raw data sin validación
        
        return MaxPowerResponse(
            max_power_data=max_power_data,
            distributor_errors=distributor_errors
        )
    
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