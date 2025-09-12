# Datadis Python SDK

SDK Python sencillo para la API oficial de Datadis (plataforma de datos de suministro de electricidad de España).

## Instalación

```bash
pip install datadis-python
```

## Uso Básico

```python
from datadis_python.client.v1.simple_client import DatadisClient

# Inicializar cliente
client = DatadisClient(username="tu_usuario", password="tu_contraseña")

# Obtener suministros
supplies = client.get_supplies()

# Obtener consumo
consumption = client.get_consumption(
    cups="ES1234000000000001JN0F",
    distributor_code="2",
    start_date="2024/01",
    end_date="2024/12"
)
```

## Documentación

Documentación completa disponible en: https://datadis-python.readthedocs.io/

## Características

- ✅ Compatible con Python 3.8+
- ✅ Autenticación automática con renovación de tokens
- ✅ Modelos Pydantic para validación de tipos
- ✅ Manejo robusto de errores
- ✅ Cobertura completa de tests
- ✅ Documentación completa

## Licencia

MIT