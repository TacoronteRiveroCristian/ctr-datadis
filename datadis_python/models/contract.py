"""
Modelos de datos para contratos.

Este módulo define los modelos de datos para contratos y información relacionada.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DateOwner(BaseModel):
    """
    Periodo de propiedad.

    :param start_date: Fecha de inicio propiedad
    :type start_date: str
    :param end_date: Fecha de fin propiedad
    :type end_date: str
    """

    start_date: str = Field(alias="startDate", description="Fecha de inicio propiedad")
    end_date: str = Field(alias="endDate", description="Fecha de fin propiedad")

    model_config = ConfigDict(populate_by_name=True)


class ContractData(BaseModel):
    """
    Modelo para datos de contrato (versión completa API v2).

    :param cups: Código CUPS del punto de suministro
    :type cups: str
    :param distributor: Nombre de la distribuidora
    :type distributor: str
    :param marketer: Comercializadora (solo si es propietario del CUPS)
    :type marketer: Optional[str]
    :param tension: Tensión
    :type tension: str
    :param access_fare: Descripción tarifa de acceso
    :type access_fare: str
    :param province: Provincia
    :type province: str
    :param municipality: Municipio
    :type municipality: str
    :param postal_code: Código postal
    :type postal_code: str
    :param contracted_power_kw: Potencias contratadas
    :type contracted_power_kw: List[float]
    :param time_discrimination: Discriminación horaria
    :type time_discrimination: Optional[str]
    :param mode_power_control: Modo de control de potencia (ICP/Maxímetro)
    :type mode_power_control: str
    :param start_date: Fecha de inicio del contrato
    :type start_date: str
    :param end_date: Fecha de fin del contrato
    :type end_date: Optional[str]
    :param code_fare: Código de tarifa de acceso (códigos CNMC)
    :type code_fare: str
    :param self_consumption_type_code: Código del tipo de autoconsumo
    :type self_consumption_type_code: Optional[str]
    :param self_consumption_type_desc: Descripción del tipo de autoconsumo
    :type self_consumption_type_desc: Optional[str]
    :param section: Sección (autoconsumo)
    :type section: Optional[str]
    :param subsection: Subsección (autoconsumo)
    :type subsection: Optional[str]
    :param partition_coefficient: Coeficiente de reparto (autoconsumo)
    :type partition_coefficient: Optional[float]
    :param cau: CAU (autoconsumo)
    :type cau: Optional[str]
    :param installed_capacity_kw: Capacidad de generación instalada
    :type installed_capacity_kw: Optional[float]
    :param date_owner: Fechas en las cuales ha sido propietario
    :type date_owner: Optional[List[DateOwner]]
    :param last_marketer_date: Fecha del último cambio de comercializadora
    :type last_marketer_date: Optional[str]
    :param max_power_install: Potencia máxima de la instalación
    :type max_power_install: Optional[str]
    """

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
    """
    Error de distribuidor según API de Datadis.

    :param distributor_code: Código del distribuidor
    :type distributor_code: str
    :param distributor_name: Nombre del distribuidor
    :type distributor_name: str
    :param error_code: Código de error
    :type error_code: str
    :param error_description: Descripción del error
    :type error_description: str
    """

    distributor_code: str
    distributor_name: str
    error_code: str
    error_description: str


@dataclass
class ContractResponse:
    """
    Respuesta completa del endpoint get_contract_detail V2 - Raw data.

    :param contracts: Raw dicts from API
    :type contracts: List[Dict[str, Any]]
    :param distributor_errors: Raw error dicts
    :type distributor_errors: List[Dict[str, Any]]
    """

    contracts: List[Dict[str, Any]]  # Raw dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class ConsumptionResponse:
    """
    Respuesta completa del endpoint get_consumption V2 - Raw data.

    :param consumption_data: Raw dicts from API
    :type consumption_data: List[Dict[str, Any]]
    :param distributor_errors: Raw error dicts
    :type distributor_errors: List[Dict[str, Any]]
    """

    consumption_data: List[Dict[str, Any]]  # Raw dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class SuppliesResponse:
    """
    Respuesta completa del endpoint get_supplies V2 - Raw data.

    :param supplies: Raw supply dicts from API
    :type supplies: List[Dict[str, Any]]
    :param distributor_errors: Raw error dicts
    :type distributor_errors: List[Dict[str, Any]]
    """

    supplies: List[Dict[str, Any]]  # Raw supply dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class MaxPowerResponse:
    """
    Respuesta completa del endpoint get_max_power V2 - Raw data.

    :param max_power_data: Raw max power dicts from API
    :type max_power_data: List[Dict[str, Any]]
    :param distributor_errors: Raw error dicts
    :type distributor_errors: List[Dict[str, Any]]
    """

    max_power_data: List[Dict[str, Any]]  # Raw max power dicts from API
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts


@dataclass
class DistributorsResponse:
    """
    Respuesta completa del endpoint get_distributors V2 - Raw data.

    :param distributor_codes: List of distributor codes
    :type distributor_codes: List[str]
    :param distributor_errors: Raw error dicts
    :type distributor_errors: List[Dict[str, Any]]
    """

    distributor_codes: List[str]  # List of distributor codes
    distributor_errors: List[Dict[str, Any]]  # Raw error dicts
