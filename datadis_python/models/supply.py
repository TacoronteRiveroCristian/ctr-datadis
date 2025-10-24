"""
Modelos de datos para puntos de suministro.

Este módulo define los modelos de datos para puntos de suministro de energía.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SupplyData(BaseModel):
    r"""
    Modelo Pydantic para datos de puntos de suministro eléctrico españoles.

    Representa la información completa de un punto de suministro (CUPS) registrado
    en el sistema eléctrico español. Cada objeto contiene todos los datos técnicos,
    geográficos y contractuales necesarios para identificar y trabajar con un punto
    de conexión específico a la red eléctrica nacional.

    Información del punto de suministro:
        - **Identificación única**: Código CUPS de 20-22 caracteres
        - **Ubicación física**: Dirección completa, código postal, provincia y municipio
        - **Información técnica**: Tipo de punto de medida y clasificación
        - **Datos del distribuidor**: Empresa responsable de la red en la zona
        - **Período contractual**: Fechas de validez del contrato actual

    Tipos de punto de medida (point_type):
        - **Tipo 1**: Potencia contratada > 450 kW (grandes industrias)
        - **Tipo 2**: 50 kW < Potencia ≤ 450 kW (medianas industrias)
        - **Tipo 3**: 15 kW < Potencia ≤ 50 kW (pequeñas industrias, grandes comercios)
        - **Tipo 4**: 10 kW < Potencia ≤ 15 kW (pequeños comercios, grandes viviendas)
        - **Tipo 5**: Potencia ≤ 10 kW (viviendas domésticas típicas)

    Estructura del código CUPS:
        - **Formato**: ESXXXXXXXXXXXXXXXXXXX
        - **Longitud**: 20-22 caracteres alfanuméricos
        - **Prefijo**: Siempre "ES" para España
        - **Identificador**: Único a nivel nacional
        - **Verificación**: Dígitos de control incluidos

    Distribuidores por zona geográfica:
        - **Viesgo (1)**: Cantabria, Asturias
        - **E-distribución (2)**: Cobertura nacional, mayor distribuidor
        - **E-redes (3)**: Galicia
        - **ASEME (4)**: Melilla (ciudad autónoma)
        - **UFD (5)**: Nacional, especialmente Cataluña y Madrid
        - **EOSA (6)**: Aragón
        - **CIDE (7)**: Ceuta (ciudad autónoma)
        - **IDE (8)**: Islas Baleares

    Example:
        Análisis básico de un punto de suministro::

            from datadis_python.models.supply import SupplyData

            # Punto de suministro doméstico típico
            supply_home = SupplyData(
                address="Calle Mayor 123, 1º A",
                cups="ES001234567890123456AB",
                postalCode="28001",
                province="Madrid",
                municipality="Madrid",
                distributor="E-distribución",
                validDateFrom="2023/01/15",
                validDateTo=None,  # Contrato activo
                pointType=5,  # Doméstico
                distributorCode="2"  # E-distribución
            )

            print(f"CUPS: {supply_home.cups}")
            print(f"Ubicación: {supply_home.address}")
            print(f"Zona: {supply_home.municipality}, {supply_home.province}")
            print(f"Distribuidor: {supply_home.distributor}")

            # Determinar tipo de instalación
            point_types = {
                1: "Gran industria (>450 kW)",
                2: "Mediana industria (50-450 kW)",
                3: "Pequeña industria (15-50 kW)",
                4: "Comercio/gran vivienda (10-15 kW)",
                5: "Vivienda doméstica (≤10 kW)"
            }

            print(f"Tipo: {point_types.get(supply_home.point_type, 'Desconocido')}")

        Análisis de vigencia contractual::

            from datetime import datetime

            def analyze_contract_validity(supply: SupplyData) -> str:
                \"\"\"Analiza el estado del contrato del suministro.\"\"\"

                if supply.valid_date_to is None:
                    return "✅ Contrato activo (sin fecha de fin)"

                # Parsear fecha de fin (formato YYYY/MM/DD)
                try:
                    end_date = datetime.strptime(supply.valid_date_to, "%Y/%m/%d")
                    current_date = datetime.now()

                    if end_date > current_date:
                        days_remaining = (end_date - current_date).days
                        return f"✅ Contrato activo ({days_remaining} días restantes)"
                    else:
                        return "❌ Contrato expirado"
                except ValueError:
                    return "⚠️ Fecha de fin inválida"

            # Usar la función
            status = analyze_contract_validity(supply_home)
            print(f"Estado contractual: {status}")

        Agrupación por distribuidor::

            # Lista de suministros de un usuario
            supplies = [
                SupplyData(
                    address="Calle A", cups="ES0012...", postalCode="28001",
                    province="Madrid", municipality="Madrid", distributor="E-distribución",
                    validDateFrom="2023/01/01", pointType=5, distributorCode="2"
                ),
                SupplyData(
                    address="Calle B", cups="ES0034...", postalCode="08001",
                    province="Barcelona", municipality="Barcelona", distributor="UFD",
                    validDateFrom="2022/06/15", pointType=4, distributorCode="5"
                )
            ]

            # Agrupar por distribuidor
            by_distributor = {}
            for supply in supplies:
                dist_name = supply.distributor
                if dist_name not in by_distributor:
                    by_distributor[dist_name] = []
                by_distributor[dist_name].append(supply)

            print("Suministros por distribuidor:")
            for distributor, supply_list in by_distributor.items():
                print(f"- {distributor}: {len(supply_list)} suministros")
                for supply in supply_list:
                    print(f"  * {supply.municipality} ({supply.cups[:8]}...)")

        Validación de código CUPS::

            def validate_cups_format(cups: str) -> bool:
                \"\"\"Valida formato básico del código CUPS español.\"\"\"

                # Verificaciones básicas
                if not cups.startswith("ES"):
                    return False
                if len(cups) < 20 or len(cups) > 22:
                    return False
                if not cups[2:].isalnum():
                    return False

                return True

            # Validar CUPS
            if validate_cups_format(supply_home.cups):
                print("✅ Formato CUPS válido")
            else:
                print("❌ Formato CUPS inválido")

        Análisis geográfico::

            # Identificar región por distribuidor
            regions = {
                "1": "Norte (Cantabria/Asturias)",
                "2": "Nacional (E-distribución)",
                "3": "Galicia",
                "4": "Melilla",
                "5": "Nacional (UFD)",
                "6": "Aragón",
                "7": "Ceuta",
                "8": "Baleares"
            }

            region = regions.get(supply_home.distributor_code, "Región desconocida")
            print(f"Región de distribución: {region}")

    :param address: Dirección física completa del punto de suministro. Incluye calle,
                   número, piso/puerta si aplica. Corresponde a la ubicación real
                   donde se encuentra la instalación eléctrica
    :type address: str
    :param cups: Código CUPS (Código Único del Punto de Suministro). Identificador
                alfanumérico único de 20-22 caracteres que identifica inequívocamente
                el punto de conexión a la red eléctrica española
    :type cups: str
    :param postal_code: Código postal de la dirección del suministro. Código numérico
                       de 5 dígitos que identifica la zona postal española
    :type postal_code: str
    :param province: Provincia española donde se ubica el punto de suministro.
                    Corresponde a la división administrativa de primer nivel
    :type province: str
    :param municipality: Municipio donde se encuentra el suministro eléctrico.
                        División administrativa local dentro de la provincia
    :type municipality: str
    :param distributor: Nombre comercial de la empresa distribuidora responsable
                       de la red eléctrica en la zona geográfica del suministro
    :type distributor: str
    :param valid_date_from: Fecha de inicio de validez del contrato actual en formato
                           YYYY/MM/DD. Marca el comienzo del período contractual vigente
    :type valid_date_from: str
    :param valid_date_to: Fecha de finalización del contrato en formato YYYY/MM/DD.
                         None para contratos sin fecha de fin definida (más común)
    :type valid_date_to: Optional[str]
    :param point_type: Tipo de punto de medida según clasificación técnica española.
                      Entero del 1 al 5 que determina el tipo de instalación y medición
    :type point_type: int
    :param distributor_code: Código numérico del distribuidor (1-8). Identificador
                           único usado en las consultas API para el distribuidor específico
    :type distributor_code: str

    :raises ValidationError: Si algún campo obligatorio falta o tiene formato incorrecto

    .. note::
       El ``point_type`` determina el tipo de contador y sistema de medición.
       Los tipos 1-3 suelen tener medición cuarto-horaria, los tipos 4-5 horaria.

    .. tip::
       Use el ``distributor_code`` para consultas posteriores de consumo, contratos
       y otros datos específicos del punto de suministro.

    .. seealso::
       - :class:`SuppliesResponse` - Respuesta estructurada de la API V2 que contiene estos datos
       - :meth:`SimpleDatadisClientV1.get_supplies` - Obtener puntos de suministro V1
       - :meth:`SimpleDatadisClientV2.get_supplies` - Obtener puntos de suministro V2
       - Códigos CUPS oficiales en la documentación del sistema eléctrico español

    .. versionadded:: 1.0
       Modelo base para puntos de suministro del sistema eléctrico español
    """

    address: str = Field(description="Dirección del suministro")
    cups: str = Field(description="Código CUPS del punto de suministro")
    postal_code: str = Field(alias="postalCode", description="Código postal")
    province: str = Field(description="Provincia")
    municipality: str = Field(description="Municipio")
    distributor: str = Field(description="Nombre de la distribuidora")
    valid_date_from: str = Field(
        alias="validDateFrom", description="Fecha de inicio del contrato (YYYY/MM/DD)"
    )
    valid_date_to: Optional[str] = Field(
        default=None,
        alias="validDateTo",
        description="Fecha de fin del contrato (YYYY/MM/DD)",
    )
    point_type: int = Field(
        alias="pointType", description="Tipo de punto de medida (1, 2, 3, 4 o 5)"
    )
    distributor_code: str = Field(
        alias="distributorCode", description="Código de distribuidora"
    )

    model_config = ConfigDict(populate_by_name=True)
