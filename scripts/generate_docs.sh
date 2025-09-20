#!/bin/bash

# Script para generar documentación con Sphinx
# Uso: ./scripts/generate_docs.sh [clean]

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

CLEAN_BUILD=${1:-false}

print_info "Iniciando generación de documentación..."

# Step 1: Clean previous build if requested
if [[ "$CLEAN_BUILD" == "clean" ]]; then
    print_info "Limpiando build anterior de documentación..."
    rm -rf docs/_build/
    print_success "Build anterior eliminado"
fi

# Step 2: Check if docs directory exists
if [[ ! -d "docs" ]]; then
    print_error "Directorio 'docs' no encontrado. Asegúrate de estar en la raíz del proyecto."
    exit 1
fi

# Step 3: Generate API documentation automatically (optional)
print_info "Generando documentación de la API automáticamente..."
poetry run sphinx-apidoc -o docs/ datadis_python/ --force --separate

# Step 4: Build HTML documentation
print_info "Construyendo documentación HTML..."
poetry run sphinx-build -b html docs docs/_build

# Step 5: Check if build was successful
if [[ -f "docs/_build/index.html" ]]; then
    print_success "Documentación generada exitosamente"
    print_info "Archivo principal: docs/_build/index.html"

    # Optional: Open in browser (uncomment if desired)
    # print_info "¿Abrir documentación en el navegador? (y/N)"
    # read -r response
    # if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    #     if command -v xdg-open > /dev/null; then
    #         xdg-open docs/_build/index.html
    #     elif command -v open > /dev/null; then
    #         open docs/_build/index.html
    #     else
    #         print_warning "No se pudo abrir el navegador automáticamente"
    #     fi
    # fi
else
    print_error "Error en la generación de documentación"
    exit 1
fi

# Step 6: Information for ReadTheDocs
print_info "Para actualizar en ReadTheDocs:"
print_info "1. Haz commit y push de los cambios"
print_info "2. ReadTheDocs detectará automáticamente los cambios"
print_info "3. O ve a https://readthedocs.org/projects/tu-proyecto/ para triggerar build manual"

print_success "Proceso de documentación completado!"