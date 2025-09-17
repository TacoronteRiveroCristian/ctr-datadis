# Suggested Commands

## Development Commands

### Dependencies and Environment
```bash
# Install dependencies
poetry install

# Install with development dependencies
poetry install --with dev

# Update dependencies
poetry update
```

### Code Quality and Linting
```bash
# Format code with Black
poetry run black datadis_python/

# Sort imports with isort
poetry run isort datadis_python/

# Lint with flake8
poetry run flake8 datadis_python/

# Type checking with mypy
poetry run mypy datadis_python/
```

### Testing
```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=datadis_python

# Run specific test markers
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m slow
```

### Documentation
```bash
# Build documentation (if Sphinx is configured)
poetry run sphinx-build -b html docs/ docs/_build/html
```

### Building and Publishing
```bash
# Build package
poetry build

# Publish to PyPI (requires authentication)
poetry publish
```

### Git and Version Control
```bash
# Standard git commands work normally
git status
git add .
git commit -m "message"
git push
```