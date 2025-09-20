"""
Modelos de respuesta de la API de Datadis (versiones v2).

Este módulo define los modelos de respuesta para las diferentes versiones de la API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DistributorError(BaseModel):
    """
    Error de distribuidor en respuestas de API v2.

    :param distributor_code: Código de distribuidora
    :type distributor_code: str
    :param distributor_name: Nombre de la distribuidora
    :type distributor_name: str
    :param error_code: Código de error
    :type error_code: str
    :param error_description: Descripción del error
    :type error_description: str
    """

    distributor_code: str = Field(
        alias="distributorCode", description="Código de distribuidora"
    )
    distributor_name: str = Field(
        alias="distributorName", description="Nombre de la distribuidora"
    )
    error_code: str = Field(alias="errorCode", description="Código de error")
    error_description: str = Field(
        alias="errorDescription", description="Descripción del error"
    )

    model_config = ConfigDict(populate_by_name=True)


class SuppliesResponse(BaseModel):
    """
    Respuesta de get-supplies-v2.

    :param supplies: Lista de datos de suministros
    :type supplies: List[SupplyData]
    :param distributor_error: Lista de errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    supplies: List["SupplyData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class ContractResponse(BaseModel):
    """
    Respuesta de get-contract-detail-v2.

    :param contract: Lista de datos de contratos
    :type contract: List[ContractData]
    :param distributor_error: Lista de errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    contract: List["ContractData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class ConsumptionResponse(BaseModel):
    """
    Respuesta de get-consumption-data-v2.

    :param time_curve: Lista de datos de consumo por tiempo
    :type time_curve: List[ConsumptionData]
    :param distributor_error: Lista de errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    time_curve: List["ConsumptionData"] = Field(default_factory=list, alias="timeCurve")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class MaxPowerResponse(BaseModel):
    """
    Respuesta de get-max-power-v2.

    :param max_power: Lista de datos de potencia máxima
    :type max_power: List[MaxPowerData]
    :param distributor_error: Lista de errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    max_power: List["MaxPowerData"] = Field(default_factory=list, alias="maxPower")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class DistributorsResponse(BaseModel):
    """
    Respuesta de get-distributors-with-supplies-v2.

    :param dist_existence_user: Datos de existencia de usuario por distribuidor
    :type dist_existence_user: dict
    :param distributor_error: Lista de errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    dist_existence_user: dict = Field(alias="distExistenceUser")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


from .consumption import ConsumptionData
from .contract import ContractData
from .max_power import MaxPowerData

# Importar modelos específicos para evitar imports circulares
from .supply import SupplyData
