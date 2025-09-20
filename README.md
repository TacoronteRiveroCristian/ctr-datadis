# ctr-datadis

[![PyPI version](https://badge.fury.io/py/ctr-datadis.svg)](https://badge.fury.io/py/ctr-datadis)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/ctr-datadis/badge/?version=latest)](https://ctr-datadis.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/tu-usuario/datadis/workflows/Tests/badge.svg)](https://github.com/tu-usuario/datadis/actions)

**A comprehensive Python SDK for interacting with the official Datadis API** (Spanish electricity supply data platform).

**Datadis** is the official platform of the Spanish government that provides access to electricity consumption data for Spanish consumers. This SDK makes it easy to access your electricity data programmatically.

## Features

- **Automatic Authentication** - Token-based authentication with automatic renewal
- **Complete API Coverage** - Access to all Datadis API endpoints
- **Type Safety** - Full type hints and Pydantic models for data validation
- **Error Handling** - Comprehensive error handling with custom exceptions
- **Python 3.9+** - Compatible with modern Python versions
- **Text Normalization** - Automatic handling of Spanish accents and special characters
- **Data Models** - Structured data with Pydantic for consumption, supply, and contract data
- **Two API Versions** - Support for both V1 and V2 clients (V2 includes reactive energy data)

## Installation

```bash
pip install ctr-datadis
```

## Quick Start

```python
from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

# Initialize client with your Datadis credentials
client = SimpleDatadisClientV1(username="12345678A", password="your_password")

# Get your supply points
supplies = client.get_supplies()
print(f"Found {len(supplies)} supply points")

# Get consumption data for a specific supply point
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",  # Your CUPS code
    distributor_code="2",           # Your distributor code
    start_date="2024/01",           # Start date (YYYY/MM)
    end_date="2024/02"              # End date (YYYY/MM)
)
print(f"Retrieved {len(consumption)} consumption records")

# For V2 client with reactive energy data
from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

client_v2 = SimpleDatadisClientV2(username="12345678A", password="your_password")
reactive_data = client_v2.get_reactive_data(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01",
    end_date="2024/02"
)
```

## Available Methods

### Supply Information
```python
# Get all supply points
supplies = client.get_supplies()

# Get contract details for a specific CUPS
contract = client.get_contract_detail(cups="ES1234...", distributor_code="2")
```

### Consumption Data
```python
# Get consumption data
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01", 
    end_date="2024/02"
)

# Get maximum power data
max_power = client.get_max_power(
    cups="ES1234000000000001JN0F",
    distributor_code="2", 
    start_date="2024/01",
    end_date="2024/02"
)
```

### Utility Information
```python
# Get available distributors
distributors = client.get_distributors()
```

## Data Models

The SDK includes Pydantic models for type-safe data handling:

- `SupplyData` - Supply point information
- `ConsumptionData` - Energy consumption records
- `ContractData` - Contract details
- `MaxPowerData` - Maximum power demand data

## Error Handling

```python
from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

try:
    supplies = client.get_supplies()
except AuthenticationError:
    print("Invalid credentials")
except APIError as e:
    print(f"API error: {e}")
except DatadisError as e:
    print(f"Datadis error: {e}")
```

## Requirements

- Python 3.9 or higher
- Valid Datadis account credentials
- Internet connection

## API Limitations

- Data is available for the last 2 years only
- Date format must be YYYY/MM (monthly data)
- Rate limiting is enforced by the Datadis platform
- Most operations require a distributor code

## Documentation

- **Complete Documentation**: [https://ctr-datadis.readthedocs.io](https://ctr-datadis.readthedocs.io)
- **API Reference**: Detailed API documentation with examples
- **Examples**: Step-by-step tutorials and use cases
- **Troubleshooting**: Common issues and solutions

## API Versions

| Feature | V1 Client | V2 Client |
|---------|-----------|-----------|
| Consumption Data | ✓ | ✓ |
| Supply Information | ✓ | ✓ |
| Contract Details | ✓ | ✓ |
| Max Power Data | ✓ | ✓ |
| Reactive Energy Data | ✗ | ✓ |

**Recommendation**: Use V1 for basic consumption data, V2 for advanced reactive energy analysis.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial SDK for the Datadis API. It is not affiliated with or endorsed by Datadis or the Spanish government.