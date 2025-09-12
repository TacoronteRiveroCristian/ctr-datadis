# Guía de Seguridad para PyPI

## 🔐 Gestión Segura de Tokens

### Token de PyPI
Tu token de PyPI (`PYPI_TOKEN`) es **extremadamente sensible**:

- ✅ **Manténlo en `.env`** (nunca en el código)
- ✅ **Añade `.env` a `.gitignore`** 
- ✅ **Usa scoped tokens** (tokens específicos para este proyecto)
- ✅ **Rota el token** periódicamente
- ❌ **NUNCA** lo compartas por email/chat/screenshot

### Configuración en GitHub Actions
Para automatizar con GitHub Actions:

1. Ve a tu repo → Settings → Secrets and variables → Actions
2. Añade `PYPI_TOKEN` como secret
3. El workflow ya está configurado para usarlo

### Configuración Local Segura
```bash
# Método 1: Archivo .env (recomendado)
echo "PYPI_TOKEN=tu_token_aqui" >> .env

# Método 2: Variable de entorno temporal
export PYPI_TOKEN="tu_token_aqui"

# Método 3: Poetry keyring (más seguro para uso frecuente)
poetry config pypi-token.pypi tu_token_aqui
```

## 🚀 Proceso de Publicación Seguro

### Antes de Publicar - CHECKLIST
- [ ] ✅ Tests pasando
- [ ] ✅ Documentación actualizada
- [ ] ✅ CHANGELOG.md actualizado
- [ ] ✅ Versión incrementada apropiadamente
- [ ] ✅ No hay secretos/tokens en el código
- [ ] ✅ Archivos sensibles en `.gitignore`

### Publicación por Primera Vez
```bash
# 1. Verificar que el nombre no esté tomado
pip search datadis-python  # O buscar en pypi.org

# 2. Hacer una publicación de test (opcional)
# Usa TestPyPI primero para probar

# 3. Publicación real
./publish-project.sh
```

### Publicaciones Posteriores
- Siempre incrementa la versión (no puedes sobreescribir)
- Usa semantic versioning
- Documenta los cambios en CHANGELOG.md

## ⚠️ Qué NO Hacer

### ❌ Errores Comunes
1. **Publicar con secretos/passwords** en el código
2. **Sobreescribir versiones** (no es posible)
3. **Publicar sin tests** 
4. **Usar tokens con permisos excesivos**
5. **Compartir tokens** por canales inseguros

### ❌ Contenido que NO Debe Ir en PyPI
- Archivos `.env` con secrets
- Claves API hardcodeadas
- Bases de datos o archivos de configuración específicos
- Archivos temporales o de testing

## 🛡️ Recuperación de Problemas

### Si Comprometes un Token
1. **Inmediatamente** revoca el token en PyPI
2. Genera un nuevo token
3. Actualiza tus secrets en GitHub Actions
4. Actualiza tu `.env` local

### Si Publicas por Error
- **No puedes borrar** versiones de PyPI
- Publica una nueva versión con correcciones
- Usa "yanked releases" si es crítico (no recomendado)

### Si Hay Problemas de Seguridad
1. Contacta a PyPI para reportar el problema
2. Publica una nueva versión con la corrección
3. Documenta el fix en CHANGELOG.md
4. Considera avisar a los usuarios

## 📋 Mantenimiento Regular

### Revisión Mensual
- [ ] Revisar logs de descargas en PyPI
- [ ] Verificar que no hay vulnerabilidades reportadas
- [ ] Actualizar dependencias si es necesario
- [ ] Rotar tokens si es necesario

### Revisión Anual
- [ ] Revisar y limpiar releases antiguos
- [ ] Actualizar metadata del paquete
- [ ] Revisar toda la documentación
- [ ] Evaluar si el paquete sigue siendo necesario

## 🔗 Enlaces Útiles

- **PyPI Security**: https://pypi.org/security/
- **Token Management**: https://pypi.org/manage/account/token/
- **Packaging Security**: https://packaging.python.org/guides/securing-package-distribution/