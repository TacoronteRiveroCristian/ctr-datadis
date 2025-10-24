"""
Modelos de respuesta de la API de Datadis (versiones v2).

Este módulo define los modelos de respuesta para las diferentes versiones de la API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DistributorError(BaseModel):
    r"""
    Modelo Pydantic para errores específicos por distribuidor en respuestas de API V2.

    Representa información detallada sobre errores o problemas experimentados por
    distribuidores específicos durante la consulta a sus sistemas. Esta funcionalidad
    es exclusiva de la API V2 y permite un manejo granular de errores, proporcionando
    transparencia sobre qué distribuidores tienen problemas y cuáles funcionan correctamente.

    Ventajas del manejo granular de errores:
        - **Transparencia total**: Identificación específica del distribuidor problemático
        - **Diagnóstico preciso**: Códigos y descripciones específicas para cada error
        - **Resiliencia**: Respuestas parcialmente exitosas cuando solo algunos distribuidores fallan
        - **Debugging**: Información detallada para resolución de problemas técnicos

    Tipos de errores comunes:
        - **Timeouts**: Distribuidor no responde en tiempo límite
        - **No data**: Sin datos disponibles para el período solicitado
        - **Auth errors**: Problemas de autenticación con el distribuidor
        - **System errors**: Errores internos del sistema del distribuidor
        - **Maintenance**: Distribuidor en mantenimiento programado

    Códigos de distribuidor españoles:
        - **"1"**: Viesgo (Cantabria, Asturias)
        - **"2"**: E-distribución/Endesa (Nacional)
        - **"3"**: E-redes (Galicia)
        - **"4"**: ASEME (Melilla)
        - **"5"**: UFD/Naturgy (Nacional)
        - **"6"**: EOSA (Aragón)
        - **"7"**: CIDE (Ceuta)
        - **"8"**: IDE (Baleares)

    Example:
        Interpretación de errores por distribuidor::

            from datadis_python.models.responses import DistributorError

            # Error típico de timeout
            timeout_error = DistributorError(
                distributorCode="2",
                distributorName="E-distribución",
                errorCode="TIMEOUT_001",
                errorDescription="Timeout al consultar datos de consumo - servidor no responde"
            )

            print(f"Distribuidor: {timeout_error.distributor_name}")
            print(f"Código: {timeout_error.distributor_code}")
            print(f"Error: {timeout_error.error_code}")
            print(f"Descripción: {timeout_error.error_description}")

        Casos de uso típicos::

            # Verificar si hay errores específicos
            if distributor_errors:
                problematic_distributors = [err.distributor_name for err in distributor_errors]
                print(f"Distribuidores con problemas: {', '.join(problematic_distributors)}")

                # Categorizar por tipo de error
                timeout_errors = [err for err in distributor_errors if "TIMEOUT" in err.error_code]
                data_errors = [err for err in distributor_errors if "NO_DATA" in err.error_code]

                if timeout_errors:
                    print(f"Timeouts detectados en: {len(timeout_errors)} distribuidores")
                if data_errors:
                    print(f"Sin datos disponibles en: {len(data_errors)} distribuidores")

    Attributes:
        distributor_code: Código único del distribuidor en formato string.
        distributor_name: Nombre comercial completo del distribuidor.
        error_code: Código específico del error para categorización técnica.
        error_description: Descripción detallada y legible del problema.

    Note:
        - Los errores por distribuidor no impiden respuestas parcialmente exitosas
        - Un error en un distribuidor no afecta a los datos de otros distribuidores
        - La presencia de DistributorError no implica fallo total de la operación
        - Los códigos de error permiten implementar retry logic específico
    """

    distributor_code: str = Field(
        alias="distributorCode", description="Código de distribuidora"
    )
    distributor_name: str = Field(
        alias="distributorName", description="Nombre de la distribuidora"
    )
    error_code: str = Field(alias="errorCode", description="Código de error")
    error_description: str = Field(
        alias="errorDescription", description="Descripción del error"
    )

    model_config = ConfigDict(populate_by_name=True)


class SuppliesResponse(BaseModel):
    r"""
    Modelo Pydantic para respuesta estructurada del endpoint get-supplies V2.

    Respuesta completa y robusta del endpoint ``get_supplies`` de la API V2 que
    incluye tanto los datos de puntos de suministro como información detallada
    sobre errores específicos por distribuidor. Esta estructura permite obtener
    datos parciales incluso cuando algunos distribuidores experimentan problemas.

    Ventajas de la estructura V2:
        - **Datos resilientes**: Obtención de suministros incluso con errores parciales
        - **Diagnóstico detallado**: Información específica sobre problemas por distribuidor
        - **Transparencia total**: Visibilidad completa del estado de cada consulta
        - **Manejo granular**: Procesamiento inteligente de respuestas mixtas

    Escenarios de respuesta típicos:
        - **Éxito completo**: Todos los suministros obtenidos, sin errores
        - **Éxito parcial**: Algunos suministros obtenidos, errores en distribuidores específicos
        - **Fallo parcial**: Datos limitados debido a múltiples errores de distribuidor
        - **Fallo total**: Sin datos, errores en todos los distribuidores consultados

    Example:
        Respuesta exitosa completa::

            from datadis_python.client.v2 import SimpleDatadisClientV2

            with SimpleDatadisClientV2("12345678A", "password") as client:
                response = client.get_supplies()

            print(f"Suministros encontrados: {len(response.supplies)}")
            print(f"Errores por distribuidor: {len(response.distributor_error)}")

            if not response.distributor_error:
                print("✅ Respuesta completa sin errores")

                # Procesar todos los suministros
                for supply in response.supplies:
                    print(f"CUPS: {supply.cups}")
                    print(f"Dirección: {supply.address}")
                    print(f"Distribuidor: {supply.distributor} (código: {supply.distributor_code})")
                    print("---")
            else:
                print("⚠️ Respuesta con errores parciales")

        Manejo de respuesta con errores::

            # Analizar errores específicos por distribuidor
            if response.distributor_error:
                print("Problemas detectados:")
                for error in response.distributor_error:
                    print(f"- {error.distributor_name}: {error.error_description}")

                # Determinar si los datos disponibles son útiles
                error_distributors = {error.distributor_code for error in response.distributor_error}
                available_supplies = [s for s in response.supplies
                                    if s.distributor_code not in error_distributors]

                print(f"Suministros utilizables: {len(available_supplies)}")

                if available_supplies:
                    print("Datos parciales disponibles para procesamiento")
                else:
                    print("Sin datos utilizables - todos los distribuidores con errores")

        Análisis por distribuidor::

            # Agrupar suministros por distribuidor
            supplies_by_distributor = {}
            for supply in response.supplies:
                dist_code = supply.distributor_code
                if dist_code not in supplies_by_distributor:
                    supplies_by_distributor[dist_code] = []
                supplies_by_distributor[dist_code].append(supply)

            # Mostrar estadísticas
            print("Distribución de suministros:")
            distributor_names = {
                "1": "Viesgo", "2": "E-distribución", "3": "E-redes",
                "4": "ASEME", "5": "UFD", "6": "EOSA", "7": "CIDE", "8": "IDE"
            }

            for dist_code, supplies_list in supplies_by_distributor.items():
                dist_name = distributor_names.get(dist_code, f"Distribuidor {dist_code}")
                print(f"- {dist_name}: {len(supplies_list)} suministros")

            # Verificar errores por distribuidor
            error_codes = {error.distributor_code for error in response.distributor_error}
            for dist_code in supplies_by_distributor.keys():
                if dist_code in error_codes:
                    print(f"  ⚠️ {distributor_names.get(dist_code)}: Datos incompletos")

        Filtrado inteligente para uso posterior::

            def get_reliable_supplies(response: SuppliesResponse):
                \"\"\"Obtiene solo suministros de distribuidores sin errores.\"\"\"

                # Identificar distribuidores problemáticos
                problem_distributors = {error.distributor_code
                                      for error in response.distributor_error}

                # Filtrar suministros confiables
                reliable_supplies = [
                    supply for supply in response.supplies
                    if supply.distributor_code not in problem_distributors
                ]

                print(f"Suministros confiables: {len(reliable_supplies)}/{len(response.supplies)}")
                return reliable_supplies

            # Usar solo datos confiables para consultas posteriores
            reliable_supplies = get_reliable_supplies(response)

            if reliable_supplies:
                # Continuar con análisis de consumo solo para suministros confiables
                first_supply = reliable_supplies[0]
                consumption_response = client.get_consumption(
                    cups=first_supply.cups,
                    distributor_code=first_supply.distributor_code,
                    date_from="2024/01",
                    date_to="2024/12"
                )

        Comparación con API V1::

            # V1: Lista simple, falla completamente si hay errores
            # supplies_v1 = client_v1.get_supplies()  # List[SupplyData] o excepción

            # V2: Respuesta estructurada con manejo de errores granular
            response_v2 = client_v2.get_supplies()  # SuppliesResponse siempre

            print("Diferencias V1 vs V2:")
            print(f"- V1: Todo o nada ({len(response_v2.supplies)} suministros)")
            print(f"- V2: Datos + errores ({len(response_v2.distributor_error)} errores)")
            print(f"- V2: Información diagnóstica disponible")

    :param supplies: Lista de objetos SupplyData validados con Pydantic. Contiene
                    todos los puntos de suministro obtenidos exitosamente de los
                    distribuidores que respondieron correctamente
    :type supplies: List[SupplyData]
    :param distributor_error: Lista de errores específicos por distribuidor. Incluye
                             información detallada sobre distribuidores que experimentaron
                             problemas durante la consulta
    :type distributor_error: List[DistributorError]

    :raises ValidationError: Si la estructura de la respuesta no es válida

    .. note::
       Una respuesta puede contener datos válidos en ``supplies`` incluso si
       ``distributor_error`` no está vacío. Evalúe ambos campos independientemente.

    .. tip::
       Para aplicaciones robustas, implemente lógica de filtrado que excluya
       suministros de distribuidores con errores de las consultas posteriores.

    .. seealso::
       - :class:`SupplyData` - Modelo individual de punto de suministro
       - :class:`DistributorError` - Información detallada de errores por distribuidor
       - :meth:`SimpleDatadisClientV2.get_supplies` - Método que retorna este modelo

    .. versionadded:: 2.0
       Respuesta estructurada con manejo robusto de errores por distribuidor
    """

    supplies: List["SupplyData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class ContractResponse(BaseModel):
    """
    Modelo Pydantic para respuesta estructurada del endpoint get-contract-detail V2.

    Respuesta completa del endpoint ``get_contract_detail`` que incluye información
    contractual detallada y manejo robusto de errores por distribuidor. Proporciona
    datos contractuales completos incluso cuando algunos distribuidores experimentan
    problemas técnicos.

    Información contractual incluida:
        - **Datos básicos**: CUPS, distribuidor, comercializadora
        - **Información técnica**: Tensión, potencias, tarifa de acceso
        - **Autoconsumo**: Configuración completa de generación renovable
        - **Histórico**: Períodos de propiedad, cambios de comercializadora

    Example:
        Análisis de contratos con manejo de errores::

            with SimpleDatadisClientV2("12345678A", "password") as client:
                response = client.get_contract_detail(
                    cups="ES001234567890123456AB",
                    distributor_code="2"
                )

            if response.contract:
                contract = response.contract[0]
                print(f"Tarifa: {contract.code_fare}")
                print(f"Potencia: {contract.contracted_power_kw} kW")

                if contract.self_consumption_type_desc:
                    print(f"Autoconsumo: {contract.self_consumption_type_desc}")

            for error in response.distributor_error:
                print(f"Error en {error.distributor_name}: {error.error_description}")

    :param contract: Lista de objetos ContractData con información contractual completa
    :type contract: List[ContractData]
    :param distributor_error: Lista de errores específicos por distribuidor
    :type distributor_error: List[DistributorError]
    """

    contract: List["ContractData"] = Field(default_factory=list)
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class ConsumptionResponse(BaseModel):
    """
    Modelo Pydantic para respuesta estructurada del endpoint get-consumption-data V2.

    Respuesta robusta del endpoint ``get_consumption`` que incluye datos de consumo
    energético detallados y manejo granular de errores por distribuidor. Permite
    análisis de consumo incluso con problemas parciales en algunos distribuidores.

    Datos de consumo incluidos:
        - **Mediciones temporales**: Consumos horarios o cuarto-horarios
        - **Autoconsumo**: Generación, autoconsumo y excedentes (si aplica)
        - **Calidad de datos**: Métodos de obtención (Real/Estimada)
        - **Períodos completos**: Rangos de fechas solicitados

    Example:
        Análisis de consumo con datos robustos::

            response = client.get_consumption(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/03"
            )

            print(f"Mediciones obtenidas: {len(response.time_curve)}")

            # Análisis básico
            total_consumption = sum(data.consumption_kwh for data in response.time_curve)
            print(f"Consumo total: {total_consumption:.2f} kWh")

            # Verificar errores
            if response.distributor_error:
                print("Advertencias de distribuidor detectadas")

    :param time_curve: Lista de objetos ConsumptionData con mediciones energéticas temporales
    :type time_curve: List[ConsumptionData]
    :param distributor_error: Lista de errores específicos por distribuidor
    :type distributor_error: List[DistributorError]
    """

    time_curve: List["ConsumptionData"] = Field(default_factory=list, alias="timeCurve")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class MaxPowerResponse(BaseModel):
    """
    Modelo Pydantic para respuesta estructurada del endpoint get-max-power V2.

    Respuesta completa del endpoint ``get_max_power`` que incluye registros de
    potencia máxima demandada y manejo robusto de errores por distribuidor.
    Esencial para análisis de eficiencia y optimización de contratos eléctricos.

    Datos de potencia incluidos:
        - **Picos de demanda**: Registros de potencia máxima por período
        - **Información temporal**: Fechas y horas exactas de los picos
        - **Períodos tarifarios**: Clasificación por franjas horarias (PUNTA/VALLE/LLANO)
        - **Análisis histórico**: Tendencias de consumo de potencia

    Example:
        Optimización de contrato basada en potencias máximas::

            response = client.get_max_power(
                cups="ES001234567890123456AB",
                distributor_code="2",
                date_from="2024/01",
                date_to="2024/12"
            )

            if response.max_power:
                max_peak = max(data.max_power for data in response.max_power)
                print(f"Pico máximo anual: {max_peak/1000:.2f} kW")

                # Recomendar potencia contratada
                recommended_power = max_peak * 1.1  # 10% de margen
                print(f"Potencia recomendada: {recommended_power/1000:.2f} kW")

    :param max_power: Lista de objetos MaxPowerData con registros de potencia máxima
    :type max_power: List[MaxPowerData]
    :param distributor_error: Lista de errores específicos por distribuidor
    :type distributor_error: List[DistributorError]
    """

    max_power: List["MaxPowerData"] = Field(default_factory=list, alias="maxPower")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


class DistributorsResponse(BaseModel):
    """
    Modelo Pydantic para respuesta estructurada del endpoint get-distributors V2.

    Respuesta del endpoint ``get_distributors`` que proporciona información sobre
    distribuidores donde el usuario tiene suministros activos, con manejo robusto
    de errores específicos por distribuidor. Útil para consultas preparatorias
    antes de solicitar datos específicos.

    Información de distribuidores incluida:
        - **Existencia de usuario**: Confirmación de suministros por distribuidor
        - **Códigos de distribuidor**: Identificadores para consultas posteriores
        - **Estado por distribuidor**: Información de disponibilidad de datos

    Example:
        Identificación de distribuidores disponibles::

            response = client.get_distributors()

            print("Distribuidores con datos disponibles:")
            for dist_code, exists in response.dist_existence_user.items():
                if exists:
                    distributor_names = {
                        "1": "Viesgo", "2": "E-distribución", "3": "E-redes",
                        "4": "ASEME", "5": "UFD", "6": "EOSA", "7": "CIDE", "8": "IDE"
                    }
                    name = distributor_names.get(dist_code, f"Distribuidor {dist_code}")
                    print(f"- {name} (código: {dist_code})")

            # Verificar errores específicos
            for error in response.distributor_error:
                print(f"Problema con {error.distributor_name}: {error.error_description}")

    :param dist_existence_user: Diccionario con códigos de distribuidor como claves
                               y valores boolean indicando existencia de datos del usuario
    :type dist_existence_user: dict
    :param distributor_error: Lista de errores específicos por distribuidor
    :type distributor_error: List[DistributorError]
    """

    dist_existence_user: dict = Field(alias="distExistenceUser")
    distributor_error: List[DistributorError] = Field(
        default_factory=list, alias="distributorError"
    )

    model_config = ConfigDict(populate_by_name=True)


from .consumption import ConsumptionData
from .contract import ContractData
from .max_power import MaxPowerData

# Importar modelos específicos para evitar imports circulares
from .supply import SupplyData
