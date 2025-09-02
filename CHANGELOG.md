# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added

- Initial release of Datadis Python SDK
- Complete implementation of Datadis API v2 endpoints
- Token-based authentication with automatic renewal
- Type-safe Pydantic models for all API responses
- Comprehensive validation system
- Custom exception hierarchy for robust error handling
- Complete test suite and documentation
- ReadTheDocs integration
- Professional README with badges

### Security

- Secure token handling with automatic expiration
- HTTPS-only communication with Datadis API

### Known Limitations

- Data availability limited to last 2 years (Datadis API limitation)
- Monthly date format required for most endpoints
- Distributor code required for most operations