Inicio Rápido
=============

Esta guía te ayudará a empezar a usar el SDK de Datadis en pocos minutos.

Configuración inicial
----------------------

Antes de comenzar, necesitas tener:

1. Una cuenta activa en `Datadis <https://datadis.es>`_
2. Tu NIF como nombre de usuario
3. Tu contraseña de acceso

Primer ejemplo
--------------

Aquí tienes un ejemplo básico para obtener tus puntos de suministro:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   # Crear cliente
   client = SimpleDatadisClientV1(
       username="tu_nif",
       password="tu_contraseña"
   )

   # Obtener puntos de suministro
   supplies = client.get_supplies()

   for supply in supplies:
       print(f"CUPS: {supply.cups}")
       print(f"Dirección: {supply.address}")
       print(f"Provincia: {supply.province}")
       print("---")

   # Cerrar cliente
   client.close()

Uso con context manager (recomendado)
--------------------------------------

Para gestionar automáticamente las conexiones:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   with SimpleDatadisClientV1("tu_nif", "tu_contraseña") as client:
       # Obtener distribuidores
       distributors = client.get_distributors()

       # Obtener suministros
       supplies = client.get_supplies()

       if supplies:
           supply = supplies[0]  # Primer suministro
           # Obtener código de distribuidor correcto
           distributor_code = "2"  # Por defecto
           if distributors and distributors[0].distributor_codes:
               distributor_code = distributors[0].distributor_codes[0]

           # Obtener consumo del último mes - NOTA: API requiere formato mensual YYYY/MM
           consumption = client.get_consumption(
               cups=supply.cups,
               distributor_code=distributor_code,
               date_from="2024/01",
               date_to="2024/01"
           )

           print(f"Registros de consumo: {len(consumption)}")

Ejemplo completo
----------------

Este ejemplo muestra cómo obtener y procesar todos los tipos de datos:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datetime import datetime, timedelta

   def main():
       # Configuración
       username = "tu_nif"
       password = "tu_contraseña"

       with SimpleDatadisClientV1(username, password) as client:
           print("Obteniendo datos de Datadis...")

           # 1. Obtener distribuidores
           distributors = client.get_distributors()
           print(f"Distribuidores disponibles: {len(distributors)}")

           # 2. Obtener puntos de suministro
           supplies = client.get_supplies()
           print(f"Puntos de suministro: {len(supplies)}")

           if not supplies:
               print("No se encontraron puntos de suministro")
               return

           # Usar el primer suministro
           supply = supplies[0]
           # Obtener código de distribuidor correcto
           distributor_code = "2"  # Por defecto
           if distributors and distributors[0].distributor_codes:
               distributor_code = distributors[0].distributor_codes[0]

           print(f"Procesando datos para CUPS: {supply.cups}")

           # 3. Obtener detalle del contrato
           contracts = client.get_contract_detail(
               cups=supply.cups,
               distributor_code=distributor_code
           )
           print(f"Contratos: {len(contracts)}")

           # 4. Obtener consumo (último mes) - NOTA: API requiere formato mensual YYYY/MM
           end_date = datetime.now()
           start_date = end_date - timedelta(days=30)

           consumption = client.get_consumption(
               cups=supply.cups,
               distributor_code=distributor_code,
               date_from=start_date.strftime("%Y/%m"),
               date_to=end_date.strftime("%Y/%m")
           )
           print(f"Registros de consumo: {len(consumption)}")

           # 5. Obtener potencia máxima - NOTA: API requiere formato mensual YYYY/MM
           max_power = client.get_max_power(
               cups=supply.cups,
               distributor_code=distributor_code,
               date_from=start_date.strftime("%Y/%m"),
               date_to=end_date.strftime("%Y/%m")
           )
           print(f"Registros de potencia máxima: {len(max_power)}")

           # Mostrar algunos datos de ejemplo
           if consumption:
               total_kwh = sum(c.consumption_kwh for c in consumption)
               print(f"Consumo total: {total_kwh:.2f} kWh")

           print("Proceso completado")

   if __name__ == "__main__":
       main()

Manejo de errores
-----------------

El SDK incluye manejo robusto de errores:

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.exceptions import (
       AuthenticationError,
       APIError,
       DatadisError
   )

   try:
       with SimpleDatadisClientV1("tu_nif", "tu_contraseña") as client:
           supplies = client.get_supplies()
           print(f"Obtenidos {len(supplies)} suministros")

   except AuthenticationError as e:
    print(f"Error de autenticación: {e}")
   except APIError as e:
    print(f"Error de API: {e}")
   except DatadisError as e:
    print(f"Error general: {e}")

Configuración avanzada
----------------------

Puedes personalizar el comportamiento del cliente:

.. code-block:: python

   client = SimpleDatadisClientV1(
       username="tu_nif",
       password="tu_contraseña",
       timeout=180,  # Timeout en segundos (default: 120)
       retries=5     # Número de reintentos (default: 3)
   )

Próximos pasos
--------------

- Consulta la :doc:`api` para ver todas las funciones disponibles
- Revisa los :doc:`examples` para casos de uso específicos
- Lee sobre :doc:`models` para entender los modelos de datos
