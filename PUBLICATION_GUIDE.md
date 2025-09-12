# Guía de Publicación - Datadis Python SDK

Esta guía explica como generar documentación para ReadTheDocs y publicar el paquete en PyPI.

## 📋 Requisitos Previos

1. **Poetry instalado** y configurado
2. **Token de PyPI** en la variable de entorno `PYPI_TOKEN` o en el archivo `.env`
3. **Cuenta en ReadTheDocs** vinculada al repositorio GitHub
4. **Tests pasando** y código sin errores de lint

## 🚀 Publicación Automática (Recomendado)

### Opción 1: Script Local

```bash
# Ejecutar el script de publicación completo
./publish-project.sh
```

Este script:
- ✅ Ejecuta tests y verificaciones de código
- ✅ Genera documentación automáticamente
- ✅ Permite seleccionar tipo de incremento de versión
- ✅ Crea commit y tag automáticamente
- ✅ Publica en PyPI
- ✅ Hace push al repositorio

### Opción 2: GitHub Actions

```bash
# Crear y push un tag para disparar la publicación automática
git tag v1.0.0
git push origin v1.0.0
```

O usar el workflow dispatch:
1. Ve a GitHub → Actions → "Release to PyPI"
2. Haz clic en "Run workflow"
3. Selecciona el tipo de incremento de versión
4. Confirma la ejecución

## 📚 Documentación para ReadTheDocs

### Generación Automática

La documentación se genera automáticamente usando Sphinx:

```bash
# Generar documentación localmente
./generate-docs.sh

# O usando Make
make docs-html

# O manualmente
poetry run sphinx-apidoc -o docs datadis_python --force --separate
poetry run sphinx-build -b html docs docs/_build/html
```

### Configuración ReadTheDocs

El archivo `.readthedocs.yaml` ya está configurado para:
- ✅ Usar Python 3.11
- ✅ Instalar dependencias automáticamente
- ✅ Generar docs en PDF y ePub
- ✅ Usar configuración en `docs/conf.py`

**ReadTheDocs se actualiza automáticamente** cuando haces push al repositorio.

## 🐍 Publicación Manual en PyPI

Si necesitas publicar manualmente:

```bash
# 1. Incrementar versión
poetry version patch  # o minor, major, etc.

# 2. Ejecutar tests y lint
make quality

# 3. Construir paquete
poetry build

# 4. Publicar (requiere PYPI_TOKEN)
poetry config pypi-token.pypi $PYPI_TOKEN
poetry publish
```

## 📝 Comandos Útiles

```bash
# Desarrollo
make install          # Instalar dependencias
make test            # Ejecutar tests
make test-cov        # Tests con cobertura
make lint            # Verificar código
make format          # Formatear código
make quality         # Ejecutar todo: format + lint + test-cov

# Documentación
make docs-auto       # Generar archivos .rst
make docs-html       # Construir HTML
make docs-live       # Servidor en vivo con autoreload
make docs-clean      # Limpiar builds

# Publicación
make publish         # Ejecutar script de publicación
make clean          # Limpiar archivos temporales
```

## 🔧 Estructura de Archivos

```
datadis-python/
├── docs/
│   ├── conf.py              # Configuración Sphinx
│   ├── requirements.txt     # Dependencias para docs
│   ├── index.rst           # Página principal
│   └── *.rst               # Documentación generada
├── .readthedocs.yaml       # Configuración ReadTheDocs
├── .github/workflows/
│   └── release.yml         # GitHub Action para release
├── publish-project.sh      # Script de publicación completo
├── generate-docs.sh        # Script solo para documentación
├── Makefile               # Comandos simplificados
└── pyproject.toml         # Configuración del proyecto
```

## 🏷️ Versionado

El proyecto sigue [Semantic Versioning](https://semver.org/):

- **patch** (1.0.0 → 1.0.1): Bugfixes
- **minor** (1.0.0 → 1.1.0): Nuevas funcionalidades
- **major** (1.0.0 → 2.0.0): Cambios incompatibles

Pre-releases:
- **prepatch**: 1.0.0 → 1.0.1a0
- **preminor**: 1.0.0 → 1.1.0a0
- **premajor**: 1.0.0 → 2.0.0a0
- **prerelease**: 1.0.1a0 → 1.0.1a1

## 🔗 Enlaces Útiles

- **PyPI**: https://pypi.org/project/datadis-python/
- **ReadTheDocs**: https://datadis-python.readthedocs.io/
- **GitHub**: https://github.com/cristiantr/datadis-python
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)

## ⚠️ Troubleshooting

### Error: "No se encontró PYPI_TOKEN"
```bash
# Añadir al .env
echo "PYPI_TOKEN=tu_token_aqui" >> .env
```

### Error en documentación
```bash
# Limpiar y regenerar
make docs-clean
make docs-html
```

### Tests fallan
```bash
# No hay tests configurados aún - está en el TODO
# Cuando se implementen:
poetry run pytest -v
poetry run pytest --lf  # Solo tests que fallaron
```

### Problemas de formato
```bash
# Aplicar formato automáticamente
make format
```

### Errores de mypy
```bash
# Mypy está temporalmente deshabilitado debido a errores de tipos
# Para rehabilitarlo, edita el Makefile y arregla los tipos
```

## ✅ Estado Actual

**Funcionalidades Verificadas:**
- ✅ Generación de documentación automática
- ✅ Configuración ReadTheDocs completa
- ✅ Scripts de publicación automatizada
- ✅ GitHub Actions para CI/CD
- ✅ Comandos Makefile funcionando
- ✅ Formato de código (Black + isort)
- ✅ Linting (flake8)
- ⚠️  Mypy temporalmente deshabilitado (errores de tipos)
- ❌ Tests no implementados aún

## 🚨 Checklist Antes de Publicar

- [ ] Tests pasan (`make test`)
- [ ] Código formateado (`make lint`)
- [ ] CHANGELOG.md actualizado
- [ ] Versión incrementada apropiadamente
- [ ] Token PyPI configurado
- [ ] Documentación generada sin errores