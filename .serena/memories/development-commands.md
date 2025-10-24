# Development Commands

## Code Quality (MANDATORY at the end)
```bash
poetry run black datadis_python/
poetry run isort datadis_python/
poetry run flake8 datadis_python/
poetry run mypy datadis_python/
```

## Testing
```bash
# Fast tests
python run_tests.py --fast

# Complete tests
python run_tests.py --all

# By component
python run_tests.py --component auth
python run_tests.py --component models

# With coverage
python run_tests.py --coverage
```

## Dependencies
```bash
poetry install              # Basic dependencies
poetry install --with dev   # With dev dependencies
```

## Build
```bash
poetry build    # Build package
```

## Current Status
- **343 tests passing** (100% success rate)
- **0 failing tests**
- **Complete Pydantic migration** (Sep 2025)
