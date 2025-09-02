Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.1.0] - 2024-01-XX
--------------------

Added
^^^^^

* Initial release of Datadis Python SDK
* Complete implementation of Datadis API v2 endpoints:

  * ``get_distributors()`` - Retrieve available distributor codes
  * ``get_supplies()`` - Get supply points information
  * ``get_contract_detail()`` - Detailed contract information
  * ``get_consumption()`` - Energy consumption data
  * ``get_max_power()`` - Maximum power demand data

* **Authentication System**:

  * Token-based authentication with automatic renewal
  * Session management with configurable timeouts
  * Automatic retry logic for expired tokens

* **Data Models**:

  * Type-safe Pydantic models for all API responses
  * ``SupplyData`` - Supply point information
  * ``ContractData`` - Contract details with self-consumption support
  * ``ConsumptionData`` - Energy consumption with generation data
  * ``MaxPowerData`` - Power demand measurements
  * ``DistributorError`` - Error handling for distributor responses

* **Validation System**:

  * CUPS code validation (ES + 18 digits + 2 letters)
  * Date format validation (YYYY/MM for monthly, YYYY/MM/DD for daily)
  * Distributor code validation (1-8)
  * Measurement type validation (0=hourly, 1=quarter-hourly)

* **Error Handling**:

  * Custom exception hierarchy:
    * ``DatadisError`` - Base exception
    * ``AuthenticationError`` - Authentication failures
    * ``APIError`` - HTTP and API errors with status codes
    * ``ValidationError`` - Parameter validation errors
  * Automatic retry logic with exponential backoff
  * Rate limiting handling (HTTP 429)

* **Development Tools**:

  * Complete test suite with pytest
  * Code formatting with Black
  * Import sorting with isort
  * Type checking with mypy
  * Linting with flake8
  * Poetry configuration for dependency management

* **Documentation**:

  * Comprehensive Sphinx documentation
  * ReadTheDocs integration
  * API reference with autodoc
  * Quick start guide
  * Practical examples
  * Professional README with badges

* **Configuration**:

  * Poetry-based project structure
  * PyPI publication ready
  * MIT License
  * Git workflow with main/develop branches
  * Pre-commit hooks configuration

Security
^^^^^^^^

* Secure token handling with automatic expiration
* No credential storage in logs or error messages
* HTTPS-only communication with Datadis API

Known Limitations
^^^^^^^^^^^^^^^^^

* Data availability limited to last 2 years (Datadis API limitation)
* Monthly date format required for most endpoints
* Distributor code required for most operations
* Rate limiting applied by Datadis (varies by endpoint)

Technical Notes
^^^^^^^^^^^^^^^

* Built on Datadis API v2 specification
* Compatible with Python 3.8, 3.9, 3.10, 3.11, 3.12
* Async support planned for future release
* Thread-safe client implementation

Breaking Changes
^^^^^^^^^^^^^^^^

* N/A - Initial release