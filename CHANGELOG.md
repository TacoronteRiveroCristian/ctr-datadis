# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [0.4.3] - 2025-01-23

### Corregido
- **Resolución de conflictos de documentación**: Integración exitosa de mejoras en documentación de ejemplos
  - Resolución de conflictos en `docs/examples.rst`, `docs/index.rst` y `docs/quickstart.rst`
  - Preservación de estructura completa de análisis anual en ejemplos
  - Mantenimiento de formato mensual YYYY/MM en toda la documentación
  - Unificación de documentación conservando funcionalidad completa de validación y manejo de errores V2

### Técnico
- Merge exitoso de rama `docs/improve-examples` a `develop`
- Resolución manual de conflictos manteniendo coherencia en documentación
- Working tree limpio sin conflictos pendientes

## [0.4.2] - 2025-01-22

### Añadido
- **Documentación completa de clases**: Implementación comprehensiva de docstrings en estilo Sphinx para todas las clases del SDK
  - Documentación detallada de modelos Pydantic con ejemplos de uso
  - Docstrings completos para clientes V1 y V2 con parámetros y tipos explicados
  - Documentación de utilidades HTTP, validadores y conversores de tipos
  - Guías de uso y casos de ejemplo integrados en la documentación de código
- **Validación robusta de CUPS**: Restauración completa de validación de formato CUPS en el SDK
  - Función `validate_cups()` completamente documentada y funcional
  - Validación de formato ES + 20-22 caracteres alfanuméricos
  - Mensajes de error descriptivos y ejemplos de uso correcto
  - Integración con conversores de tipos para validación automática

### Cambiado
- **Actualización de documentación**: Mejora significativa en la calidad de la documentación técnica
  - Ejemplos de código actualizados en quickstart.rst e index.rst
  - Documentación de API más clara con casos de uso específicos
  - Mejores explicaciones de parámetros y tipos de retorno
- **Validación de tipos de punto**: Ampliación del soporte para tipos de punto 1-5
  - Soporte añadido para tipo 5 (servicios auxiliares alternativos)
  - Actualización de mensajes de error para incluir todos los tipos válidos
  - Tests actualizados para reflejar el nuevo rango de validación

### Corregido
- **Resolución de conflictos de merge**: Integración exitosa de cambios de documentación
  - Resolución de conflictos en `type_converters.py` y `validators.py`
  - Mantenimiento de funcionalidad completa de validación CUPS
  - Preservación de compatibilidad hacia atrás en todos los métodos
- **Tests actualizados**: Corrección de tests para reflejar comportamiento actual
  - Test de validación CUPS actualizado para verificar formato correcto
  - Tests de tipos de punto actualizados para nuevo rango válido (1-5)
  - Suite completa de 343 tests pasando sin errores

### Técnico
- Merge exitoso de rama `docs/update-class-docstring` a `develop`
- Pre-commit hooks funcionando correctamente con validación completa
- Cobertura de código mantenida con documentación mejorada
- Integración continua estable con todas las verificaciones pasando

## [0.4.1] - 2025-09-22

### Cambiado
- **Validación CUPS eliminada**: Remoción completa de validación de formato CUPS en clientes V1 y V2
  - Eliminada función `validate_cups()` de `utils/validators.py`
  - `convert_cups_parameter()` ahora solo normaliza sin validar formato
  - Clientes V1 y V2 aceptan cualquier CUPS, delegando validación a API Datadis
  - Mejora robustez ante futuros cambios en formato CUPS oficial

### Corregido
- **Tests actualizados**: Tests adaptados para no esperar `ValidationError` por formato CUPS
  - 10 archivos de código modificados
  - Reducción significativa de líneas de código de validación (234 líneas eliminadas, 76 añadidas)
  - Mayor flexibilidad en aceptación de formatos CUPS
- **Dependencia twine actualizada**: Actualización de pyproject.toml para incluir twine 5.0.0

### Técnico
- Simplificación de la arquitectura de validación
- Delegación de responsabilidad de validación CUPS a la API oficial
- Mantenimiento de normalización de texto para caracteres especiales

## [0.4.0] - 2025-09-22

### Añadido
- **Validación de fechas mensuales para SimpleDatadisClientV2**: Implementación completa de validación de fechas mensuales para el cliente V2
  - Soporte para tipos flexibles: `str`, `datetime`, y `date` para fechas
  - Soporte para `str` e `int` para códigos numéricos
  - Conversión automática a formato API (`YYYY/MM`)
  - Validación estricta solo para fechas mensuales
- **Suite de tests comprehensiva para V2**: 19 casos de prueba específicos
  - Tests de rechazo de fechas diarias (string y datetime/date)
  - Tests de aceptación de fechas mensuales
  - Tests de conversión y preservación de datos
  - Tests de casos edge y extremos
  - Tests de validación de consistencia
- Nuevo archivo `tests/test_monthly_date_validation_v2.py`

### Cambiado
- **Refactorización del Cliente V2**: Migración de validación directa a conversores de tipos flexibles
  - `datadis_python/client/v2/simple_client.py` actualizado
  - Métodos actualizados: `get_consumption`, `get_max_power`, `get_reactive_data`
  - Cambio de `validate_date_range()` a `convert_date_range_to_api_format()`
- **Comportamiento V2 consistente con V1**: Unificación de validación de fechas entre ambas versiones
- **Mensajes de error mejorados**: Mensajes claros y orientativos para usuarios

### Corregido
- **Issue #3**: Validación de fechas mensuales faltante en SimpleDatadisClientV2
- **Rechazo de fechas con días específicos**: API V2 ahora rechaza correctamente fechas como `2024/01/15`
- **Aceptación de fechas mensuales válidas**: API V2 acepta correctamente fechas como `2024/01`
- **Conversión automática de datetime**: Conversión correcta de objetos datetime del primer día del mes

### Técnico
- Integración completa con branch `fix/v2-monthly-validation`
- Merge exitoso a branch `develop`
- Control de calidad completo: black, isort, flake8, mypy, pytest (74/74 tests passing)
- Cobertura de código mantenida
- Implementación lista para producción

## [0.3.1] - 2025-09-21

### Corregido
- **Validación de fechas API V1**: Corrección de la validación de fechas para aceptar solo formato mensual YYYY/MM
  - Cambio de `format_type` de "daily" a "monthly" en `SimpleDatadisClientV1`
  - Validación estricta que rechaza fechas con días específicos
  - Mensajes de error claros para orientar a usuarios sobre el formato correcto
  - Tests exhaustivos para validación de fechas mensuales (222 tests adicionales)
  - README actualizado con ejemplos correctos y advertencias sobre formato
  - Corrección de fixture `date_range` en tests para usar formato mensual

### Técnico
- Resolución del issue #2: Error en validación de fechas
- Mejoras en `type_converters.py` para validación robusta de fechas mensuales
- Nuevo archivo de tests `test_monthly_date_validation.py` con cobertura completa

## [0.3.0] - 2025-09-21

### Añadido
- **Parámetros Flexibles**: Soporte para tipos Python nativos en todos los métodos del cliente
  - Fechas: Acepta `datetime` y `date` objects además de strings
  - Números: Acepta `int` y `float` para measurement_type, point_type, etc.
  - Distributor codes: Acepta `int` además de string
- Módulo `type_converters` con conversión automática y validación robusta
- Tests exhaustivos para todas las conversiones de tipos (24 tests específicos)
- Ejemplo demostrativo `example_flexible_params.py`

### Cambiado
- Documentación actualizada con ejemplos de tipos flexibles
- README.md ampliado con sección de "Tipos de Parámetros Flexibles"
- Signaturas de métodos actualizadas con Union types para mayor flexibilidad

### Técnico
- 100% compatibilidad hacia atrás mantenida
- Validación automática de todos los tipos de parámetros
- Cobertura completa de tests (324 tests pasando)

## [0.2.5] - 2025-09-21

### Cambiado
- Estado de desarrollo actualizado a "Production/Stable" en PyPI
- Enlaces de homepage actualizados en pyproject.toml
- Versiones de GitHub Actions actualizadas para mejor compatibilidad SSL

### Técnico
- Workflow de publicación mejorado con verificación obligatoria de CHANGELOG
- Actualización de actions/setup-python@v5 y snok/install-poetry@v1.4.1

## [0.2.4] - 2025-09-21

### Corregido
- Validación de CUPS actualizada para soportar formatos reales españoles
- Referencias a CUPS obsoletos corregidas en tests

## [0.2.3] - 2025-09-21

### Añadido
- Archivo CHANGELOG.md para seguimiento de cambios
- Documentación completa de workflow de changelog
- GitHub Actions actualizado para incluir changelog en releases

### Corregido
- Badge de tests en README.md con URLs correctas
- Triggers de workflow para incluir cambios de documentación

## [0.2.2] - 2025-09-21

### Añadido
- Documentación completamente traducida al español para PyPI
- Keywords en español: energia, consumo, electricidad, españa, cups, distribuidora
- Ejemplos de código con comentarios en español

### Cambiado
- README.md completamente en español
- Descripción del proyecto en pyproject.toml actualizada
- Mejor discoverability para desarrolladores hispanohablantes

## [0.2.1] - 2025-09-21

### Cambiado
- Versión mínima de Python actualizada a 3.9+ para mayor compatibilidad
- Workflows de GitHub Actions optimizados para múltiples versiones de Python

### Corregido
- Problemas de compatibilidad con Python 3.8 en CI/CD
- Archivo poetry.lock regenerado para consistencia de dependencias
- Permisos de GitHub Actions para creación de releases

## [0.2.0] - 2025-09-21

### Añadido
- **Cliente V2** (`SimpleDatadisClientV2`) con soporte para datos de energía reactiva
- Método `get_reactive_data()` para obtener datos de energía reactiva
- Documentación completa para el nuevo cliente V2 en Sphinx
- Comparativa entre clientes V1 y V2 en documentación
- Tests comprehensivos para el cliente V2 (100+ tests adicionales)
- Workflow de publicación automática en PyPI
- Scripts de desarrollo automatizados

### Cambiado
- Estructura de documentación mejorada con secciones para ambos clientes
- README actualizado con ejemplos del cliente V2
- Arquitectura de documentación reorganizada

### Técnico
- Nuevos modelos Pydantic para datos de energía reactiva
- Endpoints V2 de la API de Datadis integrados
- Cobertura de tests ampliada a 298 tests
- GitHub Actions configurado para CI/CD completo

## [0.1.3] - 2025-09-10

### Añadido
- Implementación completa del cliente Datadis API v1
- Modelos Pydantic comprehensivos para todos los tipos de datos
- Jerarquía de excepciones personalizada para manejo de errores
- Utilidades de normalización de texto para caracteres españoles
- Type hints en todo el código
- Documentación comprehensiva con Sphinx
- Workflow de publicación en PyPI

### Cambiado
- Manejo de errores mejorado con mensajes de excepción detallados
- Gestión optimizada de tokens de autenticación
- Estructura de proyecto limpia con documentación optimizada

### Corregido
- Problemas de codificación de texto con acentos españoles y caracteres especiales
- Parseo de respuestas API para todos los tipos de endpoints
- Conflictos de nombre de paquete resueltos (publicado como ctr-datadis)

## [0.1.0] - 2025-09-01

### Añadido
- Lanzamiento inicial del SDK Python de Datadis
- Implementación básica del cliente para la API de Datadis
- Soporte para puntos de suministro, consumo y datos de distribuidora
- Manejo de autenticación con renovación automática de token
- Modelos Pydantic type-safe para respuestas de API
- Jerarquía de excepciones personalizada
- Integración con ReadTheDocs

### Seguridad
- Manejo seguro de tokens con expiración automática
- Comunicación solo HTTPS con la API de Datadis

### Limitaciones Conocidas
- Disponibilidad de datos limitada a los últimos 2 años (limitación de la API de Datadis)
- Formato de fecha mensual requerido para la mayoría de endpoints
- Código de distribuidora requerido para la mayoría de operaciones

---

## Tipos de Cambios

- **Añadido** para nuevas funcionalidades.
- **Cambiado** para cambios en funcionalidades existentes.
- **Obsoleto** para funcionalidades que pronto serán eliminadas.
- **Eliminado** para funcionalidades eliminadas.
- **Corregido** para corrección de errores.
- **Seguridad** en caso de vulnerabilidades.
- **Técnico** para cambios internos que no afectan al usuario final.
