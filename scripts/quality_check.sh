#!/bin/bash

# Script para ejecutar todos los checks de calidad de código
# Uso: ./scripts/quality_check.sh [fix]

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

FIX_ISSUES=${1:-false}

print_info "Iniciando checks de calidad de código..."

# Step 1: Check if we should fix issues automatically
if [[ "$FIX_ISSUES" == "fix" ]]; then
    print_info "Modo automático: se corregirán los problemas encontrados"

    # Format code with black
    print_info "Formateando código con Black..."
    poetry run black datadis_python/
    print_success "Código formateado"

    # Sort imports with isort
    print_info "Ordenando imports con isort..."
    poetry run isort datadis_python/
    print_success "Imports ordenados"
else
    print_info "Modo verificación: se mostrarán los problemas sin corregir"

    # Check formatting with black
    print_info "Verificando formato con Black..."
    if poetry run black --check datadis_python/; then
        print_success "Formato correcto"
    else
        print_warning "Problemas de formato encontrados. Ejecuta con 'fix' para corregir."
    fi

    # Check import sorting with isort
    print_info "Verificando orden de imports con isort..."
    if poetry run isort --check-only datadis_python/; then
        print_success "Imports correctamente ordenados"
    else
        print_warning "Problemas en orden de imports. Ejecuta con 'fix' para corregir."
    fi
fi

# Step 2: Lint with flake8 (always check, can't auto-fix)
print_info "Ejecutando linting con flake8..."
if poetry run flake8 datadis_python/; then
    print_success "Linting pasado"
else
    print_error "Problemas de linting encontrados. Revisa manualmente."
fi

# Step 3: Type checking with mypy
print_info "Verificando tipos con mypy..."
if poetry run mypy datadis_python/; then
    print_success "Type checking pasado"
else
    print_error "Problemas de tipos encontrados. Revisa manualmente."
fi

# Step 4: Run tests
print_info "Ejecutando tests..."
if poetry run pytest; then
    print_success "Todos los tests pasaron"
else
    print_error "Algunos tests fallaron"
    exit 1
fi

# Step 5: Coverage check (optional)
print_info "Ejecutando tests con coverage..."
if poetry run pytest --cov=datadis_python --cov-report=term-missing; then
    print_success "Coverage completado"
else
    print_warning "Problemas con el coverage"
fi

print_success "Todos los checks de calidad completados!"

if [[ "$FIX_ISSUES" != "fix" ]]; then
    print_info "Para corregir automáticamente problemas de formato: ./scripts/quality_check.sh fix"
fi