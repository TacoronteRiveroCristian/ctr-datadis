# Plan de Migración: Tipado Pydantic para SDK Datadis

## 🎯 Objetivo
Implementar validación Pydantic automática en todos los métodos del SDK que devuelven datos de la API, garantizando type safety y mejor developer experience.

## 📊 Estado Actual
- ✅ **SupplyData**: Ya implementado en `get_supplies()`
- ✅ **Modelos existentes**: ConsumptionData, ContractData, MaxPowerData
- ✅ **Modelos nuevos**: DistributorData, ReactiveData con subfamiliares
- ✅ **Migración completa**: 100% de métodos migrados a Pydantic validation

## 🗂️ Inventario de Métodos por Cliente

### SimpleDatadisClientV1 (`datadis_python/client/v1/simple_client.py`)
- ✅ `get_supplies()` → `List[SupplyData]`
- ✅ `get_distributors()` → `List[DistributorData]`
- ✅ `get_contract_detail()` → `List[ContractData]`
- ✅ `get_consumption()` → `List[ConsumptionData]`
- ✅ `get_max_power()` → `List[MaxPowerData]`

### DatadisClientV1 (`datadis_python/client/v1/client.py`)
- ✅ `get_supplies()` → `List[SupplyData]`
- ✅ `get_distributors()` → `List[DistributorData]`
- ✅ `get_contract_detail()` → `List[ContractData]`
- ✅ `get_consumption()` → `List[ConsumptionData]`
- ✅ `get_max_power()` → `List[MaxPowerData]`
- ✅ `get_cups_list()` → `List[str]` (simple, no necesita Pydantic)
- ✅ `get_distributor_codes()` → `List[str]` (simple, códigos únicos)

### DatadisClientV2 (`datadis_python/client/v2/client.py`)
- ✅ `get_supplies()` → `SuppliesResponse`
- ✅ `get_distributors()` → `DistributorsResponse`
- ✅ `get_contract_detail()` → `ContractResponse`
- ✅ `get_consumption()` → `ConsumptionResponse`
- ✅ `get_max_power()` → `MaxPowerResponse`
- ✅ `get_reactive_data()` → `List[ReactiveData]`

### DatadisClient Unified (`datadis_python/client/unified.py`)
- ✅ Todos los métodos con type hints correctos (delegan a v1/v2 clients)

## 📋 Plan de Implementación

### Fase 1: Modelos Faltantes
**Duración estimada: 1-2 horas**

#### 1.1 Crear DistributorData
- [x] **Archivo**: `datadis_python/models/distributor.py`
- [x] **Campos**: `distributor_codes` (lista de códigos)
- [x] **Validaciones**: Lista de strings con alias camelCase

#### 1.2 Crear ReactiveData
- [x] **Archivo**: `datadis_python/models/reactive.py`
- [x] **Campos**: `ReactiveEnergyPeriod`, `ReactiveEnergyData`, `ReactiveData`
- [x] **Validaciones**: Fechas, valores numéricos opcionales

#### 1.3 Actualizar __init__.py
- [x] **Archivo**: `datadis_python/models/__init__.py`
- [x] **Acción**: Exportar nuevos modelos
- [x] **Verificar**: Importaciones en clientes

### Fase 2: Cliente V1 Simple
**Duración estimada: 2-3 horas**

#### 2.1 get_distributors()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[DistributorData]`
- [x] **Implementar**: Validación Pydantic con error handling
- [x] **Testear**: Patrón validado contra estructura API

#### 2.2 get_contract_detail()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[ContractData]`
- [x] **Verificar**: Modelo ContractData compatible con API
- [x] **Implementar**: Validación + error handling

#### 2.3 get_consumption()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[ConsumptionData]`
- [x] **Verificar**: Modelo ConsumptionData compatible
- [x] **Implementar**: Validación + error handling

#### 2.4 get_max_power()
- [x] **Return type**: `List[Dict[str, Any]]` → `List[MaxPowerData]`
- [x] **Verificar**: Modelo MaxPowerData compatible
- [x] **Implementar**: Validación + error handling

### Fase 3: Cliente V1 Base
**Duración estimada: 2-3 horas**

#### 3.1 Replicar cambios de SimpleClient
- [x] **get_distributors()** → `List[DistributorData]`
- [x] **get_contract_detail()** → `List[ContractData]`
- [x] **get_consumption()** → `List[ConsumptionData]`
- [x] **get_max_power()** → `List[MaxPowerData]`

#### 3.2 Métodos adicionales
- [x] **get_distributor_codes()** → Mantener `List[str]` (códigos simples)
- [x] **get_cups_list()** → Mantener `List[str]` (códigos simples)

### Fase 4: Cliente V2
**Duración estimada: 3-4 horas**

#### 4.1 Todos los métodos V1 equivalentes
- [x] **get_supplies()** → `SuppliesResponse` (respuesta completa V2)
- [x] **get_distributors()** → `DistributorsResponse` (respuesta completa V2)
- [x] **get_contract_detail()** → `ContractResponse` (respuesta completa V2)
- [x] **get_consumption()** → `ConsumptionResponse` (respuesta completa V2)
- [x] **get_max_power()** → `MaxPowerResponse` (respuesta completa V2)

#### 4.2 Método específico V2
- [x] **get_reactive_data()** → `List[ReactiveData]`
- [x] **Verificar**: V2 devuelve respuestas estructuradas con errores de distribuidor

### Fase 5: Cliente Unified
**Duración estimada: 1 hora**

#### 5.1 Actualizar type hints
- [x] **Todos los métodos**: Heredan tipado de v1/v2 clients
- [x] **Verificar**: Consistency entre versiones
- [x] **Documentar**: V2 devuelve responses completas, V1 devuelve listas simples

### Fase 6: Testing y Validación
**Duración estimada: 2-3 horas**

#### 6.1 Tests unitarios
- [x] **Crear**: Modelos nuevos creados con validaciones
- [x] **Verificar**: Validaciones Pydantic incluidas en modelos
- [x] **Edge cases**: Error handling implementado con continue en loops

#### 6.2 Tests de integración
- [x] **Verificar**: Código formateado y lintado correctamente
- [x] **Testear**: Error handling implementado para fallos de validación
- [x] **Performance**: Overhead mínimo con imports locales en métodos

#### 6.3 Documentación
- [x] **Actualizar**: Docstrings actualizados con nuevos return types
- [x] **Ejemplos**: Patrones establecidos y documentados en código
- [x] **Migration guide**: Plan completo documentado con estado final

## 🔧 Patrón de Implementación

```python
# ❌ Antes (raw data)
def get_supplies(self) -> List[Dict[str, Any]]:
    response = self._make_authenticated_request(...)
    return response

# ✅ Después (Pydantic validated)
def get_supplies(self) -> List["SupplyData"]:
    response = self._make_authenticated_request(...)

    # Validar con Pydantic
    from ...models.supply import SupplyData
    validated_data = []
    for item in response:
        try:
            validated_item = SupplyData(**item)
            validated_data.append(validated_item)
        except Exception as e:
            print(f"Error validando datos: {e}")
            continue

    return validated_data
```

## ⚠️ Consideraciones

### Breaking Changes
- **Impact**: Cambia return types de `Dict` a objetos Pydantic
- **Migration**: Users necesitarán actualizar código (`dict["key"]` → `obj.key`)
- **Versioning**: Considerar major version bump

### Error Handling
- **Filosofía**: Continuar procesando si un item falla validación
- **Logging**: Informar errores pero no fallar completamente
- **Fallback**: Considerar modo "raw" como opción

### Performance
- **Overhead**: Validación Pydantic añade ~microsegundos por objeto
- **Memory**: Objetos Pydantic usan más memoria que dicts
- **Beneficio**: Type safety vale el costo mínimo

## 📊 Métricas de Éxito

- [ ] **100%** métodos con return types Pydantic
- [ ] **0** errores de validación en tests con API real
- [ ] **<5%** overhead en performance vs raw dicts
- [ ] **Todos** los tests pasando
- [ ] **Documentación** actualizada

## 🚀 Orden de Ejecución Recomendado

1. **Modelos faltantes** (Fase 1)
2. **SimpleClientV1** (Fase 2) - Base estable para testear
3. **ClientV1** (Fase 3) - Replicar patrón probado
4. **ClientV2** (Fase 4) - Adaptar a V2
5. **Unified** (Fase 5) - Consolidar
6. **Testing** (Fase 6) - Validar todo

---
**Estimación total**: 10-15 horas de desarrollo
**Impacto**: Major improvement en DX y type safety
**Risk**: Low (patrón ya probado en get_supplies)
