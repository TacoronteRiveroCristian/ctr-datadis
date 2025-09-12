#!/bin/bash

# Script para generar documentación de datadis-python
# Se puede usar localmente o en ReadTheDocs

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

DOCS_DIR="docs"
SOURCE_DIR="datadis_python"

print_info "📚 Generando documentación para datadis-python..."

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ] || [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: No se encontró pyproject.toml o el directorio $SOURCE_DIR"
    echo "Asegúrate de ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Crear directorio docs si no existe
if [ ! -d "$DOCS_DIR" ]; then
    mkdir -p "$DOCS_DIR"
    print_info "Creado directorio $DOCS_DIR"
fi

# Generar archivos RST automáticamente
print_info "Generando archivos .rst automáticamente..."
if command -v sphinx-apidoc &> /dev/null; then
    sphinx-apidoc -o "$DOCS_DIR" "$SOURCE_DIR" --force --separate
elif command -v poetry &> /dev/null; then
    poetry run sphinx-apidoc -o "$DOCS_DIR" "$SOURCE_DIR" --force --separate
else
    echo "Error: No se encontró sphinx-apidoc ni poetry"
    exit 1
fi

print_success "Archivos .rst generados en $DOCS_DIR"

# Construir documentación HTML si conf.py existe
if [ -f "$DOCS_DIR/conf.py" ]; then
    print_info "Construyendo documentación HTML..."
    
    BUILD_DIR="$DOCS_DIR/_build/html"
    
    if command -v sphinx-build &> /dev/null; then
        sphinx-build -b html "$DOCS_DIR" "$BUILD_DIR"
    elif command -v poetry &> /dev/null; then
        poetry run sphinx-build -b html "$DOCS_DIR" "$BUILD_DIR"
    else
        echo "Error: No se encontró sphinx-build ni poetry"
        exit 1
    fi
    
    print_success "Documentación HTML generada en $BUILD_DIR"
    
    # Abrir documentación si estamos en un entorno local
    if [ -n "$DISPLAY" ] && command -v xdg-open &> /dev/null; then
        print_info "Abriendo documentación en el navegador..."
        xdg-open "$BUILD_DIR/index.html" &
    fi
else
    print_info "No se encontró conf.py, solo se generaron archivos .rst"
fi

print_success "✅ Proceso de generación de documentación completado"