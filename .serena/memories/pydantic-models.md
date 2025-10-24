# Pydantic Models

## Main Models
- **SupplyData** (`models/supply.py`) - Supply points
- **ConsumptionData** (`models/consumption.py`) - Consumption data
- **ContractData** (`models/contract.py`) - Contracts with DateOwner
- **MaxPowerData** (`models/max_power.py`) - Maximum power
- **DistributorData** (`models/distributor.py`) - Distributors
- **ReactiveData** (`models/reactive.py`) - Reactive energy

## Response Wrappers
- **ConsumptionResponse**, **SuppliesResponse**, etc. in `models/responses.py`
- **DistributorError** for distributor error handling

## Features
- Automatic validation with Pydantic v2
- Field aliases (snake_case ↔ camelCase)
- Automatic Spanish text normalization
- Complete type hints

## Important Configuration
```python
class Config:
    allow_population_by_field_name = True  # Alias compatibility
```
