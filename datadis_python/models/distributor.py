"""
Modelos de datos para distribuidoras
"""

from typing import List

from pydantic import BaseModel, Field


class DistributorData(BaseModel):
    """Modelo para datos de distribuidora - simple response from V1"""

    distributor_codes: List[str] = Field(
        alias="distributorCodes", description="Lista de códigos de distribuidoras"
    )

    class Config:
        allow_population_by_field_name = True
