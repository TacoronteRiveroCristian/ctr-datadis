# Code Style and Conventions

## Code Formatting
- **Black**: Line length 88 characters, target Python 3.8+
- **isort**: Black-compatible profile, multi-line output mode 3
- **flake8**: Max line length 88, ignores E203, E501, W503, F401, F541, E402

## Type Hints
- **mypy**: Python 3.8 compatibility
- **Type hints**: Used throughout but not strictly enforced (disallow_untyped_defs = false)
- **typing-extensions**: Used for Python < 3.10 compatibility

## Import Organization
- First party imports: `datadis_python` package
- Standard library, third-party, then first-party imports (isort handles this)

## Code Structure
- **Base Classes**: Abstract base client in `client/base.py`
- **Versioned Clients**: Separate v1 and v2 client implementations
- **Models**: Pydantic models for all API data structures
- **Exceptions**: Custom exception hierarchy inheriting from base `DatadisError`
- **Utils**: Separated into specific modules (validators, http, text_utils, constants)

## Documentation Style
- Spanish docstrings and comments (following the Spanish context of Datadis)
- Author attribution in module docstrings: `:author: TacoronteRiveroCristian`

## Naming Conventions
- Classes: PascalCase (e.g., `SimpleDatadisClientV1`, `ConsumptionData`)
- Methods/Functions: snake_case (e.g., `get_consumption`, `authenticate`)
- Constants: UPPER_SNAKE_CASE
- Private methods: Leading underscore (e.g., `_make_authenticated_request`)

## Error Handling
- Custom exception hierarchy with specific error types
- Context managers supported with `__enter__`/`__exit__` methods
- Proper resource cleanup in client classes