# Suggested Commands

## Development Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks
poetry run pre-commit install
```

## Testing
```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=datadis_python

# Run specific test file
poetry run pytest tests/test_basic.py -v

# Run tests with markers
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m slow
```

## Code Quality (run after completing tasks)
```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy datadis_python

# Linting
poetry run flake8 datadis_python

# Run all quality checks in sequence
poetry run black . && poetry run isort . && poetry run flake8 datadis_python && poetry run mypy datadis_python
```

## Pre-commit
```bash
# Run pre-commit on all files
poetry run pre-commit run --all-files

# Run pre-commit on staged files
poetry run pre-commit run
```

## Documentation
```bash
# Build documentation (if Sphinx is set up)
cd docs && make html
```

## Build and Publish
```bash
# Build package
poetry build

# Publish to PyPI (for maintainers)
poetry publish
```