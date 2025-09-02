# Publication Guide

This guide explains how to publish the Datadis Python SDK to PyPI and set up ReadTheDocs documentation.

## Prerequisites

1. PyPI account: Register at [pypi.org](https://pypi.org/account/register/)
2. TestPyPI account: Register at [test.pypi.org](https://test.pypi.org/account/register/) (for testing)
3. ReadTheDocs account: Sign up at [readthedocs.org](https://readthedocs.org/)

## PyPI Publication

### Option 1: Automatic via GitHub Actions (Recommended)

1. **Set up PyPI API Token**:
   - Go to PyPI → Account Settings → API tokens
   - Create new token with scope for the project
   - Copy the token (starts with `pypi-`)

2. **Configure GitHub Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Add new secret: `PYPI_API_TOKEN` with your PyPI token

3. **Create Release**:
   - Go to GitHub repository → Releases → Create new release
   - Tag: `v0.1.0` (or current version)
   - Title: `Release v0.1.0`
   - Description: Copy from CHANGELOG.md
   - Publish release

4. **Monitor Publication**:
   - Check Actions tab for workflow status
   - Package will be automatically published to PyPI

### Option 2: Manual Publication

1. **Test on TestPyPI first**:
   ```bash
   # Configure TestPyPI
   poetry config repositories.testpypi https://test.pypi.org/legacy/
   poetry config pypi-token.testpypi <your-testpypi-token>
   
   # Build and publish to TestPyPI
   poetry build
   poetry publish -r testpypi
   
   # Test installation
   pip install --index-url https://test.pypi.org/simple/ datadis-python
   ```

2. **Publish to PyPI**:
   ```bash
   # Configure PyPI token
   poetry config pypi-token.pypi <your-pypi-token>
   
   # Build and publish
   poetry build
   poetry publish
   ```

## ReadTheDocs Setup

### 1. Import Project

1. Go to [ReadTheDocs](https://readthedocs.org/)
2. Sign in with GitHub
3. Click "Import a Project"
4. Select `datadis-python` repository
5. Click "Build Version"

### 2. Configure Project Settings

1. Go to project settings
2. **Advanced Settings**:
   - Python interpreter: `CPython 3.11`
   - Requirements file: `docs/requirements.txt`
   - Python configuration file: `docs/conf.py`

3. **Webhooks** (optional):
   - Enable GitHub webhook for automatic builds
   - This is usually set up automatically

### 3. Verify Documentation

1. Check build logs for any errors
2. Visit your documentation at `https://datadis-python.readthedocs.io/`
3. Test all pages and links

## Verification Checklist

Before publishing, verify:

### Code Quality
- [ ] All tests pass: `poetry run pytest`
- [ ] Code is formatted: `poetry run black --check .`
- [ ] Imports are sorted: `poetry run isort --check-only .`
- [ ] No linting errors: `poetry run flake8 datadis_python`
- [ ] Type checking passes: `poetry run mypy datadis_python`

### Package Build
- [ ] Package builds successfully: `poetry build`
- [ ] No warnings in build output
- [ ] Both wheel and sdist are created

### Documentation
- [ ] README.md is complete and professional
- [ ] All documentation files are present
- [ ] Examples work correctly
- [ ] API documentation is complete

### Version Management
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md is updated
- [ ] Git tags are created for releases

## Post-Publication

### 1. Update Badges

Update README.md badges with actual URLs:
- PyPI version badge
- Documentation badge
- Build status badges

### 2. Announce Release

- Create GitHub release notes
- Update project description if needed
- Share on relevant communities (optional)

### 3. Monitor

- Watch for issues and bug reports
- Monitor download statistics
- Respond to community feedback

## Troubleshooting

### Common PyPI Issues

1. **Version already exists**:
   - Increment version in `pyproject.toml`
   - Create new build

2. **Authentication failed**:
   - Verify API token is correct
   - Check token permissions

3. **Package name taken**:
   - Choose different name in `pyproject.toml`
   - Update all references

### Common ReadTheDocs Issues

1. **Build fails**:
   - Check `docs/requirements.txt` has all dependencies
   - Verify Python version in settings
   - Check Sphinx configuration

2. **Import errors**:
   - Ensure package is installed in ReadTheDocs environment
   - Check `docs/conf.py` path configuration

3. **Theme issues**:
   - Verify `sphinx-rtd-theme` is in requirements
   - Check theme configuration in `conf.py`

## Maintenance

### Regular Updates

1. **Dependencies**:
   ```bash
   poetry update
   poetry show --outdated
   ```

2. **Documentation**:
   - Keep examples up to date
   - Update API documentation
   - Review and update README

3. **Testing**:
   - Add tests for new features
   - Maintain high test coverage
   - Update CI/CD as needed

### Security

- Monitor dependencies for vulnerabilities
- Update tokens if compromised
- Review access permissions regularly

## Support

For help with:
- **PyPI**: [PyPI Help](https://pypi.org/help/)
- **ReadTheDocs**: [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- **Poetry**: [Poetry Documentation](https://python-poetry.org/docs/)
- **GitHub Actions**: [GitHub Actions Documentation](https://docs.github.com/en/actions)