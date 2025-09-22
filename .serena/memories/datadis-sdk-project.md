# Datadis SDK Project

## Description
Python SDK for the official Datadis API (Spanish electricity supply data platform).

## Main Technologies
- **Python 3.9+** with Poetry for dependency management
- **Pydantic v2** for validation and data models
- **requests** for HTTP calls
- **pytest** for testing (343 tests, 100% passing)

## Main Structure
```
datadis_python/
├── client/          # API clients (base, v1, v2, unified)
├── models/          # Pydantic models for responses
├── exceptions/      # Custom exception hierarchy
└── utils/           # Utilities (validators, http, text_utils, constants)
```

## Key Features
- Automatic authentication with token renewal
- Complete validation with Pydantic
- Robust error handling with retries
- Support for multiple API versions
- Text normalization for Spanish characters

## Main Client
`SimpleDatadisClientV1` in `client/v1/simple_client.py` is the recommended client.
