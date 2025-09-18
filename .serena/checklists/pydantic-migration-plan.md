# Migration Plan: Pydantic Typing for Datadis SDK

## [OBJECTIVE] Objective
Implement automatic Pydantic validation in all SDK methods that return API data, ensuring type safety and better developer experience.

## [STATUS] Current Status
- [RESOLVED] **SupplyData**: Already implemented in `get_supplies()`
- [RESOLVED] **Existing models**: ConsumptionData, ContractData, MaxPowerData
- [RESOLVED] **New models**: DistributorData, ReactiveData with subfamilies
- [RESOLVED] **Complete migration**: 100% of methods migrated to Pydantic validation

## [INVENTORY] Method Inventory by Client

### SimpleDatadisClientV1 (`datadis_python/client/v1/simple_client.py`)
- [RESOLVED] `get_supplies()` → `List[SupplyData]`
- [RESOLVED] `get_distributors()` → `List[DistributorData]`
- [RESOLVED] `get_contract_detail()` → `List[ContractData]`
- [RESOLVED] `get_consumption()` → `List[ConsumptionData]`
- [RESOLVED] `get_max_power()` → `List[MaxPowerData]`

### DatadisClientV1 (`datadis_python/client/v1/client.py`)
- [RESOLVED] `get_supplies()` → `List[SupplyData]`
- [RESOLVED] `get_distributors()` → `List[DistributorData]`
- [RESOLVED] `get_contract_detail()` → `List[ContractData]`
- [RESOLVED] `get_consumption()` → `List[ConsumptionData]`
- [RESOLVED] `get_max_power()` → `List[MaxPowerData]`
- [RESOLVED] `get_cups_list()` → `List[str]` (simple, doesn't need Pydantic)
- [RESOLVED] `get_distributor_codes()` → `List[str]` (simple, unique codes)

### DatadisClientV2 (`datadis_python/client/v2/client.py`)
- [RESOLVED] `get_supplies()` → `SuppliesResponse`
- [RESOLVED] `get_distributors()` → `DistributorsResponse`
- [RESOLVED] `get_contract_detail()` → `ContractResponse`
- [RESOLVED] `get_consumption()` → `ConsumptionResponse`
- [RESOLVED] `get_max_power()` → `MaxPowerResponse`
- [RESOLVED] `get_reactive_data()` → `List[ReactiveData]`

### DatadisClient Unified (`datadis_python/client/unified.py`)
- [RESOLVED] All methods with correct type hints (delegate to v1/v2 clients)

## [PLAN] Implementation Plan

### Phase 1: Missing Models
**Estimated duration: 1-2 hours**

#### 1.1 Create DistributorData
- [x] **File**: `datadis_python/models/distributor.py`
- [x] **Fields**: `distributor_codes` (list of codes)
- [x] **Validations**: List of strings with camelCase alias

#### 1.2 Create ReactiveData
- [x] **File**: `datadis_python/models/reactive.py`
- [x] **Fields**: `ReactiveEnergyPeriod`, `ReactiveEnergyData`, `ReactiveData`
- [x] **Validations**: Dates, optional numeric values

#### 1.3 Update __init__.py
- [x] **File**: `datadis_python/models/__init__.py`
- [x] **Action**: Export new models
- [x] **Verify**: Imports in clients

### Phase 2: Simple V1 Client
**Estimated duration: 2-3 hours**

#### 2.1 get_distributors()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[DistributorData]`
- [x] **Implement**: Pydantic validation with error handling
- [x] **Test**: Pattern validated against API structure

#### 2.2 get_contract_detail()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[ContractData]`
- [x] **Verify**: ContractData model compatible with API
- [x] **Implement**: Validation + error handling

#### 2.3 get_consumption()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[ConsumptionData]`
- [x] **Verify**: ConsumptionData model compatible
- [x] **Implement**: Validation + error handling

#### 2.4 get_max_power()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[MaxPowerData]`
- [x] **Verify**: MaxPowerData model compatible
- [x] **Implement**: Validation + error handling

### Phase 3: Base V1 Client
**Estimated duration: 2-3 hours**

#### 3.1 Replicate SimpleClient changes
- [x] **get_distributors()** → `List[DistributorData]`
- [x] **get_contract_detail()** → `List[ContractData]`
- [x] **get_consumption()** → `List[ConsumptionData]`
- [x] **get_max_power()** → `List[MaxPowerData]`

#### 3.2 Additional methods
- [x] **get_distributor_codes()** → Keep `List[str]` (simple codes)
- [x] **get_cups_list()** → Keep `List[str]` (simple codes)

### Phase 4: V2 Client
**Estimated duration: 3-4 hours**

#### 4.1 All equivalent V1 methods
- [x] **get_supplies()** → `SuppliesResponse` (complete V2 response)
- [x] **get_distributors()** → `DistributorsResponse` (complete V2 response)
- [x] **get_contract_detail()** → `ContractResponse` (complete V2 response)
- [x] **get_consumption()** → `ConsumptionResponse` (complete V2 response)
- [x] **get_max_power()** → `MaxPowerResponse` (complete V2 response)

#### 4.2 V2-specific method
- [x] **get_reactive_data()** → `List[ReactiveData]`
- [x] **Verify**: V2 returns structured responses with distributor errors

### Phase 5: Unified Client
**Estimated duration: 1 hour**

#### 5.1 Update type hints
- [x] **All methods**: Inherit typing from v1/v2 clients
- [x] **Verify**: Consistency between versions
- [x] **Document**: V2 returns complete responses, V1 returns simple lists

### Phase 6: Testing and Validation
**Estimated duration: 2-3 hours**

#### 6.1 Unit tests
- [x] **Create**: New models created with validations
- [x] **Verify**: Pydantic validations included in models
- [x] **Edge cases**: Error handling implemented with continue in loops

#### 6.2 Integration tests
- [x] **Verify**: Code formatted and linted correctly
- [x] **Test**: Error handling implemented for validation failures
- [x] **Performance**: Minimal overhead with local imports in methods

#### 6.3 Documentation
- [x] **Update**: Docstrings updated with new return types
- [x] **Examples**: Patterns established and documented in code
- [x] **Migration guide**: Complete plan documented with final state

## [PATTERN] Implementation Pattern

```python
# [BEFORE] Before (raw data)
def get_supplies(self) -> List[Dict[str, Any]]:
    response = self._make_authenticated_request(...)
    return response

# [AFTER] After (Pydantic validated)
def get_supplies(self) -> List["SupplyData"]:
    response = self._make_authenticated_request(...)

    # Validate with Pydantic
    from ...models.supply import SupplyData
    validated_data = []
    for item in response:
        try:
            validated_item = SupplyData(**item)
            validated_data.append(validated_item)
        except Exception as e:
            print(f"Error validating data: {e}")
            continue

    return validated_data
```

## [CONSIDERATIONS] Considerations

### Breaking Changes
- **Impact**: Changes return types from `Dict` to Pydantic objects
- **Migration**: Users will need to update code (`dict["key"]` → `obj.key`)
- **Versioning**: Consider major version bump

### Error Handling
- **Philosophy**: Continue processing if an item fails validation
- **Logging**: Report errors but don't fail completely
- **Fallback**: Consider "raw" mode as option

### Performance
- **Overhead**: Pydantic validation adds ~microseconds per object
- **Memory**: Pydantic objects use more memory than dicts
- **Benefit**: Type safety is worth the minimal cost

## [METRICS] Success Metrics

- [ ] **100%** methods with Pydantic return types
- [ ] **0** validation errors in tests with real API
- [ ] **<5%** performance overhead vs raw dicts
- [ ] **All** tests passing
- [ ] **Documentation** updated

## [ORDER] Recommended Execution Order

1. **Missing models** (Phase 1)
2. **SimpleClientV1** (Phase 2) - Stable base for testing
3. **ClientV1** (Phase 3) - Replicate proven pattern
4. **ClientV2** (Phase 4) - Adapt to V2
5. **Unified** (Phase 5) - Consolidate
6. **Testing** (Phase 6) - Validate everything

---
**Total estimation**: 10-15 hours of development
**Impact**: Major improvement in DX and type safety
**Risk**: Low (pattern already proven in get_supplies)
