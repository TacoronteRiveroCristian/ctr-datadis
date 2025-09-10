# Project Overview

## Purpose
Datadis Python SDK is a comprehensive Python SDK for interacting with the official Datadis API (Distribuidora de Información de Suministros de España). Datadis is the official Spanish platform that provides electricity supply data access.

## Key Features
- Automatic token-based authentication with renewal
- Complete API coverage for Datadis API v2 endpoints
- Full type safety with Pydantic models and type hints
- Comprehensive error handling with custom exceptions
- Built-in retry logic and rate limit handling
- Support for Python 3.8+

## Tech Stack
- **Language**: Python 3.8+
- **Build Tool**: Poetry for dependency management
- **Testing**: pytest with pytest-cov for coverage
- **Type Checking**: mypy with strict configuration
- **Formatting**: black (line length 88)
- **Import Sorting**: isort (black profile)
- **Linting**: flake8 with flake8-docstrings
- **Pre-commit**: Configured with hooks for quality assurance
- **Documentation**: Sphinx with RTD theme
- **Main Dependencies**: requests, pydantic, python-dateutil

## API Coverage
The SDK provides methods for:
- Authentication (automatic token handling)
- Getting distributors list
- Retrieving supply points
- Getting contract details
- Retrieving consumption data (hourly/quarter-hourly)
- Getting maximum power demand data

## Repository Structure
- `datadis_python/` - Main SDK package
- `tests/` - Test suite
- `examples/` - Usage examples
- `docs/` - Documentation source
- Pre-configured for PyPI publication and ReadTheDocs