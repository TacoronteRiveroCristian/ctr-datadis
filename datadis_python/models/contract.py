"""
Modelos de datos para contratos
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DateOwner(BaseModel):
    """Periodo de propiedad"""

    start_date: str = Field(alias="startDate", description="Fecha de inicio propiedad")
    end_date: str = Field(alias="endDate", description="Fecha de fin propiedad")

    model_config = ConfigDict(populate_by_name=True)


class ContractData(BaseModel):
    """Modelo para datos de contrato (versión completa API v2)"""

    cups: str = Field(description="Código CUPS del punto de suministro")
    distributor: str = Field(description="Nombre de la distribuidora")
    marketer: Optional[str] = Field(
        default=None, description="Comercializadora (solo si es propietario del CUPS)"
    )
    tension: str = Field(description="Tensión")
    access_fare: str = Field(
        alias="accessFare", description="Descripción tarifa de acceso"
    )
    province: str = Field(description="Provincia")
    municipality: str = Field(description="Municipio")
    postal_code: str = Field(alias="postalCode", description="Código postal")
    contracted_power_kw: List[float] = Field(
        alias="contractedPowerkW", description="Potencias contratadas"
    )
    time_discrimination: Optional[str] = Field(
        default=None, alias="timeDiscrimination", description="Discriminación horaria"
    )
    mode_power_control: str = Field(
        alias="modePowerControl",
        description="Modo de control de potencia (ICP/Maxímetro)",
    )
    start_date: str = Field(
        alias="startDate", description="Fecha de inicio del contrato"
    )
    end_date: Optional[str] = Field(
        default=None, alias="endDate", description="Fecha de fin del contrato"
    )
    code_fare: str = Field(
        alias="codeFare", description="Código de tarifa de acceso (códigos CNMC)"
    )
    self_consumption_type_code: Optional[str] = Field(
        default=None,
        alias="selfConsumptionTypeCode",
        description="Código del tipo de autoconsumo",
    )
    self_consumption_type_desc: Optional[str] = Field(
        default=None,
        alias="selfConsumptionTypeDesc",
        description="Descripción del tipo de autoconsumo",
    )
    section: Optional[str] = Field(default=None, description="Sección (autoconsumo)")
    subsection: Optional[str] = Field(
        default=None, description="Subsección (autoconsumo)"
    )
    partition_coefficient: Optional[float] = Field(
        default=None,
        alias="partitionCoefficient",
        description="Coeficiente de reparto (autoconsumo)",
    )
    cau: Optional[str] = Field(default=None, description="CAU (autoconsumo)")
    installed_capacity_kw: Optional[float] = Field(
        default=None,
        alias="installedCapacityKW",
        description="Capacidad de generación instalada",
    )
    date_owner: Optional[List[DateOwner]] = Field(
        default=None,
        alias="dateOwner",
        description="Fechas en las cuales ha sido propietario",
    )
    last_marketer_date: Optional[str] = Field(
        default=None,
        alias="lastMarketerDate",
        description="Fecha del último cambio de comercializadora",
    )
    max_power_install: Optional[str] = Field(
        default=None,
        alias="maxPowerInstall",
        description="Potencia máxima de la instalación",
    )

    model_config = ConfigDict(populate_by_name=True)


@dataclass
class DistributorError:
    """Error de distribuidor según API de Datadis"""

    distributor_code: str
    distributor_name: str
    error_code: str
    error_description: str


@dataclass
class ContractResponse:
    """Respuesta completa del endpoint get_contract_detail V2 - Raw data"""

    contracts: List[Dict[str, Any]]  # Raw dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class ConsumptionResponse:
    """Respuesta completa del endpoint get_consumption V2 - Raw data"""

    consumption_data: List[Dict[str, Any]]  # Raw dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class SuppliesResponse:
    """Respuesta completa del endpoint get_supplies V2 - Raw data"""

    supplies: List[Dict[str, Any]]  # Raw supply dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class MaxPowerResponse:
    """Respuesta completa del endpoint get_max_power V2 - Raw data"""

    max_power_data: List[Dict[str, Any]]  # Raw max power dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class DistributorsResponse:
    """Respuesta completa del endpoint get_distributors V2 - Raw data"""

    distributor_codes: List[str]  # List of distributor codes
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts
