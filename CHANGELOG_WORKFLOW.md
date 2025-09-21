# Workflow de Changelog

Este documento explica cómo mantener el changelog del proyecto.

## Formato

Seguimos el estándar [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) en español.

## Workflow Recomendado

### 1. Durante el Desarrollo

Mientras desarrollas una feature, **NO actualices el changelog**. En su lugar, acumula los cambios en la sección `[Sin Publicar]`:

```markdown
## [Sin Publicar]

### Añadido
- Nueva funcionalidad X
- Método Y para hacer Z

### Cambiado
- Comportamiento del método A

### Corregido
- Bug en la validación de fechas
```

### 2. Antes de un Release

Cuando vayas a hacer un release:

1. **Mueve los cambios** de `[Sin Publicar]` a una nueva sección con la versión:

```markdown
## [0.2.3] - 2024-09-21

### Añadido
- Nueva funcionalidad X
- Método Y para hacer Z

### Cambiado
- Comportamiento del método A

### Corregido
- Bug en la validación de fechas

## [Sin Publicar]

(vacío o cambios futuros)
```

2. **Actualiza la versión** en `pyproject.toml`
3. **Commit ambos cambios** juntos:

```bash
git add CHANGELOG.md pyproject.toml
git commit -m "bump: version 0.2.3"
git push origin main
```

### 3. Automatización

El sistema automáticamente:
- ✅ Detecta el cambio de versión
- ✅ Extrae el changelog de la versión actual
- ✅ Crea el GitHub Release con el changelog
- ✅ Publica en PyPI

## Tipos de Cambios

### Categorías Principales

- **Añadido** - Para nuevas funcionalidades
- **Cambiado** - Para cambios en funcionalidades existentes
- **Obsoleto** - Para funcionalidades que pronto serán eliminadas
- **Eliminado** - Para funcionalidades eliminadas
- **Corregido** - Para corrección de errores
- **Seguridad** - En caso de vulnerabilidades

### Categorías Técnicas

- **Técnico** - Para cambios internos que no afectan al usuario final

## Ejemplos de Entradas

### ✅ Buenos Ejemplos

```markdown
### Añadido
- Cliente V2 con soporte para datos de energía reactiva
- Método `get_reactive_data()` para obtener datos de energía reactiva
- Validación automática de códigos CUPS

### Cambiado
- Versión mínima de Python actualizada a 3.9+
- Mejorado el manejo de errores en autenticación

### Corregido
- Problema con caracteres especiales en nombres de distribuidoras
- Error en parseo de fechas con formato incorrecto
```

### ❌ Malos Ejemplos

```markdown
### Añadido
- Cosas nuevas
- Fixes varios
- Mejoras de rendimiento (muy vago)

### Cambiado
- Código refactorizado (no explica el impacto)
```

## Versionado Semántico

Seguimos [SemVer](https://semver.org/lang/es/):

- **MAJOR** (1.0.0): Cambios incompatibles en la API
- **MINOR** (0.1.0): Nueva funcionalidad compatible hacia atrás
- **PATCH** (0.0.1): Correcciones de errores compatibles

### Ejemplos

- Añadir cliente V2: `0.1.0` → `0.2.0` (MINOR)
- Corregir bug: `0.2.0` → `0.2.1` (PATCH)
- Cambiar interfaz de método: `0.2.1` → `1.0.0` (MAJOR)

## Consejos

### Para Desarrolladores

1. **Escribe pensando en el usuario**: ¿Qué necesita saber quien usa el SDK?
2. **Sé específico**: En lugar de "mejoras", explica qué se mejoró
3. **Menciona breaking changes**: Siempre destacar cambios incompatibles
4. **Incluye ejemplos**: Para funcionalidades complejas

### Para Releases

1. **Revisa el changelog** antes de publicar
2. **Verifica la versión** según el tipo de cambios
3. **Fecha correcta**: Usa formato YYYY-MM-DD
4. **Links funcionando**: Verifica que las referencias funcionen

## Automatización Actual

El workflow de GitHub Actions:

1. **Detecta** cambio de versión en `pyproject.toml`
2. **Extrae** la sección correspondiente del CHANGELOG.md
3. **Crea** el GitHub Release con ese contenido
4. **Publica** en PyPI automáticamente

## Mantenimiento

### Mensualmente
- Revisar que el changelog esté actualizado
- Verificar que los releases tengan changelog correcto

### Antes de Releases Importantes
- Revisar todo el changelog desde el último release mayor
- Asegurar coherencia en el formato
- Validar que no falten cambios importantes

---

**Recuerda**: Un buen changelog es la diferencia entre un proyecto profesional y uno amateur. Los usuarios lo agradecerán.
