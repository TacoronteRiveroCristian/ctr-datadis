"""
Modelos de datos para distribuidoras.

Este módulo define los modelos de datos para información de distribuidoras.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class DistributorData(BaseModel):
    """
    Modelo Pydantic para datos de distribuidoras eléctricas españolas.

    Representa la información de las empresas distribuidoras de energía eléctrica
    donde el usuario tiene puntos de suministro activos. Las distribuidoras son
    las empresas responsables del mantenimiento y operación de las redes eléctricas
    en España, y cada zona geográfica está asignada a una distribuidora específica.

    Sistema eléctrico español:
        Las distribuidoras están reguladas por la CNMC (Comisión Nacional de los
        Mercados y la Competencia) y tienen asignadas zonas geográficas exclusivas
        donde son responsables de la red de distribución eléctrica.

    Distribuidoras principales en España:
        - **Código "1"**: **Viesgo** - Cantabria, Asturias
        - **Código "2"**: **E-distribución (Endesa)** - Nacional (mayor cobertura)
        - **Código "3"**: **E-redes** - Galicia
        - **Código "4"**: **ASEME** - Melilla
        - **Código "5"**: **UFD (Naturgy)** - Nacional, especialmente Cataluña, Madrid
        - **Código "6"**: **EOSA** - Aragón
        - **Código "7"**: **CIDE** - Ceuta
        - **Código "8"**: **IDE (Redeia)** - Islas Baleares

    Diferencia con comercializadoras:
        - **Distribuidoras**: Mantienen y operan la red física (cables, transformadores)
        - **Comercializadoras**: Venden la energía y emiten facturas al usuario final

    Example:
        Uso básico del modelo::

            from datadis_python.models.distributor import DistributorData

            # Datos típicos de respuesta V1
            distributor_data = DistributorData(
                distributorCodes=["2", "5"]  # E-distribución y UFD
            )

            print("Distribuidoras donde tienes suministros:")
            for code in distributor_data.distributor_codes:
                distributor_name = {
                    "1": "Viesgo",
                    "2": "E-distribución (Endesa)",
                    "3": "E-redes",
                    "4": "ASEME",
                    "5": "UFD (Naturgy)",
                    "6": "EOSA",
                    "7": "CIDE",
                    "8": "IDE (Redeia)"
                }.get(code, f"Distribuidor {code}")

                print(f"- Código {code}: {distributor_name}")

        Uso con clientes V1::

            from datadis_python.client.v1 import SimpleDatadisClientV1

            with SimpleDatadisClientV1("12345678A", "password") as client:
                # Obtener distribuidoras donde el usuario tiene suministros
                distributors = client.get_distributors()

                print(f"Distribuidoras encontradas: {len(distributors)}")
                for dist in distributors:
                    print(f"Códigos: {dist.distributor_codes}")

                # Usar el primer código para consultas posteriores
                if distributors and distributors[0].distributor_codes:
                    first_code = distributors[0].distributor_codes[0]
                    supplies = client.get_supplies(distributor_code=first_code)

        Filtrado por zona geográfica::

            # Ejemplo: usuario con suministros en múltiples zonas
            multi_zone_data = DistributorData(
                distributorCodes=["2", "5", "8"]  # Endesa, Naturgy, Baleares
            )

            # Identificar regiones
            regions = {
                "2": "Península (Endesa)",
                "5": "Cataluña/Madrid (Naturgy)",
                "8": "Islas Baleares (IDE)"
            }

            for code in multi_zone_data.distributor_codes:
                print(f"Suministros en: {regions.get(code, 'Región desconocida')}")

    :param distributor_codes: Lista de códigos de distribuidoras donde el usuario
                             tiene puntos de suministro activos. Cada código identifica
                             una empresa distribuidora específica del sistema eléctrico español
    :type distributor_codes: List[str]

    :raises ValidationError: Si la lista está vacía o contiene valores no válidos

    .. note::
       Este modelo representa la respuesta simplificada de la API V1. La API V2
       utiliza modelos más complejos con información extendida de cada distribuidor.

    .. seealso::
       - :class:`DistributorsResponse` - Respuesta estructurada de la API V2
       - :meth:`SimpleDatadisClientV1.get_distributors` - Obtener distribuidoras V1
       - :meth:`SimpleDatadisClientV2.get_distributors` - Obtener distribuidoras V2
       - Los códigos obtenidos se usan en métodos de consulta específicos

    .. versionadded:: 1.0
       Soporte para códigos de distribuidor en API V1
    """

    distributor_codes: List[str] = Field(
        alias="distributorCodes", description="Lista de códigos de distribuidoras"
    )

    model_config = ConfigDict(populate_by_name=True)
