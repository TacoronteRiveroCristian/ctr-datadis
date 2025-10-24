# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `ctr-datadis`, a comprehensive Python SDK for the official Datadis API (Spanish electricity supply data platform). The SDK provides developers with type-safe access to electricity consumption data, supply information, and related utilities for Spanish energy consumers.

## Current Status (v0.4.2)

- **343 tests passing** (100% success rate)
- **Complete Pydantic migration** from Dict to validated models
- **Comprehensive documentation** with Sphinx-style docstrings
- **Production-ready** with automated CI/CD and PyPI publishing

## Critical Domain Knowledge

### Spanish Electricity Domain
- **CUPS Format**: ES + 20-22 alphanumeric characters (e.g., ES1234567890123456789012AB)
- **Monthly Dates Only**: API requires YYYY/MM format, NOT YYYY/MM/DD
- **Distributor Codes**: 1-8 representing major Spanish electricity distributors
- **Point Types**: 1-5 (including type 5 for auxiliary services, added v0.4.2)

### Historical Issues (Learn from CHANGELOG.md)
- **CUPS Validation**: Removed in v0.4.1, restored in v0.4.2 due to user issues
- **Monthly Date Validation**: Recurring problem - users attempt daily format
- **V1/V2 Consistency**: Keep behaviors aligned between API versions



## Additional Development Rules

- **Test-First Development**: MANDATORY - Write tests BEFORE implementation for all features/bugfixes
- **After each feature**: You must always create the corresponding tests for every new feature or bugfix, and verify that they pass before considering the task complete.
- **Docstrings**: All docstrings must follow the Sphinx (reStructuredText) style, both in classes and in functions/methods.
- **Emojis**: Emojis must never be used in code, comments, docstrings, or documentation.
- **Breaking Changes**: Require careful analysis - learn from v0.4.1 CUPS validation removal issue

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
# Fast tests (day-to-day development)
python run_tests.py --fast

# Complete test suite
python run_tests.py --all

# Component-specific tests
python run_tests.py --component auth
python run_tests.py --component models
python run_tests.py --component client_v1

# With coverage
python run_tests.py --coverage

# Traditional pytest (also works)
poetry run pytest
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
- **SimpleDatadisClientV1** (`client/v1/simple_client.py`): **RECOMMENDED** main client implementation
- **DatadisClientV1** (`client/v1/client.py`): Standard V1 client with additional methods
- **SimpleDatadisClientV2** (`client/v2/simple_client.py`): V2 client with reactive energy support
- **UnifiedDatadisClient** (`client/unified.py`): Multi-version abstraction

### Key Components
- **Models** (`models/`): **Fully migrated** to Pydantic v2 for type-safe API responses
  - Core: `ConsumptionData`, `SupplyData`, `ContractData`, `MaxPowerData`
  - Advanced: `DistributorData`, `ReactiveData` (V2 only)
  - Response wrappers: `ConsumptionResponse`, `SuppliesResponse`, etc.
- **Exceptions** (`exceptions/`): Custom exception hierarchy
  - `DatadisError` (base) → `AuthenticationError`, `APIError`, `ValidationError`, `NetworkError`
- **Utils** (`utils/`):
  - `validators.py`: CUPS validation, date range validation
  - `type_converters.py`: Flexible parameter conversion (datetime/date → string)
  - `text_utils.py`: Spanish character normalization
  - `http.py`: HTTP client with retry logic
  - `constants.py`: API endpoints and configuration

### Authentication Flow
1. Client initialized with username/password
2. Automatic token management with expiry tracking
3. Token renewal before requests
4. All API calls include authentication headers

### Pydantic Integration Pattern
```python
# TYPE_CHECKING imports to avoid circular dependencies
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...models.supply import SupplyData

# Validation with graceful error handling
validated_data = []
for item in raw_data:
    try:
        validated_item = SupplyData(**item)
        validated_data.append(validated_item)
    except Exception as e:
        print(f"Error validating: {e}")
        continue  # Continue without failing entire request
```

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
- **Python 3.9+** compatible with mypy (updated from 3.8 in v0.2.1)
- Widely used throughout codebase
- `typing-extensions` for compatibility
- **TYPE_CHECKING pattern** for avoiding circular imports in models

## When Task is Complete

Always run these commands in order:
1. `poetry run black datadis_python/`
2. `poetry run isort datadis_python/`
3. `poetry run flake8 datadis_python/`
4. `poetry run mypy datadis_python/`

## Testing Strategy

### Test Organization
- **343 tests** organized by component with pytest markers
- **conftest.py**: Centralized fixtures for authenticated clients and sample data
- **run_tests.py**: Custom test runner with component filtering

### Critical Test Patterns
```python
# Monthly date validation (recurring issue)
@pytest.mark.monthly_validation
def test_rejects_daily_dates():
    with pytest.raises(ValidationError):
        client.get_consumption(date_from="2024/01/15")  # Should fail

# CUPS validation (historical problem)
@pytest.mark.cups_validation
def test_cups_format_validation():
    valid_cups = "ES1234567890123456789012AB"
    result = validate_cups(valid_cups)
    assert result == valid_cups.upper()

# Pydantic model compatibility
@pytest.mark.models
def test_model_alias_compatibility():
    # Must support both camelCase (API) and snake_case (Python)
    data_camel = {"fieldName": "value"}
    data_snake = {"field_name": "value"}
    assert Model(**data_camel) == Model(**data_snake)
```

### Test Markers (Use These)
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.models` - Pydantic model tests
- `@pytest.mark.client_v1` / `@pytest.mark.client_v2` - Client-specific
- `@pytest.mark.monthly_validation` - Date validation tests
- `@pytest.mark.cups_validation` - CUPS validation tests

## Publishing

### Release Process
1. Update CHANGELOG.md with new version
2. `poetry version [patch|minor|major]`
3. Commit changes and create GitHub release
4. **GitHub Actions automatically publishes to PyPI** as `ctr-datadis`

### PyPI Package
- **Name**: `ctr-datadis` (due to naming conflict)
- **Audience**: Spanish-speaking developers
- **Keywords**: energia, consumo, electricidad, españa, cups, distribuidora
- **Classification**: Production/Stable

## Advanced Git Workflows

### Git Worktrees (Recommended for Complex Features)
```bash
# Work on feature while maintaining stable develop
git worktree add ../datadis-feature feature/nueva-funcionalidad

# Test in production environment while developing
git worktree add ../datadis-hotfix hotfix/cups-validation

# Documentation updates in parallel
git worktree add ../datadis-docs docs/update-sphinx
```

### Branch Strategy
- **main**: Production releases (v0.4.2)
- **develop**: Active development
- **feature/**: New features
- **hotfix/**: Critical fixes (CUPS, date validation)
- **docs/**: Documentation updates
