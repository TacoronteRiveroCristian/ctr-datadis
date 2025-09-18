"""
Modelos de datos para distribuidoras
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class DistributorData(BaseModel):
    """Modelo para datos de distribuidora - simple response from V1"""

    distributor_codes: List[str] = Field(
        alias="distributorCodes", description="Lista de códigos de distribuidoras"
    )

    model_config = ConfigDict(populate_by_name=True)
