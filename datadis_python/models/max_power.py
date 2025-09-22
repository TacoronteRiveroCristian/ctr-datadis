"""
Modelos de datos para potencia máxima.

Este módulo define los modelos de datos para información de potencia máxima.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaxPowerData(BaseModel):
    """
    Modelo Pydantic para datos de potencia máxima demandada en suministros eléctricos.

    Representa el registro de potencia eléctrica máxima demandada en un punto de
    suministro durante un período determinado. Esta información es crucial para
    la facturación eléctrica, optimización de contratos y análisis de consumo,
    especialmente en instalaciones comerciales e industriales con control por maxímetro.

    Conceptos fundamentales:
        - **Potencia máxima**: Pico de demanda eléctrica registrado en un período
        - **Control por maxímetro**: Sistema que registra automáticamente los picos de potencia
        - **Períodos tarifarios**: Franjas horarias con diferentes precios de energía
        - **Penalizaciones**: Excesos sobre la potencia contratada pueden generar recargos

    Sistemas de control de potencia en España:
        - **ICP (Interruptor Control Potencia)**: Corta el suministro si se excede la potencia
        - **Maxímetro**: Registra los picos pero permite el consumo (con posible recargo)

    Períodos tarifarios comunes:
        - **PUNTA**: Horas de mayor demanda nacional (18:00-22:00 invierno)
        - **LLANO**: Horas intermedias de demanda
        - **VALLE**: Horas de menor demanda (01:00-08:00)
        - **P1-P6**: Períodos numerados según discriminación horaria específica

    Example:
        Análisis de potencia máxima doméstica::

            from datadis_python.models.max_power import MaxPowerData

            # Pico de potencia en hora punta
            max_power_home = MaxPowerData(
                cups="ES001234567890123456AB",
                date="2024/12/15",
                time="19:30",  # Hora punta de invierno
                maxPower=4250.0,  # 4.25 kW
                period="PUNTA"
            )

            print(f"Potencia máxima: {max_power_home.max_power / 1000:.2f} kW")
            print(f"Momento pico: {max_power_home.date} a las {max_power_home.time}")
            print(f"Período tarifario: {max_power_home.period}")

            # Verificar si excede potencia contratada
            potencia_contratada = 5750  # 5.75 kW en W
            if max_power_home.max_power > potencia_contratada:
                exceso = max_power_home.max_power - potencia_contratada
                print(f"⚠️ Exceso: {exceso:.0f} W sobre lo contratado")
            else:
                print("✅ Dentro de la potencia contratada")

        Instalación comercial con múltiples períodos::

            # Ejemplo de pequeño comercio
            power_records = [
                MaxPowerData(
                    cups="ES009876543210987654AB",
                    date="2024/11/20",
                    time="09:15",
                    maxPower=12500.0,  # 12.5 kW
                    period="LLANO"
                ),
                MaxPowerData(
                    cups="ES009876543210987654AB",
                    date="2024/11/20",
                    time="20:45",
                    maxPower=15200.0,  # 15.2 kW
                    period="PUNTA"
                )
            ]

            # Analizar picos por período
            for record in power_records:
                kw_power = record.max_power / 1000
                print(f"Período {record.period}: {kw_power:.1f} kW a las {record.time}")

        Optimización de contrato basada en datos históricos::

            from datadis_python.client.v2 import SimpleDatadisClientV2

            with SimpleDatadisClientV2("12345678A", "password") as client:
                # Obtener datos de potencia máxima del último año
                max_power_response = client.get_max_power(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/12"
                )

                # Analizar patrones para optimizar contrato
                monthly_peaks = {}
                for power_data in max_power_response.max_power_data:
                    month = power_data.date[:7]  # YYYY/MM
                    current_peak = monthly_peaks.get(month, 0)
                    monthly_peaks[month] = max(current_peak, power_data.max_power)

                avg_peak = sum(monthly_peaks.values()) / len(monthly_peaks)
                print(f"Potencia promedio máxima: {avg_peak/1000:.2f} kW")

    :param cups: Código CUPS del punto de suministro. Identificador único del punto
                de conexión donde se registró la potencia máxima
    :type cups: str
    :param date: Fecha en que se registró la potencia máxima en formato YYYY/MM/DD.
                Corresponde al día específico en que ocurrió el pico de demanda
    :type date: str
    :param time: Hora exacta del pico de potencia en formato HH:MM (24h).
                Momento preciso en que se registró la demanda máxima del período
    :type time: str
    :param max_power: Potencia máxima demandada expresada en vatios (W).
                     Representa el pico de consumo eléctrico registrado en el momento especificado
    :type max_power: float
    :param period: Período tarifario en el que ocurrió el pico. Valores típicos:
                  "PUNTA", "LLANO", "VALLE" o códigos numéricos "P1"-"P6" según discriminación horaria
    :type period: str

    :raises ValidationError: Si algún campo obligatorio falta o tiene formato incorrecto

    .. note::
       La potencia se expresa en vatios (W). Para convertir a kilovatios: ``max_power / 1000``

    .. tip::
       Para instalaciones con ICP, los picos registrados normalmente no excederán
       la potencia contratada ya que el interruptor cortaría el suministro.

    .. seealso::
       - :class:`MaxPowerResponse` - Respuesta estructurada de la API V2
       - :meth:`SimpleDatadisClientV1.get_max_power` - Obtener datos V1
       - :meth:`SimpleDatadisClientV2.get_max_power` - Obtener datos V2
       - :class:`ContractData` - Información sobre potencias contratadas

    .. versionadded:: 1.0
       Soporte para datos de potencia máxima de contadores inteligentes
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
