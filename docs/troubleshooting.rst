Solución de Problemas
=====================

Esta sección cubre los problemas más comunes que puedes encontrar al usar el SDK de Datadis y cómo resolverlos.

Problemas de Autenticación
---------------------------

Error: "Error de autenticación"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- ``AuthenticationError`` al inicializar el cliente
- Mensaje: "Error de autenticación: 401" o similar

**Causas posibles:**

1. **Credenciales incorrectas**

   .. code-block:: python

    # Incorrecto
      client = SimpleDatadisClientV1("12345678A", "password_incorrecto")

   **Solución:** Verifica que tu NIF y contraseña sean correctos en `datadis.es <https://datadis.es>`_

2. **Formato de NIF incorrecto**

   .. code-block:: python

      # ❌ Incorrecto
      client = SimpleDatadisClientV1("12345678", "password")  # Sin letra

    # Correcto
      client = SimpleDatadisClientV1("12345678A", "password")

3. **Cuenta bloqueada o inactiva**

   **Solución:** Inicia sesión directamente en la web de Datadis para verificar el estado de tu cuenta.

Error: "Timeout en autenticación"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- El proceso de autenticación se cuelga o falla por timeout

**Soluciones:**

1. **Aumentar timeout de autenticación**

   .. code-block:: python

      client = SimpleDatadisClientV1(
          username="tu_nif",
          password="tu_password",
          timeout=180  # Aumentar a 3 minutos
      )

2. **Problemas de conectividad**

   .. code-block:: bash

      # Verificar conectividad
      ping datadis.es
      curl -I https://datadis.es

Problemas de Conectividad
-------------------------

Error: "Timeout después de X intentos"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- Timeouts frecuentes en operaciones de la API
- Respuestas lentas o incompletas

**Soluciones:**

1. **Configurar timeouts más largos**

   .. code-block:: python

      client = SimpleDatadisClientV1(
          username="tu_nif",
          password="tu_password",
          timeout=300,  # 5 minutos
          retries=5     # Más reintentos
      )

2. **Implementar reintentos personalizados**

   .. code-block:: python

      import time
      from datadis_python.exceptions import DatadisError

      def obtener_con_reintentos(func, max_intentos=5):
          for intento in range(max_intentos):
              try:
                  return func()
              except DatadisError as e:
                  if "timeout" in str(e).lower():
                      espera = min(60, (2 ** intento) * 5)
                      print(f"Timeout. Reintentando en {espera}s...")
                      time.sleep(espera)
                  else:
                      raise
          raise DatadisError("Demasiados timeouts")

Error: "Connection refused" o "Network unreachable"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Diagnóstico:**

.. code-block:: python

   import requests

   def verificar_conectividad():
       """Verifica la conectividad con Datadis"""
       urls = [
           "https://datadis.es",
           "https://api.datadis.es",
       ]

       for url in urls:
           try:
               response = requests.get(url, timeout=10)
               print(f"✅ {url}: {response.status_code}")
           except Exception as e:
               print(f"❌ {url}: {e}")

**Soluciones:**
- Verificar conexión a internet
- Comprobar firewall/proxy corporativo
- Usar VPN si estás fuera de España

Problemas con Datos
--------------------

Error: "No se encontraron datos"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- Las listas devueltas están vacías
- No se obtienen datos de consumo o suministros

**Diagnósticos:**

.. code-block:: python

   def diagnosticar_datos(client):
       """Diagnóstica problemas con datos"""

       print("🔍 Diagnosticando disponibilidad de datos...")

       # 1. Verificar distribuidores
       distribuidores = client.get_distributors()
       print(f"📍 Distribuidores: {len(distribuidores)}")

       # 2. Verificar suministros
       suministros = client.get_supplies()
       print(f"🏠 Suministros: {len(suministros)}")

       if not suministros:
           print("❌ No hay suministros disponibles. Verifica tu cuenta en datadis.es")
           return

       # 3. Probar diferentes rangos de fechas
       from datetime import datetime, timedelta

       suministro = suministros[0]
       distribuidor = distribuidores[0].code if distribuidores else "2"

       rangos = [
           (30, "último mes"),
           (90, "últimos 3 meses"),
           (365, "último año")
       ]

       for dias, descripcion in rangos:
           fin = datetime.now()
           inicio = fin - timedelta(days=dias)

           try:
               consumo = client.get_consumption(
                   cups=suministro.cups,
                   distributor_code=distribuidor,
                   date_from=inicio.strftime("%Y/%m/%d"),
                   date_to=fin.strftime("%Y/%m/%d")
               )
               print(f"📊 {descripcion}: {len(consumo)} registros")

               if consumo:
                   break

           except Exception as e:
               print(f"❌ Error en {descripcion}: {e}")

Error: "Error validando datos"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- Warnings sobre errores de validación
- Algunos registros no se procesan

**Soluciones:**

1. **Inspeccionar datos problemáticos**

   .. code-block:: python

      def inspeccionar_respuesta_api(endpoint_func, *args, **kwargs):
          """Inspecciona la respuesta cruda de la API"""

          # Hacer request manual para ver datos crudos
          import json
          from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

          with SimpleDatadisClientV1("tu_nif", "tu_password") as client:
              # Acceder al método interno para ver respuesta cruda
              response = client._make_authenticated_request(
                  endpoint="/get-consumption",  # Ejemplo
                  params={
                      "cups": "tu_cups",
                      "distributorCode": "2",
                      "startDate": "2024/01/01",
                      "endDate": "2024/01/31"
                  }
              )

              # Guardar respuesta para análisis
              with open("respuesta_cruda.json", "w") as f:
                  json.dump(response, f, indent=2)

              print("Respuesta guardada en respuesta_cruda.json")

2. **Manejo robusto de validación**

   .. code-block:: python

      from pydantic import ValidationError
      from datadis_python.models.consumption import ConsumptionData

      def procesar_datos_con_tolerancia(datos_crudos):
          """Procesa datos con tolerancia a errores"""

          datos_validos = []
          errores = []

          for i, item in enumerate(datos_crudos):
              try:
                  dato_validado = ConsumptionData(**item)
                  datos_validos.append(dato_validado)
              except ValidationError as e:
                  errores.append({
                      "indice": i,
                      "datos": item,
                      "error": str(e)
                  })

          print(f"✅ Procesados: {len(datos_validos)}")
          print(f"❌ Errores: {len(errores)}")

          return datos_validos, errores

Problemas de Rendimiento
-------------------------

Consultas Muy Lentas
~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- Las consultas tardan minutos en completarse
- Timeouts frecuentes

**Optimizaciones:**

1. **Reducir el rango de fechas**

   .. code-block:: python

      # ❌ Muy amplio (puede ser lento)
      consumo = client.get_consumption(
          cups=cups,
          distributor_code=distributor_code,
          date_from="2020/01/01",  # 4 años de datos
          date_to="2024/01/01"
      )

      # ✅ Rangos más pequeños
      from datetime import datetime, timedelta

      def obtener_consumo_por_meses(client, cups, distributor_code, fecha_inicio, fecha_fin):
          """Obtiene datos mes a mes para evitar timeouts"""

          todos_los_datos = []
          fecha_actual = datetime.strptime(fecha_inicio, "%Y/%m/%d")
          fecha_limite = datetime.strptime(fecha_fin, "%Y/%m/%d")

          while fecha_actual <= fecha_limite:
              # Calcular fin de mes
              if fecha_actual.month == 12:
                  fin_mes = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1) - timedelta(days=1)
              else:
                  fin_mes = fecha_actual.replace(month=fecha_actual.month + 1, day=1) - timedelta(days=1)

              fin_mes = min(fin_mes, fecha_limite)

              print(f"📊 Obteniendo datos: {fecha_actual.strftime('%Y/%m/%d')} - {fin_mes.strftime('%Y/%m/%d')}")

              try:
                  datos_mes = client.get_consumption(
                      cups=cups,
                      distributor_code=distributor_code,
                      date_from=fecha_actual.strftime("%Y/%m/%d"),
                      date_to=fin_mes.strftime("%Y/%m/%d")
                  )
                  todos_los_datos.extend(datos_mes)

              except Exception as e:
                  print(f"❌ Error en mes {fecha_actual.strftime('%Y/%m')}: {e}")

              # Siguiente mes
              if fecha_actual.month == 12:
                  fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1)
              else:
                  fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1, day=1)

          return todos_los_datos

2. **Procesamiento en paralelo (con cuidado)**

   .. code-block:: python

      import asyncio
      import time
      from concurrent.futures import ThreadPoolExecutor

      def obtener_datos_paralelo(suministros, username, password):
          """Obtiene datos de múltiples suministros en paralelo"""

          def procesar_suministro(suministro):
              with SimpleDatadisClientV1(username, password) as client:
                  return client.get_consumption(
                      cups=suministro.cups,
                      distributor_code="2",
                      date_from="2024/01/01",
                      date_to="2024/01/31"
                  )

          # Limitar concurrencia para no sobrecargar la API
          with ThreadPoolExecutor(max_workers=2) as executor:
              resultados = list(executor.map(procesar_suministro, suministros))

          return resultados

Problemas Específicos de la API
-------------------------------

Error: "CUPS no válido"
~~~~~~~~~~~~~~~~~~~~~~~

**Síntomas:**
- Error 400 con mensaje sobre CUPS inválido

**Verificaciones:**

.. code-block:: python

   def validar_cups(cups):
       """Valida formato de CUPS"""
       import re

       # CUPS debe tener 22 caracteres: ES + 20 dígitos/letras
       patron = r'^ES\d{16}[A-Z]{2}\d[A-Z]$'

       if not re.match(patron, cups):
           print(f"❌ CUPS inválido: {cups}")
           print("Formato esperado: ES + 16 dígitos + 2 letras + 1 dígito + 1 letra")
           return False

       print(f"✅ CUPS válido: {cups}")
       return True

Error: "Distributor code no válido"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solución:**

.. code-block:: python

   def obtener_codigo_distribuidor_valido(client, cups):
       """Obtiene el código de distribuidor correcto"""

       # Primero obtener lista de distribuidores
       distribuidores = client.get_distributors()
       print("📍 Distribuidores disponibles:")
       for dist in distribuidores:
           print(f"  - {dist.code}: {dist.name}")

       # Si conoces la provincia, puedes intentar mapear
       mapeo_provincias = {
           "Madrid": "2",
           "Barcelona": "1",
           "Valencia": "3",
           # Añadir más según necesidad
       }

       return distribuidores[0].code if distribuidores else "2"

Herramientas de Diagnóstico
---------------------------

Script de Diagnóstico Completo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   """
   Script de diagnóstico para problemas con el SDK de Datadis
   """

   import sys
   import traceback
   from datetime import datetime, timedelta
   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.exceptions import DatadisError

   def ejecutar_diagnostico(username, password):
       """Ejecuta diagnóstico completo"""

       print("🔍 DIAGNÓSTICO DEL SDK DE DATADIS")
       print("=" * 50)

       try:
           with SimpleDatadisClientV1(username, password, timeout=60) as client:

               # 1. Test de autenticación
               print("\n1️⃣  Test de autenticación...")
               if client.token:
                   print("✅ Autenticación exitosa")
               else:
                   print("❌ Error de autenticación")
                   return

               # 2. Test de distribuidores
               print("\n2️⃣  Test de distribuidores...")
               try:
                   distribuidores = client.get_distributors()
                   print(f"✅ Distribuidores obtenidos: {len(distribuidores)}")
                   for dist in distribuidores:
                       print(f"   - {dist.code}: {dist.name}")
               except Exception as e:
                   print(f"❌ Error obteniendo distribuidores: {e}")

               # 3. Test de suministros
               print("\n3️⃣  Test de suministros...")
               try:
                   suministros = client.get_supplies()
                   print(f"✅ Suministros obtenidos: {len(suministros)}")
                   for i, sup in enumerate(suministros[:3]):  # Solo primeros 3
                       print(f"   {i+1}. {sup.cups} - {getattr(sup, 'address', 'N/A')}")
               except Exception as e:
                   print(f"❌ Error obteniendo suministros: {e}")
                   return

               if not suministros:
                   print("❌ No hay suministros disponibles")
                   return

               # 4. Test de consumo
               print("\n4️⃣  Test de consumo...")
               suministro = suministros[0]
               codigo_dist = distribuidores[0].code if distribuidores else "2"

               # Probar diferentes rangos
               rangos_test = [
                   (7, "última semana"),
                   (30, "último mes"),
                   (90, "últimos 3 meses")
               ]

               for dias, descripcion in rangos_test:
                   try:
                       fin = datetime.now()
                       inicio = fin - timedelta(days=dias)

                       consumo = client.get_consumption(
                           cups=suministro.cups,
                           distributor_code=codigo_dist,
                           date_from=inicio.strftime("%Y/%m/%d"),
                           date_to=fin.strftime("%Y/%m/%d")
                       )

                       if consumo:
                           total = sum(c.consumption_kwh for c in consumo)
                           print(f"   ✅ {descripcion}: {len(consumo)} registros, {total:.2f} kWh total")
                           break
                       else:
                           print(f"   ⚠️  {descripcion}: sin datos")

                   except Exception as e:
                       print(f"   ❌ {descripcion}: {e}")

               print("\n✅ Diagnóstico completado")

       except DatadisError as e:
           print(f"\n❌ Error del SDK: {e}")
           print("\nDetalles técnicos:")
           traceback.print_exc()

       except Exception as e:
           print(f"\n❌ Error inesperado: {e}")
           print("\nDetalles técnicos:")
           traceback.print_exc()

   if __name__ == "__main__":
       if len(sys.argv) != 3:
           print("Uso: python diagnostico.py <NIF> <contraseña>")
           sys.exit(1)

       username, password = sys.argv[1], sys.argv[2]
       ejecutar_diagnostico(username, password)

Contacto y Soporte
------------------

Si después de seguir esta guía sigues teniendo problemas:

1. **Revisa los logs**: Activa logging detallado para obtener más información
2. **Documenta el error**: Incluye el mensaje de error completo y contexto
3. **Verifica versiones**: Asegúrate de usar la versión más reciente del SDK
4. **Crea un issue**: Reporta el problema en el repositorio de GitHub

.. code-block:: python

   # Activar logging detallado
   import logging
   logging.basicConfig(level=logging.DEBUG)

   # Mostrar información del sistema
   import sys
   import datadis_python

   print(f"Python: {sys.version}")
   print(f"SDK Datadis: {datadis_python.__version__}")

**Información útil para reportar bugs:**
- Versión de Python
- Versión del SDK
- Sistema operativo
- Mensaje de error completo
- Código que causa el problema
- Datos de entrada (sin credenciales)
