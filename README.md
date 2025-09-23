# ctr-datadis

[![PyPI version](https://badge.fury.io/py/ctr-datadis.svg)](https://badge.fury.io/py/ctr-datadis)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/ctr-datadis/badge/?version=latest)](https://ctr-datadis.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/TacoronteRiveroCristian/ctr-datadis/workflows/Auto%20Publish%20on%20Main%20Push/badge.svg)](https://github.com/TacoronteRiveroCristian/ctr-datadis/actions)

**Un SDK completo de Python para interactuar con la API oficial de Datadis** (plataforma española de datos de suministro eléctrico).

**Datadis** es la plataforma oficial del gobierno español que proporciona acceso a los datos de consumo eléctrico para los consumidores españoles. Este SDK facilita el acceso a tus datos eléctricos de forma programática.

## Características

- **Autenticación Automática** - Autenticación basada en tokens con renovación automática
- **Cobertura Completa de API** - Acceso a todos los endpoints de la API de Datadis
- **Parámetros Flexibles** - Acepta tipos Python nativos (datetime, int, float) además de strings
- **Seguridad de Tipos** - Type hints completos y modelos Pydantic para validación de datos
- **Manejo de Errores** - Manejo exhaustivo de errores con excepciones personalizadas
- **Python 3.9+** - Compatible con versiones modernas de Python
- **Normalización de Texto** - Manejo automático de acentos españoles y caracteres especiales
- **Modelos de Datos** - Datos estructurados con Pydantic para consumo, suministro y datos de contrato
- **Dos Versiones de API** - Soporte para clientes V1 y V2 (V2 incluye datos de energía reactiva)

## Instalación

```bash
pip install ctr-datadis
```

## Inicio Rápido

```python
from datetime import datetime, date
from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

# Inicializar cliente con tus credenciales de Datadis
client = SimpleDatadisClientV1(username="12345678A", password="tu_password")

# Obtener tus puntos de suministro
supplies = client.get_supplies()
print(f"Encontrados {len(supplies)} puntos de suministro")

# IMPORTANTE: Datadis solo acepta fechas MENSUALES (YYYY/MM), NO fechas diarias
# Obtener datos de consumo con tipos flexibles (más pythónico!)
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",  # Tu código CUPS
    distributor_code=2,             # int en lugar de string
    date_from=datetime(2024, 1, 1),  # datetime object (solo primer día del mes)
    date_to=datetime(2024, 2, 1),    # datetime object (solo primer día del mes)
    measurement_type=0              # int en lugar de string
)
print(f"Obtenidos {len(consumption)} registros de consumo")

# También funciona con strings mensuales (formato requerido por Datadis)
consumption_classic = client.get_consumption(
    cups="ES1234000000000001JN0F",
    distributor_code="2",           # string clásico
    date_from="2024/01",            # formato mensual OBLIGATORIO
    date_to="2024/02"               # formato mensual OBLIGATORIO
)

# Para cliente V2 con datos de energía reactiva
from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

client_v2 = SimpleDatadisClientV2(username="12345678A", password="tu_password")
reactive_data = client_v2.get_reactive_data(
    cups="ES1234000000000001JN0F",
    distributor_code=2,             # También acepta tipos flexibles
    date_from=datetime(2024, 1, 1), # solo primer día del mes
    date_to=datetime(2024, 2, 1)    # solo primer día del mes
)
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
```python
# ESTAS YA NO SON VÁLIDAS (contienen días específicos):
# date_from = "2024/01/15"           # RECHAZADO: contiene día específico
# date_from = datetime(2024, 1, 15)  # RECHAZADO: contiene día específico
# date_from = date(2024, 1, 15)      # RECHAZADO: contiene día específico

# SOLO ESTAS SON VÁLIDAS (formato mensual):
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

## Versiones de API

| Característica | Cliente V1 | Cliente V2 |
|----------------|------------|------------|
| Datos de Consumo | ✓ | ✓ |
| Información de Suministro | ✓ | ✓ |
| Detalles del Contrato | ✓ | ✓ |
| Datos de Potencia Máxima | ✓ | ✓ |
| Datos de Energía Reactiva | ✗ | ✓ |

**Recomendación**: Usa V1 para datos básicos de consumo, V2 para análisis avanzado de energía reactiva.

## Contribuciones

Las contribuciones son bienvenidas! No dudes en enviar un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## Descargo de Responsabilidad

Este es un SDK no oficial para la API de Datadis. No está afiliado ni respaldado por Datadis o el gobierno español.
