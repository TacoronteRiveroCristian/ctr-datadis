Modelos de Datos
================

El SDK utiliza Pydantic para proporcionar modelos de datos type-safe que validan automáticamente las respuestas de la API de Datadis. Todos los modelos incluyen validación de tipos y conversión automática de datos.

Características Generales
--------------------------

Todos los modelos comparten estas características:

- **Validación automática**: Los datos se validan al crear instancias
- **Serialización**: Conversión automática a/desde JSON
- **Type hints**: Soporte completo para IDEs y herramientas de análisis
- **Alias de campos**: Mapeo automático entre nombres de la API y Python
- **Documentación integrada**: Cada campo está documentado

Modelo de Consumo Energético
-----------------------------

.. autoclass:: datadis_python.models.consumption.ConsumptionData
   :members:
   :undoc-members:

El modelo ``ConsumptionData`` representa un registro de consumo energético:

.. code-block:: python

   from datadis_python.models.consumption import ConsumptionData

   # Crear desde diccionario (como viene de la API)
   consumo = ConsumptionData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       consumptionKWh=2.5,
       obtainMethod="Real"
   )

   # Acceder a los datos
   print(f"Consumo: {consumo.consumption_kwh} kWh")
   print(f"Fecha: {consumo.date} {consumo.time}")
   print(f"Método: {consumo.obtain_method}")

   # Serializar a diccionario
   data = consumo.model_dump()

Modelo de Punto de Suministro
------------------------------

.. autoclass:: datadis_python.models.supply.SupplyData
   :members:
   :undoc-members:

Representa un punto de suministro eléctrico:

.. code-block:: python

   from datadis_python.models.supply import SupplyData

   suministro = SupplyData(
       cups="ES1234000000000001JN0F",
       distributorCode="2",
       address="Calle Ejemplo 123",
       postalCode="28001",
       province="Madrid",
       municipality="Madrid",
       validDateFrom="2020/01/01",
       validDateTo="2025/12/31"
   )

   print(f"CUPS: {suministro.cups}")
   print(f"Dirección: {suministro.address}")
   print(f"Válido hasta: {suministro.valid_date_to}")

Modelo de Contrato
------------------

.. autoclass:: datadis_python.models.contract.ContractData
   :members:
   :undoc-members:

Información contractual del suministro:

.. code-block:: python

   from datadis_python.models.contract import ContractData

   contrato = ContractData(
       cups="ES1234000000000001JN0F",
       distributorCode="2",
       marketer="Iberdrola",
       tension="BT",
       accessRate="2.0TD",
       contractedPowerP1=5.5,
       contractedPowerP2=5.5,
       validDateFrom="2023/01/01"
   )

   print(f"Comercializadora: {contrato.marketer}")
   print(f"Tarifa: {contrato.access_rate}")
   print(f"Potencia P1: {contrato.contracted_power_p1} kW")

Modelo de Distribuidor
----------------------

.. autoclass:: datadis_python.models.distributor.DistributorData
   :members:
   :undoc-members:

Información sobre las empresas distribuidoras:

.. code-block:: python

   from datadis_python.models.distributor import DistributorData

   distribuidor = DistributorData(
       distributorCodes=["2", "3", "5"]
   )

   print(f"Códigos disponibles: {distribuidor.distributor_codes}")
   print(f"Primer código: {distribuidor.distributor_codes[0]}")

Modelo de Potencia Máxima
--------------------------

.. autoclass:: datadis_python.models.max_power.MaxPowerData
   :members:
   :undoc-members:

Registros de potencia máxima demandada:

.. code-block:: python

   from datadis_python.models.max_power import MaxPowerData

   potencia = MaxPowerData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="19:00",
       maxPower=4.2,
       period="P1"
   )

   print(f"Potencia máxima: {potencia.max_power} kW")
   print(f"Período: {potencia.period}")

Modelo de Energía Reactiva
---------------------------

.. autoclass:: datadis_python.models.reactive.ReactiveData
   :members:
   :undoc-members:

Datos de energía reactiva:

.. code-block:: python

   from datadis_python.models.reactive import ReactiveData

   reactiva = ReactiveData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       reactiveEnergyQ1=0.5,
       reactiveEnergyQ2=0.3,
       reactiveEnergyQ3=0.1,
       reactiveEnergyQ4=0.2
   )

   print(f"Q1: {reactiva.reactive_energy_q1} kVArh")

Modelos de Respuesta
--------------------

Respuesta Base
~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.responses.DatadisResponse
   :members:
   :undoc-members:

Respuesta de Error
~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.responses.ErrorResponse
   :members:
   :undoc-members:

Respuesta Paginada
~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.responses.PaginatedResponse
   :members:
   :undoc-members:

Validación y Errores
--------------------

Manejo de Errores de Validación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Los modelos de Pydantic validan automáticamente los datos:

.. code-block:: python

   from datadis_python.models.consumption import ConsumptionData
   from pydantic import ValidationError

   try:
       # Datos inválidos
       consumo = ConsumptionData(
           cups="",  # CUPS vacío (inválido)
           date="fecha-incorrecta",  # Formato incorrecto
           time="25:70",  # Hora inválida
           consumptionKWh="no-es-numero"  # Tipo incorrecto
       )
   except ValidationError as e:
       print("Errores de validación:")
       for error in e.errors():
           print(f"- {error['loc']}: {error['msg']}")

Conversión Automática de Tipos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pydantic intenta convertir tipos automáticamente cuando es posible:

.. code-block:: python

   from datadis_python.models.consumption import ConsumptionData

   # Los números como string se convierten automáticamente
   consumo = ConsumptionData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       consumptionKWh="2.5",  # String que se convierte a float
       obtainMethod="Real"
   )

   print(type(consumo.consumption_kwh))  # <class 'float'>
   print(consumo.consumption_kwh)        # 2.5

Configuración del Modelo
~~~~~~~~~~~~~~~~~~~~~~~~

Los modelos incluyen configuración específica:

.. code-block:: python

   # Todos los modelos permiten usar alias
   data = {
       "consumptionKWh": 2.5  # Nombre de la API
   }

   consumo = ConsumptionData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       obtainMethod="Real",
       **data
   )

   # Acceso con nombre pythónico
   print(consumo.consumption_kwh)  # 2.5

Serialización Avanzada
----------------------

Exportar a JSON
~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from datadis_python.models.consumption import ConsumptionData

   consumo = ConsumptionData(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       consumptionKWh=2.5,
       obtainMethod="Real"
   )

   # Exportar a JSON
   json_data = consumo.model_dump_json(indent=2)
   print(json_data)

   # Cargar desde JSON
   consumo_cargado = ConsumptionData.model_validate_json(json_data)

Filtrar Campos
~~~~~~~~~~~~~~

.. code-block:: python

   # Incluir solo ciertos campos
   data = consumo.model_dump(include={'cups', 'consumption_kwh'})

   # Excluir campos
   data = consumo.model_dump(exclude={'time'})

   # Usar alias en la salida
   data = consumo.model_dump(by_alias=True)

Creación de Modelos Personalizados
-----------------------------------

Si necesitas extender los modelos:

.. code-block:: python

   from datadis_python.models.consumption import ConsumptionData
   from pydantic import computed_field

   class ConsumptionExtended(ConsumptionData):
       """Modelo extendido con campos calculados"""

       @computed_field
       @property
       def consumption_wh(self) -> float:
           """Consumo en Wh en lugar de kWh"""
           return self.consumption_kwh * 1000

       @computed_field
       @property
       def fecha_completa(self) -> str:
           """Fecha y hora combinadas"""
           return f"{self.date} {self.time}"

   # Uso
   consumo = ConsumptionExtended(
       cups="ES1234000000000001JN0F",
       date="2024/01/15",
       time="01:00",
       consumptionKWh=2.5,
       obtainMethod="Real"
   )

   print(f"Consumo: {consumo.consumption_wh} Wh")
   print(f"Timestamp: {consumo.fecha_completa}")

Mejores Prácticas
-----------------

1. **Validación temprana**: Usa los modelos inmediatamente después de recibir datos
2. **Type hints**: Aprovecha las anotaciones de tipo para mejor desarrollo
3. **Serialización**: Usa ``model_dump()`` para convertir a diccionarios
4. **Manejo de errores**: Captura ``ValidationError`` para datos inválidos
5. **Documentación**: Los docstrings están disponibles en tiempo de ejecución
