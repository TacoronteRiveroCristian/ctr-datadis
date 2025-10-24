# Pytest - Project-Specific Patterns

## Current Status
- **343 tests** passing (100% success in v0.4.2)
- **Custom test runner**: `python run_tests.py`
- **High coverage** consistently maintained

## Key Fixtures (conftest.py)
- `authenticated_v1_client` - Authenticated V1 client
- `authenticated_v2_client` - Authenticated V2 client
- `sample_*_data` - Sample data for each model
- `mock_auth_success` - Successful authentication mock

## Specific Testing Patterns

### 1. Date Validation Tests
```python
# Recurring pattern for monthly dates
def test_monthly_date_validation():
    # REJECTS dates with specific days
    with pytest.raises(ValidationError):
        client.get_consumption(date_from="2024/01/15")

    # ACCEPTS monthly dates
    result = client.get_consumption(date_from="2024/01")
```

### 2. CUPS Tests
```python
# CUPS validation (recurring theme in changelog)
def test_cups_validation():
    # Format: ES + 20-22 alphanumeric characters
    valid_cups = "ES1234567890123456789012"
    result = validate_cups(valid_cups)
```

### 3. Pydantic Model Tests
```python
# Pattern for model tests
def test_model_alias_compatibility():
    # Must support camelCase AND snake_case
    data_camel = {"fieldName": "value"}
    data_snake = {"field_name": "value"}
    assert Model(**data_camel) == Model(**data_snake)
```

## Critical Markers
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.monthly_validation` - Monthly dates
- `@pytest.mark.cups_validation` - CUPS validation
- `@pytest.mark.client_v1` / `@pytest.mark.client_v2`
