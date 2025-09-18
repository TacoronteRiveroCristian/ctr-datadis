"""
Modelos de datos para energía reactiva
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReactiveEnergyPeriod(BaseModel):
    """Modelo para datos de un período de energía reactiva"""

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
    """Modelo para datos de energía reactiva"""

    cups: str = Field(description="CUPS del punto de suministro")
    energy: List[ReactiveEnergyPeriod] = Field(
        description="Lista de datos de energía reactiva por período"
    )

    model_config = ConfigDict(populate_by_name=True)


class ReactiveData(BaseModel):
    """Modelo para respuesta de energía reactiva"""

    reactive_energy: ReactiveEnergyData = Field(
        alias="reactiveEnergy", description="Datos de energía reactiva"
    )

    model_config = ConfigDict(populate_by_name=True)
