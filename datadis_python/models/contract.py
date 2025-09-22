"""
Modelos de datos para contratos.

Este módulo define los modelos de datos para contratos y información relacionada.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DateOwner(BaseModel):
    """
    Modelo Pydantic para períodos de propiedad de un punto de suministro.

    Representa un período temporal durante el cual el usuario autenticado ha sido
    propietario o titular de un punto de suministro (CUPS). Esta información es
    especialmente relevante para consultas históricas y para entender los períodos
    de responsabilidad sobre un contrato eléctrico.

    Casos de uso comunes:
        - **Cambios de propiedad**: Transferencias de titularidad entre personas
        - **Alquileres**: Períodos como inquilino vs. propietario
        - **Herencias**: Cambios de titularidad por herencia
        - **Compraventa**: Traspaso en ventas de inmuebles

    Example:
        Período de propiedad típico::

            from datadis_python.models.contract import DateOwner

            # Período como propietario
            ownership = DateOwner(
                startDate="2020/01/15",
                endDate="2024/06/30"
            )

            print(f"Propietario desde: {ownership.start_date}")
            print(f"Hasta: {ownership.end_date}")

        Múltiples períodos (en contexto de ContractData)::

            # Usuario fue propietario en dos períodos diferentes
            periods = [
                DateOwner(startDate="2018/03/01", endDate="2019/12/31"),
                DateOwner(startDate="2022/06/01", endDate="2024/08/15")
            ]

            for i, period in enumerate(periods, 1):
                print(f"Período {i}: {period.start_date} - {period.end_date}")

    :param start_date: Fecha de inicio del período de propiedad en formato YYYY/MM/DD.
                      Fecha desde la cual el usuario es considerado propietario o titular
                      del punto de suministro eléctrico
    :type start_date: str
    :param end_date: Fecha de finalización del período de propiedad en formato YYYY/MM/DD.
                    Fecha hasta la cual el usuario mantuvo la titularidad del suministro
    :type end_date: str

    :raises ValidationError: Si las fechas no tienen formato válido o faltan campos obligatorios

    .. note::
       Las fechas deben seguir el formato estándar de Datadis: YYYY/MM/DD (año/mes/día)

    .. seealso::
       - :class:`ContractData` - Modelo que incluye lista de períodos de propiedad
       - :meth:`SimpleDatadisClientV2.get_contract_detail` - Obtener información contractual completa
    """

    start_date: str = Field(alias="startDate", description="Fecha de inicio propiedad")
    end_date: str = Field(alias="endDate", description="Fecha de fin propiedad")

    model_config = ConfigDict(populate_by_name=True)


class ContractData(BaseModel):
    """
    Modelo Pydantic completo para datos contractuales de suministros eléctricos.

    Representa la información contractual completa de un punto de suministro (CUPS),
    incluyendo datos técnicos, comerciales, tarifarios y de autoconsumo. Este modelo
    contiene toda la información relevante sobre el contrato eléctrico asociado a
    una instalación, desde datos básicos hasta configuraciones avanzadas de autoconsumo.

    Información contractual incluida:
        - **Datos básicos**: CUPS, distribuidor, comercializadora, ubicación
        - **Información técnica**: Tensión, potencias contratadas, control de potencia
        - **Datos tarifarios**: Tarifa de acceso, discriminación horaria, códigos CNMC
        - **Autoconsumo**: Tipo, configuración, coeficientes, CAU
        - **Histórico**: Períodos de propiedad, cambios de comercializadora

    Tipos de instalaciones soportadas:
        - **Consumo tradicional**: Sin generación propia
        - **Autoconsumo individual**: Instalación fotovoltaica privada
        - **Autoconsumo colectivo**: Instalaciones compartidas entre varios usuarios
        - **Autoconsumo con excedentes**: Venta de energía sobrante a la red
        - **Autoconsumo sin excedentes**: Generación solo para consumo propio

    Códigos de tarifa de acceso (CNMC):
        - **2.0TD**: Baja tensión ≤ 15 kW (doméstico típico)
        - **3.0TD**: Baja tensión > 15 kW ≤ 100 kW (comercios, pequeña industria)
        - **6.1TD**: Alta tensión 1-36 kV (gran industria)
        - **6.2TD**: Alta tensión 36-72.5 kV
        - **6.3TD**: Alta tensión 72.5-145 kV
        - **6.4TD**: Alta tensión ≥ 145 kV

    Example:
        Contrato doméstico básico sin autoconsumo::

            from datadis_python.models.contract import ContractData

            # Vivienda típica con tarifa 2.0TD
            contract_home = ContractData(
                cups="ES001234567890123456AB",
                distributor="E-distribución",
                marketer="Iberdrola",
                tension="BT",
                accessFare="2.0TD (Peaje de acceso 2.0TD)",
                province="Madrid",
                municipality="Madrid",
                postalCode="28001",
                contractedPowerkW=[5.75],  # 5.75 kW contratados
                timeDiscrimination="DHA",   # Discriminación horaria
                modePowerControl="ICP",     # Interruptor Control Potencia
                startDate="2023/01/15",
                codeFare="2.0TD"
            )

            print(f"Potencia contratada: {contract_home.contracted_power_kw[0]} kW")
            print(f"Tarifa: {contract_home.code_fare}")

        Instalación con autoconsumo fotovoltaico::

            from datadis_python.models.contract import ContractData, DateOwner

            # Casa con paneles solares y autoconsumo
            contract_solar = ContractData(
                cups="ES001234567890123456AB",
                distributor="UFD",
                marketer="Naturgy",
                tension="BT",
                accessFare="2.0TD con autoconsumo",
                province="Valencia",
                municipality="Valencia",
                postalCode="46001",
                contractedPowerkW=[4.60],
                modePowerControl="ICP",
                startDate="2022/03/01",
                codeFare="2.0TD",
                # Configuración de autoconsumo
                selfConsumptionTypeCode="41",
                selfConsumptionTypeDesc="Autoconsumo con excedentes acogido a compensación",
                installedCapacityKW=5.0,  # 5 kW de paneles solares
                cau="ES00123456789",      # Código de Autoconsumo Único
                dateOwner=[
                    DateOwner(startDate="2022/03/01", endDate="2024/12/31")
                ]
            )

            print(f"Tipo autoconsumo: {contract_solar.self_consumption_type_desc}")
            print(f"Potencia instalada: {contract_solar.installed_capacity_kw} kW")

        Autoconsumo colectivo con coeficiente de reparto::

            # Instalación compartida en comunidad de vecinos
            contract_collective = ContractData(
                cups="ES001234567890123456AB",
                distributor="E-distribución",
                tension="BT",
                accessFare="2.0TD autoconsumo colectivo",
                province="Barcelona",
                municipality="Barcelona",
                postalCode="08001",
                contractedPowerkW=[3.45],
                codeFare="2.0TD",
                selfConsumptionTypeCode="43",
                selfConsumptionTypeDesc="Autoconsumo colectivo con excedentes",
                partitionCoefficient=0.15,  # 15% del total generado
                cau="ES00987654321",
                installedCapacityKW=20.0,    # Instalación total compartida
                startDate="2023/06/01"
            )

            print(f"Coeficiente de reparto: {contract_collective.partition_coefficient}")

    :param cups: Código CUPS del punto de suministro. Identificador único nacional
                de 20-22 caracteres que identifica inequívocamente el punto de conexión
    :type cups: str
    :param distributor: Nombre de la empresa distribuidora responsable de la red
                       en la zona geográfica del suministro
    :type distributor: str
    :param marketer: Empresa comercializadora que factura la energía. Solo visible
                    si el usuario autenticado es propietario del CUPS
    :type marketer: Optional[str]
    :param tension: Nivel de tensión del suministro. Valores típicos: "BT" (Baja Tensión),
                   "AT" (Alta Tensión), "MT" (Media Tensión)
    :type tension: str
    :param access_fare: Descripción completa de la tarifa de acceso aplicable.
                       Incluye el código y descripción extendida
    :type access_fare: str
    :param province: Provincia donde se ubica físicamente el punto de suministro
    :type province: str
    :param municipality: Municipio de ubicación del suministro eléctrico
    :type municipality: str
    :param postal_code: Código postal de la dirección del punto de suministro
    :type postal_code: str
    :param contracted_power_kw: Lista de potencias contratadas en kW por período tarifario.
                               Para tarifas simples: un valor. Para discriminación horaria: múltiples valores
    :type contracted_power_kw: List[float]
    :param time_discrimination: Tipo de discriminación horaria aplicada. Valores típicos:
                               "DHA" (Discriminación Horaria), "DHS" (Supervalle), None (tarifa simple)
    :type time_discrimination: Optional[str]
    :param mode_power_control: Sistema de control de la potencia contratada.
                              "ICP" (Interruptor Control Potencia) o "Maxímetro"
    :type mode_power_control: str
    :param start_date: Fecha de inicio de vigencia del contrato en formato YYYY/MM/DD
    :type start_date: str
    :param end_date: Fecha de finalización del contrato. None para contratos activos
    :type end_date: Optional[str]
    :param code_fare: Código oficial de la tarifa de acceso según clasificación CNMC.
                     Define la estructura tarifaria aplicable
    :type code_fare: str
    :param self_consumption_type_code: Código numérico del tipo de autoconsumo según RD 244/2019.
                                      Códigos 4X para diferentes modalidades de autoconsumo
    :type self_consumption_type_code: Optional[str]
    :param self_consumption_type_desc: Descripción detallada del tipo de autoconsumo configurado.
                                      Especifica modalidad, excedentes y acogimiento a compensación
    :type self_consumption_type_desc: Optional[str]
    :param section: Clasificación de sección para autoconsumo según normativa vigente
    :type section: Optional[str]
    :param subsection: Subclasificación específica dentro de la sección de autoconsumo
    :type subsection: Optional[str]
    :param partition_coefficient: Coeficiente de reparto para autoconsumo colectivo.
                                 Porcentaje de la energía generada asignado a este CUPS (0.0-1.0)
    :type partition_coefficient: Optional[float]
    :param cau: Código de Autoconsumo Único. Identificador oficial de la instalación
               de autoconsumo asignado por la administración competente
    :type cau: Optional[str]
    :param installed_capacity_kw: Potencia pico instalada de generación renovable en kW.
                                 Suma de toda la capacidad de generación asociada al autoconsumo
    :type installed_capacity_kw: Optional[float]
    :param date_owner: Lista de períodos durante los cuales el usuario autenticado
                      ha sido propietario del punto de suministro
    :type date_owner: Optional[List[DateOwner]]
    :param last_marketer_date: Fecha del último cambio de empresa comercializadora
                              en formato YYYY/MM/DD
    :type last_marketer_date: Optional[str]
    :param max_power_install: Potencia máxima de la instalación eléctrica en formato texto.
                             Puede incluir información adicional sobre limitaciones técnicas
    :type max_power_install: Optional[str]

    :raises ValidationError: Si algún campo obligatorio está ausente o tiene formato incorrecto

    .. note::
       Para autoconsumo colectivo, el ``partition_coefficient`` debe sumar 1.0 entre
       todos los participantes de la instalación compartida.

    .. seealso::
       - :class:`DateOwner` - Modelo para períodos de propiedad
       - :class:`ContractResponse` - Respuesta estructurada de la API V2
       - :meth:`SimpleDatadisClientV2.get_contract_detail` - Obtener datos contractuales
       - RD 244/2019 para códigos de autoconsumo oficiales

    .. versionadded:: 2.0
       Soporte completo para autoconsumo y datos contractuales extendidos
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
