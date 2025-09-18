# Arquitectura del SDK Datadis - Guía Completa

## [ARQUITECTURA] Arquitectura General

### Estructura del Proyecto
```
datadis_python/
├── client/                    # Clientes API
│   ├── base.py               # Cliente base abstracto
│   ├── unified.py            # Cliente unificado multi-versión
│   ├── v1/                   # Cliente API v1
│   │   ├── client.py         # Cliente v1 estándar
│   │   └── simple_client.py  # Cliente v1 simplificado (principal)
│   └── v2/                   # Cliente API v2
│       └── client.py         # Cliente v2 (futuro)
├── models/                   # Modelos Pydantic
│   ├── consumption.py        # Datos de consumo
│   ├── contract.py          # Datos de contrato
│   ├── distributor.py       # Datos de distribuidor
│   ├── max_power.py         # Datos de potencia máxima
│   ├── reactive.py          # Datos de energía reactiva
│   ├── responses.py         # Modelos de respuesta
│   └── supply.py            # Datos de suministro
├── exceptions/              # Jerarquía de excepciones
├── utils/                   # Utilidades
│   ├── constants.py         # Constantes y endpoints
│   ├── http.py             # Cliente HTTP base
│   ├── text_utils.py       # Normalización de texto
│   └── validators.py       # Validadores
└── __init__.py             # API pública
```

## [COMPONENTES] Componentes Principales

### 1. **Cliente Principal: SimpleDatadisClientV1**
**Archivo**: `datadis_python/client/v1/simple_client.py`

**Responsabilidades**:
- Autenticación automática con Datadis
- Gestión de tokens y renovación
- Retry logic para requests fallidos
- Normalización de respuestas
- Validación con modelos Pydantic

**Métodos Principales**:
```python
# Autenticación
authenticate() -> str

# Obtener datos
get_supplies(distributor_code: Optional[str] = None) -> List[SupplyData]
get_consumption(cups: str, distributor_code: str, date_from: str, date_to: str, measurement_type: int = 0) -> List[ConsumptionData]
get_contract_detail(cups: str, distributor_code: str) -> List[ContractData]
get_max_power(cups: str, distributor_code: str, date_from: str, date_to: str) -> List[MaxPowerData]
get_distributors() -> List[DistributorData]
```

**Características**:
- [OK] **Robusto**: Manejo completo de errores + retry logic
- [OK] **Type-safe**: Respuestas validadas con Pydantic
- [OK] **Auto-healing**: Renovación automática de tokens
- [OK] **Logging**: Output informativo para debugging

### 2. **Modelos Pydantic (Type-Safe)**
**Directorio**: `datadis_python/models/`

**Validación Automática**:
- Todos los datos de la API se validan automáticamente
- Conversión de tipos automática
- Alias para nombres de campos (snake_case ↔ camelCase)
- Normalización de texto (tildes, caracteres especiales)

**Modelos Principales**:
```python
# Punto de suministro
SupplyData:
    - address: str
    - cups: str (validado formato CUPS)
    - distributor: str (normalizado)
    - distributor_code: str
    - point_type: int
    - province: str, municipality: str

# Consumo eléctrico
ConsumptionData:
    - cups: str
    - date: str, time: str
    - consumption_kwh: float
    - obtain_method: str
    - generation_energy_kwh: Optional[float]

# Contrato
ContractData:
    - cups: str
    - distributor: str, marketer: str
    - tension: str, access_fare: str
    - contracted_power_kw: List[float]
    - start_date: str, end_date: Optional[str]
```

### 3. **Sistema de Excepciones**
**Archivo**: `datadis_python/exceptions/`

**Jerarquía**:
```python
DatadisError (base)
├── AuthenticationError      # Errores de autenticación
├── APIError                # Errores HTTP de la API
├── ValidationError         # Errores de validación
├── NetworkError           # Errores de red/timeout
└── ConfigurationError     # Errores de configuración
```

**Uso en Cliente**:
- `APIError`: Se propaga directamente en primer intento
- `DatadisError`: Wrapper final después de agotar retries
- `AuthenticationError`: Token inválido/expirado
- `ValidationError`: Datos de entrada inválidos

### 4. **Utilidades y Validadores**
**Archivos**: `datladis_python/utils/`

**Validadores Principales** (`validators.py`):
```python
validate_cups(cups: str) -> str:
    # Formato: ES + 22 dígitos + 2 alfanuméricos
    # Ejemplo: "ES0123456789012345678901AB"

validate_date_range(date_from: str, date_to: str) -> tuple:
    # Formato: "YYYY/MM/DD"
    # Validaciones: rango válido, no futuro, no >2 años atrás

validate_distributor_code(code: str) -> str:
    # Códigos válidos: "1"-"8"
    # 1=Viesgo, 2=E-distribución, etc.
```

**Normalización de Texto** (`text_utils.py`):
```python
normalize_text(text: str) -> str:
    # "DISTRIBUCIÓN" → "DISTRIBUCION"
    # Maneja doble codificación UTF-8
    # Remueve tildes y caracteres especiales

normalize_api_response(response) -> dict/list:
    # Normaliza toda la respuesta recursivamente
    # Aplicado automáticamente por el cliente
```

**Cliente HTTP Base** (`http.py`):
- Retry logic configurable
- Timeout management
- Logging de requests
- Error handling unificado

## 🔗 Flujo de Datos

### 1. **Autenticación**
```
Usuario → SimpleDatadisClientV1 → POST /login-usuarios
        ← Token JWT ← API Response
Cliente almacena token + timestamp
```

### 2. **Request Típico**
```
1. Usuario llama método (ej: get_consumption)
2. Cliente valida parámetros con validators
3. Cliente verifica/renueva token si necesario
4. HTTP request con retry logic
5. Respuesta normalizada (text_utils)
6. Validación con Pydantic models
7. Return typed objects al usuario
```

### 3. **Manejo de Errores**
```
HTTP Error → APIError (primer intento)
           → Retry logic (configurable)
           → APIError (si persiste)
           → DatadisError (after all retries)
```

## 📐 Patrones de Diseño Utilizados

### 1. **Factory Pattern**
- `UnifiedDatadisClient`: Crea cliente V1/V2 según necesidad
- Abstracción de versiones de API

### 2. **Template Method**
- `BaseDatadisClient`: Define estructura común
- Subclases implementan detalles específicos

### 3. **Decorator Pattern**
- Retry logic aplicado transparentemente
- Normalización automática de respuestas

### 4. **Strategy Pattern**
- Diferentes validadores según tipo de dato
- Diferentes clientes según versión API

## [CONFIGURACION] Configuración y Constantes

**Archivo**: `datadis_python/utils/constants.py`

```python
# URLs base
DATADIS_BASE_URL = "https://datadis.es"
DATADIS_API_BASE = "https://datadis.es/api-private/api"

# Endpoints V1
API_V1_ENDPOINTS = {
    "supplies": "/get-supplies",
    "consumption": "/get-consumption-data",
    "contracts": "/get-contract-detail",
    "max_power": "/get-max-power",
    "distributors": "/get-distributors-with-supplies"
}

# Configuración por defecto
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
TOKEN_EXPIRY_BUFFER = 300  # 5 minutos
```

## [API] API Pública (datadis_python/__init__.py)

**Exports Principales**:
```python
# Cliente principal
from .client.v1.simple_client import SimpleDatadisClientV1

# Modelos
from .models import (
    SupplyData, ConsumptionData, ContractData,
    MaxPowerData, DistributorData
)

# Excepciones
from .exceptions import (
    DatadisError, APIError, AuthenticationError,
    ValidationError, NetworkError
)

# Utilidades públicas
from .utils.validators import validate_cups, validate_date_range
```

## [EXTENSIBILIDAD] Extensibilidad

### Para Agregar Nuevos Endpoints:
1. **Agregar endpoint** en `constants.py`
2. **Crear modelo Pydantic** en `models/`
3. **Implementar método** en `SimpleDatadisClientV1`
4. **Escribir tests** siguiendo patrones existentes
5. **Actualizar API pública** en `__init__.py`

### Para Nueva Versión API (V3, etc.):
1. **Crear directorio** `client/v3/`
2. **Implementar cliente** heredando de `BaseDatadisClient`
3. **Actualizar** `UnifiedDatadisClient`
4. **Mantener** compatibilidad hacia atrás

---

**Esta arquitectura garantiza**:
- [OK] **Mantenibilidad**: Separación clara de responsabilidades
- [OK] **Extensibilidad**: Fácil agregar nuevas features
- [OK] **Robustez**: Error handling + retry logic
- [OK] **Type Safety**: Validación automática con Pydantic
- [OK] **Testing**: Arquitectura testeable con mocks
