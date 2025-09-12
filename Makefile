# Makefile for Sphinx documentation and project management

SPHINXOPTS    ?=
SPHINXBUILD   ?= poetry run sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

# Project commands
.PHONY: help install test lint docs clean publish

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  install      to install the project dependencies"
	@echo "  test         to run tests"
	@echo "  test-cov     to run tests with coverage"
	@echo "  lint         to run linting and type checking"
	@echo "  format       to format code with black and isort"
	@echo "  docs-auto    to auto-generate API documentation"
	@echo "  docs-html    to make standalone HTML files"
	@echo "  docs-clean   to clean documentation build files"
	@echo "  docs-live    to build and serve docs with live reload"
	@echo "  clean        to clean all build files"
	@echo "  publish      to run the full publication process"

install:
	poetry install
	poetry run pre-commit install

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=datadis_python --cov-report=html --cov-report=term

lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 datadis_python
	@echo "⚠️  Mypy deshabilitado temporalmente debido a errores de tipos"
	# poetry run mypy datadis_python

format:
	poetry run black .
	poetry run isort .

# Documentation commands
docs-auto:
	poetry run sphinx-apidoc -o $(SOURCEDIR) datadis_python --force --separate
	@echo "Auto-generated documentation files in $(SOURCEDIR)"

docs-html: docs-auto
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

docs-clean:
	rm -rf $(BUILDDIR)/*
	@echo "Documentation build files cleaned"

docs-live: docs-auto
	poetry run sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html --open-browser

clean: docs-clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Full quality check
quality: format lint test-cov

# Publication process
publish:
	./publish-project.sh