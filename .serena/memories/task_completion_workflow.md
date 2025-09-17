# Task Completion Workflow

## When a Task is Completed

### Code Quality Checks (Run in Order)
1. **Format Code**: `poetry run black datadis_python/`
2. **Sort Imports**: `poetry run isort datadis_python/`
3. **Lint Code**: `poetry run flake8 datadis_python/`
4. **Type Check**: `poetry run mypy datadis_python/`

### Testing (If Tests Exist)
Note: Currently no test directory exists, but pyproject.toml is configured for pytest
- `poetry run pytest` (when tests are available)
- `poetry run pytest --cov=datadis_python` (with coverage)

### Building (Before Publishing)
- `poetry build` to ensure package builds correctly

### Documentation (If Modified)
- Update docstrings if public APIs changed
- Rebuild documentation if Sphinx docs exist

## Pre-commit Workflow
Although no pre-commit config exists, recommended workflow:
1. Run Black formatting
2. Run isort import sorting  
3. Run flake8 linting
4. Run mypy type checking
5. Ensure no linting errors before committing

## Release Process
- Version bumping is handled in `pyproject.toml`
- GitHub Actions automatically publishes to PyPI on release creation
- CI/CD pipeline builds and publishes via `poetry build` and `poetry publish`