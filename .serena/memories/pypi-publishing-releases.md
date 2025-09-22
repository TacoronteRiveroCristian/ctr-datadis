# PyPI - Publishing and Releases

## PyPI Configuration (pyproject.toml)

### Package Metadata
- **Name**: `ctr-datadis` (due to naming conflict)
- **Description**: In Spanish for Hispanic audience
- **Keywords**: energia, consumo, electricidad, españa, cups, distribuidora
- **Classification**: Production/Stable (since v0.2.5)
- **Python**: Requires >=3.9 (established v0.2.1)

### Project URLs
- **Homepage**: GitHub repository
- **Documentation**: ReadTheDocs
- **Repository**: GitHub repository
- **Issues**: GitHub issues

## Release Process (Automated)

### GitHub Actions Workflow
1. **Trigger**: Create release on GitHub
2. **Verification**: CHANGELOG.md must be updated
3. **Build**: `poetry build` creates wheel and tarball
4. **Publish**: `poetry publish` with PYPI_API_TOKEN
5. **Notification**: Automatic release notes

### Pre-Release Checklist
- [ ] CHANGELOG.md updated with new version
- [ ] Tests passing (343/343)
- [ ] Documentation updated
- [ ] Version bump in pyproject.toml
- [ ] Semantic tag (v0.4.2)

## Semantic Versioning (Project Pattern)

### Release History
- **v0.1.0**: Initial release
- **v0.2.0**: V2 client + reactive energy (MINOR)
- **v0.3.0**: Flexible parameters (MINOR)
- **v0.4.0**: V2 monthly date validation (MINOR)
- **v0.4.1**: Remove CUPS validation (PATCH - but breaking)
- **v0.4.2**: Restore CUPS validation + docs (PATCH)

### Versioning Criteria
- **MAJOR**: Breaking changes in public API
- **MINOR**: New features without breaking changes
- **PATCH**: Bug fixes and documentation

## Resolved Historical Problems

### v0.2.1: Python Compatibility
- **Problem**: CI/CD failing on Python 3.8
- **Solution**: Minimum Python 3.9+
- **Lesson**: Testing on multiple Python versions

### v0.2.3: CHANGELOG Automation
- **Problem**: Releases without documenting changes
- **Solution**: Mandatory CHANGELOG.md in workflow
- **Benefit**: Complete traceability

### v0.2.5: SSL Issues
- **Problem**: GitHub Actions with SSL errors
- **Solution**: Update actions to recent versions
- **Maintenance**: Review actions periodically

## Multi-Language Distribution
- **PyPI Description**: Spanish and English
- **Keywords**: Focus on Hispanic market
- **Documentation**: Primarily Spanish
- **Code**: Spanish comments, English variables
