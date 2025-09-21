# ctr-datadis

[![PyPI version](https://badge.fury.io/py/ctr-datadis.svg)](https://badge.fury.io/py/ctr-datadis)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/ctr-datadis/badge/?version=latest)](https://ctr-datadis.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/tu-usuario/datadis/workflows/Tests/badge.svg)](https://github.com/tu-usuario/datadis/actions)

**Un SDK completo de Python para interactuar con la API oficial de Datadis** (plataforma española de datos de suministro eléctrico).

**Datadis** es la plataforma oficial del gobierno español que proporciona acceso a los datos de consumo eléctrico para los consumidores españoles. Este SDK facilita el acceso a tus datos eléctricos de forma programática.

## Características

- **Autenticación Automática** - Autenticación basada en tokens con renovación automática
- **Cobertura Completa de API** - Acceso a todos los endpoints de la API de Datadis
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
from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

# Inicializar cliente con tus credenciales de Datadis
client = SimpleDatadisClientV1(username="12345678A", password="tu_password")

# Obtener tus puntos de suministro
supplies = client.get_supplies()
print(f"Encontrados {len(supplies)} puntos de suministro")

# Obtener datos de consumo para un punto de suministro específico
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",  # Tu código CUPS
    distributor_code="2",           # Tu código de distribuidora
    start_date="2024/01",           # Fecha de inicio (YYYY/MM)
    end_date="2024/02"              # Fecha de fin (YYYY/MM)
)
print(f"Obtenidos {len(consumption)} registros de consumo")

# Para cliente V2 con datos de energía reactiva
from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

client_v2 = SimpleDatadisClientV2(username="12345678A", password="tu_password")
reactive_data = client_v2.get_reactive_data(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01",
    end_date="2024/02"
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
# Obtener datos de consumo
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01",
    end_date="2024/02"
)

# Obtener datos de potencia máxima
max_power = client.get_max_power(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01",
    end_date="2024/02"
)
```

### Información de Distribuidoras
```python
# Obtener distribuidoras disponibles
distributors = client.get_distributors()
```

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
- El formato de fecha debe ser YYYY/MM (datos mensuales)
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