Manejo de Excepciones
=====================

El SDK de Datadis incluye una jerarquía de excepciones personalizadas para manejar diferentes tipos de errores que pueden ocurrir durante la interacción con la API.

Jerarquía de Excepciones
-------------------------

.. code-block:: text

   DatadisError (base)
   ├── AuthenticationError
   ├── APIError
   └── ValidationError

Todas las excepciones heredan de ``DatadisError``, lo que permite capturar cualquier error específico del SDK.

DatadisError (Excepción Base)
-----------------------------

.. autoclass:: datadis_python.exceptions.DatadisError
   :members:
   :undoc-members:

Excepción base para todos los errores del SDK. Hereda de ``Exception``.

.. code-block:: python

   from datadis_python.exceptions import DatadisError

   try:
       # Operación con el cliente
       result = client.get_supplies()
   except DatadisError as e:
       print(f"Error del SDK de Datadis: {e}")

AuthenticationError
-------------------

.. autoclass:: datadis_python.exceptions.AuthenticationError
   :members:
   :undoc-members:

Se produce cuando hay problemas de autenticación con la API de Datadis.

**Causas comunes:**

- Credenciales incorrectas (NIF/contraseña)
- Token expirado
- Problemas de conectividad durante la autenticación
- Servidor de autenticación no disponible

.. code-block:: python

   from datadis_python.exceptions import AuthenticationError
   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   try:
       client = SimpleDatadisClientV1("nif_incorrecto", "password_incorrecta")
       supplies = client.get_supplies()
   except AuthenticationError as e:
       print(f"Error de autenticación: {e}")
       # Posibles acciones:
       # - Verificar credenciales
       # - Reintentar tras un tiempo
       # - Solicitar nuevas credenciales al usuario

APIError
--------

.. autoclass:: datadis_python.exceptions.APIError
   :members:
   :undoc-members:

Se produce cuando la API de Datadis devuelve un error HTTP (4xx, 5xx).

**Causas comunes:**

- Error HTTP 400: Parámetros incorrectos
- Error HTTP 404: Recurso no encontrado
- Error HTTP 429: Límite de velocidad excedido
- Error HTTP 500: Error interno del servidor
- Error HTTP 503: Servicio no disponible

.. code-block:: python

   from datadis_python.exceptions import APIError

   try:
       consumption = client.get_consumption(
           cups="CUPS_INVALIDO",
           distributor_code="999",  # Código inválido
           date_from="2024/01/01",
           date_to="2024/01/31"
       )
   except APIError as e:
       print(f"Error de API: {e}")
       print(f"Código HTTP: {e.status_code}")

       if e.status_code == 400:
           print("Parámetros incorrectos")
       elif e.status_code == 404:
           print("Recurso no encontrado")
       elif e.status_code == 429:
           print("Límite de velocidad excedido - esperar antes de reintentar")
       elif e.status_code >= 500:
           print("Error del servidor - reintentar más tarde")

ValidationError
---------------

.. autoclass:: datadis_python.exceptions.ValidationError
   :members:
   :undoc-members:

Se produce cuando los datos no pasan la validación de Pydantic.

**Causas comunes:**

- Datos con formato incorrecto
- Tipos de datos incorrectos
- Campos requeridos faltantes
- Valores fuera de rango

.. code-block:: python

   from datadis_python.exceptions import ValidationError
   from datadis_python.models.consumption import ConsumptionData

   try:
       # Datos con formato incorrecto
       invalid_data = {
           "cups": "",  # CUPS vacío
           "date": "fecha-incorrecta",
           "time": "25:70",  # Hora inválida
           "consumptionKWh": "no-es-numero"
       }
       consumption = ConsumptionData(**invalid_data)
   except ValidationError as e:
       print(f"Error de validación: {e}")
       for error in e.errors():
           print(f"- Campo '{error['loc'][0]}': {error['msg']}")

Estrategias de Manejo de Errores
---------------------------------

Manejo Específico por Tipo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.exceptions import (
       AuthenticationError,
       APIError,
       ValidationError,
       DatadisError
   )
   import time

   def obtener_datos_con_manejo_robusto(username, password, cups, distributor_code):
       """Ejemplo de manejo robusto de errores"""

       max_intentos = 3
       tiempo_espera = 5

       for intento in range(max_intentos):
           try:
               with SimpleDatadisClientV1(username, password) as client:
                   return client.get_consumption(
                       cups=cups,
                       distributor_code=distributor_code,
                       date_from="2024/01/01",
                       date_to="2024/01/31"
                   )

           except AuthenticationError as e:
               print(f"❌ Error de autenticación: {e}")
               # No reintentar para errores de credenciales
               raise

           except APIError as e:
               print(f"⚠️  Error de API (intento {intento + 1}/{max_intentos}): {e}")

               if e.status_code == 429:  # Rate limit
                   tiempo_espera *= 2  # Backoff exponencial
                   print(f"⏳ Rate limit excedido. Esperando {tiempo_espera}s...")
                   time.sleep(tiempo_espera)
               elif e.status_code >= 500:  # Error del servidor
                   print(f"🔄 Error del servidor. Esperando {tiempo_espera}s...")
                   time.sleep(tiempo_espera)
               else:
                   # Errores 4xx (excepto 429) no son recuperables
                   raise

           except ValidationError as e:
               print(f"❌ Error de validación: {e}")
               # Los errores de validación no son recuperables
               raise

           except DatadisError as e:
               print(f"⚠️  Error general (intento {intento + 1}/{max_intentos}): {e}")
               if intento < max_intentos - 1:
                   time.sleep(tiempo_espera)
               else:
                   raise

       raise DatadisError(f"No se pudo obtener datos después de {max_intentos} intentos")

Wrapper con Logging
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from functools import wraps
   from datadis_python.exceptions import DatadisError

   # Configurar logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   def log_datadis_errors(func):
       """Decorator para logging automático de errores"""
       @wraps(func)
       def wrapper(*args, **kwargs):
           try:
               result = func(*args, **kwargs)
               logger.info(f"✅ {func.__name__} ejecutado exitosamente")
               return result
           except AuthenticationError as e:
               logger.error(f"🔐 Error de autenticación en {func.__name__}: {e}")
               raise
           except APIError as e:
               logger.error(f"🌐 Error de API en {func.__name__}: {e} (HTTP {e.status_code})")
               raise
           except ValidationError as e:
               logger.error(f"✅ Error de validación en {func.__name__}: {e}")
               raise
           except DatadisError as e:
               logger.error(f"❌ Error general en {func.__name__}: {e}")
               raise
       return wrapper

   # Uso del decorator
   @log_datadis_errors
   def obtener_suministros(username, password):
       with SimpleDatadisClientV1(username, password) as client:
           return client.get_supplies()

Context Manager con Manejo de Errores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from contextlib import contextmanager
   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.exceptions import DatadisError

   @contextmanager
   def datadis_client_with_error_handling(username, password, **kwargs):
       """Context manager que maneja errores automáticamente"""
       client = None
       try:
           client = SimpleDatadisClientV1(username, password, **kwargs)
           yield client
       except AuthenticationError:
           print("❌ Credenciales incorrectas o problema de autenticación")
           raise
       except APIError as e:
           if e.status_code == 429:
               print("⏳ Límite de velocidad excedido. Intenta más tarde.")
           elif e.status_code >= 500:
               print("🔧 Problema del servidor. Intenta más tarde.")
           else:
               print(f"🌐 Error de API: {e}")
           raise
       except ValidationError as e:
           print(f"📋 Datos inválidos: {e}")
           raise
       except DatadisError as e:
           print(f"❌ Error general: {e}")
           raise
       finally:
           if client:
               client.close()

   # Uso
   try:
       with datadis_client_with_error_handling("tu_nif", "tu_password") as client:
           supplies = client.get_supplies()
           print(f"Obtenidos {len(supplies)} suministros")
   except DatadisError:
       print("No se pudieron obtener los datos")

Reintentos Inteligentes
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import random
   from datadis_python.exceptions import APIError, DatadisError

   def ejecutar_con_reintentos(func, max_intentos=3, *args, **kwargs):
       """Ejecuta una función con reintentos inteligentes"""

       for intento in range(max_intentos):
           try:
               return func(*args, **kwargs)

           except APIError as e:
               if e.status_code == 429:  # Rate limit
                   # Backoff exponencial con jitter
                   espera = (2 ** intento) + random.uniform(0, 1)
                   print(f"⏳ Rate limit. Esperando {espera:.1f}s...")
                   time.sleep(espera)
               elif e.status_code >= 500:  # Error del servidor
                   espera = 2 ** intento
                   print(f"🔄 Error del servidor. Esperando {espera}s...")
                   time.sleep(espera)
               else:
                   # Otros errores de API no son recuperables
                   raise

           except DatadisError as e:
               if intento < max_intentos - 1:
                   espera = 1 + random.uniform(0, 1)
                   print(f"⚠️  Error general. Reintentando en {espera:.1f}s...")
                   time.sleep(espera)
               else:
                   raise

       raise DatadisError(f"Operación falló después de {max_intentos} intentos")

   # Uso
   def obtener_datos():
       with SimpleDatadisClientV1("tu_nif", "tu_password") as client:
           return client.get_supplies()

   try:
       supplies = ejecutar_con_reintentos(obtener_datos, max_intentos=5)
       print(f"✅ Obtenidos {len(supplies)} suministros")
   except DatadisError as e:
       print(f"❌ Error final: {e}")

Mejores Prácticas
-----------------

1. **Captura específica**: Captura tipos específicos de excepción cuando sea posible
2. **Logging**: Registra errores para debugging y monitoreo
3. **Reintentos inteligentes**: Implementa backoff exponencial para errores recuperables
4. **Timeouts**: Usa timeouts apropiados para evitar bloqueos
5. **Validación temprana**: Valida parámetros antes de hacer llamadas a la API
6. **Manejo graceful**: Proporciona fallbacks o mensajes de error útiles al usuario
7. **No reintentar errores de autenticación**: Los errores 401/403 no son recuperables
8. **Respetar rate limits**: Implementa delays apropiados para errores 429
