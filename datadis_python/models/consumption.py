"""
Modelos de datos para consumos.

Este módulo define los modelos de datos para los consumos energéticos.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConsumptionData(BaseModel):
    """
    Modelo para datos de consumo energético.

    :param cups: Código CUPS del punto de suministro
    :type cups: str
    :param date: Fecha de la medición (YYYY/MM/DD)
    :type date: str
    :param time: Hora de la medición (HH:MM)
    :type time: str
    :param consumption_kwh: Energía consumida (kWh)
    :type consumption_kwh: float
    :param obtain_method: Método de obtención de la energía (Real/Estimada)
    :type obtain_method: str
    :param surplus_energy_kwh: Energía vertida (neteada/facturada) (kWh)
    :type surplus_energy_kwh: Optional[float]
    :param generation_energy_kwh: Energía generada (neteada/facturada) (kWh)
    :type generation_energy_kwh: Optional[float]
    :param self_consumption_energy_kwh: Energía autoconsumida (neteada/facturada) (kWh)
    :type self_consumption_energy_kwh: Optional[float]
    """

    cups: str = Field(description="Código CUPS del punto de suministro")
    date: str = Field(description="Fecha de la medición (YYYY/MM/DD)")
    time: str = Field(description="Hora de la medición (HH:MM)")
    consumption_kwh: float = Field(
        alias="consumptionKWh", description="Energía consumida (kWh)"
    )
    obtain_method: str = Field(
        alias="obtainMethod",
        description="Método de obtención de la energía (Real/Estimada)",
    )
    surplus_energy_kwh: Optional[float] = Field(
        default=None,
        alias="surplusEnergyKWh",
        description="Energía vertida (neteada/facturada) (kWh)",
    )
    generation_energy_kwh: Optional[float] = Field(
        default=None,
        alias="generationEnergyKWh",
        description="Energía generada (neteada/facturada) (kWh)",
    )
    self_consumption_energy_kwh: Optional[float] = Field(
        default=None,
        alias="selfConsumptionEnergyKWh",
        description="Energía autoconsumida (neteada/facturada) (kWh)",
    )

    model_config = ConfigDict(populate_by_name=True)
