"""
Modelos de datos para potencia máxima.

Este módulo define los modelos de datos para información de potencia máxima.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaxPowerData(BaseModel):
    """
    Modelo para datos de potencia máxima.

    :param cups: Código CUPS del punto de suministro
    :type cups: str
    :param date: Fecha en la que se demandó la potencia máxima (YYYY/MM/DD)
    :type date: str
    :param time: Hora en la que se demandó la potencia máxima (HH:MM)
    :type time: str
    :param max_power: Potencia máxima demandada (W)
    :type max_power: float
    :param period: Periodo (VALLE, LLANO, PUNTA, 1-6)
    :type period: str
    """

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
