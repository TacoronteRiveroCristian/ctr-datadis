# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [Sin Publicar]

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
