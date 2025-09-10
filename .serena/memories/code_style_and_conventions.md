# Code Style and Conventions

## Formatting and Style
- **Line Length**: 88 characters (Black configuration)
- **Code Formatter**: Black with Python 3.8 target
- **Import Sorting**: isort with Black profile
- **Known First Party**: datadis_python

## Type Annotations
- **Strict Type Checking**: mypy configured with strict settings
- **Required**: Type hints for all function parameters and return values
- **Python Version**: 3.8 compatible typing
- **Additional Types**: Uses typing-extensions for Python < 3.10

## Documentation Style
- **Docstring Format**: Google-style docstrings for all public methods and classes
- **Requirements**: Include Args, Returns, and Raises sections
- **Example Format**:
```python
def method_name(param: str) -> ReturnType:
    """Brief description.

    Args:
        param: Parameter description

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception occurs
    """
```

## Naming Conventions
- **Package Name**: datadis_python
- **Classes**: PascalCase (e.g., DatadisClient, ConsumptionData)
- **Functions/Methods**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private Members**: Leading underscore

## Error Handling
- **Custom Exceptions**: Defined in datadis_python.exceptions
- **Hierarchy**: DatadisError (base) -> AuthenticationError, APIError
- **Pattern**: Specific exception types for different error scenarios

## Testing Conventions
- **Framework**: pytest
- **Structure**: Test classes for grouping (TestDatadisClient)
- **Naming**: test_method_scenario pattern
- **Markers**: unit, integration, slow
- **Mocking**: Use responses library for HTTP mocking