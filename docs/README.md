# Documentación de ctr-datadis

Esta carpeta contiene la documentación completa del SDK de Datadis generada con Sphinx.

## Estructura

- `index.rst` - Página principal de la documentación
- `installation.rst` - Guía de instalación
- `quickstart.rst` - Inicio rápido con ejemplos básicos
- `api.rst` - Referencia completa de la API
- `examples.rst` - Ejemplos avanzados de uso
- `models.rst` - Documentación de modelos de datos
- `exceptions.rst` - Manejo de excepciones
- `troubleshooting.rst` - Solución de problemas
- `modules.rst` - Módulos generados automáticamente
- `conf.py` - Configuración de Sphinx

## Construir la documentación

Para construir la documentación localmente:

```bash
cd docs
poetry run sphinx-build -b html . _build/html
```

La documentación estará disponible en `_build/html/index.html`.

## Para ReadTheDocs

ReadTheDocs construirá automáticamente la documentación usando:
- El archivo `.readthedocs.yaml` en la raíz del proyecto
- Las dependencias en `docs/requirements.txt`
- La configuración en `docs/conf.py`

## Características

- ✅ Documentación automática de docstrings
- ✅ Ejemplos de código con syntax highlighting
- ✅ Navegación interactiva
- ✅ Búsqueda integrada
- ✅ Tema ReadTheDocs
- ✅ Enlaces a documentación externa (Pydantic, Requests)
- ✅ Documentación en español