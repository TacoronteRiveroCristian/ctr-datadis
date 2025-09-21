# Architecture Overview

## Client Architecture
The SDK uses a layered client architecture:

### Base Client (`client/base.py`)
- `BaseDatadisClient`: Abstract base class with common functionality
- Handles authentication, token management, and HTTP requests
- Provides abstract methods for API endpoints
- Context manager support for resource cleanup

### Versioned Clients
- **V1 Client** (`client/v1/`): Simple client implementation
  - `SimpleDatadisClientV1`: Concrete implementation of base client
  - Direct API method implementations
- **V2 Client** (`client/v2/`): Future API version support
- **Unified Client** (`client/unified.py`): Abstraction over multiple versions

### Data Models (`models/`)
- **Pydantic Models**: Type-safe data structures for API responses
  - `ConsumptionData`: Energy consumption records
  - `SupplyData`: Supply point information
  - `ContractData`: Contract details with `DateOwner` sub-model
  - `MaxPowerData`: Maximum power demand data
- **Response Wrappers**: API response containers
  - `ConsumptionResponse`, `SuppliesResponse`, etc.
  - `DistributorError`: Error handling for distributor responses

### Exception Hierarchy (`exceptions/`)
```
DatadisError (base)
├── AuthenticationError
├── APIError
└── ValidationError
```

### Utilities (`utils/`)
- **HTTP Utils**: Request/response handling helpers
- **Validators**: Input validation functions
- **Text Utils**: Spanish text normalization (accents, special chars)
- **Constants**: API endpoints, timeouts, retry settings

## Authentication Flow
1. Client initialization with username/password
2. Token request to authentication endpoint
3. Token stored with expiry tracking
4. Automatic token renewal before expiry
5. All API requests include authentication header

## API Integration Pattern
- RESTful API client with automatic authentication
- Retry logic for failed requests
- Response parsing into typed Pydantic models
- Error handling with specific exception types
