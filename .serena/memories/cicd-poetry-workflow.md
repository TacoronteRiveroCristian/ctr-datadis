# CI/CD and Poetry - Project Workflows

## Poetry - Dependency Management

### Essential Commands
```bash
poetry install                # Basic dependencies
poetry install --with dev     # With dev dependencies
poetry update                 # Update dependencies
poetry build                  # Build package for PyPI
poetry publish               # Publish to PyPI
```

### pyproject.toml Structure
- **Production dependencies**: requests, pydantic, python-dateutil
- **Development dependencies**: pytest, black, isort, flake8, mypy, sphinx
- **Configuration**: build-system = poetry-core
- **Metadata**: name="ctr-datadis", Spanish description

## GitHub Actions CI/CD

### Main Workflow (.github/workflows/)
1. **Tests**: Multiple Python versions (3.9+)
2. **Quality**: black, isort, flake8, mypy
3. **Build**: poetry build for verification
4. **Security**: Dependency scan
5. **Release**: Automatic PyPI publishing

### Important Triggers
- **push**: main/develop branches
- **pull_request**: All PRs
- **release**: created (triggers PyPI publishing)
- **paths**: Includes documentation changes

### Configured Secrets
- **PYPI_API_TOKEN**: For automatic publishing
- **GITHUB_TOKEN**: For releases

## Semantic Versioning

### Historical Pattern (from Changelog)
- **Major**: Breaking changes (v0.4.1 → v0.5.0)
- **Minor**: New features (v0.3.0 → v0.4.0)
- **Patch**: Bug fixes (v0.4.1 → v0.4.2)

### Release Process
1. Update CHANGELOG.md with new version
2. poetry version [patch|minor|major]
3. Commit changes
4. Create tag and release on GitHub
5. GitHub Actions automatically publishes to PyPI

## Resolved Historical Problems
- **SSL Issues**: Actions updated to v5
- **Permissions**: GITHUB_TOKEN configured
- **Dependencies**: poetry.lock regenerated for consistency
- **Python versions**: 3.9+ support established
