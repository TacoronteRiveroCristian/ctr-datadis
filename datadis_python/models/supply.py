"""
Modelos de datos para puntos de suministro
"""

from typing import Optional

from pydantic import BaseModel, Field


class SupplyData(BaseModel):
    """Modelo para datos de punto de suministro"""

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

    class Config:
        allow_population_by_field_name = True
