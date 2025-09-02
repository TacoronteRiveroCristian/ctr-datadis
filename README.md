# Datadis Python SDK

Un SDK Python sencillo y completo para interactuar con la API oficial de Datadis (Distribuidora de Información de Suministros de España).

## Características

- 🔑 Autenticación automática y gestión de tokens
- 📊 Acceso completo a todos los endpoints de Datadis
- 🛡️ Validación de parámetros y manejo de errores
- 📝 Type hints completos para mejor experiencia de desarrollo
- 🐍 Compatible con Python 3.8+
- ⚡ API v2 actualizada con endpoints reales

## Instalación

```bash
pip install datadis-python
```

O usando Poetry:

```bash
poetry add datadis-python
```

## Uso Rápido

```python
from datadis_python import DatadisClient

# Inicializar cliente (NIF como username)
client = DatadisClient(
    username="12345678A",  # Tu NIF registrado en Datadis
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

# Obtener consumos (formato mensual YYYY/MM)
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

### Autenticación
- Login automático con NIF y contraseña
- Renovación automática de tokens
- Manejo de sesiones seguras

### Endpoints Disponibles (API v2)
- ✅ **Distribuidores**: Lista de códigos de distribuidores disponibles
- ✅ **Puntos de suministro**: Datos CUPS e información básica
- ✅ **Contratos**: Información detallada de contratos de suministro
- ✅ **Consumos**: Datos de consumo energético (horario/cuarto horario)
- ✅ **Potencia máxima**: Mediciones de potencia demandada
- ⏳ **Energía reactiva**: Datos de energía reactiva (próximamente)

### Validaciones
- Formato CUPS correcto (ES + 18 dígitos + 2 letras)
- Rangos de fechas válidos (máximo 2 años hacia atrás)
- Códigos de distribuidor válidos (1-8)
- Parámetros requeridos por la API

### Códigos de Distribuidor
- 1: Viesgo
- 2: E-distribución  
- 3: E-redes
- 4: ASEME
- 5: UFD
- 6: EOSA
- 7: CIDE
- 8: IDE

## Documentación Completa

### Cliente Principal

```python
from datadis_python import DatadisClient

client = DatadisClient(
    username="12345678A",  # NIF registrado en Datadis
    password="password",
    timeout=30,   # timeout en segundos
    retries=3     # reintentos automáticos
)
```

### Métodos Disponibles

#### Obtener Distribuidores
```python
distributors = client.get_distributors()
# Devuelve: ['2', '8'] (ejemplo)
```

#### Obtener Puntos de Suministro
```python
supplies = client.get_supplies()
# Opcionalmente filtrar por distribuidor:
supplies = client.get_supplies(distributor_code="2")
```

#### Obtener Detalle de Contrato
```python
contract = client.get_contract_detail(
    cups="ES001234567890123456AB",
    distributor_code="2"
)
# Devuelve información completa del contrato
```

#### Obtener Consumos
```python
consumptions = client.get_consumption(
    cups="ES001234567890123456AB",
    distributor_code="2", 
    date_from="2024/01",      # Formato YYYY/MM
    date_to="2024/02",
    measurement_type=0,       # 0=hora, 1=cuarto hora
    point_type=1             # Obtenido de supplies
)
```

#### Obtener Potencias Máximas
```python
max_powers = client.get_max_power(
    cups="ES001234567890123456AB",
    distributor_code="2",
    date_from="2024/01",     # Formato YYYY/MM
    date_to="2024/02"
)
```

### Modelos de Datos

Los datos se devuelven como objetos Python tipados con Pydantic:

```python
# Ejemplo de datos de suministro
supply = supplies[0]
print(f"CUPS: {supply.cups}")
print(f"Dirección: {supply.address}")
print(f"Distribuidor: {supply.distributor}")

# Ejemplo de datos de consumo
consumption = consumptions[0]
print(f"Fecha: {consumption.date} {consumption.time}")
print(f"Consumo: {consumption.consumption_kwh} kWh")
print(f"Método: {consumption.obtain_method}")
```

### Manejo de Errores

```python
from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

try:
    supplies = client.get_supplies()
except AuthenticationError:
    print("Error de autenticación - verifica NIF y contraseña")
except APIError as e:
    print(f"Error de API: {e.message} (código: {e.status_code})")
except DatadisError as e:
    print(f"Error general: {e}")
```

### Limitaciones Importantes

⚠️ **Limitaciones de la API de Datadis:**
- Datos disponibles solo para los **últimos 2 años**
- Requiere **código de distribuidor** para la mayoría de consultas
- Formato de fechas específico: **YYYY/MM** (mensual) 
- Rate limiting aplicado por Datadis

## Desarrollo

### Setup de Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/datadis-python.git
cd datadis-python

# Instalar con Poetry
poetry install

# Activar entorno virtual
poetry shell

# Ejecutar tests
poetry run pytest

# Ejecutar ejemplo
poetry run python examples/basic_usage.py
```

### Ejecutar Tests

```bash
# Tests unitarios
poetry run pytest tests/

# Tests con cobertura
poetry run pytest --cov=datadis_python tests/
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Changelog

### v0.1.0 (Actual)
- ✅ Implementación inicial basada en API v2 real de Datadis
- ✅ Endpoints: distribuidores, suministros, contratos, consumos, potencia máxima
- ✅ Validaciones completas de parámetros
- ✅ Modelos tipados con Pydantic
- ✅ Manejo robusto de errores
- ✅ Documentación completa

## Roadmap

- [ ] Endpoint de energía reactiva
- [ ] Cliente asíncrono (async/await)
- [ ] Cache de respuestas
- [ ] CLI para uso desde terminal
- [ ] Exportación a CSV/Excel
- [ ] Integración con pandas

## Licencia

MIT License - ver archivo [LICENSE](LICENSE) para detalles.

## Soporte

- 📚 [Documentación oficial de Datadis](https://datadis.es)
- 🐛 [Issues en GitHub](https://github.com/tu-usuario/datadis-python/issues)
- 💬 [Discusiones](https://github.com/tu-usuario/datadis-python/discussions)

## Descargo de Responsabilidad

Este proyecto no está oficialmente afiliado con Datadis. Es una implementación independiente del SDK para facilitar el acceso a su API pública siguiendo la documentación oficial disponible.