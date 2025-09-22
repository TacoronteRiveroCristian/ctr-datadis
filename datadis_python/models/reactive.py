"""
Modelos de datos para energía reactiva.

Este módulo define los modelos de datos para información de energía reactiva.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .responses import DistributorError


class ReactiveEnergyPeriod(BaseModel):
    """
    Modelo Pydantic para datos de energía reactiva por período tarifario.

    Representa las mediciones de energía reactiva registradas en un mes específico,
    desglosadas por los diferentes períodos tarifarios establecidos en el sistema
    eléctrico español. La energía reactiva es necesaria para el funcionamiento de
    equipos inductivos pero no realiza trabajo útil, y su exceso puede penalizarse.

    Conceptos fundamentales de energía reactiva:
        - **Energía activa**: Realiza trabajo útil (kWh) - la que se factura normalmente
        - **Energía reactiva**: Necesaria para equipos inductivos (kVArh) - puede penalizarse
        - **Factor de potencia**: Relación entre energía activa y aparente (cos φ)
        - **Penalizaciones**: Se aplican si el factor de potencia es inferior a 0.95

    Equipos que consumen energía reactiva:
        - **Motores eléctricos**: Especialmente en arranque y con poca carga
        - **Transformadores**: En vacío o con poca carga
        - **Lámparas fluorescentes**: Sin condensador de corrección
        - **Soldadores de arco**: Durante el funcionamiento
        - **Hornos de inducción**: Para calentamiento industrial

    Períodos tarifarios en discriminación horaria:
        - **P1**: Punta (horas de mayor demanda nacional)
        - **P2**: Llano alto (horas intermedias altas)
        - **P3**: Llano (horas intermedias)
        - **P4**: Valle alto (horas intermedias bajas)
        - **P5**: Valle (horas de menor demanda)
        - **P6**: Supervalle (madrugada, solo algunas tarifas)

    Example:
        Análisis de consumo reactivo mensual::

            from datadis_python.models.reactive import ReactiveEnergyPeriod

            # Datos de energía reactiva de una industria en enero
            reactive_period = ReactiveEnergyPeriod(
                date="2024/01",
                energy_p1=125.5,  # kVArh en horas punta
                energy_p2=89.2,   # kVArh en llano alto
                energy_p3=156.8,  # kVArh en llano
                energy_p4=None,   # No aplica para esta tarifa
                energy_p5=78.3,   # kVArh en valle
                energy_p6=None    # No aplica
            )

            # Calcular total reactivo mensual
            total_reactive = sum(filter(None, [
                reactive_period.energy_p1, reactive_period.energy_p2,
                reactive_period.energy_p3, reactive_period.energy_p5
            ]))

            print(f"Mes: {reactive_period.date}")
            print(f"Total energía reactiva: {total_reactive:.1f} kVArh")

        Detección de penalizaciones potenciales::

            # Supongamos 1000 kWh de energía activa en el mismo período
            energia_activa = 1000.0  # kWh del mes
            energia_reactiva = total_reactive  # del ejemplo anterior

            # Calcular factor de potencia aproximado
            import math
            factor_potencia = energia_activa / math.sqrt(energia_activa**2 + energia_reactiva**2)

            print(f"Factor de potencia estimado: {factor_potencia:.3f}")

            if factor_potencia < 0.95:
                print("⚠️ Riesgo de penalización por energía reactiva")
                print("Considere instalar condensadores de corrección")
            else:
                print("✅ Factor de potencia dentro de límites normales")

        Análisis por períodos tarifarios::

            periods_data = [
                ("P1 (Punta)", reactive_period.energy_p1),
                ("P2 (Llano alto)", reactive_period.energy_p2),
                ("P3 (Llano)", reactive_period.energy_p3),
                ("P5 (Valle)", reactive_period.energy_p5)
            ]

            print("Consumo reactivo por período:")
            for period_name, energy in periods_data:
                if energy is not None:
                    print(f"- {period_name}: {energy:.1f} kVArh")

    :param date: Fecha del período en formato YYYY/MM. Corresponde al mes para el cual
                se registraron las mediciones de energía reactiva
    :type date: str
    :param energy_p1: Energía reactiva consumida durante el período P1 (Punta) expresada
                     en kilovatios-amperio reactivo hora (kVArh)
    :type energy_p1: Optional[float]
    :param energy_p2: Energía reactiva consumida durante el período P2 (Llano alto) en kVArh
    :type energy_p2: Optional[float]
    :param energy_p3: Energía reactiva consumida durante el período P3 (Llano) en kVArh
    :type energy_p3: Optional[float]
    :param energy_p4: Energía reactiva consumida durante el período P4 (Valle alto) en kVArh.
                     Puede ser None si la tarifa no incluye este período
    :type energy_p4: Optional[float]
    :param energy_p5: Energía reactiva consumida durante el período P5 (Valle) en kVArh
    :type energy_p5: Optional[float]
    :param energy_p6: Energía reactiva consumida durante el período P6 (Supervalle) en kVArh.
                     Solo aplicable en tarifas con discriminación horaria extendida
    :type energy_p6: Optional[float]

    :raises ValidationError: Si la fecha no tiene formato válido YYYY/MM

    .. note::
       Los valores None indican que el período tarifario no aplica para la tarifa específica
       del suministro o que no hay datos disponibles para ese período.

    .. tip::
       Para reducir la energía reactiva: instale condensadores de corrección,
       optimice el funcionamiento de motores y reemplace equipos ineficientes.

    .. seealso::
       - :class:`ReactiveEnergyData` - Contenedor completo de datos reactivos
       - :class:`ReactiveResponse` - Respuesta de la API V2 con manejo de errores
       - Factor de potencia objetivo: cos φ ≥ 0.95 para evitar penalizaciones
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
    Modelo Pydantic completo para datos de energía reactiva de un punto de suministro.

    Contenedor principal que agrupa toda la información de energía reactiva de un CUPS
    específico, incluyendo las mediciones por períodos tarifarios y información de
    estado o errores. Este modelo representa la respuesta detallada de la API para
    consultas de energía reactiva, exclusiva de la versión V2.

    Información incluida:
        - **Identificación**: Código CUPS del punto de suministro
        - **Datos temporales**: Lista de períodos con mediciones mensuales
        - **Control de errores**: Códigos y descripciones de posibles incidencias
        - **Validación**: Estructura validada con Pydantic para garantizar integridad

    Estados posibles de la respuesta:
        - **Datos completos**: code=None, mediciones disponibles en energy
        - **Sin datos**: Períodos sin mediciones (energy vacío)
        - **Error parcial**: Algunos períodos con datos, otros con errores
        - **Error total**: code!=None con descripción del problema

    Example:
        Uso básico con datos completos::

            from datadis_python.models.reactive import ReactiveEnergyData, ReactiveEnergyPeriod

            # Datos de energía reactiva de una instalación industrial
            reactive_data = ReactiveEnergyData(
                cups="ES001234567890123456AB",
                energy=[
                    ReactiveEnergyPeriod(
                        date="2024/01",
                        energy_p1=156.8, energy_p2=98.5,
                        energy_p3=203.2, energy_p5=89.1
                    ),
                    ReactiveEnergyPeriod(
                        date="2024/02",
                        energy_p1=142.3, energy_p2=87.9,
                        energy_p3=189.5, energy_p5=76.8
                    )
                ],
                code=None,  # Sin errores
                code_desc=None
            )

            print(f"CUPS: {reactive_data.cups}")
            print(f"Períodos disponibles: {len(reactive_data.energy)}")

            # Análisis mensual
            for period in reactive_data.energy:
                total_month = sum(filter(None, [
                    period.energy_p1, period.energy_p2,
                    period.energy_p3, period.energy_p5
                ]))
                print(f"Mes {period.date}: {total_month:.1f} kVArh")

        Manejo de errores en la respuesta::

            # Caso con error en los datos
            reactive_error = ReactiveEnergyData(
                cups="ES009876543210987654AB",
                energy=[],  # Sin datos
                code="ERR_404",
                code_desc="No hay datos de energía reactiva para el período solicitado"
            )

            if reactive_error.code:
                print(f"Error {reactive_error.code}: {reactive_error.code_desc}")
                print("No se pueden analizar datos de energía reactiva")
            else:
                # Procesar datos normalmente
                pass

        Análisis de eficiencia energética::

            # Calcular tendencias de energía reactiva
            monthly_totals = []
            for period in reactive_data.energy:
                monthly_reactive = sum(filter(None, [
                    period.energy_p1, period.energy_p2,
                    period.energy_p3, period.energy_p4,
                    period.energy_p5, period.energy_p6
                ]))
                monthly_totals.append(monthly_reactive)

            if monthly_totals:
                avg_reactive = sum(monthly_totals) / len(monthly_totals)
                print(f"Promedio mensual energía reactiva: {avg_reactive:.1f} kVArh")

                # Detectar tendencias
                if len(monthly_totals) >= 2:
                    trend = monthly_totals[-1] - monthly_totals[0]
                    if trend > 0:
                        print("📈 Tendencia creciente - revisar factor de potencia")
                    else:
                        print("📉 Tendencia decreciente - mejorando eficiencia")

        Comparación entre períodos tarifarios::

            # Identificar el período con mayor consumo reactivo
            period_totals = {}
            for monthly_data in reactive_data.energy:
                for p_num, energy in [
                    ("P1", monthly_data.energy_p1), ("P2", monthly_data.energy_p2),
                    ("P3", monthly_data.energy_p3), ("P4", monthly_data.energy_p4),
                    ("P5", monthly_data.energy_p5), ("P6", monthly_data.energy_p6)
                ]:
                    if energy is not None:
                        period_totals[p_num] = period_totals.get(p_num, 0) + energy

            if period_totals:
                max_period = max(period_totals, key=period_totals.get)
                print(f"Período con mayor consumo reactivo: {max_period}")
                print(f"Total acumulado: {period_totals[max_period]:.1f} kVArh")

    :param cups: Código CUPS del punto de suministro para el cual se consultaron
                los datos de energía reactiva. Identificador único del punto de conexión
    :type cups: str
    :param energy: Lista de objetos ReactiveEnergyPeriod con las mediciones mensuales
                  de energía reactiva desglosadas por períodos tarifarios
    :type energy: List[ReactiveEnergyPeriod]
    :param code: Código de error o estado. None si la consulta fue exitosa,
                string con código específico si hubo problemas en la obtención de datos
    :type code: Optional[str]
    :param code_desc: Descripción detallada del error o estado. Proporciona información
                     legible sobre el problema específico encontrado durante la consulta
    :type code_desc: Optional[str]

    :raises ValidationError: Si el CUPS tiene formato inválido o faltan campos obligatorios

    .. note::
       La energía reactiva solo está disponible en la API V2 y requiere que el contador
       inteligente del suministro soporte medición de energía reactiva.

    .. warning::
       Un ``code`` diferente de None indica problemas en la obtención de datos.
       Siempre verificar este campo antes de procesar las mediciones.

    .. seealso::
       - :class:`ReactiveEnergyPeriod` - Modelo de mediciones por período
       - :class:`ReactiveResponse` - Respuesta completa con errores de distribuidor
       - :meth:`SimpleDatadisClientV2.get_reactive_data` - Método para obtener estos datos

    .. versionadded:: 2.0
       Funcionalidad exclusiva de la API V2 para análisis avanzado de eficiencia energética
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
    Modelo Pydantic simplificado para respuesta de energía reactiva.

    Wrapper o contenedor simple para datos de energía reactiva que encapsula
    la información principal en un objeto ReactiveEnergyData. Este modelo
    representa la estructura de respuesta básica de algunos endpoints de
    energía reactiva, proporcionando acceso directo a los datos principales.

    Casos de uso:
        - **Respuestas simples**: Cuando solo se necesitan los datos principales
        - **Compatibilidad**: Para mantener consistencia con otras APIs
        - **Encapsulación**: Estructura que puede extenderse en futuras versiones

    Example:
        Uso básico del modelo wrapper::

            from datadis_python.models.reactive import ReactiveData, ReactiveEnergyData

            # Datos encapsulados en el wrapper
            reactive_wrapper = ReactiveData(
                reactiveEnergy=ReactiveEnergyData(
                    cups="ES001234567890123456AB",
                    energy=[],  # Lista de períodos
                    code=None,
                    code_desc=None
                )
            )

            # Acceso a los datos principales
            main_data = reactive_wrapper.reactive_energy
            print(f"CUPS: {main_data.cups}")
            print(f"Períodos disponibles: {len(main_data.energy)}")

        Procesamiento directo::

            # Trabajar directamente con los datos encapsulados
            if reactive_wrapper.reactive_energy.code is None:
                # Procesar datos de energía reactiva
                for period in reactive_wrapper.reactive_energy.energy:
                    print(f"Mes {period.date}: datos disponibles")
            else:
                print(f"Error: {reactive_wrapper.reactive_energy.code_desc}")

    :param reactive_energy: Objeto ReactiveEnergyData que contiene toda la información
                           de energía reactiva para el punto de suministro consultado
    :type reactive_energy: ReactiveEnergyData

    :raises ValidationError: Si el objeto ReactiveEnergyData no es válido

    .. note::
       Este modelo es principalmente un wrapper. Para acceso a datos detallados,
       utilice directamente el atributo ``reactive_energy``.

    .. seealso::
       - :class:`ReactiveEnergyData` - Modelo principal con los datos detallados
       - :class:`ReactiveResponse` - Versión extendida con manejo de errores por distribuidor
    """

    reactive_energy: ReactiveEnergyData = Field(
        alias="reactiveEnergy", description="Datos de energía reactiva"
    )

    model_config = ConfigDict(populate_by_name=True)


class ReactiveResponse(BaseModel):
    r"""
    Modelo Pydantic completo para respuesta estructurada de energía reactiva V2.

    Respuesta completa y robusta del endpoint ``get_reactive_data`` de la API V2,
    que incluye tanto los datos de energía reactiva como información detallada
    sobre errores específicos por distribuidor. Esta estructura permite manejar
    casos donde algunos distribuidores proporcionan datos correctamente mientras
    otros experimentan problemas técnicos.

    Características de la respuesta V2:
        - **Datos principales**: Información completa de energía reactiva
        - **Manejo granular de errores**: Errores específicos por distribuidor
        - **Robustez**: Respuesta parcial en caso de fallos de algunos distribuidores
        - **Información detallada**: Códigos y descripciones específicas de errores

    Ventajas sobre respuestas simples:
        - **Transparencia**: Visibilidad completa de problemas por distribuidor
        - **Resiliencia**: Datos útiles incluso con errores parciales
        - **Diagnóstico**: Información detallada para resolución de problemas
        - **Consistencia**: Estructura uniforme independientemente del estado

    Example:
        Respuesta exitosa completa::

            from datadis_python.models.reactive import ReactiveResponse
            from datadis_python.client.v2 import SimpleDatadisClientV2

            with SimpleDatadisClientV2("12345678A", "password") as client:
                response = client.get_reactive_data(
                    cups="ES001234567890123456AB",
                    distributor_code="2",
                    date_from="2024/01",
                    date_to="2024/06"
                )

            # Verificar respuesta completa
            if not response.distributor_error:
                print("✅ Datos obtenidos sin errores")
                reactive_data = response.reactive_energy

                print(f"CUPS: {reactive_data.cups}")
                print(f"Períodos con datos: {len(reactive_data.energy)}")

                # Procesar datos de energía reactiva
                for period in reactive_data.energy:
                    total_reactive = sum(filter(None, [
                        period.energy_p1, period.energy_p2, period.energy_p3,
                        period.energy_p4, period.energy_p5, period.energy_p6
                    ]))
                    print(f"Mes {period.date}: {total_reactive:.1f} kVArh")
            else:
                print("❌ Errores detectados por distribuidor")

        Manejo de errores por distribuidor::

            # Respuesta con errores específicos
            if response.distributor_error:
                print("Errores por distribuidor:")
                for error in response.distributor_error:
                    print(f"- {error.distributor_name} (código {error.distributor_code}):")
                    print(f"  Error {error.error_code}: {error.error_description}")

                # Evaluar si los datos son utilizables
                if response.reactive_energy.code is None:
                    print("Los datos principales están disponibles a pesar de errores")
                else:
                    print("Error crítico - datos no disponibles")

        Análisis robusto con manejo de errores::

            def analyze_reactive_response(response: ReactiveResponse):
                \"\"\"Analiza respuesta de energía reactiva con manejo robusto de errores.\"\"\"

                # Verificar estado general
                print(f"Estado de la respuesta:")
                print(f"- Errores de distribuidor: {len(response.distributor_error)}")
                print(f"- Datos principales disponibles: {response.reactive_energy.code is None}")

                # Procesar errores si existen
                if response.distributor_error:
                    error_types = {}
                    for error in response.distributor_error:
                        error_types[error.error_code] = error_types.get(error.error_code, 0) + 1

                    print("Tipos de errores encontrados:")
                    for error_code, count in error_types.items():
                        print(f"- {error_code}: {count} distribuidor(es)")

                # Analizar datos disponibles
                if response.reactive_energy.code is None and response.reactive_energy.energy:
                    print(f"✅ Análisis de {len(response.reactive_energy.energy)} períodos")

                    total_periods = len(response.reactive_energy.energy)
                    periods_with_data = sum(1 for p in response.reactive_energy.energy
                                          if any([p.energy_p1, p.energy_p2, p.energy_p3,
                                                p.energy_p4, p.energy_p5, p.energy_p6]))

                    completeness = (periods_with_data / total_periods) * 100
                    print(f"Completitud de datos: {completeness:.1f}%")

                    return True  # Datos utilizables
                else:
                    print(f"❌ Datos no disponibles: {response.reactive_energy.code_desc}")
                    return False  # Datos no utilizables

            # Usar la función de análisis
            data_available = analyze_reactive_response(response)
            if data_available:
                # Continuar con el análisis de eficiencia energética
                pass

        Comparación de respuestas V1 vs V2::

            # V1: Sin información de errores específicos
            # Si falla, toda la respuesta falla sin detalles

            # V2: Información granular de errores
            response_v2 = client.get_reactive_data(...)

            print("Información detallada V2:")
            print(f"- Datos obtenidos: {response_v2.reactive_energy.code is None}")
            print(f"- Errores por distribuidor: {len(response_v2.distributor_error)}")

            # Decidir estrategia basada en errores específicos
            if response_v2.distributor_error:
                for error in response_v2.distributor_error:
                    if "TIMEOUT" in error.error_code:
                        print(f"Reintento recomendado para {error.distributor_name}")
                    elif "NO_DATA" in error.error_code:
                        print(f"Sin datos históricos en {error.distributor_name}")

    :param reactive_energy: Objeto ReactiveEnergyData con toda la información de energía
                           reactiva del punto de suministro consultado
    :type reactive_energy: ReactiveEnergyData
    :param distributor_error: Lista de errores específicos por distribuidor eléctrico.
                             Incluye información detallada sobre problemas encontrados
                             durante la consulta a cada distribuidor involucrado
    :type distributor_error: List[DistributorError]

    :raises ValidationError: Si algún componente de la respuesta no es válido

    .. note::
       Una respuesta puede tener datos válidos en ``reactive_energy`` incluso si
       ``distributor_error`` contiene elementos. Evalúe ambos campos independientemente.

    .. tip::
       Para aplicaciones críticas, implemente lógica de reintento basada en los
       códigos de error específicos de cada distribuidor.

    .. seealso::
       - :class:`ReactiveEnergyData` - Datos principales de energía reactiva
       - :class:`DistributorError` - Información detallada de errores por distribuidor
       - :meth:`SimpleDatadisClientV2.get_reactive_data` - Método que retorna este modelo

    .. versionadded:: 2.0
       Estructura de respuesta robusta con manejo granular de errores por distribuidor
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
