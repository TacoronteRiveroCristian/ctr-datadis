# 🚀 Cómo Publicar datadis-python a PyPI

## 🎯 Opciones de Publicación

### ⚡ OPCIÓN 1: Script Automatizado (MÁS FÁCIL)
```bash
./publish-project.sh
```
**¿Qué hace?**
- ✅ Ejecuta todos los tests y verificaciones
- ✅ Te pregunta qué tipo de versión quieres (patch/minor/major)
- ✅ Genera documentación automáticamente
- ✅ Crea commit y tag
- ✅ Construye y publica a PyPI
- ✅ Hace push al repositorio

### 🤖 OPCIÓN 2: GitHub Actions (MÁS PROFESIONAL)
```bash
# Método A: Por tag
git tag v0.2.0
git push origin v0.2.0
# Se dispara automáticamente

# Método B: Manual desde GitHub
# 1. Ve a: https://github.com/tu-usuario/datadis-python/actions
# 2. Selecciona "Release to PyPI"
# 3. Clic "Run workflow"
# 4. Elige tipo de versión
# 5. ¡Listo!
```

### 🛠️ OPCIÓN 3: Manual (MÁS CONTROL)
```bash
# 1. Preparación
poetry run black .
poetry run isort .
poetry run flake8 datadis_python
# poetry run pytest  # Cuando implementes tests

# 2. Versión
poetry version patch  # o minor/major

# 3. Commit y tag
git add pyproject.toml
git commit -m "chore: bump version to $(poetry version --short)"
git tag "v$(poetry version --short)"

# 4. Build
poetry build

# 5. Configurar token
source .env  # Carga PYPI_TOKEN
poetry config pypi-token.pypi $PYPI_TOKEN

# 6. Publicar
poetry publish

# 7. Push
git push origin develop
git push origin "v$(poetry version --short)"
```

## 📋 Pre-Checklist (IMPORTANTE)

Antes de publicar **cualquier versión**:

- [ ] ✅ El código está formateado (`make format`)
- [ ] ✅ No hay errores de lint (`make lint`)
- [ ] ✅ README.md está actualizado
- [ ] ✅ CHANGELOG.md tiene los cambios de esta versión
- [ ] ✅ La documentación se genera sin errores (`make docs-html`)
- [ ] ✅ No hay secretos/passwords en el código
- [ ] ✅ El token PYPI_TOKEN está en .env

## 🎛️ Tipos de Versión

```bash
# Versión actual: 0.1.0

poetry version patch    # → 0.1.1 (bugfixes)
poetry version minor    # → 0.2.0 (nuevas funcionalidades)
poetry version major    # → 1.0.0 (cambios incompatibles)

# Pre-releases (para testing):
poetry version prepatch # → 0.1.1a0
poetry version preminor # → 0.2.0a0
poetry version premajor # → 1.0.0a0
```

## 🔍 Verificar Publicación

Después de publicar, verifica:

1. **PyPI**: https://pypi.org/project/datadis-python/
2. **Instalación**: `pip install datadis-python==VERSION_NUEVA`
3. **Documentación**: https://datadis-python.readthedocs.io/
4. **GitHub Release**: Se crea automáticamente

## 🆘 Si Algo Sale Mal

### Error: "File already exists"
- No puedes sobreescribir versiones en PyPI
- Incrementa la versión y publica de nuevo

### Error: "Invalid token"
- Verifica que PYPI_TOKEN está correcto en .env
- Regenera el token en PyPI si es necesario

### Error: "Package name already taken"
- El nombre `datadis-python` parece estar disponible
- Si no, cambia el nombre en pyproject.toml

### Build fails
```bash
# Limpiar y rebuild
make clean
poetry build
```

## 🎉 Primera Publicación

Para la **primera vez**:

1. **Verifica el nombre** está disponible en PyPI
2. **Usa el script**: `./publish-project.sh`
3. **Selecciona "patch"** para ir a v0.1.1
4. **Verifica que funcione**: `pip install datadis-python`

## 🔄 Publicaciones Regulares

Para **actualizaciones**:

- **patch**: Bugfixes, correcciones menores
- **minor**: Nuevas funcionalidades compatibles
- **major**: Cambios que rompen compatibilidad

¡Tu paquete estará disponible globalmente en minutos! 🌍