# Pydantic - Project-Specific Patterns

## Standard Configuration
```python
class Config:
    allow_population_by_field_name = True  # CRITICAL for compatibility
```

## Alias Pattern (Recurring)
```python
class ModelData(BaseModel):
    field_name: str = Field(alias="fieldName", description="...")
    another_field: int = Field(alias="anotherField")
```
**Reason**: Datadis API uses camelCase, Python uses snake_case

## Models by Domain

### 1. Supply Models
- **SupplyData**: Basic supply point information
- **ContractData**: Contracts with DateOwner sub-model
- Key fields: `cups`, `distributor_code`, `address`

### 2. Consumption Models
- **ConsumptionData**: Electrical consumption data
- **MaxPowerData**: Maximum demanded power
- **ReactiveData**: Reactive energy (V2 only)

### 3. Response Models
- **ConsumptionResponse**, **SuppliesResponse** for V2
- **DistributorError**: Distributor-specific errors

## Applied Automatic Validation
```python
from ...models.model import ModelData

validated_data = []
for item in raw_data:
    try:
        validated_item = ModelData(**item)
        validated_data.append(validated_item)
    except Exception as e:
        print(f"Error validating: {e}")
        continue  # DON'T fail for one invalid item
```

## TYPE_CHECKING Pattern (Avoid Circular Imports)
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.supply import SupplyData
```

## Automatic Normalization
- **Text normalization**: Applied automatically
- **CUPS uppercase**: Automatic conversion
- **Dates**: datetime → API string conversion
