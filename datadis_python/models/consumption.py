"""
Modelos de datos para consumos.

Este módulo define los modelos de datos para los consumos energéticos.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConsumptionData(BaseModel):
    """
    Modelo Pydantic para datos de consumo energético de Datadis.

    Representa una medición de consumo eléctrico proveniente de los contadores
    inteligentes de las distribuidoras eléctricas españolas. Los datos incluyen
    tanto consumo tradicional como información de autoconsumo y generación para
    instalaciones con paneles solares u otras fuentes de energía renovable.

    Características principales:
        - **Validación automática**: Todos los campos se validan con Pydantic
        - **Compatibilidad de alias**: Soporta tanto nombres Python como nombres API
        - **Datos de autoconsumo**: Información completa para instalaciones fotovoltaicas
        - **Granularidad temporal**: Mediciones horarias o cuarto-horarias según disponibilidad
        - **Métodos de obtención**: Distingue entre mediciones reales y estimadas

    Tipos de mediciones soportadas:
        - **Consumo tradicional**: Energía consumida de la red eléctrica
        - **Autoconsumo**: Energía generada y consumida localmente (sin pasar por la red)
        - **Excedentes/Vertidos**: Energía generada y vendida a la red eléctrica
        - **Generación total**: Energía total producida por la instalación renovable

    Métodos de obtención de datos:
        - **"Real"**: Medición directa del contador inteligente
        - **"Estimada"**: Estimación basada en patrones históricos o interpolación
        - **"Provisional"**: Datos preliminares pendientes de validación final

    Example:
        Uso básico del modelo::

            from datadis_python.models.consumption import ConsumptionData

            # Datos típicos de consumo sin autoconsumo
            consumption_basic = ConsumptionData(
                cups="ES001234567890123456AB",
                date="2024/12/15",
                time="14:00",
                consumptionKWh=2.45,
                obtainMethod="Real"
            )

            print(f"Consumo: {consumption_basic.consumption_kwh} kWh")
            print(f"Método: {consumption_basic.obtain_method}")

        Datos de instalación con autoconsumo fotovoltaico::

            # Instalación con paneles solares
            consumption_solar = ConsumptionData(
                cups="ES001234567890123456AB",
                date="2024/07/20",
                time="13:00",  # Hora de máxima producción solar
                consumptionKWh=0.25,      # Poca energía de la red
                obtainMethod="Real",
                surplusEnergyKWh=3.20,    # Excedente vendido a la red
                generationEnergyKWh=5.80, # Generación total de paneles
                selfConsumptionEnergyKWh=2.60  # Autoconsumo directo
            )

            # Verificar balance energético
            total_consumption = (consumption_solar.consumption_kwh +
                               consumption_solar.self_consumption_energy_kwh)
            print(f"Consumo total real: {total_consumption} kWh")
            print(f"Excedente vendido: {consumption_solar.surplus_energy_kwh} kWh")

        Validación automática con alias::

            # Usando nombres de la API (camelCase)
            data_api = {
                "cups": "ES001234567890123456AB",
                "date": "2024/12/15",
                "time": "10:30",
                "consumptionKWh": 1.85,  # Nombre API
                "obtainMethod": "Estimada"
            }

            consumption = ConsumptionData(**data_api)
            print(f"Consumo: {consumption.consumption_kwh}")  # Acceso Python

    :param cups: Código CUPS del punto de suministro. Identificador único de 22 caracteres
                que identifica de forma inequívoca el punto de conexión a la red eléctrica
    :type cups: str
    :param date: Fecha de la medición en formato YYYY/MM/DD. Corresponde al día de la
                lectura del contador, en zona horaria española (CET/CEST)
    :type date: str
    :param time: Hora de la medición en formato HH:MM (24h). Para mediciones horarias
                normalmente :00, para cuarto-horarias :00, :15, :30, :45
    :type time: str
    :param consumption_kwh: Energía activa consumida desde la red eléctrica en kWh.
                           Representa la energía que el usuario ha tomado de la red
                           durante el período de medición
    :type consumption_kwh: float
    :param obtain_method: Método de obtención de los datos. Valores posibles:
                         "Real" (medición directa), "Estimada" (cálculo), "Provisional"
    :type obtain_method: str
    :param surplus_energy_kwh: Energía excedentaria vertida a la red en kWh. Solo aplica
                              para instalaciones de autoconsumo con excedentes. Representa
                              la energía generada localmente y vendida/cedida a la red
    :type surplus_energy_kwh: Optional[float]
    :param generation_energy_kwh: Energía total generada por la instalación renovable en kWh.
                                 Suma del autoconsumo directo más los excedentes vertidos.
                                 Solo aplica para instalaciones con generación propia
    :type generation_energy_kwh: Optional[float]
    :param self_consumption_energy_kwh: Energía autoconsumida directamente en kWh.
                                       Energía generada localmente y consumida sin pasar
                                       por la red. Solo aplica para instalaciones de autoconsumo
    :type self_consumption_energy_kwh: Optional[float]

    :raises ValidationError: Si algún campo no cumple las validaciones de Pydantic
                            (tipos incorrectos, valores nulos en campos obligatorios, etc.)

    .. note::
       Para instalaciones con autoconsumo, se cumple la ecuación:
       ``generation_energy_kwh = self_consumption_energy_kwh + surplus_energy_kwh``

    .. seealso::
       - :class:`ConsumptionResponse` - Respuesta estructurada de la API V2
       - :meth:`SimpleDatadisClientV1.get_consumption` - Obtener datos V1
       - :meth:`SimpleDatadisClientV2.get_consumption` - Obtener datos V2
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
