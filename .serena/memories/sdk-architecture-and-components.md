# Datadis SDK Architecture - Complete Guide

## [ARCHITECTURE] General Architecture

### Project Structure
```
datadis_python/
├── client/                    # API clients
│   ├── base.py               # Abstract base client
│   ├── unified.py            # Multi-version unified client
│   ├── v1/                   # API v1 client
│   │   ├── client.py         # Standard v1 client
│   │   └── simple_client.py  # Simplified v1 client (main)
│   └── v2/                   # API v2 client
│       └── client.py         # v2 client (future)
├── models/                   # Pydantic models
│   ├── consumption.py        # Consumption data
│   ├── contract.py          # Contract data
│   ├── distributor.py       # Distributor data
│   ├── max_power.py         # Maximum power data
│   ├── reactive.py          # Reactive energy data
│   ├── responses.py         # Response models
│   └── supply.py            # Supply data
├── exceptions/              # Exception hierarchy
├── utils/                   # Utilities
│   ├── constants.py         # Constants and endpoints
│   ├── http.py             # Base HTTP client
│   ├── text_utils.py       # Text normalization
│   └── validators.py       # Validators
└── __init__.py             # Public API
```

## [COMPONENTS] Main Components

### 1. **Main Client: SimpleDatadisClientV1**
**File**: `datadis_python/client/v1/simple_client.py`

**Responsibilities**:
- Automatic authentication with Datadis
- Token management and renewal
- Retry logic for failed requests
- Response normalization
- Validation with Pydantic models

**Main Methods**:
```python
# Authentication
authenticate() -> str

# Get data
get_supplies(distributor_code: Optional[str] = None) -> List[SupplyData]
get_consumption(cups: str, distributor_code: str, date_from: str, date_to: str, measurement_type: int = 0) -> List[ConsumptionData]
get_contract_detail(cups: str, distributor_code: str) -> List[ContractData]
get_max_power(cups: str, distributor_code: str, date_from: str, date_to: str) -> List[MaxPowerData]
get_distributors() -> List[DistributorData]
```

**Characteristics**:
- [OK] **Robust**: Complete error handling + retry logic
- [OK] **Type-safe**: Responses validated with Pydantic
- [OK] **Auto-healing**: Automatic token renewal
- [OK] **Logging**: Informative output for debugging

### 2. **Pydantic Models (Type-Safe)**
**Directory**: `datadis_python/models/`

**Automatic Validation**:
- All API data is automatically validated
- Automatic type conversion
- Aliases for field names (snake_case ↔ camelCase)
- Text normalization (accents, special characters)

**Main Models**:
```python
# Supply point
SupplyData:
    - address: str
    - cups: str (validated CUPS format)
    - distributor: str (normalized)
    - distributor_code: str
    - point_type: int
    - province: str, municipality: str

# Electric consumption
ConsumptionData:
    - cups: str
    - date: str, time: str
    - consumption_kwh: float
    - obtain_method: str
    - generation_energy_kwh: Optional[float]

# Contract
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
├── AuthenticationError      # Authentication errors
├── APIError                # HTTP API errors
├── ValidationError         # Validation errors
├── NetworkError           # Network/timeout errors
└── ConfigurationError     # Configuration errors
```

**Client Usage**:
- `APIError`: Propagated directly on first attempt
- `DatadisError`: Final wrapper after exhausting retries
- `AuthenticationError`: Invalid/expired token
- `ValidationError`: Invalid input data

### 4. **Utilities and Validators**
**Archivos**: `datladis_python/utils/`

**Main Validators** (`validators.py`):
```python
validate_cups(cups: str) -> str:
    # Format: ES + 22 digits + 2 alphanumeric
    # Ejemplo: "ES0123456789012345678901AB"

validate_date_range(date_from: str, date_to: str) -> tuple:
    # Format: "YYYY/MM/DD"
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
    # Applied automatically by the client
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
