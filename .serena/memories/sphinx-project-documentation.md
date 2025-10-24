# Sphinx - Project Documentation

## Documentation Structure
```
docs/
├── conf.py              # Sphinx configuration
├── index.rst           # Main page
├── quickstart.rst      # Quick guide
├── api/                # API documentation
└── _build/             # Generated documentation
```

## Sphinx Configuration (From Project)

### Active Extensions
- `sphinx.ext.autodoc` - Automatic code documentation
- `sphinx.ext.viewcode` - Source code links
- `sphinx.ext.napoleon` - Google/NumPy docstring support

### Theme and Style
- **Theme**: Generally ReadTheDocs theme
- **Language**: Spanish (matching project context)
- **Integration**: ReadTheDocs hosting

## Docstring Patterns (From Project)

### Sphinx Style (reStructuredText)
```python
def get_consumption(self, cups: str, date_from: str, date_to: str):
    """
    Get electrical consumption data for a specific CUPS.

    :param cups: CUPS code of supply point
    :type cups: str
    :param date_from: Start date in YYYY/MM format
    :type date_from: str
    :param date_to: End date in YYYY/MM format
    :type date_to: str
    :return: List of consumption data
    :rtype: List[ConsumptionData]
    :raises ValidationError: If date format is incorrect
    :raises APIError: If there's an error in Datadis API

    .. note::
       Dates must be monthly (YYYY/MM), not daily.

    .. example::
       >>> client.get_consumption("ES1234567890123456789012", "2024/01", "2024/03")
    """
```

## Documentation Building

### Local Commands
```bash
# Generate documentation
cd docs/
sphinx-build -b html . _build/html

# With Poetry
poetry run sphinx-build -b html docs/ docs/_build/html

# Clean and rebuild
make clean html  # If Makefile exists
```

### CI/CD Integration
- **ReadTheDocs**: Automatic build on commits
- **GitHub Pages**: Alternative hosting
- **Verification**: Docs builds in GitHub Actions

## Historical Problems (From Changelog)

### v0.4.2: Complete Class Documentation
- **Problem**: Incomplete docstrings
- **Solution**: Comprehensive Sphinx-style documentation
- **Result**: Integrated usage examples

### Continuous Improvements
- **v0.2.0**: V1 vs V2 comparative documentation
- **Ongoing**: Updates with new features
- **Principle**: Documentation as code
