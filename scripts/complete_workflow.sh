#!/bin/bash

# Script completo de workflow para desarrollo y publicación
# Uso: ./scripts/complete_workflow.sh [test|prod]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}============================================${NC}"
}

# Check if environment argument is provided
ENVIRONMENT=${1:-test}

if [[ "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Argumento inválido. Uso: $0 [test|prod]"
    exit 1
fi

print_header "WORKFLOW COMPLETO DATADIS SDK - AMBIENTE: $ENVIRONMENT"

# Step 1: Quality checks and fixes
print_header "PASO 1: QUALITY CHECKS Y CORRECCIONES"
./scripts/quality_check.sh fix

# Step 2: Generate documentation
print_header "PASO 2: GENERACIÓN DE DOCUMENTACIÓN"
./scripts/generate_docs.sh clean

# Step 3: Git status check
print_header "PASO 3: VERIFICACIÓN DE GIT"
print_info "Estado actual del repositorio:"
git status

print_warning "¿Los cambios están listos para commit? (y/N)"
read -r git_response
if [[ "$git_response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    print_info "Continuando con el workflow..."
else
    print_warning "Haz commit de los cambios antes de continuar"
    print_info "Comandos sugeridos:"
    print_info "  git add ."
    print_info "  git commit -m 'feat: descripción de los cambios'"
    print_info "  git push"
    exit 0
fi

# Step 4: Build and publish
print_header "PASO 4: BUILD Y PUBLICACIÓN"
./scripts/build_and_publish.sh $ENVIRONMENT

# Step 5: Final instructions
print_header "PROCESO COMPLETADO"
print_success "Workflow completado exitosamente!"

if [[ "$ENVIRONMENT" == "test" ]]; then
    print_info "Paquete publicado en TestPyPI"
    print_info "Para instalar: pip install -i https://test.pypi.org/simple/ ctr-datadis"
else
    print_info "Paquete publicado en PyPI"
    print_info "Para instalar: pip install ctr-datadis"
fi

print_info "Documentación generada en: docs/_build/index.html"
print_info "ReadTheDocs se actualizará automáticamente con el próximo push"

print_header "PRÓXIMOS PASOS RECOMENDADOS"
echo "1. Verificar instalación del paquete en un entorno limpio"
echo "2. Probar la documentación en ReadTheDocs"
echo "3. Crear release en GitHub con las notas de cambios"
echo "4. Actualizar el CHANGELOG.md si es necesario"
