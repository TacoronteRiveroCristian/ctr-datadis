"""
Modelos de datos para potencia máxima
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaxPowerData(BaseModel):
    """Modelo para datos de potencia máxima"""

    cups: str = Field(description="Código CUPS del punto de suministro")
    date: str = Field(
        description="Fecha en la que se demandó la potencia máxima (YYYY/MM/DD)"
    )
    time: str = Field(
        description="Hora en la que se demandó la potencia máxima (HH:MM)"
    )
    max_power: float = Field(
        alias="maxPower", description="Potencia máxima demandada (W)"
    )
    period: str = Field(description="Periodo (VALLE, LLANO, PUNTA, 1-6)")

    model_config = ConfigDict(populate_by_name=True)
