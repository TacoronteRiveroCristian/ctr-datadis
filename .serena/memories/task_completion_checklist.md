# Task Completion Checklist

## Required Steps After Completing Any Task

### 1. Code Quality Checks (MANDATORY)
Run all quality tools in this order:
```bash
poetry run black .
poetry run isort .
poetry run flake8 datadis_python
poetry run mypy datadis_python
```

### 2. Testing (MANDATORY)
```bash
# Run full test suite
poetry run pytest

# Run with coverage if adding new code
poetry run pytest --cov=datadis_python
```

### 3. Pre-commit Validation
```bash
poetry run pre-commit run --all-files
```

### 4. Documentation Updates (if applicable)
- Update docstrings for new/modified public methods
- Use Google-style docstring format
- Include type hints for all parameters and returns

### 5. Git Workflow
- Follow conventional commit format:
  - `feat:` for new features
  - `fix:` for bug fixes  
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for test updates

### 6. Branch Strategy
- Work on `develop` branch for active development
- Create feature branches: `feature/description`
- Create bugfix branches: `bugfix/description`

## Pre-commit Hooks
The repository has pre-commit hooks configured that will automatically run:
- trailing-whitespace removal
- end-of-file-fixer
- YAML/JSON/TOML validation
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking

## Quality Standards
- **Type Coverage**: All functions must have type hints
- **Test Coverage**: Aim for >90% coverage
- **Documentation**: All public APIs must have docstrings
- **Linting**: Zero flake8 violations allowed
- **Formatting**: Code must pass Black and isort