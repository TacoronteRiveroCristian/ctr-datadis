"""
Modelos de datos para energía reactiva.

Este módulo define los modelos de datos para información de energía reactiva.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .responses import DistributorError


class ReactiveEnergyPeriod(BaseModel):
    """
    Modelo para datos de un período de energía reactiva.

    :param date: Fecha (AAAA/MM)
    :type date: str
    :param energy_p1: Energía reactiva en el Periodo 1
    :type energy_p1: Optional[float]
    :param energy_p2: Energía reactiva en el Periodo 2
    :type energy_p2: Optional[float]
    :param energy_p3: Energía reactiva en el Periodo 3
    :type energy_p3: Optional[float]
    :param energy_p4: Energía reactiva en el Periodo 4
    :type energy_p4: Optional[float]
    :param energy_p5: Energía reactiva en el Periodo 5
    :type energy_p5: Optional[float]
    :param energy_p6: Energía reactiva en el Periodo 6
    :type energy_p6: Optional[float]
    """

    date: str = Field(description="Fecha (AAAA/MM)")
    energy_p1: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 1"
    )
    energy_p2: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 2"
    )
    energy_p3: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 3"
    )
    energy_p4: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 4"
    )
    energy_p5: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 5"
    )
    energy_p6: Optional[float] = Field(
        default=None, description="Energía reactiva en el Periodo 6"
    )

    model_config = ConfigDict(populate_by_name=True)


class ReactiveEnergyData(BaseModel):
    """
    Modelo para datos de energía reactiva.

    :param cups: CUPS del punto de suministro
    :type cups: str
    :param energy: Lista de datos de energía reactiva por período
    :type energy: List[ReactiveEnergyPeriod]
    :param code: Código de error
    :type code: Optional[str]
    :param code_desc: Descripción del error
    :type code_desc: Optional[str]
    """

    cups: str = Field(description="CUPS del punto de suministro")
    energy: List[ReactiveEnergyPeriod] = Field(
        description="Lista de datos de energía reactiva por período"
    )
    code: Optional[str] = Field(default=None, description="Código de error")
    code_desc: Optional[str] = Field(
        default=None, alias="code_desc", description="Descripción del error"
    )

    model_config = ConfigDict(populate_by_name=True)


class ReactiveData(BaseModel):
    """
    Modelo para respuesta de energía reactiva.

    :param reactive_energy: Datos de energía reactiva
    :type reactive_energy: ReactiveEnergyData
    """

    reactive_energy: ReactiveEnergyData = Field(
        alias="reactiveEnergy", description="Datos de energía reactiva"
    )

    model_config = ConfigDict(populate_by_name=True)


class ReactiveResponse(BaseModel):
    """
    Respuesta completa de get-reactive-data-v2.

    :param reactive_energy: Datos de energía reactiva
    :type reactive_energy: ReactiveEnergyData
    :param distributor_error: Errores de distribuidora
    :type distributor_error: List[DistributorError]
    """

    reactive_energy: ReactiveEnergyData = Field(
        alias="reactiveEnergy", description="Datos de energía reactiva"
    )
    distributor_error: List[DistributorError] = Field(
        default_factory=list,
        alias="distributorError",
        description="Errores de distribuidora",
    )

    model_config = ConfigDict(populate_by_name=True)
