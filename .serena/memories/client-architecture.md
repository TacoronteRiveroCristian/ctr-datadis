# Client Architecture

## Client Hierarchy
1. **BaseDatadisClient** (`client/base.py`) - Abstract base class
2. **SimpleDatadisClientV1** (`client/v1/simple_client.py`) - Main client
3. **DatadisClientV1** (`client/v1/client.py`) - Standard V1 client
4. **DatadisClientV2** (`client/v2/client.py`) - V2 client (future)
5. **UnifiedDatadisClient** (`client/unified.py`) - Multi-version abstraction

## Recommended Client: SimpleDatadisClientV1
Main methods:
- `authenticate()` - Automatic authentication
- `get_supplies()` - Get supply points
- `get_consumption()` - Consumption data
- `get_contract_detail()` - Contract details
- `get_max_power()` - Maximum power
- `get_distributors()` - Distributors

## Authentication Flow
1. Initialization with username/password
2. Token request to login endpoint
3. Storage with expiry timestamp
4. Automatic token renewal before expiry
5. Authentication headers in all requests
