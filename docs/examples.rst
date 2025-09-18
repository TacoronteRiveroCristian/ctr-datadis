Ejemplos de Uso
===============

Esta sección muestra ejemplos prácticos para casos de uso comunes.

Análisis de Consumo Mensual
----------------------------

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datetime import datetime, timedelta
   import json

   def analizar_consumo_mensual(username, password, cups, distributor_code):
       """Analiza el consumo energético del último mes"""

       with SimpleDatadisClientV1(username, password) as client:
           # Calcular fechas (último mes completo)
           hoy = datetime.now()
           fin_mes_anterior = hoy.replace(day=1) - timedelta(days=1)
           inicio_mes_anterior = fin_mes_anterior.replace(day=1)

           fecha_inicio = inicio_mes_anterior.strftime("%Y/%m/%d")
           fecha_fin = fin_mes_anterior.strftime("%Y/%m/%d")

           print(f"📊 Analizando consumo: {fecha_inicio} - {fecha_fin}")

           # Obtener datos de consumo
           consumo = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=fecha_inicio,
               date_to=fecha_fin
           )

           if not consumo:
               print("❌ No se encontraron datos de consumo")
               return

           # Análisis básico
           total_kwh = sum(c.consumption_kwh for c in consumo)
           consumo_diario = {}

           for registro in consumo:
               fecha = registro.date
               if fecha not in consumo_diario:
                   consumo_diario[fecha] = 0
               consumo_diario[fecha] += registro.consumption_kwh

           # Estadísticas
           consumo_por_dia = list(consumo_diario.values())
           consumo_promedio = total_kwh / len(consumo_diario) if consumo_diario else 0
           consumo_maximo = max(consumo_por_dia) if consumo_por_dia else 0
           consumo_minimo = min(consumo_por_dia) if consumo_por_dia else 0

           # Resultados
           print(f"💡 Consumo total: {total_kwh:.2f} kWh")
           print(f"📈 Consumo promedio diario: {consumo_promedio:.2f} kWh")
           print(f"🔺 Consumo máximo diario: {consumo_maximo:.2f} kWh")
           print(f"🔻 Consumo mínimo diario: {consumo_minimo:.2f} kWh")
           print(f"📅 Días con datos: {len(consumo_diario)}")

           return {
               "total_kwh": total_kwh,
               "promedio_diario": consumo_promedio,
               "maximo_diario": consumo_maximo,
               "minimo_diario": consumo_minimo,
               "dias_con_datos": len(consumo_diario),
               "consumo_diario": consumo_diario
           }

   # Uso
   resultado = analizar_consumo_mensual(
       username="tu_nif",
       password="tu_contraseña",
       cups="ES1234000000000001JN0F",
       distributor_code="2"
   )

Comparación de Períodos
------------------------

.. code-block:: python

   def comparar_periodos(username, password, cups, distributor_code, meses_atras=2):
       """Compara el consumo de diferentes períodos"""

       with SimpleDatadisClientV1(username, password) as client:
           resultados = {}

           for i in range(meses_atras):
               # Calcular fechas para cada mes
               hoy = datetime.now()
               fecha_fin = (hoy.replace(day=1) - timedelta(days=1)) - timedelta(days=32*i)
               fecha_inicio = fecha_fin.replace(day=1)

               periodo = fecha_inicio.strftime("%Y/%m")
               fecha_inicio_str = fecha_inicio.strftime("%Y/%m/%d")
               fecha_fin_str = fecha_fin.strftime("%Y/%m/%d")

               print(f"📊 Procesando período: {periodo}")

               # Obtener consumo
               consumo = client.get_consumption(
                   cups=cups,
                   distributor_code=distributor_code,
                   date_from=fecha_inicio_str,
                   date_to=fecha_fin_str
               )

               total_kwh = sum(c.consumption_kwh for c in consumo)
               resultados[periodo] = {
                   "total_kwh": total_kwh,
                   "registros": len(consumo)
               }

           # Mostrar comparación
           print("\n📈 Comparación de períodos:")
           for periodo, datos in resultados.items():
               print(f"{periodo}: {datos['total_kwh']:.2f} kWh ({datos['registros']} registros)")

           return resultados

Exportar Datos a JSON
----------------------

.. code-block:: python

   def exportar_datos_completos(username, password, cups, distributor_code, fecha_inicio, fecha_fin):
       """Exporta todos los datos disponibles a formato JSON"""

       with SimpleDatadisClientV1(username, password) as client:
           datos_completos = {
               "metadata": {
                   "cups": cups,
                   "distributor_code": distributor_code,
                   "fecha_inicio": fecha_inicio,
                   "fecha_fin": fecha_fin,
                   "exportado_en": datetime.now().isoformat()
               },
               "datos": {}
           }

           print("📊 Exportando datos completos...")

           # 1. Consumo
           print("⚡ Obteniendo consumo...")
           consumo = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=fecha_inicio,
               date_to=fecha_fin
           )
           datos_completos["datos"]["consumo"] = [
               c.model_dump() for c in consumo
           ]

           # 2. Potencia máxima
           print("🔋 Obteniendo potencia máxima...")
           potencia = client.get_max_power(
               cups=cups,
               distributor_code=distributor_code,
               date_from=fecha_inicio,
               date_to=fecha_fin
           )
           datos_completos["datos"]["potencia_maxima"] = [
               p.model_dump() for p in potencia
           ]

           # 3. Contratos
           print("📋 Obteniendo contratos...")
           contratos = client.get_contract_detail(
               cups=cups,
               distributor_code=distributor_code
           )
           datos_completos["datos"]["contratos"] = [
               c.model_dump() for c in contratos
           ]

           # Guardar archivo
           filename = f"datadis_export_{cups}_{fecha_inicio.replace('/', '-')}_to_{fecha_fin.replace('/', '-')}.json"
           with open(filename, 'w', encoding='utf-8') as f:
               json.dump(datos_completos, f, indent=2, ensure_ascii=False)

           print(f"✅ Datos exportados a: {filename}")
           return filename

Monitoreo de Múltiples Suministros
-----------------------------------

.. code-block:: python

   def monitorear_todos_los_suministros(username, password):
       """Obtiene datos de todos los puntos de suministro disponibles"""

       with SimpleDatadisClientV1(username, password) as client:
           # Obtener suministros y distribuidores
           suministros = client.get_supplies()
           distribuidores = client.get_distributors()

           if not suministros:
               print("❌ No se encontraron puntos de suministro")
               return

           print(f"🏠 Procesando {len(suministros)} puntos de suministro...")

           # Fecha para consulta (último mes)
           fin = datetime.now()
           inicio = fin - timedelta(days=30)
           fecha_inicio = inicio.strftime("%Y/%m/%d")
           fecha_fin = fin.strftime("%Y/%m/%d")

           resultados = []

           for i, suministro in enumerate(suministros, 1):
               print(f"\n📊 Procesando suministro {i}/{len(suministros)}: {suministro.cups}")

               # Encontrar distribuidor
               codigo_distribuidor = "2"  # Por defecto
               for dist in distribuidores:
                   if hasattr(dist, 'code'):
                       codigo_distribuidor = dist.code
                       break

               try:
                   # Obtener consumo
                   consumo = client.get_consumption(
                       cups=suministro.cups,
                       distributor_code=codigo_distribuidor,
                       date_from=fecha_inicio,
                       date_to=fecha_fin
                   )

                   total_kwh = sum(c.consumption_kwh for c in consumo)

                   resultado = {
                       "cups": suministro.cups,
                       "direccion": getattr(suministro, 'address', 'N/A'),
                       "provincia": getattr(suministro, 'province', 'N/A'),
                       "total_kwh": total_kwh,
                       "registros": len(consumo),
                       "distribuidor": codigo_distribuidor
                   }

                   resultados.append(resultado)
                   print(f"✅ Consumo: {total_kwh:.2f} kWh ({len(consumo)} registros)")

               except Exception as e:
                   print(f"❌ Error procesando {suministro.cups}: {e}")
                   resultados.append({
                       "cups": suministro.cups,
                       "error": str(e)
                   })

           # Resumen
           print(f"\n📈 Resumen de {len(resultados)} suministros:")
           total_general = 0
           for resultado in resultados:
               if "error" not in resultado:
                   print(f"  {resultado['cups']}: {resultado['total_kwh']:.2f} kWh")
                   total_general += resultado['total_kwh']
               else:
                   print(f"  {resultado['cups']}: ERROR - {resultado['error']}")

           print(f"\n💡 Consumo total de todos los suministros: {total_general:.2f} kWh")
           return resultados

Validación y Limpieza de Datos
-------------------------------

.. code-block:: python

   def validar_y_limpiar_datos(username, password, cups, distributor_code, fecha_inicio, fecha_fin):
       """Valida y limpia los datos obtenidos de la API"""

       with SimpleDatadisClientV1(username, password) as client:
           print("🔍 Obteniendo y validando datos...")

           consumo = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=fecha_inicio,
               date_to=fecha_fin
           )

           print(f"📊 Datos originales: {len(consumo)} registros")

           # Validaciones
           datos_validos = []
           errores = {
               "consumo_negativo": 0,
               "fecha_invalida": 0,
               "valores_extremos": 0
           }

           for registro in consumo:
               # Validar consumo no negativo
               if registro.consumption_kwh < 0:
                   errores["consumo_negativo"] += 1
                   continue

               # Validar valores extremos (>100 kWh por hora es sospechoso)
               if registro.consumption_kwh > 100:
                   errores["valores_extremos"] += 1
                   continue

               # Validar formato de fecha
               try:
                   datetime.strptime(registro.date, "%Y/%m/%d")
               except ValueError:
                   errores["fecha_invalida"] += 1
                   continue

               datos_validos.append(registro)

           # Resultados de validación
           print(f"✅ Datos válidos: {len(datos_validos)}")
           print(f"❌ Errores encontrados:")
           for tipo_error, cantidad in errores.items():
               if cantidad > 0:
                   print(f"  - {tipo_error}: {cantidad}")

           # Estadísticas de datos limpios
           if datos_validos:
               consumos = [d.consumption_kwh for d in datos_validos]
               print(f"\n📈 Estadísticas de datos limpios:")
               print(f"  - Total: {sum(consumos):.2f} kWh")
               print(f"  - Promedio: {sum(consumos)/len(consumos):.2f} kWh")
               print(f"  - Máximo: {max(consumos):.2f} kWh")
               print(f"  - Mínimo: {min(consumos):.2f} kWh")

           return datos_validos, errores

Uso con Configuración Personalizada
------------------------------------

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datadis_python.exceptions import DatadisError

   class DatadisManager:
       """Clase wrapper para gestionar múltiples operaciones con Datadis"""

       def __init__(self, username, password, timeout=180, retries=5):
           self.username = username
           self.password = password
           self.timeout = timeout
           self.retries = retries
           self._client = None

       def __enter__(self):
           self._client = SimpleDatadisClientV1(
               username=self.username,
               password=self.password,
               timeout=self.timeout,
               retries=self.retries
           )
           return self

       def __exit__(self, exc_type, exc_val, exc_tb):
           if self._client:
               self._client.close()

       def obtener_resumen_completo(self):
           """Obtiene un resumen completo de la cuenta"""
           if not self._client:
               raise DatadisError("Cliente no inicializado")

           resumen = {
               "distribuidores": [],
               "suministros": [],
               "contratos": [],
               "estado": "ok"
           }

           try:
               # Distribuidores
               resumen["distribuidores"] = self._client.get_distributors()

               # Suministros
               resumen["suministros"] = self._client.get_supplies()

               # Contratos para cada suministro
               for suministro in resumen["suministros"]:
                   if resumen["distribuidores"]:
                       codigo_dist = resumen["distribuidores"][0].code
                       contratos = self._client.get_contract_detail(
                           cups=suministro.cups,
                           distributor_code=codigo_dist
                       )
                       resumen["contratos"].extend(contratos)

           except Exception as e:
               resumen["estado"] = f"error: {e}"

           return resumen

   # Uso
   with DatadisManager("tu_nif", "tu_contraseña", timeout=240, retries=3) as manager:
       resumen = manager.obtener_resumen_completo()
       print(f"Estado: {resumen['estado']}")
       print(f"Distribuidores: {len(resumen['distribuidores'])}")
       print(f"Suministros: {len(resumen['suministros'])}")
       print(f"Contratos: {len(resumen['contratos'])}")