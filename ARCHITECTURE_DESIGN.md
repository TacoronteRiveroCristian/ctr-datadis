# Arquitectura del SDK Datadis Python

## Estructura Actual vs Propuesta

### Estructura Actual (Monolítica)
```
datadis_python/
├── client/datadis_client.py  # Un solo cliente mezclando v1 y v2
├── models/                   # Modelos sin separación por versión
├── utils/constants.py        # Endpoints mezclados
└── exceptions/               # OK
```

### Nueva Estructura Propuesta (Modular)
```
datadis_python/
├── client/
│   ├── __init__.py
│   ├── base.py              # BaseDatadisClient - funcionalidad común
│   ├── v1/
│   │   ├── __init__.py
│   │   └── client.py        # DatadisClientV1 (API estable)
│   ├── v2/
│   │   ├── __init__.py
│   │   └── client.py        # DatadisClientV2 (API moderna)
│   └── unified.py           # DatadisClient (wrapper que expone ambas)
├── models/
│   ├── __init__.py
│   ├── base.py              # Tipos base comunes
│   ├── v1/                  # Modelos para respuestas v1
│   │   ├── __init__.py
│   │   ├── supply.py
│   │   ├── consumption.py
│   │   ├── contract.py
│   │   └── max_power.py
│   └── v2/                  # Modelos para respuestas v2
│       ├── __init__.py
│       ├── supply.py
│       ├── consumption.py
│       ├── contract.py
│       └── max_power.py
├── utils/
│   ├── __init__.py
│   ├── constants.py         # Constantes separadas por versión
│   ├── validators.py        # Validadores comunes (opcional)
│   └── http.py             # Utilidades HTTP comunes
├── exceptions/              # Sin cambios - ya está bien
└── __init__.py
```

## Principios de Diseño

### 1. Separación de Responsabilidades
- **BaseDatadisClient**: Autenticación, HTTP requests, manejo de errores
- **ClientV1**: Endpoints v1, serialización raw
- **ClientV2**: Endpoints v2, modelos Pydantic
- **UnifiedClient**: Wrapper que expone ambas versiones

### 2. APIs Similares a InfluxDB
```python
# Opción 1: Clientes específicos
from datadis_python.client.v1 import DatadisClientV1
from datadis_python.client.v2 import DatadisClientV2

client_v1 = DatadisClientV1(username, password)
client_v2 = DatadisClientV2(username, password)

# Opción 2: Cliente unificado
from datadis_python import DatadisClient

client = DatadisClient(username, password)
client.v1.get_supplies()  # API v1
client.v2.get_supplies()  # API v2
```

### 3. Compatibilidad y Flexibilidad
- **V1**: Raw responses (List[Dict], Dict) - Para máxima compatibilidad
- **V2**: Typed responses (Pydantic models) - Para desarrollo moderno
- **Común**: Autenticación, configuración, manejo de errores

## Plan de Implementación

### Fase 1: Infraestructura Base
1. Crear `client/base.py` - Cliente base con auth y HTTP
2. Crear `utils/http.py` - Utilidades HTTP comunes
3. Refactorizar `utils/constants.py` - Separar por versiones

### Fase 2: Cliente V1 (API Estable)
1. Implementar `client/v1/client.py` - Endpoints v1 raw
2. Crear modelos v1 básicos (opcional, mayormente Dict)
3. Probar compatibilidad con tu código existente

### Fase 3: Cliente V2 (API Moderna)
1. Implementar `client/v2/client.py` - Endpoints v2 tipados
2. Migrar modelos Pydantic actuales a `models/v2/`
3. Mantener validaciones y tipos

### Fase 4: Cliente Unificado
1. Crear `client/unified.py` - Wrapper que expone v1 y v2
2. Actualizar `__init__.py` - Imports principales
3. API común para funciones comunes

### Fase 5: Documentación y Ejemplos
1. Documentar cada versión
2. Ejemplos de migración v1 -> v2
3. Guía de mejores prácticas

## Beneficios de esta Arquitectura

1. **Flexibilidad**: Usar v1 para velocidad, v2 para tipos
2. **Compatibilidad**: V1 mantiene tu código actual funcionando
3. **Evolución**: V2 permite mejoras futuras
4. **Claridad**: Separación clara de responsabilidades
5. **Mantenimiento**: Cambios en una versión no afectan la otra

## Casos de Uso

### Desarrollo Rápido (V1)
```python
client = DatadisClientV1(username, password)
supplies = client.get_supplies()  # List[Dict] - directo de API
print(supplies[0]['cups'])
```

### Desarrollo Tipado (V2)
```python
client = DatadisClientV2(username, password)
supplies = client.get_supplies()  # List[SupplyData] - tipado
print(supplies[0].cups)  # Autocompletado IDE
```

### Migración Gradual
```python
client = DatadisClient(username, password)
# Usar v1 para partes estables
raw_data = client.v1.get_supplies()
# Usar v2 para nuevas funciones
typed_data = client.v2.get_consumption(...)
```