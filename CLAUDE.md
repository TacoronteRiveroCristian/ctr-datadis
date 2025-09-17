# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `ctr-datadis`, a comprehensive Python SDK for the official Datadis API (Spanish electricity supply data platform). The SDK provides developers with type-safe access to electricity consumption data, supply information, and related utilities for Spanish energy consumers.

## Development Commands

### Dependencies
```bash
# Install dependencies
poetry install

# Install with development dependencies
poetry install --with dev
```

### Code Quality (Run these after making changes)
```bash
# Format code
poetry run black datadis_python/

# Sort imports
poetry run isort datadis_python/

# Lint code
poetry run flake8 datadis_python/

# Type check
poetry run mypy datadis_python/
```

### Testing
```bash
# Run tests (when available)
poetry run pytest

# Run with coverage
poetry run pytest --cov=datadis_python
```

### Building
```bash
# Build package
poetry build
```

## Architecture

### Client Hierarchy
- **BaseDatadisClient** (`client/base.py`): Abstract base with authentication and HTTP handling
- **SimpleDatadisClientV1** (`client/v1/simple_client.py`): Main client implementation
- **V2 Client** (`client/v2/`): Future API version support
- **Unified Client** (`client/unified.py`): Multi-version abstraction

### Key Components
- **Models** (`models/`): Pydantic data models for type-safe API responses
  - `ConsumptionData`, `SupplyData`, `ContractData`, `MaxPowerData`
  - Response wrappers and error models
- **Exceptions** (`exceptions/`): Custom exception hierarchy
  - `DatadisError` (base) → `AuthenticationError`, `APIError`, `ValidationError`
- **Utils** (`utils/`): HTTP helpers, validators, text normalization, constants

### Authentication Flow
1. Client initialized with username/password
2. Automatic token management with expiry tracking
3. Token renewal before requests
4. All API calls include authentication headers

## Code Style

### Formatting
- **Black**: 88 character line length, Python 3.8+ target
- **isort**: Black-compatible profile
- **flake8**: 88 char limit, ignores E203, E501, W503, F401, F541, E402

### Conventions
- Classes: PascalCase (`DatadisClient`, `ConsumptionData`)
- Methods: snake_case (`get_consumption`, `authenticate`)
- Private methods: Leading underscore (`_make_authenticated_request`)
- Spanish docstrings/comments (matching Datadis context)

### Type Hints
- Python 3.8 compatible with mypy
- Not strictly enforced but widely used
- `typing-extensions` for older Python versions

## When Task is Complete

Always run these commands in order:
1. `poetry run black datadis_python/`
2. `poetry run isort datadis_python/`
3. `poetry run flake8 datadis_python/`
4. `poetry run mypy datadis_python/`

## Publishing

GitHub Actions automatically publishes to PyPI on release creation via `poetry build` and `poetry publish`.