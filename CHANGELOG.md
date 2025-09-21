# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [Sin Publicar]

### Añadido
- Archivo CHANGELOG.md para seguimiento de cambios
- Documentación de workflow de changelog

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
