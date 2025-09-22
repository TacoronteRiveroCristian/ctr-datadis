Inicio Rápido
=============

Esta guía te ayudará a empezar a usar el SDK de Datadis en pocos minutos. El SDK incluye dos versiones del cliente: V1 (básico) y V2 (recomendado con manejo avanzado de errores).

Configuración inicial
----------------------

Antes de comenzar, necesitas tener:

1. Una cuenta activa en `Datadis <https://datadis.es>`_
2. Tu NIF como nombre de usuario
3. Tu contraseña de acceso

.. note::
   **Importante**: La API de Datadis solo acepta fechas en formato mensual (YYYY/MM). No es posible especificar días específicos.

Instalación
-----------

.. code-block:: bash

   pip install ctr-datadis

Elección de Cliente: V1 vs V2
------------------------------

**Cliente V1 (Básico)**
   - Respuestas simples (listas directas)
   - Manejo básico de errores
   - Compatible con versiones anteriores
   - Ideal para scripts simples

**Cliente V2 (Recomendado)**
   - Respuestas estructuradas con información de errores por distribuidor
   - Manejo robusto de errores
   - Funcionalidad exclusiva: energía reactiva
   - Ideal para aplicaciones de producción

Primer ejemplo - Cliente V1
----------------------------

Ejemplo básico con el cliente V1:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   # Crear cliente V1
   client = SimpleDatadisClientV1(
       username="tu_nif",
       password="tu_contraseña"
   )

   # Obtener puntos de suministro
   supplies = client.get_supplies()

   for supply in supplies:
       print(f"CUPS: {supply.cups}")
       print(f"Dirección: {supply.address}")
       print(f"Distribuidor: {supply.distributor}")
       print("---")

   # Cerrar cliente
   client.close()

Primer ejemplo - Cliente V2 (Recomendado)
------------------------------------------

Ejemplo con manejo mejorado de errores usando V2:

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   # Crear cliente V2
   with SimpleDatadisClientV2("tu_nif", "tu_contraseña") as client:
       # Obtener puntos de suministro con manejo de errores
       supplies_response = client.get_supplies()

       print(f"Suministros obtenidos: {len(supplies_response.supplies)}")

       # Verificar errores por distribuidor
       if supplies_response.distributor_error:
           print("Errores encontrados:")
           for error in supplies_response.distributor_error:
               print(f"- {error.distributorName}: {error.errorDescription}")

       # Procesar suministros válidos
       for supply in supplies_response.supplies:
           print(f"CUPS: {supply.cups}")
           print(f"Dirección: {supply.address}")
           print(f"Distribuidor: {supply.distributor}")
           print("---")

Obtener datos de consumo
------------------------

Cliente V1 - Obtener consumo anual
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   with SimpleDatadisClientV1("tu_nif", "tu_contraseña") as client:
       # Obtener suministros
       supplies = client.get_supplies()

       if supplies:
           supply = supplies[0]  # Primer suministro

           # Obtener consumo de todo 2024 (formato mensual)
           consumption = client.get_consumption(
               cups=supply.cups,
               distributor_code=supply.distributorCode,
               date_from="2024/01",  # Enero 2024
               date_to="2024/12"     # Diciembre 2024
           )

           print(f"Registros de consumo: {len(consumption)}")

           # Calcular consumo total
           total_kwh = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
           print(f"Consumo total 2024: {total_kwh:.2f} kWh")

Cliente V2 - Obtener consumo con manejo de errores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   with SimpleDatadisClientV2("tu_nif", "tu_contraseña") as client:
       # Obtener suministros
       supplies_response = client.get_supplies()

       if supplies_response.supplies:
           supply = supplies_response.supplies[0]

           # Obtener consumo con manejo robusto de errores
           consumption_response = client.get_consumption(
               cups=supply.cups,
               distributor_code=supply.distributorCode,
               date_from="2024/01",
               date_to="2024/12"
           )

           # Verificar errores específicos
           if consumption_response.distributor_error:
               print("Errores al obtener consumo:")
               for error in consumption_response.distributor_error:
                   print(f"- {error.distributorName}: {error.errorDescription}")

           # Procesar datos válidos
           consumption = consumption_response.time_curve
           if consumption:
               total_kwh = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
               real_data = len([c for c in consumption if c.obtainMethod == "Real"])

               print(f"Consumo total 2024: {total_kwh:.2f} kWh")
               print(f"Datos reales: {real_data}/{len(consumption)} registros")

Ejemplo completo - Análisis de datos
-------------------------------------

Este ejemplo muestra cómo obtener y analizar todos los tipos de datos disponibles:

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2
   from datadis_python.exceptions import AuthenticationError, APIError, DatadisError

   def analizar_datos_completos(username, password, year="2024"):
       """Análisis completo de datos de un año específico"""

       try:
           with SimpleDatadisClientV2(username, password) as client:
               print(f"Analizando datos del año {year}...")

               # 1. Obtener distribuidores disponibles
               distributors_response = client.get_distributors()
               distributor_codes = distributors_response.dist_existence_user.get("distributorCodes", [])
               print(f"Distribuidores disponibles: {len(distributor_codes)}")

               # 2. Obtener todos los puntos de suministro
               supplies_response = client.get_supplies()
               supplies = supplies_response.supplies
               print(f"Puntos de suministro: {len(supplies)}")

               if not supplies:
                   print("No se encontraron puntos de suministro")
                   return

               # Analizar cada suministro
               for i, supply in enumerate(supplies, 1):
                   print(f"\n--- Analizando suministro {i}/{len(supplies)} ---")
                   print(f"CUPS: {supply.cups}")
                   print(f"Dirección: {supply.address}")
                   print(f"Distribuidor: {supply.distributor}")

                   try:
                       # 3. Obtener detalles del contrato
                       contract_response = client.get_contract_detail(
                           cups=supply.cups,
                           distributor_code=supply.distributorCode
                       )

                       if contract_response.contract:
                           contract = contract_response.contract[0]
                           print(f"Potencia contratada: {contract.contractedPowerkW} kW")
                           print(f"Tarifa: {contract.accessFare}")

                       # 4. Obtener datos de consumo del año
                       consumption_response = client.get_consumption(
                           cups=supply.cups,
                           distributor_code=supply.distributorCode,
                           date_from=f"{year}/01",
                           date_to=f"{year}/12"
                       )

                       consumption = consumption_response.time_curve
                       if consumption:
                           total_consumo = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
                           total_excedentes = sum(c.surplusEnergyKWh for c in consumption if c.surplusEnergyKWh)

                           print(f"Consumo total {year}: {total_consumo:.2f} kWh")
                           print(f"Excedentes generados: {total_excedentes:.2f} kWh")
                           print(f"Registros: {len(consumption)}")

                           # Verificar si tiene autoconsumo
                           tiene_autoconsumo = any(c.selfConsumptionKWh for c in consumption)
                           if tiene_autoconsumo:
                               total_autoconsumo = sum(c.selfConsumptionKWh for c in consumption if c.selfConsumptionKWh)
                               print(f"Autoconsumo: {total_autoconsumo:.2f} kWh")

                       # 5. Obtener potencias máximas
                       max_power_response = client.get_max_power(
                           cups=supply.cups,
                           distributor_code=supply.distributorCode,
                           date_from=f"{year}/01",
                           date_to=f"{year}/12"
                       )

                       if max_power_response.max_power:
                           potencias = [p.maxPower for p in max_power_response.max_power]
                           potencia_maxima_kw = max(potencias) / 1000
                           print(f"Potencia máxima registrada: {potencia_maxima_kw:.2f} kW")

                       # 6. Intentar obtener energía reactiva (solo V2)
                       try:
                           reactive_data = client.get_reactive_data(
                               cups=supply.cups,
                               distributor_code=supply.distributorCode,
                               date_from=f"{year}/01",
                               date_to=f"{year}/12"
                           )

                           if reactive_data:
                               print(f"Datos de energía reactiva: {len(reactive_data)} registros")
                           else:
                               print("Sin datos de energía reactiva")

                       except Exception as e:
                           print(f"Energía reactiva no disponible: {e}")

                   except Exception as e:
                       print(f"Error procesando {supply.cups}: {e}")

               print(f"\nAnálisis completado para {len(supplies)} suministros")

       except AuthenticationError as e:
           print(f"Error de autenticación: {e}")
           print("Verifica tu NIF y contraseña")
       except APIError as e:
           print(f"Error de API: {e}")
       except DatadisError as e:
           print(f"Error de conexión: {e}")
       except Exception as e:
           print(f"Error inesperado: {e}")

   # Ejecutar análisis
   if __name__ == "__main__":
       analizar_datos_completos(
           username="tu_nif",
           password="tu_contraseña",
           year="2024"
       )

Manejo de errores específicos
-----------------------------

El cliente V2 proporciona información detallada sobre errores por distribuidor:

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2
   from datadis_python.exceptions import AuthenticationError, APIError, DatadisError

   def manejar_errores_avanzado():
       try:
           with SimpleDatadisClientV2("tu_nif", "tu_contraseña") as client:
               # Intentar obtener suministros
               supplies_response = client.get_supplies()

               # Analizar errores específicos por distribuidor
               if supplies_response.distributor_error:
                   print("Errores por distribuidor:")
                   for error in supplies_response.distributor_error:
                       print(f"Distribuidor: {error.distributorName}")
                       print(f"Código de error: {error.errorCode}")
                       print(f"Descripción: {error.errorDescription}")
                       print("---")

               # Procesar solo los suministros que se obtuvieron correctamente
               if supplies_response.supplies:
                   print(f"Suministros válidos: {len(supplies_response.supplies)}")
                   for supply in supplies_response.supplies:
                       print(f"- {supply.cups} ({supply.distributor})")
               else:
                   print("No se pudieron obtener suministros de ningún distribuidor")

       except AuthenticationError:
           print("Credenciales inválidas. Verifica tu NIF y contraseña.")
       except APIError as e:
           print(f"Error de la API de Datadis: {e}")
       except DatadisError as e:
           print(f"Error de conexión o timeout: {e}")

Configuración avanzada
----------------------

Puedes personalizar el comportamiento del cliente:

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   # Configuración para conexiones lentas o inestables
   client = SimpleDatadisClientV2(
       username="tu_nif",
       password="tu_contraseña",
       timeout=240,  # Timeout extendido (default: 120 segundos)
       retries=5     # Más reintentos (default: 3)
   )

   # También funciona con context manager
   with SimpleDatadisClientV2("tu_nif", "tu_contraseña", timeout=180, retries=4) as client:
       supplies_response = client.get_supplies()

Comparación V1 vs V2
--------------------

Ejemplo que muestra las diferencias principales:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   def comparar_versiones(username, password):
       print("=== Cliente V1 ===")
       try:
           with SimpleDatadisClientV1(username, password) as client_v1:
               # V1 devuelve una lista directa
               supplies_v1 = client_v1.get_supplies()
               print(f"Suministros V1: {len(supplies_v1)} (lista simple)")

               if supplies_v1:
                   consumption_v1 = client_v1.get_consumption(
                       cups=supplies_v1[0].cups,
                       distributor_code=supplies_v1[0].distributorCode,
                       date_from="2024/01",
                       date_to="2024/03"
                   )
                   print(f"Consumo V1: {len(consumption_v1)} registros (lista simple)")
       except Exception as e:
           print(f"Error en V1: {e}")

       print("\n=== Cliente V2 ===")
       try:
           with SimpleDatadisClientV2(username, password) as client_v2:
               # V2 devuelve objetos de respuesta estructurados
               supplies_response_v2 = client_v2.get_supplies()
               print(f"Suministros V2: {len(supplies_response_v2.supplies)} (respuesta estructurada)")

               if supplies_response_v2.distributor_error:
                   print(f"Errores detectados: {len(supplies_response_v2.distributor_error)}")

               if supplies_response_v2.supplies:
                   consumption_response_v2 = client_v2.get_consumption(
                       cups=supplies_response_v2.supplies[0].cups,
                       distributor_code=supplies_response_v2.supplies[0].distributorCode,
                       date_from="2024/01",
                       date_to="2024/03"
                   )
                   print(f"Consumo V2: {len(consumption_response_v2.time_curve)} registros (respuesta estructurada)")

                   # Funcionalidad exclusiva de V2
                   try:
                       reactive_data = client_v2.get_reactive_data(
                           cups=supplies_response_v2.supplies[0].cups,
                           distributor_code=supplies_response_v2.supplies[0].distributorCode,
                           date_from="2024/01",
                           date_to="2024/03"
                       )
                       print(f"Energía reactiva V2: {len(reactive_data)} registros (solo en V2)")
                   except Exception as e:
                       print(f"Energía reactiva no disponible: {e}")
       except Exception as e:
           print(f"Error en V2: {e}")

Casos de uso recomendados
-------------------------

**Usa Cliente V1 cuando:**
- Necesites compatibilidad con código existente
- Implementes scripts simples o prototipos rápidos
- No requieras manejo avanzado de errores
- Trabajes con un solo distribuidor conocido

**Usa Cliente V2 cuando:**
- Desarrolles aplicaciones de producción
- Necesites manejo robusto de errores por distribuidor
- Quieras acceso a energía reactiva
- Trabajes con múltiples distribuidores
- Requieras información detallada de fallos

Próximos pasos
--------------

- Consulta los :doc:`examples` para casos de uso específicos y scripts completos
- Revisa la :doc:`api` para ver todas las funciones disponibles
- Lee sobre :doc:`models` para entender los modelos de datos
- Consulta :doc:`troubleshooting` si encuentras problemas
