# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2024-12-12

### Added
- Complete Datadis API v1 client implementation
- Comprehensive Pydantic models for all data types
- Custom exception hierarchy for error handling
- Text normalization utilities for Spanish characters
- Type hints throughout the entire codebase
- Comprehensive documentation with Sphinx
- PyPI publication workflow

### Changed
- Improved error handling with detailed exception messages
- Optimized authentication token management
- Clean project structure with streamlined documentation

### Fixed
- Text encoding issues with Spanish accents and special characters
- API response parsing for all endpoint types
- Package name conflicts resolved (published as ctr-datadis)

## [0.1.0] - 2024-12-01

### Added
- Initial release of the Datadis Python SDK
- Basic client implementation for Datadis API
- Support for supply points, consumption, and distributor data
- Authentication handling with automatic token renewal
- Type-safe Pydantic models for API responses
- Custom exception hierarchy
- ReadTheDocs integration

### Security
- Secure token handling with automatic expiration
- HTTPS-only communication with Datadis API

### Known Limitations
- Data availability limited to last 2 years (Datadis API limitation)
- Monthly date format required for most endpoints
- Distributor code required for most operations
