# ctr-datadis

[![PyPI version](https://badge.fury.io/py/ctr-datadis.svg)](https://badge.fury.io/py/ctr-datadis)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/ctr-datadis/badge/?version=latest)](https://ctr-datadis.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/TacoronteRiveroCristian/ctr-datadis/workflows/Auto%20Publish%20on%20Main%20Push/badge.svg)](https://github.com/TacoronteRiveroCristian/ctr-datadis/actions)

**Un SDK completo de Python para interactuar con la API oficial de Datadis** (plataforma española de datos de suministro eléctrico).

**Datadis** es la plataforma oficial del gobierno español que proporciona acceso a los datos de consumo eléctrico para los consumidores españoles. Este SDK facilita el acceso a tus datos eléctricos de forma programática.

## Características

- **Dos Versiones de Cliente** - V1 (básico) y V2 (recomendado con manejo avanzado de errores)
- **Autenticación Automática** - Autenticación basada en tokens con renovación automática
- **Cobertura Completa de API** - Acceso a todos los endpoints de la API de Datadis
- **Manejo Robusto de Errores** - V2 incluye manejo específico de errores por distribuidor
- **Parámetros Flexibles** - Acepta tipos Python nativos (datetime, int, float) además de strings
- **Seguridad de Tipos** - Type hints completos y modelos Pydantic para validación de datos
- **Context Managers** - Gestión automática de recursos con declaraciones `with`
- **Python 3.9+** - Compatible con versiones modernas de Python
- **Normalización de Texto** - Manejo automático de acentos españoles y caracteres especiales
- **Datos de Energía Reactiva** - Acceso exclusivo en V2 para análisis energético avanzado

## Instalación

```bash
pip install ctr-datadis
```

## Inicio Rápido

### Cliente V1 (Básico)

```python
from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

# Usar context manager (recomendado)
with SimpleDatadisClientV1(username="12345678A", password="tu_password") as client:
    # Obtener puntos de suministro
    supplies = client.get_supplies()
    print(f"Encontrados {len(supplies)} puntos de suministro")

    if supplies:
        # Obtener consumo anual (formato mensual OBLIGATORIO)
        consumption = client.get_consumption(
            cups=supplies[0].cups,
            distributor_code=supplies[0].distributorCode,
            date_from="2024/01",  # Enero 2024
            date_to="2024/12"     # Diciembre 2024
        )

        total_kwh = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
        print(f"Consumo total 2024: {total_kwh:.2f} kWh")
```

### Cliente V2 (Recomendado - con manejo de errores mejorado)

```python
from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

with SimpleDatadisClientV2(username="12345678A", password="tu_password") as client:
    # Obtener suministros con manejo de errores
    supplies_response = client.get_supplies()

    print(f"Suministros obtenidos: {len(supplies_response.supplies)}")

    # Verificar errores por distribuidor (exclusivo V2)
    if supplies_response.distributor_error:
        for error in supplies_response.distributor_error:
            print(f"Error en {error.distributorName}: {error.errorDescription}")

    if supplies_response.supplies:
        supply = supplies_response.supplies[0]

        # Obtener consumo con manejo robusto de errores
        consumption_response = client.get_consumption(
            cups=supply.cups,
            distributor_code=supply.distributorCode,
            date_from="2024/01",
            date_to="2024/12"
        )

        if consumption_response.time_curve:
            total_kwh = sum(c.consumptionKWh for c in consumption_response.time_curve
                          if c.consumptionKWh)
            print(f"Consumo total 2024: {total_kwh:.2f} kWh")

        # Funcionalidad exclusiva V2: Energía reactiva
        reactive_data = client.get_reactive_data(
            cups=supply.cups,
            distributor_code=supply.distributorCode,
            date_from="2024/01",
            date_to="2024/12"
        )
        print(f"Datos de energía reactiva: {len(reactive_data)} registros")
```

## Métodos Disponibles

### Información de Suministro
```python
# Obtener todos los puntos de suministro
supplies = client.get_supplies()

# Obtener detalles del contrato para un CUPS específico
contract = client.get_contract_detail(cups="ES1234...", distributor_code="2")
```

### Datos de Consumo
```python
from datetime import datetime, date

# Obtener datos de consumo con fechas mensuales (OBLIGATORIO)
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",
    distributor_code=2,             # int o string
    date_from=datetime(2024, 1, 1), # datetime (solo primer día), date o string YYYY/MM
    date_to=datetime(2024, 2, 1),   # datetime (solo primer día), date o string YYYY/MM
    measurement_type=0,             # int, float o string
    point_type=1                    # int, float o string (opcional)
)

# Obtener datos de potencia máxima
max_power = client.get_max_power(
    cups="ES1234000000000001JN0F",
    distributor_code=2,             # int o string
    date_from=datetime(2024, 1, 1), # datetime (solo primer día), date o string YYYY/MM
    date_to=datetime(2024, 2, 1)    # datetime (solo primer día), date o string YYYY/MM
)
```

### Información de Distribuidoras
```python
# Obtener distribuidoras disponibles
distributors = client.get_distributors()
```

## Tipos de Parámetros Flexibles

El SDK acepta múltiples tipos de parámetros para mayor comodidad, manteniendo 100% de compatibilidad hacia atrás:

### Fechas (IMPORTANTE: Solo formato mensual)

La API de Datadis **SOLO acepta fechas mensuales**. No es posible especificar días específicos.

```python
# ESTAS NO SON VÁLIDAS (contienen días específicos):
# date_from = "2024/01/15"           # RECHAZADO: contiene día específico
# date_from = datetime(2024, 1, 15)  # RECHAZADO: contiene día específico
# date_from = date(2024, 1, 15)      # RECHAZADO: contiene día específico

# ESTAS SON VÁLIDAS (formato mensual):
date_from = "2024/01"              # String YYYY/MM (RECOMENDADO)
date_from = datetime(2024, 1, 1)   # datetime primer día del mes (se convierte a 2024/01)
date_from = date(2024, 1, 1)       # date primer día del mes (se convierte a 2024/01)
```

### Números
```python
# Measurement type, point type, etc.:
measurement_type = "0"             # String tradicional
measurement_type = 0               # int
measurement_type = 0.0             # float

# Distributor code:
distributor_code = "2"             # String tradicional
distributor_code = 2               # int
```

### Conversión Automática
- Las fechas `datetime`/`date` se convierten automáticamente al formato API mensual (YYYY/MM)
- **IMPORTANTE**: Solo se aceptan `datetime`/`date` del primer día del mes (día 1)
- Los números `int`/`float` se convierten a strings
- Los strings se validan para asegurar formato mensual correcto (YYYY/MM)
- **Validación estricta** - fechas con días específicos serán rechazadas

## Modelos de Datos

El SDK incluye modelos Pydantic para manejo seguro de tipos:

- `SupplyData` - Información de puntos de suministro
- `ConsumptionData` - Registros de consumo energético
- `ContractData` - Detalles del contrato
- `MaxPowerData` - Datos de demanda de potencia máxima

## Manejo de Errores

```python
from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

try:
    supplies = client.get_supplies()
except AuthenticationError:
    print("Credenciales inválidas")
except APIError as e:
    print(f"Error de API: {e}")
except DatadisError as e:
    print(f"Error de Datadis: {e}")
```

## Requisitos

- Python 3.9 o superior
- Credenciales válidas de cuenta Datadis
- Conexión a internet

## Limitaciones de la API

- Los datos están disponibles solo para los últimos 2 años
- **CRÍTICO**: El formato de fecha DEBE ser YYYY/MM (solo datos mensuales, NO diarios)
- Fechas con días específicos (ej: "2024/01/15") serán rechazadas automáticamente
- La plataforma Datadis aplica limitación de velocidad (rate limiting)
- La mayoría de operaciones requieren un código de distribuidora

## Documentación

- **Documentación Completa**: [https://ctr-datadis.readthedocs.io](https://ctr-datadis.readthedocs.io)
- **Referencia de API**: Documentación detallada de la API con ejemplos
- **Ejemplos**: Tutoriales paso a paso y casos de uso
- **Solución de Problemas**: Problemas comunes y soluciones

## Comparación de Versiones

| Característica | Cliente V1 | Cliente V2 |
|----------------|------------|------------|
| **Datos de Consumo** | ✓ | ✓ |
| **Información de Suministro** | ✓ | ✓ |
| **Detalles del Contrato** | ✓ | ✓ |
| **Datos de Potencia Máxima** | ✓ | ✓ |
| **Datos de Energía Reactiva** | ✗ | ✓ |
| **Manejo de Errores por Distribuidor** | ✗ | ✓ |
| **Respuestas Estructuradas** | ✗ | ✓ |
| **Información de Errores Detallada** | ✗ | ✓ |
| **Soporte para NIFs Autorizados** | Limitado | ✓ |
| **Tipo de Respuesta** | Lista simple | Objeto estructurado |

### ¿Cuál elegir?

**Usa Cliente V1 cuando:**
- Migres código existente
- Necesites respuestas simples (listas directas)
- Implementes scripts básicos
- Solo requieras datos de consumo estándar

**Usa Cliente V2 cuando:** (Recomendado)
- Desarrolles aplicaciones de producción
- Necesites manejo robusto de errores
- Quieras acceso a energía reactiva
- Requieras información detallada de fallos
- Trabajes con múltiples distribuidores

## Contribuciones

Las contribuciones son bienvenidas! No dudes en enviar un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## Descargo de Responsabilidad

Este es un SDK no oficial para la API de Datadis. No está afiliado ni respaldado por Datadis o el gobierno español.
