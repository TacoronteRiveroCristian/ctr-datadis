# Testing Strategy - Datadis SDK

## [STATUS] Current Status (Completed)

### Fully Functional Test Suite
- [OK] **243 tests passing** (100% success rate)
- [OK] **0 tests failing**
- [OK] **Complete coverage** of all SDK components

### Test Structure
```
tests/
├── test_auth.py              # Authentication tests
├── test_client_v1.py         # V1 client tests
├── test_client_v2.py         # V2 client tests
├── test_models.py            # Pydantic model tests
├── test_utils.py             # Utility tests
├── test_exceptions.py        # Error handling tests
├── test_integration.py       # Integration tests
├── test_coverage_and_quality.py  # Quality meta-tests
├── conftest.py               # Shared fixtures
└── pytest.ini               # Pytest configuration
```

## [RULE] **FUNDAMENTAL RULE: Test-First Development**

### **MANDATORY for New Features**
Every new feature, method, class or functionality **MUST** be accompanied by tests before merge:

1. **New Client Methods**: Unit tests + integration
2. **New Pydantic Models**: Validation + serialization tests
3. **New Utilities**: Edge cases + error handling tests
4. **New Exceptions**: Correct propagation tests
5. **New Endpoints**: Mocks + response tests

### **Required Development Flow**
```
1. Design API/method
2. [OK] Write tests FIRST
3. Implement functionality
4. [OK] Tests must pass
5. Code review + tests review
6. Merge only if 100% tests passing
```

## [CONFIGURATION] Testing Configuration

### Pytest Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Mandatory markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests
    slow: Slow tests (may take several seconds)
    auth: Authentication tests
    models: Pydantic model tests
    client_v1: V1 client tests
    client_v2: V2 client tests
    utils: Utility function tests
    errors: Error handling tests
```

### Test Runner (run_tests.py)
```bash
# Fast tests (unit only)
python run_tests.py --fast

# Complete tests
python run_tests.py --full

# Specific tests by component
python run_tests.py --component auth
python run_tests.py --component models

# With coverage
python run_tests.py --coverage

# Complete suite
python run_tests.py --all
```

## [PATTERNS] Established Testing Patterns

### 1. **Pydantic Model Tests**
```python
def test_model_validation():
    """Test model validation."""
    data = {"field": "value"}
    model = MyModel(**data)
    assert model.field == "value"

def test_model_invalid_data():
    """Test invalid data."""
    with pytest.raises(ValidationError):
        MyModel(invalid_field="value")
```

### 2. **Client Tests with Mocks**
```python
@pytest.mark.client_v1
def test_get_method_success(authenticated_v1_client):
    """Test successful method."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}/endpoint",
            json=sample_response,
            status=200,
        )

        result = authenticated_v1_client.get_method()
        assert isinstance(result, list)
        assert len(result) > 0
```

### 3. **Error Handling Tests**
```python
def test_api_error_handling():
    """Test HTTP error handling."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            json={"error": "Not found"},
            status=404,
        )

        with pytest.raises(APIError) as exc_info:
            client.method()
        assert "404" in str(exc_info.value)
```

## [FIXTURES] Centralized Fixtures (conftest.py)

### Authentication Fixtures
- `test_credentials`: Test credentials
- `test_token`: Valid JWT token
- `authenticated_v1_client`: Authenticated V1 client
- `authenticated_v2_client`: Authenticated V2 client

### Data Fixtures
- `sample_supply_data`: Supply point data
- `sample_consumption_data`: Consumption data
- `sample_contract_data`: Contract data
- `sample_distributor_data`: Distributor data

### Mocking Fixtures
- `mock_auth_success`: Successful authentication mock
- `mock_v1_api_responses`: Complete mocks for V1 API
- `mock_v2_api_responses`: Complete mocks for V2 API

## [PROBLEMS] Resolved Problems and Lessons Learned

### 1. **CUPS Validation**
- **Problem**: Incorrect format (16 vs 22 digits)
- **Solution**: Correct pattern `^ES\d{22}[A-Z0-9]{2}$`
- **Lesson**: Validate with real API data

### 2. **Error Wrapping**
- **Problem**: APIError incorrectly wrapped in DatadisError
- **Solution**: Propagate APIError directly on first attempt
- **Lesson**: Tests should verify exact exception types

### 3. **Mock Configuration**
- **Problem**: "Not all requests executed" due to retry mechanisms
- **Solution**: Configure mocks = number of attempts (retries + 1)
- **Lesson**: Align mocks with retry logic

### 4. **URL Encoding**
- **Problem**: Tests expected unencoded URLs
- **Solution**: Verify encoded URLs (`%2F` instead of `/`)
- **Lesson**: Tests should reflect real HTTP behavior

### 5. **Text Normalization**
- **Problem**: Fixtures with accents vs normalized API
- **Solution**: Use normalized text in fixtures
- **Lesson**: Fixtures should simulate real API response

## [CHECKLIST] Checklist for New Features

### Before Implementation:
- [ ] Are tests written BEFORE implementation?
- [ ] Are happy path + edge cases covered?
- [ ] Are different error types tested?
- [ ] Are mocks configured correctly?

### During Implementation:
- [ ] Do tests pass locally?
- [ ] Is 100% pass rate maintained?
- [ ] Do new tests use existing fixtures?
- [ ] Are established patterns followed?

### Before Merge:
- [ ] Do all tests pass in CI?
- [ ] Is coverage maintained high?
- [ ] Are tests understandable and maintainable?
- [ ] Are special cases documented?

## [COMMANDS] Frequent Testing Commands

```bash
# Day-to-day development
python run_tests.py --fast

# Before commit
python run_tests.py --coverage

# Testing new feature
python run_tests.py --component [component]

# Complete pre-release validation
python run_tests.py --all

# Debug specific test
poetry run pytest tests/test_file.py::test_method -v -s
```

## [METRICS] Quality Metrics

### Maintained Objectives:
- **Pass Rate**: 100% (243/243 tests)
- **Coverage**: >90% (configured in run_tests.py)
- **Performance**: Fast tests <30s, complete <60s
- **Maintainability**: Reusable fixtures, consistent patterns

---

**IMPORTANT**: This testing strategy ensures the SDK maintains its robustness and reliability. Test quality should not be compromised for development speed.
