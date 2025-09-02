"""
Modelos de respuesta de la API de Datadis (versiones v2)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DistributorError(BaseModel):
    """Error de distribuidor en respuestas de API v2"""
    
    distributor_code: str = Field(alias="distributorCode", description="Código de distribuidora")
    distributor_name: str = Field(alias="distributorName", description="Nombre de la distribuidora") 
    error_code: str = Field(alias="errorCode", description="Código de error")
    error_description: str = Field(alias="errorDescription", description="Descripción del error")

    class Config:
        allow_population_by_field_name = True


class SuppliesResponse(BaseModel):
    """Respuesta de get-supplies-v2"""
    
    supplies: List["SupplyData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    class Config:
        allow_population_by_field_name = True


class ContractResponse(BaseModel):
    """Respuesta de get-contract-detail-v2"""
    
    contract: List["ContractData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    class Config:
        allow_population_by_field_name = True


class ConsumptionResponse(BaseModel):
    """Respuesta de get-consumption-data-v2"""
    
    time_curve: List["ConsumptionData"] = Field(
        default_factory=list, alias="timeCurve"
    )
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    class Config:
        allow_population_by_field_name = True


class MaxPowerResponse(BaseModel):
    """Respuesta de get-max-power-v2"""
    
    max_power: List["MaxPowerData"] = Field(
        default_factory=list, alias="maxPower"
    )
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    class Config:
        allow_population_by_field_name = True


class DistributorsResponse(BaseModel):
    """Respuesta de get-distributors-with-supplies-v2"""
    
    dist_existence_user: dict = Field(alias="distExistenceUser")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    class Config:
        allow_population_by_field_name = True


# Importar modelos específicos para evitar imports circulares
from .supply import SupplyData
from .contract import ContractData  
from .consumption import ConsumptionData
from .max_power import MaxPowerData