# Estrategia de Testing - SDK Datadis

## [ESTADO] Estado Actual (Completado)

### Suite de Tests Completamente Funcional
- [OK] **243 tests pasando** (100% success rate)
- [OK] **0 tests fallando**
- [OK] **Cobertura completa** de todos los componentes del SDK

### Estructura de Tests
```
tests/
├── test_auth.py              # Tests de autenticación
├── test_client_v1.py         # Tests del cliente V1
├── test_client_v2.py         # Tests del cliente V2
├── test_models.py            # Tests de modelos Pydantic
├── test_utils.py             # Tests de utilidades
├── test_exceptions.py        # Tests de manejo de errores
├── test_integration.py       # Tests de integración
├── test_coverage_and_quality.py  # Meta-tests de calidad
├── conftest.py               # Fixtures compartidas
└── pytest.ini               # Configuración de pytest
```

## [REGLA] **REGLA FUNDAMENTAL: Test-First Development**

### **OBLIGATORIO para Nuevas Funcionalidades**
Cada nueva feature, método, clase o funcionalidad **DEBE** ir acompañada de tests antes del merge:

1. **Nuevos Métodos de Cliente**: Tests unitarios + integración
2. **Nuevos Modelos Pydantic**: Tests de validación + serialización
3. **Nuevas Utilidades**: Tests de edge cases + error handling
4. **Nuevas Excepciones**: Tests de propagación correcta
5. **Nuevos Endpoints**: Mocks + tests de respuesta

### **Flujo de Desarrollo Requerido**
```
1. Diseñar API/método
2. [OK] Escribir tests PRIMERO
3. Implementar funcionalidad
4. [OK] Tests deben pasar
5. Code review + tests review
6. Merge solo si 100% tests passing
```

## [CONFIGURACION] Configuración de Testing

### Pytest Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marcadores obligatorios
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests
    slow: Slow tests (may take several seconds)
    auth: Authentication tests
    models: Pydantic model tests
    client_v1: V1 client tests
    client_v2: V2 client tests
    utils: Utility function tests
    errors: Error handling tests
```

### Ejecutor de Tests (run_tests.py)
```bash
# Tests rápidos (solo unit)
python run_tests.py --fast

# Tests completos
python run_tests.py --full

# Tests específicos por componente
python run_tests.py --component auth
python run_tests.py --component models

# Con coverage
python run_tests.py --coverage

# Suite completa
python run_tests.py --all
```

## [PATRONES] Patrones de Testing Establecidos

### 1. **Tests de Modelos Pydantic**
```python
def test_model_validation():
    """Test validación de modelo."""
    data = {"field": "value"}
    model = MyModel(**data)
    assert model.field == "value"

def test_model_invalid_data():
    """Test datos inválidos."""
    with pytest.raises(ValidationError):
        MyModel(invalid_field="value")
```

### 2. **Tests de Cliente con Mocks**
```python
@pytest.mark.client_v1
def test_get_method_success(authenticated_v1_client):
    """Test método exitoso."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"{DATADIS_API_BASE}/endpoint",
            json=sample_response,
            status=200,
        )

        result = authenticated_v1_client.get_method()
        assert isinstance(result, list)
        assert len(result) > 0
```

### 3. **Tests de Manejo de Errores**
```python
def test_api_error_handling():
    """Test manejo de errores HTTP."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            url,
            json={"error": "Not found"},
            status=404,
        )

        with pytest.raises(APIError) as exc_info:
            client.method()
        assert "404" in str(exc_info.value)
```

## [FIXTURES] Fixtures Centralizadas (conftest.py)

### Fixtures de Autenticación
- `test_credentials`: Credenciales de prueba
- `test_token`: Token JWT válido
- `authenticated_v1_client`: Cliente V1 autenticado
- `authenticated_v2_client`: Cliente V2 autenticado

### Fixtures de Datos
- `sample_supply_data`: Datos de punto de suministro
- `sample_consumption_data`: Datos de consumo
- `sample_contract_data`: Datos de contrato
- `sample_distributor_data`: Datos de distribuidor

### Fixtures de Mocking
- `mock_auth_success`: Mock de autenticación exitosa
- `mock_v1_api_responses`: Mocks completos para API V1
- `mock_v2_api_responses`: Mocks completos para API V2

## [PROBLEMAS] Problemas Resueltos y Lecciones Aprendidas

### 1. **Validación CUPS**
- **Problema**: Formato incorrecto (16 vs 22 dígitos)
- **Solución**: Patrón correcto `^ES\d{22}[A-Z0-9]{2}$`
- **Lección**: Validar con datos reales de la API

### 2. **Error Wrapping**
- **Problema**: APIError wrapeado incorrectamente en DatadisError
- **Solución**: Propagar APIError directamente en primer intento
- **Lección**: Tests deben verificar tipos de excepción exactos

### 3. **Mock Configuration**
- **Problema**: "Not all requests executed" por retry mechanisms
- **Solución**: Configurar mocks = número de intentos (retries + 1)
- **Lección**: Alinear mocks con lógica de reintentos

### 4. **URL Encoding**
- **Problema**: Tests esperaban URLs sin encoding
- **Solución**: Verificar URLs encoded (`%2F` en lugar de `/`)
- **Lección**: Tests deben reflejar comportamiento real de HTTP

### 5. **Normalización de Texto**
- **Problema**: Fixtures con tildes vs API normalizada
- **Solución**: Usar texto normalizado en fixtures
- **Lección**: Fixtures deben simular respuesta real de API

## [CHECKLIST] Checklist para Nuevas Features

### Antes de Implementar:
- [ ] ¿Los tests están escritos ANTES de la implementación?
- [ ] ¿Se cubren casos happy path + edge cases?
- [ ] ¿Se prueban diferentes tipos de errores?
- [ ] ¿Los mocks están configurados correctamente?

### Durante Implementación:
- [ ] ¿Los tests pasan localmente?
- [ ] ¿Se mantiene 100% pass rate?
- [ ] ¿Los nuevos tests usan fixtures existentes?
- [ ] ¿Se siguen patrones establecidos?

### Antes de Merge:
- [ ] ¿Todos los tests pasan en CI?
- [ ] ¿Coverage se mantiene alto?
- [ ] ¿Tests son comprensibles y mantenibles?
- [ ] ¿Se documentaron casos especiales?

## [COMANDOS] Comandos de Testing Frecuentes

```bash
# Desarrollo día a día
python run_tests.py --fast

# Antes de commit
python run_tests.py --coverage

# Testing de nueva feature
python run_tests.py --component [component]

# Validación completa pre-release
python run_tests.py --all

# Debug de test específico
poetry run pytest tests/test_file.py::test_method -v -s
```

## [METRICAS] Métricas de Calidad

### Objetivos Mantenidos:
- **Pass Rate**: 100% (243/243 tests)
- **Coverage**: >90% (configurado en run_tests.py)
- **Performance**: Tests rápidos <30s, completos <60s
- **Mantenibilidad**: Fixtures reutilizables, patrones consistentes

---

**IMPORTANTE**: Esta estrategia de testing asegura que el SDK mantenga su robustez y confiabilidad. No se debe comprometer la calidad de tests por velocidad de desarrollo.
