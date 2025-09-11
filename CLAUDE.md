# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Datadis Python SDK - A comprehensive Python SDK for interacting with the official Datadis API (Spanish electricity supply data platform). Built with Poetry, supports Python 3.8+, and includes full type safety with Pydantic models.

## Essential Commands

### Development Setup
```bash
poetry install                    # Install dependencies
poetry shell                      # Activate virtual environment
poetry run pre-commit install     # Install pre-commit hooks
```

### Testing
```bash
poetry run pytest                           # Run all tests
poetry run pytest --cov=datadis_python     # Run with coverage
poetry run pytest tests/test_basic.py -v   # Run specific test file
poetry run pytest -m unit                  # Run unit tests only
```

### Code Quality (Required After Any Changes)
```bash
poetry run black .                    # Format code
poetry run isort .                    # Sort imports
poetry run flake8 datadis_python      # Lint code
poetry run mypy datadis_python        # Type check
```

**Run all quality checks in sequence:**
```bash
poetry run black . && poetry run isort . && poetry run flake8 datadis_python && poetry run mypy datadis_python
```

### Pre-commit
```bash
poetry run pre-commit run --all-files    # Run all pre-commit hooks
```

## Architecture

### Package Structure
- `datadis_python/client/` - Main DatadisClient implementation
- `datadis_python/models/` - Pydantic data models (SupplyData, ConsumptionData, etc.)
- `datadis_python/exceptions/` - Custom exception hierarchy
- `datadis_python/utils/` - Utility functions

### Key Design Patterns
- **Single Client**: DatadisClient handles all API operations
- **Type Safety**: Full type hints + Pydantic validation
- **Error Handling**: Custom exceptions (DatadisError → AuthenticationError, APIError)
- **Auto-Authentication**: Token management with automatic renewal

## Code Standards

### Style
- **Line Length**: 88 characters (Black)
- **Formatter**: Black with Python 3.8 target
- **Import Sort**: isort with Black profile
- **Linter**: flake8 with flake8-docstrings

### Text Encoding and Character Handling
- **No Accents**: Remove all accents and tildes from text data to avoid encoding issues
- **ASCII Safe**: Convert "ñ" to "n", "á" to "a", "é" to "e", "í" to "i", "ó" to "o", "ú" to "u"
- **Encoding**: Always use UTF-8 encoding but normalize special characters
- **API Responses**: Apply text normalization to all string fields from Datadis API

### Documentation
- **Format**: Google-style docstrings for all public APIs
- **Required**: Args, Returns, Raises sections
- **Type Hints**: Mandatory for all function parameters and returns

### Testing
- **Framework**: pytest with coverage
- **Structure**: Test classes (TestDatadisClient)
- **Naming**: `test_method_scenario` pattern
- **Mocking**: Use `responses` library for HTTP calls
- **Target**: >90% coverage

## Git Workflow

### Branch Strategy
- `main` - Stable releases
- `develop` - Active development
- `feature/xyz` - New features
- `bugfix/xyz` - Bug fixes

### Commit Format
Follow Conventional Commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation updates
- `refactor:` - Code refactoring
- `test:` - Test changes

## Task Completion Checklist

**MANDATORY after any code changes:**

1. **Quality Checks**: Run black, isort, flake8, mypy
2. **Testing**: Run pytest (with coverage for new code)
3. **Pre-commit**: Validate with `poetry run pre-commit run --all-files`
4. **Type Safety**: Ensure all functions have type hints
5. **Documentation**: Update docstrings for public APIs

## API Context

The SDK provides methods for Datadis API v2:
- `get_distributors()` - Available distributor codes
- `get_supplies()` - Supply point information
- `get_contract_detail()` - Contract details for CUPS
- `get_consumption()` - Energy consumption data
- `get_max_power()` - Maximum power demand data

**Important API Limitations:**
- Data available for last 2 years only
- Date format: YYYY/MM (monthly)
- Most operations require distributor code
- Rate limiting enforced by Datadis

## Professional Messages

All messages must be written in a professional manner, without the use of emoticons.
