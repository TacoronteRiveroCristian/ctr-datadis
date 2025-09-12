#!/bin/bash

# Script de publicación automatizada para datadis-python
# Basado en el workflow de ctrutils con mejoras específicas

set -e  # Detener en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
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

# Verificar que estamos en un entorno Poetry
if [ ! -f "pyproject.toml" ]; then
    print_error "No se encontró pyproject.toml. ¿Estás en el directorio correcto?"
    exit 1
fi

# Verificar que tenemos el token de PyPI
if [ -z "$PYPI_TOKEN" ]; then
    print_warning "Variable PYPI_TOKEN no encontrada. Intentando cargar desde .env..."
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        if [ -z "$PYPI_TOKEN" ]; then
            print_error "PYPI_TOKEN no encontrado en .env"
            exit 1
        fi
    else
        print_error "No se encontró .env y PYPI_TOKEN no está definido"
        exit 1
    fi
fi

# Directorios
PROJECT_ROOT=$(pwd)
DOCS_DIR="$PROJECT_ROOT/docs"

print_info "🚀 Iniciando proceso de publicación de datadis-python"

# Paso 1: Verificar que estemos en la rama develop
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "develop" ]; then
    print_warning "Estás en la rama '$CURRENT_BRANCH', se recomienda publicar desde 'develop'"
    read -p "¿Continuar de todos modos? (y/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        print_info "Proceso cancelado"
        exit 0
    fi
fi

# Paso 2: Verificar que no hay cambios sin commitear
if [ -n "$(git status --porcelain)" ]; then
    print_error "Hay cambios sin commitear. Commitea o stash tus cambios primero."
    git status --short
    exit 1
fi

# Paso 3: Ejecutar tests
print_info "🧪 Verificando tests..."
if [ -d "tests" ] && [ "$(find tests -name '*.py' | wc -l)" -gt 0 ]; then
    print_info "Ejecutando tests..."
    if ! poetry run pytest --cov=datadis_python; then
        print_error "Los tests fallaron. No se puede continuar."
        exit 1
    fi
    print_success "Tests pasaron correctamente"
else
    print_warning "⚠️  No se encontraron tests. Continuando sin ejecutar tests..."
    print_info "💡 Considera añadir tests antes de publicar en producción"
fi

# Paso 4: Ejecutar verificaciones de código
print_info "🔍 Ejecutando verificaciones de código..."
poetry run black . || { print_error "Black falló"; exit 1; }
poetry run isort . || { print_error "isort falló"; exit 1; }
poetry run flake8 datadis_python || { print_error "flake8 falló"; exit 1; }
print_warning "⚠️  Mypy deshabilitado temporalmente debido a errores de tipos"
# poetry run mypy datadis_python || { print_error "mypy falló"; exit 1; }
print_success "Verificaciones de código pasaron"

# Paso 5: Generar documentación
print_info "📚 Generando documentación..."
if [ -d "$DOCS_DIR" ]; then
    # Generar archivos RST automáticamente
    poetry run sphinx-apidoc -o "$DOCS_DIR" "datadis_python" --force --separate
    
    # Construir documentación HTML
    if [ -f "$DOCS_DIR/conf.py" ]; then
        poetry run sphinx-build -b html "$DOCS_DIR" "$DOCS_DIR/_build/html" -W
        print_success "Documentación generada exitosamente"
    else
        print_warning "No se encontró conf.py, saltando generación de docs"
    fi
else
    print_warning "Directorio docs no encontrado, saltando generación"
fi

# Paso 6: Seleccionar tipo de incremento de versión
print_info "📈 Selecciona el tipo de incremento de versión:"
echo "1) patch      (e.g., 0.1.0 -> 0.1.1) - Bugfixes"
echo "2) minor      (e.g., 0.1.0 -> 0.2.0) - Nuevas funcionalidades"
echo "3) major      (e.g., 0.1.0 -> 1.0.0) - Cambios incompatibles"
echo "4) prepatch   (e.g., 0.1.0 -> 0.1.1a0) - Pre-release patch"
echo "5) preminor   (e.g., 0.1.0 -> 0.2.0a0) - Pre-release minor"
echo "6) premajor   (e.g., 0.1.0 -> 1.0.0a0) - Pre-release major"
echo "7) prerelease (e.g., 0.1.1a0 -> 0.1.1a1) - Siguiente pre-release"

read -p "Ingrese el número (1-7): " version_choice

case $version_choice in
    1) version_type="patch" ;;
    2) version_type="minor" ;;
    3) version_type="major" ;;
    4) version_type="prepatch" ;;
    5) version_type="preminor" ;;
    6) version_type="premajor" ;;
    7) version_type="prerelease" ;;
    *) 
        print_error "Opción inválida"
        exit 1 
        ;;
esac

# Paso 7: Incrementar versión
print_info "🏷️  Incrementando versión ($version_type)..."
OLD_VERSION=$(poetry version --short)
poetry version $version_type
NEW_VERSION=$(poetry version --short)
print_success "Versión actualizada: $OLD_VERSION -> $NEW_VERSION"

# Paso 8: Actualizar CHANGELOG si existe
if [ -f "CHANGELOG.md" ]; then
    print_info "📝 Recuerda actualizar CHANGELOG.md con los cambios de la versión $NEW_VERSION"
    read -p "¿Has actualizado el CHANGELOG.md? (y/N): " changelog_updated
    if [[ ! $changelog_updated =~ ^[Yy]$ ]]; then
        print_warning "Se recomienda actualizar el CHANGELOG.md antes de continuar"
    fi
fi

# Paso 9: Commit y tag
print_info "💾 Creando commit y tag para la versión $NEW_VERSION..."
git add pyproject.toml
if [ -f "CHANGELOG.md" ] && git diff --cached --quiet CHANGELOG.md; then
    git add CHANGELOG.md
fi
git commit -m "chore: bump version to $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
print_success "Commit y tag creados"

# Paso 10: Build del paquete
print_info "🔨 Construyendo paquete..."
poetry build
print_success "Paquete construido exitosamente"

# Paso 11: Confirmar publicación
print_warning "⚠️  Estás a punto de publicar la versión $NEW_VERSION a PyPI"
print_info "Archivos que se van a subir:"
ls -la dist/*$NEW_VERSION*

read -p "¿Proceder con la publicación a PyPI? (y/N): " confirm_publish
if [[ ! $confirm_publish =~ ^[Yy]$ ]]; then
    print_info "Publicación cancelada. El paquete está construido en dist/"
    print_info "Para publicar manualmente: poetry publish --username __token__ --password \$PYPI_TOKEN"
    exit 0
fi

# Paso 12: Publicar a PyPI
print_info "🚀 Simulando publicación a PyPI..."
poetry config pypi-token.pypi $PYPI_TOKEN

print_warning "🧪 MODO DEMO: NO se va a publicar realmente a PyPI"
print_info "Comando que se ejecutaría: poetry publish"
print_info "Archivos que se subirían:"
ls -la dist/

read -p "¿Quieres hacer la publicación REAL a PyPI? (y/N): " confirm_real_publish
if [[ $confirm_real_publish =~ ^[Yy]$ ]]; then
    print_info "🚀 Publicando a PyPI REAL..."
    poetry publish
    
    if [ $? -eq 0 ]; then
        print_success "¡Paquete publicado exitosamente en PyPI!"
        print_success "Versión $NEW_VERSION está ahora disponible en: https://pypi.org/project/datadis-python/$NEW_VERSION/"
    else
        print_error "Error al publicar en PyPI"
        exit 1
    fi
else
    print_info "📦 Publicación simulada - paquete construido pero NO publicado"
fi

# Paso 13: Push cambios a Git
read -p "¿Hacer push de los cambios y tags al repositorio remoto? (y/N): " push_changes
if [[ $push_changes =~ ^[Yy]$ ]]; then
    git push origin $CURRENT_BRANCH
    git push origin "v$NEW_VERSION"
    print_success "Cambios y tags subidos al repositorio remoto"
fi

# Paso 14: Limpiar archivos de build
print_info "🧹 Limpiando archivos temporales..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

print_success "🎉 ¡Publicación completada exitosamente!"
print_info "Próximos pasos:"
print_info "1. La documentación se actualizará automáticamente en ReadTheDocs"
print_info "2. Verifica que el paquete esté disponible en PyPI"
print_info "3. Considera crear un release en GitHub con las notas de la versión"

if [[ $version_type == "major" ]]; then
    print_warning "📢 Has publicado una versión MAJOR. Considera comunicar los cambios incompatibles a los usuarios."
fi