# Workflow de Publicación Automática

Este documento explica cómo funciona el sistema de publicación automática para el SDK de Datadis.

## Resumen del Workflow

### Un Solo Comando: Push a Main
Todo se publica automáticamente con un simple:
```bash
git push origin main
```

### Qué se Publica Automáticamente

| Servicio | Trigger | Condición |
|----------|---------|-----------|
| **ReadTheDocs** | Push a `main` | Siempre |
| **PyPI** | Push a `main` | Solo si cambió la versión |
| **GitHub Release** | Push a `main` | Solo si cambió la versión |

## Proceso Completo

### 1. Desarrollo Local
```bash
# Hacer cambios en el código
# ...

# Ejecutar quality checks
./scripts/quality_check.sh fix

# Actualizar versión en pyproject.toml (para publicar)
# version = "0.1.4"  # Cambiar aquí

# Commit y push
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main
```

### 2. Automatización en GitHub

#### Detección de Cambios
- GitHub Actions verifica si cambió la versión en `pyproject.toml`
- Si NO cambió: Solo actualiza ReadTheDocs
- Si SÍ cambió: Ejecuta pipeline completo

#### Tests y Quality Checks
- Ejecuta tests en Python 3.8, 3.9, 3.10, 3.11, 3.12
- Verifica formateo (Black, isort)
- Ejecuta linting (flake8)
- Verifica tipos (mypy)
- Genera coverage report

#### Publicación (Solo si cambió versión)
1. **TestPyPI**: Publica primero en ambiente de prueba
2. **PyPI**: Publica en producción
3. **GitHub Release**: Crea release automático con tag

#### Documentación
- ReadTheDocs se actualiza automáticamente
- Sphinx regenera toda la documentación
- Incluye API docs, ejemplos y guías

## Configuración Requerida

### 1. Secretos de GitHub
Añadir en `Settings > Secrets and variables > Actions`:

```bash
PYPI_API_TOKEN=pypi-...          # Token de PyPI
TESTPYPI_API_TOKEN=pypi-...      # Token de TestPyPI (opcional)
```

### 2. ReadTheDocs
1. Conectar repositorio en [readthedocs.org](https://readthedocs.org)
2. El archivo `.readthedocs.yml` ya está configurado
3. Builds automáticos activados

### 3. PyPI Tokens
```bash
# Generar tokens en:
# PyPI: https://pypi.org/manage/account/token/
# TestPyPI: https://test.pypi.org/manage/account/token/
```

## Workflow para Diferentes Escenarios

### Bug Fix (Sin publicar)
```bash
# Solo corregir código, NO cambiar versión
git add .
git commit -m "fix: corregir bug en autenticación"
git push origin main
# Solo se actualiza ReadTheDocs
```

### Nueva Versión
```bash
# 1. Cambiar versión en pyproject.toml
version = "0.1.5"

# 2. Commit y push
git add .
git commit -m "feat: nueva funcionalidad de datos reactivos"
git push origin main

# Se ejecuta:
# - Tests en todas las versiones de Python
# - Publicación en TestPyPI y PyPI
# - Creación de GitHub Release
# - Actualización de ReadTheDocs
```

### Solo Documentación
```bash
# Cambios solo en docs/ o README.md
git add .
git commit -m "docs: actualizar ejemplos"
git push origin main
# Solo se actualiza ReadTheDocs
```

## Scripts Locales Disponibles

### Desarrollo Diario
```bash
./scripts/quality_check.sh fix    # Corregir formato y ejecutar tests
./scripts/generate_docs.sh clean  # Generar documentación localmente
```

### Publicación Manual (Emergencias)
```bash
./scripts/complete_workflow.sh test  # Publicar en TestPyPI
./scripts/complete_workflow.sh prod  # Publicar en PyPI producción
```

## Monitoreo

### GitHub Actions
- Ver progreso en `Actions` tab del repositorio
- Logs detallados de cada paso
- Notificaciones por email si falla

### ReadTheDocs
- Panel en [readthedocs.org](https://readthedocs.org)
- Builds automáticos en cada push
- Logs de Sphinx disponibles

### PyPI
- Paquetes aparecen automáticamente
- Verificar en https://pypi.org/project/ctr-datadis/

## Solución de Problemas

### Falla la Publicación en PyPI
```bash
# Verificar secretos en GitHub
# Verificar que la versión sea única
# Revisar logs en GitHub Actions
```

### Falla ReadTheDocs
```bash
# Verificar .readthedocs.yml
# Revisar requirements.txt en docs/
# Verificar conf.py de Sphinx
```

### Tests Fallan
```bash
# Ejecutar localmente primero
./scripts/quality_check.sh

# Corregir errores antes de push
```

## Ventajas de este Workflow

1. **Automatización Completa**: Un solo push publica todo
2. **Seguridad**: Tests obligatorios antes de publicar
3. **Documentación Sincronizada**: Siempre actualizada
4. **Releases Automáticos**: Con tags y changelogs
5. **Testing Múltiple**: En todas las versiones de Python
6. **Rápido**: Solo publica si realmente hay cambios

## Recursos Adicionales

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [ReadTheDocs Configuration](https://docs.readthedocs.io/en/stable/config-file/v2.html)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

**Tip**: Siempre incrementa la versión en `pyproject.toml` cuando quieras publicar una nueva versión. El sistema detecta automáticamente los cambios de versión y activa la publicación completa.