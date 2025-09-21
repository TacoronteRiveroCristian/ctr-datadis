# Datadis API Reference Documentation

**Fecha de documentación:** 20 de septiembre de 2025
**Versión:** Extraída del archivo doc-api.txt oficial de Datadis
**Estado:** Documento de referencia para el SDK de Python

## Introducción

La API de Datadis permite acceder a la información de consumo almacenada en las bases de datos de las distintas distribuidoras eléctricas españolas, utilizando una única API unificada.

### Características principales:
- **Solo consulta**: API de solo lectura (no permite añadir, modificar o borrar información)
- **Verbos HTTP**: POST para autenticación, GET para consultas
- **Autenticación**: Token Bearer requerido para todas las operaciones
- **URL Base**: `https://datadis.es/`
- **Formato**: REST API siguiendo estándares HTTP

## Códigos de Respuesta HTTP

| Código | Descripción | Tipo |
|--------|-------------|------|
| 200 | OK | Respuesta satisfactoria |
| 400 | Bad Request | Error del cliente |
| 401 | Unauthorized | Error del cliente |
| 403 | Forbidden | Error del cliente |
| 404 | Not Found | Error del cliente |
| 429 | Too Many Requests | Error del cliente |
| 500 | Internal Server Error | Error del servidor |

## Autenticación

### POST `/nikola-auth/tokens/login`

Obtiene el token de autenticación para el área privada.

**URL completa:** `https://datadis.es/nikola-auth/tokens/login`

**Parámetros:**
- `username` (string, required): NIF del usuario dado de alta en Datadis
- `password` (string, required): Contraseña de acceso a Datadis del usuario

---

## API Privada (Requiere Autenticación)

### 1. Gestión de Suministros

#### GET `/api-private/api/get-supplies` (V1)

Busca todos los suministros del usuario.

**Parámetros:**
- `authorizedNif` (string, optional): NIF de personas autorizadas
- `distributorCode` (string, optional): Código del distribuidor

**Respuesta:**
```json
[
  {
    "address": "String",
    "cups": "String",
    "postalCode": "String",
    "province": "String",
    "municipality": "String",
    "distributor": "String",
    "validDateFrom": "String", // formato: aaaa/MM/dd
    "validDateTo": "String",   // formato: aaaa/MM/dd
    "pointType": Integer,      // 1, 2, 3, 4 o 5
    "distributorCode": "String"
  }
]
```

#### GET `/api-private/api/get-supplies-v2` (V2)

Versión mejorada que incluye manejo de errores por distribuidor.

**Respuesta:**
```json
{
  "supplies": [...], // mismo formato que V1
  "distributorError": [
    {
      "distributorCode": "String",
      "distributorName": "String",
      "errorCode": "String",
      "errorDescription": "String"
    }
  ]
}
```

### 2. Detalles de Contrato

#### GET `/api-private/api/get-contract-detail` (V1)

Obtiene los detalles del contrato para un CUPS específico.

**Parámetros:**
- `cups` (string, required): CUPS del suministro
- `distributorCode` (string, required): Código del distribuidor
- `authorizedNif` (string, optional): NIF autorizado

**Respuesta:**
```json
[
  {
    "cups": "String",
    "distributor": "String",
    "marketer": "String", // solo si es propietario
    "tension": "String",
    "accessFare": "String",
    "province": "String",
    "municipality": "String",
    "postalCode": "String",
    "contractedPowerkW": [Number],
    "timeDiscrimination": "String",
    "modePowerControl": "String", // ICP/Maxímetro
    "startDate": "String",
    "endDate": "String",
    "codeFare": "String",
    "selfConsumptionTypeCode": "String",
    "selfConsumptionTypeDesc": "String",
    "section": "String",
    "subsection": "String",
    "partitionCoefficient": Number,
    "cau": "String",
    "installedCapacityKW": Number,
    "dateOwner": [{"String", "String"}],
    "lastMarketerDate": "String",
    "maxPowerInstall": "String"
  }
]
```

#### GET `/api-private/api/get-contract-detail-v2` (V2)

Versión V2 con manejo de errores mejorado:
```json
{
  "contract": [...], // mismo formato que V1
  "distributorError": [...] // array de errores
}
```

### 3. Datos de Consumo

#### GET `/api-private/api/get-consumption-data` (V1)

Obtiene los datos de consumo para un período específico.

**Parámetros:**
- `cups` (string, required): CUPS del suministro
- `distributorCode` (string, required): Código del distribuidor
- `startDate` (string, required): Fecha inicio (AAAA/MM)
- `endDate` (string, required): Fecha fin (AAAA/MM)
- `measurementType` (string, required): 0=hora, 1=cuarto hora
- `pointType` (string, required): Tipo de punto de medida
- `authorizedNif` (string, optional): NIF autorizado

**Nota:** Consulta cuarto horaria solo disponible para PointType 1 y 2, y PointType 3 en E-distribución.

**Respuesta:**
```json
[
  {
    "cups": "String",
    "date": "String", // aaaa/MM/dd
    "time": "String", // hh:mm
    "consumptionKWh": Number,
    "obtainMethod": "String", // Real/Estimada
    "surplusEnergyKWh": Number,
    "generationEnergyKWh": Number,
    "selfConsumptionEnergyKWh": Number
  }
]
```

#### GET `/api-private/api/get-consumption-data-v2` (V2)

Versión V2 con estructura mejorada:
```json
{
  "timeCurve": [...], // mismo formato que V1
  "distributorError": [...] // manejo de errores
}
```

### 4. Potencia Máxima

#### GET `/api-private/api/get-max-power` (V1) / `get-max-power-v2` (V2)

Obtiene la potencia máxima demandada en un período.

**Parámetros:** (iguales que consumption-data excepto measurementType)

**Respuesta V1:**
```json
[
  {
    "cups": "String",
    "date": "String", // aaaa/MM/dd
    "time": "String", // hh:mm
    "maxPower": Number, // Potencia en W
    "period": "String"  // VALLE, LLANO, PUNTA, 1-6
  }
]
```

**Respuesta V2:**
```json
{
  "maxPower": [...], // mismo formato que V1
  "distributorError": [...]
}
```

### 5. Distribuidores con Suministros

#### GET `/api-private/api/get-distributors-with-supplies` (V1)

Lista códigos de distribuidores donde el usuario tiene suministros.

**Respuesta:**
```json
[
  {
    "distributorCodes": ["String", "String"]
  }
]
```

#### GET `/api-private/api/get-distributors-with-supplies-v2` (V2)

**Respuesta mejorada:**
```json
{
  "distExistenceUser": {
    "distributorCodes": ["String", "String"]
  },
  "distributorError": [...]
}
```

### 6. Datos de Energía Reactiva (Solo V2)

#### GET `/api-private/api/get-reactive-data-v2`

**Parámetros:**
- `cups` (string, required)
- `distributorCode` (string, required)
- `startDate` (string, required): AAAA/MM
- `endDate` (string, required): AAAA/MM
- `authorizedNif` (string, optional)

**Respuesta:**
```json
{
  "reactiveEnergy": {
    "cups": "String",
    "energy": [
      {
        "date": "String", // aaaa/MM
        "energy_p1": Number,
        "energy_p2": Number,
        "energy_p3": Number,
        "energy_p4": Number,
        "energy_p5": Number,
        "energy_p6": Number
      }
    ],
    "code": "String",
    "code_desc": "String"
  },
  "distributorError": [...]
}
```

### 7. Gestión de Autorizaciones

#### GET `/api-private/api/new-authorization`

Crea una nueva autorización.

**Parámetros:**
- `authorizedNif` (string, required): NIF de la persona que autoriza
- `startDate` (string, optional): Fecha inicio autorización
- `endDate` (string, optional): Fecha fin autorización
- `cups` (String[], optional): CUPS específicos (vacío = todos)

#### GET `/api-private/api/cancel-authorization`

Cancela una autorización existente.

**Parámetros:**
- `authorizedNif` (string, required): NIF a cancelar
- `cups` (String[], optional): CUPS específicos (vacío = todos)

#### GET `/api-private/api/list-authorization`

Lista todas las autorizaciones.

**Parámetros:**
- `ownerNif` (string, optional): NIF del propietario

**Respuesta:**
```json
[
  {
    "id": Number,
    "ownerDocument": "String",
    "requesterDocument": "String",
    "status": "String",
    "validityDateStart": "String",
    "validityDateEnd": "String",
    "distributorCodeFather": "String"
  }
]
```

---

## API Pública (Sin Autenticación)

### 1. Búsqueda por Conjunto de Datos

#### GET `/api-public/api-search`

Búsqueda agregada de datos por zonas, sectores, etc.

**Parámetros principales:**
- `startDate` (required): AAAA/MM/dd
- `endDate` (required): AAAA/MM/dd
- `page` (required): Número de página (primera = 0)
- `pageSize` (required): Resultados por página (máx. 2000)
- `community` (required): Código de comunidad autónoma (máx. 2)

**Parámetros opcionales:**
- `measurementType`: Tipo punto medida (01-05)
- `distributor`: Código distribuidor
- `fare`: Código tarifa
- `provinceMunicipality`: Código provincia/municipio
- `postalCode`: Código postal
- `economicSector`: Sector económico (1-4)
- `tension`: Tensión eléctrica (E0-E6)
- `timeDiscrimination`: Discriminación horaria
- `sort`: Ordenación de resultados

#### GET `/api-public/api-sum-search`

Versión sumatoria que devuelve totales agregados.

### 2. Búsqueda de Autoconsumo

#### GET `/api-public/api-search-auto`

Búsqueda específica para datos de autoconsumo.

**Parámetros adicionales específicos:**
- `selfConsumption`: Tipo de autoconsumo (31-77)

#### GET `/api-public/api-sum-search-auto`

Versión sumatoria para autoconsumo.

---

## Códigos de Distribuidores

| Código | Distribuidor |
|--------|-------------|
| 1 | Viesgo |
| 2 | E-distribución |
| 3 | E-redes |
| 4 | ASEME |
| 5 | UFD |
| 6 | EOSA |
| 7 | CIDE |
| 8 | IDE |

## Códigos de Comunidades Autónomas

| Código | Comunidad |
|--------|-----------|
| 01 | Andalucía |
| 02 | Aragón |
| 03 | Principado de Asturias |
| 04 | Islas Baleares |
| 05 | Canarias |
| 06 | Cantabria |
| 07 | Castilla y León |
| 08 | Castilla La Mancha |
| 09 | Cataluña |
| 10 | Comunidad Valenciana |
| 11 | Extremadura |
| 12 | Galicia |
| 13 | Comunidad de Madrid |
| 14 | Región de Murcia |
| 15 | Comunidad Foral de Navarra |
| 16 | País Vasco |
| 17 | La Rioja |
| 18 | Ceuta |
| 19 | Melilla |

## Notas de Implementación

### Diferencias entre V1 y V2:
- **V2** incluye manejo de errores por distribuidor
- **V2** tiene estructura de respuesta más robusta
- **V1** mantiene compatibilidad con implementaciones existentes
- **V2** es la versión recomendada para nuevas implementaciones

### Consideraciones técnicas:
- Los tokens de autenticación tienen expiración
- Las consultas cuarto horarias tienen limitaciones por tipo de punto
- Los códigos de distribuidor son específicos y deben validarse
- Las fechas siguen formatos específicos (AAAA/MM o AAAA/MM/dd)

### Limitaciones de la API:
- API de solo lectura
- Límites de paginación (máx. 2000 resultados)
- Restricciones en consultas cuarto horarias
- URLs no diseñadas para navegadores web

---

**Documento generado automáticamente el 20/09/2025 para el SDK de Python datadis_python**
