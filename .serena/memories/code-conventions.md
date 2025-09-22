# Code Conventions

## Formatting
- **Black**: 88 characters per line, Python 3.9+
- **isort**: Black-compatible profile
- **flake8**: 88 chars, ignores E203, E501, W503, F401, F541, E402
- **mypy**: Python 3.9 compatibility

## Naming
- **Classes**: PascalCase (`DatadisClient`, `ConsumptionData`)
- **Methods**: snake_case (`get_consumption`, `authenticate`)
- **Private**: underscore (`_make_authenticated_request`)
- **Constants**: UPPER_SNAKE_CASE (`API_V1_ENDPOINTS`)

## Documentation
- **Docstrings**: Sphinx style (reStructuredText)
- **Language**: Spanish (Datadis context)
- **Author**: TacoronteRiveroCristian

## Exceptions
Hierarchy:
```
DatadisError (base)
├── AuthenticationError
├── APIError
├── ValidationError
├── NetworkError
└── ConfigurationError
```

## Important Rules
- **NEVER** use emojis in code/comments
- **Test-First Development** mandatory
- **No commented code** in production
