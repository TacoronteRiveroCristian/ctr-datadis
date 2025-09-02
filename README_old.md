# Datadis Python SDK

Un SDK Python sencillo y completo para interactuar con la API oficial de Datadis (Distribuidora de Informaci�n de Suministros de Espa�a).

## Caracter�sticas

- = Autenticaci�n autom�tica y gesti�n de tokens
- =� Acceso completo a todos los endpoints de Datadis
- =� Validaci�n de par�metros y manejo de errores
- =� Type hints completos para mejor experiencia de desarrollo
- = Compatible con Python 3.8+
- � As�ncrono y s�ncrono

## Instalaci�n

```bash
pip install datadis-python
```

O usando Poetry:

```bash
poetry add datadis-python
```

## Uso R�pido

```python
from datadis_python import DatadisClient

# Inicializar cliente
client = DatadisClient(
    username="tu_usuario",
    password="tu_password"
)

# Obtener distribuidores disponibles
distributors = client.get_distributors()

# Obtener puntos de suministro
supplies = client.get_supplies()

# Obtener detalle del contrato (requiere distributor_code)
contract = client.get_contract_detail(
    cups="ES001234567890123456AB",
    distributor_code="2"  # Código del distribuidor
)

# Obtener consumos (formato mensual)
consumptions = client.get_consumption(
    cups="ES001234567890123456AB",
    distributor_code="2",
    date_from="2024/01",  # Formato: YYYY/MM
    date_to="2024/12",
    measurement_type=0,   # 0=hora, 1=cuarto hora
    point_type=1
)

# Obtener potencias máximas
max_powers = client.get_max_power(
    cups="ES001234567890123456AB", 
    distributor_code="2",
    date_from="2024/01",
    date_to="2024/12"
)
```

## Funcionalidades

### Autenticaci�n
- Login autom�tico
- Renovaci�n de tokens
- Manejo de sesiones

### Endpoints Disponibles
-  **Contratos**: Informaci�n de contratos de suministro
-  **Consumos**: Datos de consumo energ�tico
-  **Facturas**: Informaci�n de facturaci�n
-  **Puntos de suministro**: Datos CUPS
-  **Medidas**: Lecturas de contadores

### Validaciones
- Formato CUPS
- Rangos de fechas
- Par�metros requeridos
- L�mites de la API

## Documentaci�n Completa

### Cliente Principal

```python
from datadis_python import DatadisClient

client = DatadisClient(
    username="usuario",
    password="password",
    timeout=30,  # timeout en segundos
    retries=3    # reintentos autom�ticos
)
```

### M�todos Disponibles

#### Obtener Contratos
```python
contracts = client.get_contracts()
# Devuelve lista de contratos disponibles
```

#### Obtener Consumos
```python
consumptions = client.get_consumption(
    cups="ES001234567890123456AB",
    date_from="2024-01-01",
    date_to="2024-12-31",
    measurement_type=0,  # 0: Consumo, 1: Generaci�n
    point_type=1         # Tipo de punto
)
```

#### Obtener Facturas
```python
invoices = client.get_invoices(
    cups="ES001234567890123456AB", 
    date_from="2024-01-01",
    date_to="2024-12-31"
)
```

#### Obtener Puntos de Suministro
```python
supplies = client.get_supplies()
```

### Modelos de Datos

Los datos se devuelven como objetos Python tipados:

```python
# Ejemplo de datos de consumo
consumption = consumptions[0]
print(f"Consumo: {consumption.consumption_kwh} kWh")
print(f"Fecha: {consumption.date}")
print(f"Precio: {consumption.price}")
```

### Manejo de Errores

```python
from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

try:
    consumptions = client.get_consumption(cups="INVALID_CUPS")
except AuthenticationError:
    print("Error de autenticaci�n")
except APIError as e:
    print(f"Error de API: {e.message} (c�digo: {e.status_code})")
except DatadisError as e:
    print(f"Error general: {e}")
```

## Desarrollo

### Requisitos
- Python 3.8+
- Poetry para gesti�n de dependencias

### Setup de Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/datadis-python.git
cd datadis-python

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell

# Ejecutar tests
poetry run pytest

# Ejecutar linting
poetry run black .
poetry run isort .
poetry run mypy datadis_python
```

### Ejecutar Tests

```bash
# Tests unitarios
poetry run pytest tests/

# Tests con cobertura
poetry run pytest --cov=datadis_python tests/

# Tests de integraci�n (requiere credenciales)
poetry run pytest tests/integration/ --username=tu_usuario --password=tu_password
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'A�ade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Roadmap

- [ ] Soporte para cliente as�ncrono
- [ ] Cache de respuestas
- [ ] CLI para uso desde terminal
- [ ] Exportaci�n a diferentes formatos (CSV, Excel)
- [ ] Documentaci�n interactiva
- [ ] Ejemplos avanzados

## Licencia

MIT License - ver archivo [LICENSE](LICENSE) para detalles.

## Soporte

- =� [Documentaci�n oficial de Datadis](https://datadis.es)
- = [Issues en GitHub](https://github.com/tu-usuario/datadis-python/issues)
- =� [Discusiones](https://github.com/tu-usuario/datadis-python/discussions)

## Descargo de Responsabilidad

Este proyecto no est� oficialmente afiliado con Datadis. Es una implementaci�n independiente del SDK para facilitar el acceso a su API p�blica.