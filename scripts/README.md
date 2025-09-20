# Scripts de Workflow

Esta carpeta contiene scripts de bash para desarrollo local del SDK de Datadis.

> **Nota**: La publicación es ahora **automática** con push a `main`. Estos scripts son principalmente para desarrollo local y emergencias.

## Scripts Disponibles

### 1. `quality_check.sh` - Checks de Calidad de Código

Ejecuta todos los checks de calidad: formateo, linting, type checking y tests.

```bash
# Solo verificar (no corregir automáticamente)
./scripts/quality_check.sh

# Corregir automáticamente problemas de formato
./scripts/quality_check.sh fix
```

**Qué hace:**
- Ejecuta Black para formateo de código
- Ejecuta isort para ordenar imports
- Ejecuta flake8 para linting
- Ejecuta mypy para type checking
- Ejecuta pytest para tests
- Genera reporte de coverage

### 2. `generate_docs.sh` - Generación de Documentación

Genera la documentación con Sphinx.

```bash
# Generar documentación
./scripts/generate_docs.sh

# Generar documentación limpiando build anterior
./scripts/generate_docs.sh clean
```

**Qué hace:**
- Limpia builds anteriores (si se especifica)
- Genera documentación API automáticamente
- Construye documentación HTML con Sphinx
- Proporciona información para actualizar ReadTheDocs

### 3. `build_and_publish.sh` - Build y Publicación en PyPI

Construye y publica el paquete en PyPI o TestPyPI.

```bash
# Publicar en TestPyPI (recomendado para pruebas)
./scripts/build_and_publish.sh test

# Publicar en PyPI de producción
./scripts/build_and_publish.sh prod
```

**Qué hace:**
- Limpia builds anteriores
- Ejecuta checks de calidad
- Ejecuta tests
- Construye el paquete
- Verifica el paquete
- Publica en el repositorio especificado

### 4. `complete_workflow.sh` - Workflow Completo

Ejecuta todo el workflow de desarrollo en secuencia.

```bash
# Workflow completo para TestPyPI
./scripts/complete_workflow.sh test

# Workflow completo para PyPI de producción
./scripts/complete_workflow.sh prod
```

**Qué hace:**
- Ejecuta quality checks con correcciones automáticas
- Genera documentación
- Verifica estado de git
- Construye y publica el paquete
- Proporciona instrucciones finales

## Workflow Recomendado

### Para Desarrollo Diario
```bash
# Verificar calidad del código
./scripts/quality_check.sh

# Corregir problemas automáticamente
./scripts/quality_check.sh fix
```

### Para Actualizar Documentación
```bash
# Generar documentación
./scripts/generate_docs.sh clean

# Hacer commit y push para actualizar ReadTheDocs
git add docs/
git commit -m "docs: actualizar documentación"
git push
```

### Para Publicar Nueva Versión

1. **Actualizar versión en `pyproject.toml`**
2. **Ejecutar workflow completo:**
   ```bash
   # Primero probar en TestPyPI
   ./scripts/complete_workflow.sh test

   # Si todo está bien, publicar en producción
   ./scripts/complete_workflow.sh prod
   ```

## Configuración Requerida

### Para PyPI
Configurar credenciales de PyPI:
```bash
poetry config pypi-token.pypi your-pypi-token
poetry config pypi-token.testpypi your-testpypi-token
```

### Para ReadTheDocs
1. Conectar el repositorio en ReadTheDocs.org
2. Los builds se activarán automáticamente en cada push

## Solución de Problemas

### Script no ejecutable
```bash
chmod +x scripts/*.sh
```

### Comando poetry no encontrado
```bash
# Instalar poetry
curl -sSL https://install.python-poetry.org | python3 -

# O usar pip
pip install poetry
```

### Error de dependencias
```bash
# Reinstalar dependencias
poetry install --with dev
```