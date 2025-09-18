# Test Suite Documentation - Datadis Python SDK

Esta documentación describe la suite de tests comprensiva para el SDK de Python de Datadis, diseñada para garantizar la calidad, confiabilidad y mantenibilidad del código.

## Estructura de Tests

```
tests/
├── conftest.py                    # Configuración global y fixtures
├── test_auth.py                   # Tests de autenticación y sesiones
├── test_client_v1.py             # Tests del cliente V1
├── test_client_v2.py             # Tests del cliente V2
├── test_exceptions.py             # Tests de manejo de errores
├── test_integration.py            # Tests de integración end-to-end
├── test_models.py                 # Tests de modelos Pydantic
├── test_utils.py                  # Tests de funciones utilitarias
├── test_coverage_and_quality.py  # Tests de calidad y cobertura
├── pytest.ini                    # Configuración de pytest
├── run_tests.py                  # Script de ejecución de tests
└── README.md                     # Esta documentación
```

## Categorías de Tests

### 🏃 Tests Unitarios (`unit`)
Tests rápidos y aislados que validan funcionalidades específicas:
- **Modelos Pydantic**: Validación, serialización, deserialización
- **Autenticación**: Login, tokens, renovación
- **Utilidades**: Validadores, normalización de texto, HTTP client
- **Excepciones**: Jerarquía de errores, propagación

### 🔗 Tests de Integración (`integration`)
Tests que validan la interacción entre componentes:
- **Workflows completos**: Auth → Supplies → Consumption → Contracts
- **Compatibilidad V1/V2**: Mismos datos, diferentes formatos
- **Recuperación de errores**: Reintentos, renovación de tokens
- **Escenarios reales**: Múltiples suministros, gestión de propiedades

### 🐌 Tests Lentos (`slow`)
Tests que pueden tomar más tiempo:
- **Performance**: Benchmarks, múltiples requests
- **Datasets grandes**: Manejo de muchos registros
- **Timeouts**: Escenarios de tiempo agotado

### [COMPONENTES] Tests por Componente
Tests organizados por área funcional:
- `auth`: Autenticación y manejo de sesiones
- `models`: Validación de modelos Pydantic
- `client_v1`: Cliente V1 específico
- `client_v2`: Cliente V2 específico
- `utils`: Funciones utilitarias
- `errors`: Manejo de errores

## Ejecución de Tests

### Método Rápido
```bash
# Tests unitarios rápidos
python run_tests.py --fast

# Tests de un componente específico
python run_tests.py --component auth
python run_tests.py --component models
```

### Método Completo
```bash
# Todos los tests
python run_tests.py --full

# Tests con coverage
python run_tests.py --coverage

# Suite completa (tests + quality checks)
python run_tests.py --all
```

### Método Manual con pytest
```bash
# Tests básicos
poetry run pytest

# Tests con coverage
poetry run pytest --cov=datadis_python --cov-report=html

# Tests específicos
poetry run pytest -m unit                    # Solo unitarios
poetry run pytest -m integration             # Solo integración
poetry run pytest -m "auth and not slow"     # Auth rápidos
poetry run pytest tests/test_models.py       # Solo modelos
```

## Configuración y Fixtures

### Fixtures Principales (`conftest.py`)

#### Credenciales y Autenticación
- `test_credentials`: Credenciales de prueba
- `test_token`: Token JWT de prueba
- `mock_auth_success`: Mock de autenticación exitosa
- `mock_auth_failure`: Mock de autenticación fallida

#### Clientes
- `v1_client`: Cliente V1 sin autenticar
- `v2_client`: Cliente V2 sin autenticar
- `authenticated_v1_client`: Cliente V1 ya autenticado
- `authenticated_v2_client`: Cliente V2 ya autenticado

#### Datos de Prueba
- `sample_supply_data`: Datos de suministro de ejemplo
- `sample_consumption_data`: Datos de consumo de ejemplo
- `sample_contract_data`: Datos de contrato de ejemplo
- `sample_max_power_data`: Datos de potencia máxima
- `sample_distributor_data`: Datos de distribuidor

#### Helpers de Validación
- `assert_valid_cups`: Validador de códigos CUPS
- `assert_valid_date_format`: Validador de formato de fecha
- `assert_valid_time_format`: Validador de formato de hora

### Estrategia de Mocking

Todos los tests usan mocking completo de HTTP requests:

```python
# Ejemplo de mock en test
with responses.RequestsMock() as rsps:
    rsps.add(
        responses.GET,
        f"{DATADIS_API_BASE}/get-supplies",
        json=sample_data,
        status=200
    )

    result = client.get_supplies()
    assert len(result) > 0
```

## Coverage y Calidad

### Métricas de Coverage
- **Target**: >95% de cobertura de código
- **Incluye**: Todo el código en `datladis_python/`
- **Excluye**: Tests, ejemplos, documentación

### Reportes de Coverage
```bash
# Generar reporte HTML
poetry run pytest --cov=datadis_python --cov-report=html
# Ver en: htmlcov/index.html

# Reporte en terminal
poetry run pytest --cov=datadis_python --cov-report=term-missing

# Reporte JSON
poetry run pytest --cov=datadis_python --cov-report=json
```

### Quality Checks
El script `run_tests.py --quality` ejecuta:
- **Black**: Formato de código
- **isort**: Orden de imports
- **flake8**: Linting
- **mypy**: Type checking

## Casos de Test Importantes

### 1. Validación de Modelos Pydantic

```python
def test_consumption_data_validation(sample_consumption_data):
    # Test creación exitosa
    consumption = ConsumptionData(**sample_consumption_data)
    assert consumption.cups == sample_consumption_data["cups"]

    # Test validación de aliases
    assert consumption.consumption_kwh == sample_consumption_data["consumptionKWh"]

    # Test serialización JSON
    json_str = consumption.model_dump_json(by_alias=True)
    restored = ConsumptionData.model_validate_json(json_str)
    assert restored.consumption_kwh == consumption.consumption_kwh
```

### 2. Autenticación y Renovación de Tokens

```python
def test_token_renewal_on_401(authenticated_v1_client, test_token):
    with responses.RequestsMock() as rsps:
        # Request falla con 401
        rsps.add(responses.GET, url, status=401)

        # Nueva autenticación automática
        rsps.add(responses.POST, auth_url, body=f"{test_token}_renewed", status=200)

        # Request exitoso con nuevo token
        rsps.add(responses.GET, url, json=data, status=200)

        result = client.get_supplies()

        # Verificar renovación automática
        assert client.token == f"{test_token}_renewed"
```

### 3. Flujos de Integración Completos

```python
def test_complete_workflow_v1(authenticated_v1_client):
    # 1. Obtener distribuidores
    distributors = client.get_distributors()

    # 2. Obtener suministros
    supplies = client.get_supplies()

    # 3. Obtener consumo para cada suministro
    for supply in supplies:
        consumption = client.get_consumption(
            cups=supply.cups,
            distributor_code=supply.distributor_code,
            date_from="2024/01/01",
            date_to="2024/01/31"
        )
        assert len(consumption) > 0
```

### 4. Manejo de Errores

```python
def test_api_error_propagation(authenticated_v1_client):
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=500, json={"error": "Server error"})

        with pytest.raises(APIError) as exc_info:
            client.get_supplies()

        assert exc_info.value.status_code == 500
```

## Mejores Prácticas

### [BUENAS PRACTICAS] Hacer
- **Usar fixtures**: Reutilizar configuración común
- **Tests aislados**: Cada test debe ser independiente
- **Mocking completo**: No hacer requests HTTP reales
- **Assertions específicas**: Verificar comportamiento exacto
- **Casos edge**: Probar valores límite y errores
- **Documentar tests complejos**: Explicar casos no obvios

### [EVITAR] Evitar
- **Tests dependientes**: No asumir orden de ejecución
- **Requests reales**: Siempre usar mocks
- **Fixtures mutables**: Evitar efectos secundarios
- **Tests lentos**: Mantener tests unitarios rápidos
- **Código duplicado**: Usar helpers y fixtures
- **Assertions vagas**: Ser específico en verificaciones

## Troubleshooting

### Tests Fallan
```bash
# Ver detalles de fallos
pytest -v --tb=long

# Ejecutar test específico
pytest tests/test_auth.py::TestV1Authentication::test_successful_authentication -v

# Debug con print
pytest -s tests/test_auth.py
```

### Coverage Bajo
```bash
# Ver líneas no cubiertas
pytest --cov=datadis_python --cov-report=term-missing

# Generar reporte HTML detallado
pytest --cov=datadis_python --cov-report=html
```

### Tests Lentos
```bash
# Ver duración de tests
pytest --durations=10

# Solo tests rápidos
pytest -m "unit and not slow"
```

### Problemas de Imports
```bash
# Verificar instalación
poetry install --with dev

# Verificar Python path
python -c "import datadis_python; print(datadis_python.__file__)"
```

## Contribuir

### Añadir Nuevos Tests

1. **Identificar necesidad**: ¿Qué funcionalidad falta coverage?
2. **Elegir ubicación**: ¿Unit, integration, o componente específico?
3. **Usar fixtures**: Reutilizar configuración existente
4. **Añadir markers**: Categorizar apropiadamente
5. **Documentar**: Explicar casos complejos

### Ejemplo de Test Nuevo

```python
@pytest.mark.unit
@pytest.mark.client_v1
def test_new_functionality(authenticated_v1_client, sample_data):
    """Test nueva funcionalidad del cliente V1."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://datadis.es/api-private/api/new-endpoint",
            json=sample_data,
            status=200
        )

        result = authenticated_v1_client.new_method()

        assert result is not None
        assert len(result) > 0
```

### Mantener Tests

- **Ejecutar regularmente**: `python run_tests.py --all`
- **Actualizar fixtures**: Cuando cambie la API
- **Revisar coverage**: Mantener >95%
- **Optimizar velocidad**: Tests unitarios <0.1s cada uno
- **Documentar cambios**: Actualizar README cuando sea necesario

## Integración CI/CD

Para integrar en GitHub Actions u otros sistemas CI/CD:

```yaml
# Ejemplo .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install poetry && poetry install --with dev
      - name: Run quality checks
        run: python run_tests.py --quality
      - name: Run tests with coverage
        run: python run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

Este test suite garantiza la calidad y confiabilidad del SDK de Datadis Python, proporcionando una base sólida para el desarrollo y mantenimiento continuo del proyecto.
