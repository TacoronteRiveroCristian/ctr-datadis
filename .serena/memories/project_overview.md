# Project Overview

## Purpose
ctr-datadis is a comprehensive Python SDK for interacting with the official Datadis API (Spanish electricity supply data platform). It provides developers with a simple way to access electricity consumption data, supply information, and related utilities for Spanish energy consumers.

## Tech Stack
- **Language**: Python 3.8+
- **Build Tool**: Poetry for dependency management and packaging
- **HTTP Client**: requests library for API calls
- **Data Validation**: Pydantic v2 for type-safe data models
- **Date Handling**: python-dateutil for date operations

## Key Features
- Automatic token-based authentication with renewal
- Complete API coverage for all Datadis endpoints
- Type safety with full type hints and Pydantic models
- Comprehensive error handling with custom exceptions
- Context manager support for proper resource cleanup
- Text normalization for Spanish accents and special characters

## Package Structure
- `datadis_python/` - Main package directory
  - `client/` - API client implementations (v1, v2, base, unified)
  - `models/` - Pydantic data models for API responses
  - `exceptions/` - Custom exception classes
  - `utils/` - Utility functions (validators, HTTP helpers, text utils, constants)
  - `doc/` - Documentation files