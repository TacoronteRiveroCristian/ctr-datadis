"""
Modelos de datos para puntos de suministro.

Este módulo define los modelos de datos para puntos de suministro de energía.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SupplyData(BaseModel):
    """
    Modelo para datos de punto de suministro.

    :param address: Dirección del suministro
    :type address: str
    :param cups: Código CUPS del punto de suministro
    :type cups: str
    :param postal_code: Código postal
    :type postal_code: str
    :param province: Provincia
    :type province: str
    :param municipality: Municipio
    :type municipality: str
    :param distributor: Nombre de la distribuidora
    :type distributor: str
    :param valid_date_from: Fecha de inicio del contrato (YYYY/MM/DD)
    :type valid_date_from: str
    :param valid_date_to: Fecha de fin del contrato (YYYY/MM/DD)
    :type valid_date_to: Optional[str]
    :param point_type: Tipo de punto de medida (1, 2, 3, 4 o 5)
    :type point_type: int
    :param distributor_code: Código de distribuidora
    :type distributor_code: str
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
