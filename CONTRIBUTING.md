# Contributing to Datadis Python SDK

We welcome contributions to the Datadis Python SDK! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- Git

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/datadis-python.git
   cd datadis-python
   ```

3. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Activate the virtual environment:
   ```bash
   poetry shell
   ```

6. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Development Workflow

### Branch Strategy

- `main` - Stable release branch
- `develop` - Active development branch
- `feature/xyz` - Feature branches
- `bugfix/xyz` - Bug fix branches
- `hotfix/xyz` - Critical fixes

### Making Changes

1. Create a new branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Add or update tests for your changes

4. Run the test suite:
   ```bash
   poetry run pytest
   ```

5. Run code quality checks:
   ```bash
   poetry run black .
   poetry run isort .
   poetry run flake8 datadis_python
   poetry run mypy datadis_python
   ```

6. Commit your changes with a descriptive message:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

7. Push your branch and create a Pull Request

## Coding Standards

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for reactive energy data endpoint
fix: handle authentication token expiration correctly
docs: update API documentation for get_consumption method
```

### Code Documentation

- Use Google-style docstrings for all public methods and classes
- Include type hints for all function parameters and return values
- Add inline comments for complex logic

Example:
```python
def get_consumption(
    self,
    cups: str,
    distributor_code: str,
    date_from: str,
    date_to: str,
    measurement_type: int = 0
) -> List[ConsumptionData]:
    """Retrieve consumption data for a specific CUPS.

    Args:
        cups: CUPS code (format: ES + 18 digits + 2 letters)
        distributor_code: Distributor code (1-8)
        date_from: Start date in YYYY/MM format
        date_to: End date in YYYY/MM format
        measurement_type: 0 for hourly, 1 for quarter-hourly

    Returns:
        List of consumption data records

    Raises:
        ValidationError: If parameters are invalid
        AuthenticationError: If authentication fails
        APIError: If API request fails
    """
```

### Testing

- Write tests for all new functionality
- Aim for high test coverage (>90%)
- Use descriptive test names
- Group related tests in classes
- Mock external API calls

Example:
```python
class TestDatadisClient:
    """Tests for DatadisClient class."""

    def test_get_supplies_success(self, mock_client):
        """Test successful retrieval of supply points."""
        # Test implementation
        pass

    def test_get_supplies_authentication_error(self, mock_client):
        """Test handling of authentication errors."""
        # Test implementation
        pass
```

## Pull Request Process

1. **Title**: Use a clear, descriptive title
2. **Description**: Provide a detailed description of changes
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update documentation if needed
5. **Changelog**: Add entry to CHANGELOG.md for significant changes

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented appropriately
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## Reporting Issues

When reporting issues, please include:

- Python version
- SDK version
- Operating system
- Complete error traceback
- Minimal code example to reproduce the issue
- Expected vs actual behavior

## Feature Requests

For feature requests, please:

- Check if the feature already exists
- Provide a clear description of the feature
- Explain the use case and benefits
- Consider if it fits the project scope

## Documentation

- Keep documentation up to date with code changes
- Use clear, concise language
- Provide practical examples
- Follow reStructuredText format for Sphinx docs

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Publish to PyPI automatically via GitHub Actions

## Questions?

If you have questions about contributing, please:

- Check existing issues and discussions
- Create a new discussion on GitHub
- Reach out to maintainers

Thank you for contributing to the Datadis Python SDK!