#!/bin/bash

# Script para construir y publicar el paquete en PyPI
# Uso: ./scripts/build_and_publish.sh [test|prod]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment argument is provided
ENVIRONMENT=${1:-test}

if [[ "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Argumento inválido. Uso: $0 [test|prod]"
    exit 1
fi

print_info "Iniciando proceso de construcción y publicación para ambiente: $ENVIRONMENT"

# Step 1: Clean previous builds
print_info "Limpiando builds anteriores..."
rm -rf dist/ build/ *.egg-info/
print_success "Builds anteriores eliminados"

# Step 2: Run quality checks
print_info "Ejecutando checks de calidad..."
poetry run black datadis_python/
poetry run isort datadis_python/
poetry run flake8 datadis_python/
poetry run mypy datadis_python/
print_success "Checks de calidad completados"

# Step 3: Run tests
print_info "Ejecutando tests..."
poetry run pytest
print_success "Tests completados exitosamente"

# Step 4: Build package
print_info "Construyendo paquete..."
poetry build
print_success "Paquete construido exitosamente"

# Step 5: Check package
print_info "Verificando paquete..."
poetry run twine check dist/*
print_success "Paquete verificado"

# Step 6: Publish
if [[ "$ENVIRONMENT" == "test" ]]; then
    print_info "Publicando en TestPyPI..."
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry publish -r testpypi
    print_success "Paquete publicado en TestPyPI"
    print_warning "Para instalar desde TestPyPI: pip install -i https://test.pypi.org/simple/ ctr-datadis"
else
    print_warning "¿Estás seguro de que quieres publicar en PyPI de producción? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Publicando en PyPI..."
        poetry publish
        print_success "Paquete publicado en PyPI"
        print_success "Para instalar: pip install ctr-datadis"
    else
        print_info "Publicación cancelada"
        exit 0
    fi
fi

print_success "Proceso completado exitosamente!"
