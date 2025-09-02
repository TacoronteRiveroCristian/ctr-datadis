# Datadis Python SDK

A comprehensive Python SDK for interacting with the official Datadis API (Distribuidora de Información de Suministros de España).

[![PyPI version](https://badge.fury.io/py/datadis-python.svg)](https://badge.fury.io/py/datadis-python)
[![Python](https://img.shields.io/pypi/pyversions/datadis-python.svg)](https://pypi.org/project/datadis-python/)
[![Documentation Status](https://readthedocs.org/projects/datadis-python/badge/?version=latest)](https://datadis-python.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Datadis is the official Spanish platform that provides electricity supply data access. This SDK provides a simple and robust interface to interact with the Datadis API v2, allowing developers to retrieve consumption data, contract information, supply points, and more.

## Features

- **Automatic Authentication**: Token-based authentication with automatic renewal
- **Complete API Coverage**: Access to all Datadis API v2 endpoints
- **Type Safety**: Full type hints and Pydantic models for data validation
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Rate Limiting**: Built-in retry logic and rate limit handling
- **Python 3.8+**: Compatible with modern Python versions

## Installation

Install the package using pip:

```bash
pip install datadis-python
```

Or using Poetry:

```bash
poetry add datadis-python
```

## Quick Start

```python
from datadis_python import DatadisClient

# Initialize client with your NIF and password
client = DatadisClient(
    username="12345678A",  # Your NIF registered in Datadis
    password="your_password"
)

# Get available distributors
distributors = client.get_distributors()

# Get supply points
supplies = client.get_supplies()

# Get contract details
contract = client.get_contract_detail(
    cups="ES001234567890123456AB",
    distributor_code="2"
)

# Get consumption data
consumptions = client.get_consumption(
    cups="ES001234567890123456AB",
    distributor_code="2",
    date_from="2024/01",
    date_to="2024/02",
    measurement_type=0,
    point_type=1
)
```

## API Reference

### Authentication

The client automatically handles authentication using your Datadis credentials:

- **Username**: Your NIF (National Identity Document) registered in Datadis
- **Password**: Your Datadis account password

### Available Methods

#### `get_distributors() -> List[str]`

Retrieves the list of available distributor codes for your account.

**Returns**: List of distributor codes (e.g., ['2', '8'])

#### `get_supplies(distributor_code: Optional[str] = None) -> List[SupplyData]`

Retrieves supply points information.

**Parameters**:
- `distributor_code` (optional): Filter by specific distributor

**Returns**: List of SupplyData objects containing CUPS, address, and distributor information

#### `get_contract_detail(cups: str, distributor_code: str) -> Optional[ContractData]`

Retrieves detailed contract information for a specific CUPS.

**Parameters**:
- `cups`: CUPS code (format: ES + 18 digits + 2 letters)
- `distributor_code`: Distributor code (1-8)

**Returns**: ContractData object with complete contract information

#### `get_consumption(cups: str, distributor_code: str, date_from: str, date_to: str, measurement_type: int = 0, point_type: Optional[int] = None) -> List[ConsumptionData]`

Retrieves consumption data for a specific CUPS and date range.

**Parameters**:
- `cups`: CUPS code
- `distributor_code`: Distributor code
- `date_from`: Start date (format: YYYY/MM)
- `date_to`: End date (format: YYYY/MM)
- `measurement_type`: 0 for hourly, 1 for quarter-hourly
- `point_type`: Point type (obtained from supplies)

**Returns**: List of ConsumptionData objects

#### `get_max_power(cups: str, distributor_code: str, date_from: str, date_to: str) -> List[MaxPowerData]`

Retrieves maximum power demand data.

**Parameters**:
- `cups`: CUPS code
- `distributor_code`: Distributor code
- `date_from`: Start date (format: YYYY/MM)
- `date_to`: End date (format: YYYY/MM)

**Returns**: List of MaxPowerData objects

### Data Models

All API responses are returned as typed Pydantic models:

- `SupplyData`: Supply point information
- `ContractData`: Contract details
- `ConsumptionData`: Energy consumption data
- `MaxPowerData`: Maximum power demand data

### Error Handling

The SDK provides specific exceptions for different error scenarios:

```python
from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

try:
    supplies = client.get_supplies()
except AuthenticationError:
    print("Authentication failed - check credentials")
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except DatadisError as e:
    print(f"General error: {e}")
```

### Distributor Codes

- 1: Viesgo
- 2: E-distribución
- 3: E-redes
- 4: ASEME
- 5: UFD
- 6: EOSA
- 7: CIDE
- 8: IDE

## API Limitations

**Important limitations imposed by the Datadis API**:

- Data is available for the **last 2 years only**
- Most operations require a **distributor code**
- Date format must be **YYYY/MM** (monthly)
- Rate limiting is applied by Datadis

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/datadis-python.git
cd datadis-python

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Testing

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=datadis_python

# Run specific test file
poetry run pytest tests/test_basic.py -v
```

### Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy datadis_python

# Linting
poetry run flake8 datadis_python
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

## Changelog

### 0.1.0 (2024-01-XX)

- Initial release
- Full implementation of Datadis API v2
- Support for all major endpoints
- Comprehensive error handling and validation
- Complete test suite and documentation

## Documentation

Complete documentation is available at [https://datadis-python.readthedocs.io/](https://datadis-python.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://datadis-python.readthedocs.io/](https://datadis-python.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/your-username/datadis-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/datadis-python/discussions)

## Disclaimer

This project is not officially affiliated with Datadis. It is an independent implementation created to facilitate access to the public Datadis API following the official documentation.