# Architecture and Code Structure

## Package Structure
```
datadis_python/
├── __init__.py          # Package exports and version
├── client/              # Main client implementation
├── models/              # Pydantic data models
├── exceptions/          # Custom exception classes
└── utils/               # Utility functions
```

## Key Components

### Client Architecture
- **DatadisClient**: Main entry point for SDK
- **Authentication**: Automatic token management with renewal
- **HTTP Layer**: Built on requests library with retry logic
- **Rate Limiting**: Built-in handling for API rate limits

### Data Models (Pydantic)
- **SupplyData**: Supply point information
- **ContractData**: Contract details  
- **ConsumptionData**: Energy consumption records
- **MaxPowerData**: Maximum power demand records
- All models provide type safety and validation

### Exception Hierarchy
```
DatadisError (base)
├── AuthenticationError
├── APIError
└── ValidationError
```

### API Endpoint Coverage
- Authentication endpoints
- Distributor information
- Supply point data
- Contract details
- Consumption data (hourly/quarter-hourly)
- Maximum power demand

## Design Patterns
- **Client Pattern**: Single client class for all operations
- **Model Validation**: Pydantic for automatic data validation
- **Exception Chaining**: Specific exceptions for different error types
- **Retry Logic**: Built-in retry mechanism for transient failures

## External Dependencies
- **requests**: HTTP client
- **pydantic**: Data validation and models
- **python-dateutil**: Date parsing utilities
- **typing-extensions**: Backport typing features for Python < 3.10

## Development Dependencies
- **pytest ecosystem**: Testing framework with coverage and mocking
- **Code quality**: black, isort, flake8, mypy
- **Documentation**: Sphinx with RTD theme
- **Pre-commit**: Automated quality checks