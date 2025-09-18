# Workflow de Desarrollo - SDK Datadis

## [FLUJO] Flujo de Desarrollo Obligatorio

### **REGLA ORO: Test-First Development**
```
[PROHIBIDO] PROHIBIDO: Código sin tests
[OBLIGATORIO] OBLIGATORIO: Tests antes de implementación
```

### Workflow Estándar:
```
1. [PLANIFICAR] Planificar feature/bugfix
2. [OK] Escribir tests PRIMERO
3. 🔴 Verificar que tests fallan (TDD)
4. 💻 Implementar código mínimo para pasar tests
5. [OK] Verificar que tests pasan
6. 🔄 Refactorizar si necesario
7. [METRICAS] Ejecutar suite completa
8. [DOCUMENTAR] Code review + test review
9. [OK] Merge solo si 100% tests passing
```

## [ESTANDARES] Estándares de Código

### **Formateo y Linting (OBLIGATORIO)**
```bash
# Antes de cada commit:
poetry run black datadis_python/
poetry run isort datadis_python/
poetry run flake8 datadis_python/
poetry run mypy datadis_python/

# O usar el script integrado:
python run_tests.py --quality
```

### **Configuración Black**
- 88 caracteres por línea
- Target Python 3.8+
- Strings consistentes

### **Configuración isort**
- Perfil compatible con Black
- Separación por categorías
- Imports ordenados alfabéticamente

### **Configuración flake8**
- Max line length: 88
- Ignores: E203, E501, W503, F401, F541, E402
- Focus en errores lógicos

### **MyPy Type Checking**
- Python 3.8 compatible
- Strict mode habilitado
- `typing-extensions` para retrocompatibilidad

## [NOMENCLATURA] Convenciones de Nomenclatura

### **Python Code Style**
```python
# Clases: PascalCase
class DatadisClient:
class ConsumptionData:

# Métodos y funciones: snake_case
def get_consumption():
def validate_cups():

# Constantes: UPPER_SNAKE_CASE
API_V1_ENDPOINTS = {}
DEFAULT_TIMEOUT = 30

# Variables privadas: _leading_underscore
def _make_authenticated_request():
self._token = None
```

### **Archivos y Directorios**
```
# Archivos: snake_case
simple_client.py
text_utils.py
consumption.py

# Directorios: snake_case
client/v1/
utils/
models/
```

## [TESTING] Estándares de Testing

### **Marcadores Obligatorios**
```python
@pytest.mark.unit          # Tests unitarios rápidos
@pytest.mark.integration   # Tests de integración
@pytest.mark.slow         # Tests que toman >5 segundos
@pytest.mark.auth         # Tests de autenticación
@pytest.mark.models       # Tests de modelos Pydantic
@pytest.mark.client_v1    # Tests específicos V1
@pytest.mark.client_v2    # Tests específicos V2
@pytest.mark.utils        # Tests de utilidades
@pytest.mark.errors       # Tests de manejo de errores
```

### **Naming Convention Tests**
```python
# Estructura obligatoria
def test_[component]_[scenario]_[expected_result]():
    """Descripción clara del test."""

# Ejemplos:
def test_validate_cups_valid_format_returns_uppercase():
def test_client_authentication_empty_response_raises_error():
def test_consumption_model_invalid_data_raises_validation_error():
```

### **Estructura de Test**
```python
def test_feature():
    """Descripción clara de qué se prueba."""
    # Arrange: Preparar datos/mocks
    client = SimpleDatadisClientV1(username="test", password="test")

    # Act: Ejecutar acción
    result = client.method()

    # Assert: Verificar resultados
    assert isinstance(result, ExpectedType)
    assert result.property == expected_value
```

## [COMANDOS] Comandos de Desarrollo

### **Testing Durante Desarrollo**
```bash
# Tests rápidos (día a día)
python run_tests.py --fast

# Tests de componente específico
python run_tests.py --component auth
python run_tests.py --component models
python run_tests.py --component client_v1

# Test específico con debug
poetry run pytest tests/test_file.py::test_method -v -s

# Tests con coverage
python run_tests.py --coverage
```

### **Validación Pre-Commit**
```bash
# Calidad de código
python run_tests.py --quality

# Suite completa
python run_tests.py --all

# Solo si todo pasa → commit
```

### **Debugging y Desarrollo**
```bash
# Tests con output detallado
poetry run pytest -v -s

# Tests con breakpoints
poetry run pytest --pdb

# Coverage específico
poetry run pytest --cov=datadis_python/models tests/test_models.py
```

## [CONFIGURACION] Configuración del Entorno

### **Poetry Setup**
```bash
# Instalar dependencias de desarrollo
poetry install --with dev

# Activar shell
poetry shell

# Agregar nueva dependencia
poetry add requests pydantic

# Agregar dependencia de desarrollo
poetry add --group dev pytest black mypy
```

### **Pre-commit Hooks (Recomendado)**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests-fast
        name: Fast Tests
        entry: python run_tests.py --fast
        language: system
        pass_filenames: false

      - id: quality-checks
        name: Quality Checks
        entry: python run_tests.py --quality
        language: system
        pass_filenames: false
```

## [PROCESO] Proceso de Code Review

### **Checklist para el Autor**
- [ ] [OK] Tests escritos ANTES de implementación
- [ ] [OK] Todos los tests pasan localmente
- [ ] [OK] Calidad de código validada (black, flake8, mypy)
- [ ] [OK] Documentación actualizada si necesario
- [ ] [OK] Sin código comentado o debug prints
- [ ] [OK] Nombres descriptivos y claros

### **Checklist para el Reviewer**
- [ ] [TESTING] ¿Tests cubren casos felices y edge cases?
- [ ] [SEGURIDAD] ¿Manejo de errores es apropiado?
- [ ] 📐 ¿Sigue patrones arquitecturales del SDK?
- [ ] [MANTENIMIENTO] ¿Es mantenible y extensible?
- [ ] [DOCUMENTACION] ¿Documentación es clara?
- [ ] ⚡ ¿Performance es aceptable?

## [DEFINICION] Definición de "Done"

### **Para Features Nuevas**
- [ ] [OK] Tests unitarios + integración escritos
- [ ] [OK] Tests pasan en múltiples entornos
- [ ] [OK] Documentación actualizada
- [ ] [OK] Code review aprobado
- [ ] [OK] Sin regresiones en suite existente
- [ ] [OK] Performance aceptable

### **Para Bug Fixes**
- [ ] [OK] Test que reproduce el bug
- [ ] [OK] Fix implementado
- [ ] [OK] Test pasa después del fix
- [ ] [OK] Sin efectos secundarios
- [ ] [OK] Root cause documentado

### **Para Refactoring**
- [ ] [OK] Todos los tests existentes siguen pasando
- [ ] [OK] No hay cambios en API pública
- [ ] [OK] Performance mantenida o mejorada
- [ ] [OK] Código más limpio/mantenible

## [POLITICAS] Políticas de Calidad

### **Tolerancia Cero**
```
[PROHIBIDO] NUNCA permitir:
- Tests fallando en main branch
- Código sin tests
- Commits que rompan la build
- Secrets/keys en código
- Código comentado en production
```

### **Métricas Mínimas**
```
[REQUERIDO] REQUERIDO mantener:
- Test coverage: >90%
- Test pass rate: 100%
- Type coverage: >80%
- Performance: Tests <60s total
```

### **Dependencias**
```python
# Solo dependencias necesarias
# Evaluar impacto antes de agregar
# Mantener actualizadas (security)
# Documentar razón de inclusión
```

## [METRICAS] Métricas y Monitoring

### **CI/CD Checks**
- [OK] Tests unitarios + integración
- [OK] Calidad de código (black, flake8, mypy)
- [OK] Security scan de dependencias
- [OK] Coverage report
- [OK] Performance regression tests

### **Release Checklist**
- [ ] [METRICAS] Todos los tests pasan
- [ ] [DOCUMENTACION] CHANGELOG actualizado
- [ ] [VERSION] Version bump apropiado (semver)
- [ ] 📚 Documentación actualizada
- [ ] 🔒 Security review completado
- [ ] ⚡ Performance validada

---

**Este workflow asegura**:
- [OK] **Calidad**: Código robusto y bien probado
- [OK] **Mantenibilidad**: Estándares consistentes
- [OK] **Colaboración**: Proceso claro para el equipo
- [OK] **Confiabilidad**: Sin regresiones o bugs
- [OK] **Velocidad**: Desarrollo eficiente con buen tooling
