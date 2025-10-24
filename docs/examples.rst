Ejemplos de Uso
===============

Esta sección muestra ejemplos prácticos para casos de uso comunes con ambas versiones del cliente.

.. note::
   **IMPORTANTE sobre formatos de fecha**: La API de Datadis requiere fechas en formato mensual (YYYY/MM) para los endpoints de consumo y potencia máxima. NO se permiten fechas con días específicos (YYYY/MM/DD).

Análisis de Consumo Anual
--------------------------

Cliente V1 - Análisis Básico
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datetime import datetime
   import json

   def analizar_consumo_anual_v1(username, password, cups, distributor_code, year="2024"):
       """Analiza el consumo energético de todo un año usando cliente V1"""

       with SimpleDatadisClientV1(username, password) as client:
           print(f"Analizando consumo anual {year} con cliente V1")

           # Obtener datos de todo el año (formato mensual requerido)
           consumption = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",  # Enero
               date_to=f"{year}/12"     # Diciembre
           )

           if not consumption:
               print("No se encontraron datos de consumo")
               return None

           # Análisis por meses
           consumo_mensual = {}
           for registro in consumption:
               # Extraer mes del timestamp (YYYY/MM/DD HH:MM:SS)
               mes = registro.date[:7]  # YYYY/MM
               if mes not in consumo_mensual:
                   consumo_mensual[mes] = 0
               if registro.consumptionKWh:
                   consumo_mensual[mes] += registro.consumptionKWh

           # Estadísticas anuales
           total_anual = sum(consumo_mensual.values())
           promedio_mensual = total_anual / 12 if consumo_mensual else 0

           mes_mayor_consumo = max(consumo_mensual, key=consumo_mensual.get) if consumo_mensual else None
           mes_menor_consumo = min(consumo_mensual, key=consumo_mensual.get) if consumo_mensual else None

           # Resultados
           print(f"Consumo total: {total_kwh:.2f} kWh")
           print(f"Consumo promedio diario: {consumo_promedio:.2f} kWh")
           print(f"Consumo máximo diario: {consumo_maximo:.2f} kWh")
           print(f"Consumo mínimo diario: {consumo_minimo:.2f} kWh")
           print(f"Días con datos: {len(consumo_diario)}")

           return {
               "total_anual": total_anual,
               "promedio_mensual": promedio_mensual,
               "consumo_mensual": consumo_mensual,
               "mes_mayor_consumo": mes_mayor_consumo,
               "mes_menor_consumo": mes_menor_consumo,
               "registros_totales": len(consumption)
           }

   # Uso del ejemplo - NOTA: usar fechas en formato mensual YYYY/MM
   resultado = analizar_consumo_anual_v1(
       username="tu_nif",
       password="tu_contraseña",
       cups="ES1234000000000001JN0F",
       distributor_code="2",
       year="2024"
   )

Cliente V2 - Análisis Robusto con Manejo de Errores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   def analizar_consumo_anual_v2(username, password, cups, distributor_code, year="2024"):
       """Analiza el consumo energético con manejo robusto de errores usando cliente V2"""

       with SimpleDatadisClientV2(username, password) as client:
           print(f"Analizando consumo anual {year} con cliente V2")

           # Obtener datos con manejo de errores mejorado
           consumption_response = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",
               date_to=f"{year}/12"
           )

               print(f"Procesando período: {periodo}")

           consumption = consumption_response.time_curve
           if not consumption:
               print("No se encontraron datos de consumo")
               return None

           # Análisis detallado
           consumo_mensual = {}
           datos_por_metodo = {"Real": 0, "Estimada": 0}

           # Mostrar comparación
           print("\nComparación de períodos:")
           for periodo, datos in resultados.items():
               print(f"{periodo}: {datos['total_kwh']:.2f} kWh ({datos['registros']} registros)")

               if registro.consumptionKWh:
                   consumo_mensual[mes]["consumo"] += registro.consumptionKWh
               if registro.surplusEnergyKWh:
                   consumo_mensual[mes]["excedentes"] += registro.surplusEnergyKWh
               if registro.selfConsumptionKWh:
                   consumo_mensual[mes]["autoconsumo"] += registro.selfConsumptionKWh

               consumo_mensual[mes]["registros"] += 1

               # Contar método de obtención
               if registro.obtainMethod:
                   datos_por_metodo[registro.obtainMethod] = datos_por_metodo.get(registro.obtainMethod, 0) + 1

           # Estadísticas anuales
           total_consumo = sum(mes_data["consumo"] for mes_data in consumo_mensual.values())
           total_excedentes = sum(mes_data["excedentes"] for mes_data in consumo_mensual.values())
           total_autoconsumo = sum(mes_data["autoconsumo"] for mes_data in consumo_mensual.values())

           print(f"Consumo total anual: {total_consumo:.2f} kWh")
           print(f"Excedentes totales: {total_excedentes:.2f} kWh")
           print(f"Autoconsumo total: {total_autoconsumo:.2f} kWh")
           print(f"Datos reales: {datos_por_metodo.get('Real', 0)} registros")
           print(f"Datos estimados: {datos_por_metodo.get('Estimada', 0)} registros")

           return {
               "total_consumo": total_consumo,
               "total_excedentes": total_excedentes,
               "total_autoconsumo": total_autoconsumo,
               "consumo_mensual": consumo_mensual,
               "datos_por_metodo": datos_por_metodo,
               "errores_distribuidor": len(consumption_response.distributor_error)
           }

           print("Exportando datos completos...")

           # 1. Consumo
           print("Obteniendo consumo...")
           consumo = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",
               date_to=f"{year}/12"
           )

           # 2. Potencia máxima
           print("Obteniendo potencia máxima...")
           potencia = client.get_max_power(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",
               date_to=f"{year}/12"
           )

           # 3. Contratos
           print("Obteniendo contratos...")
           contratos = client.get_contract_detail(
               cups=cups,
               distributor_code=distributor_code
           )

           # Preparar datos para análisis
           datos_consumo = []
           for registro in consumption_response.time_curve:
               datos_consumo.append({
                   "fecha": registro.date,
                   "consumo_kwh": registro.consumptionKWh or 0,
                   "excedentes_kwh": registro.surplusEnergyKWh or 0,
                   "autoconsumo_kwh": registro.selfConsumptionKWh or 0,
                   "metodo": registro.obtainMethod
               })

           print(f"Datos exportados a: {filename}")
           return filename

           # Análisis mensual
           resumen_mensual = df.groupby('mes').agg({
               'consumo_kwh': 'sum',
               'excedentes_kwh': 'sum',
               'autoconsumo_kwh': 'sum'
           }).round(2)

           # Información del contrato
           contrato_info = {}
           if contract_response.contract:
               contrato = contract_response.contract[0]
               contrato_info = {
                   "potencia_contratada_kw": contrato.contractedPowerkW,
                   "tarifa": contrato.accessFare,
                   "tipo_punto": contrato.pointType,
                   "tension": contrato.voltage,
                   "comercializadora": contrato.marketer
               }

           # Generar gráficos
           fig, axes = plt.subplots(2, 2, figsize=(15, 12))

           # Gráfico 1: Consumo mensual
           resumen_mensual['consumo_kwh'].plot(kind='bar', ax=axes[0,0], color='steelblue')
           axes[0,0].set_title('Consumo Mensual (kWh)')
           axes[0,0].set_ylabel('kWh')

           if not suministros:
               print("No se encontraron puntos de suministro")
               return

           print(f"Procesando {len(suministros)} puntos de suministro...")

           # Gráfico 4: Distribución horaria (si hay datos horarios)
           if len(df) > 100:  # Solo si hay suficientes datos
               df['hora'] = df['fecha'].dt.hour
               consumo_por_hora = df.groupby('hora')['consumo_kwh'].mean()
               consumo_por_hora.plot(kind='bar', ax=axes[1,1], color='orange')
               axes[1,1].set_title('Patrón de Consumo por Hora')
               axes[1,1].set_ylabel('kWh promedio')

           plt.tight_layout()
           plt.savefig(f'informe_consumo_{cups}_{year}.png', dpi=300, bbox_inches='tight')
           print(f"Gráficos guardados en: informe_consumo_{cups}_{year}.png")

           for i, suministro in enumerate(suministros, 1):
               print(f"\nProcesando suministro {i}/{len(suministros)}: {suministro.cups}")

           # Guardar informe completo
           with open(f'informe_detallado_{cups}_{year}.json', 'w', encoding='utf-8') as f:
               json.dump(estadisticas, f, indent=2, ensure_ascii=False, default=str)

           print("Informe detallado generado:")
           print(f"- Consumo total: {estadisticas['consumo_total_kwh']} kWh")
           print(f"- Promedio mensual: {estadisticas['consumo_promedio_mensual']} kWh")
           print(f"- Mayor consumo: {estadisticas['mes_mayor_consumo']}")
           print(f"- Tiene autoconsumo: {estadisticas['tiene_autoconsumo']}")

           return estadisticas

   # Ejemplo de uso completo
   if __name__ == "__main__":
       # Configuración
       USERNAME = "tu_nif"
       PASSWORD = "tu_contraseña"
       YEAR = "2024"

                   resultados.append(resultado)
                   print(f"Consumo: {total_kwh:.2f} kWh ({len(consumo)} registros)")

               except Exception as e:
                   print(f"Error procesando {suministro.cups}: {e}")
                   resultados.append({
                       "cups": suministro.cups,
                       "error": str(e)
                   })

           # Resumen
           print(f"\nResumen de {len(resultados)} suministros:")
           total_general = 0
           for resultado in resultados:
               if "error" not in resultado:
                   print(f"  {resultado['cups']}: {resultado['total_kwh']:.2f} kWh")
                   total_general += resultado['total_kwh']
               else:
                   print(f"  {resultado['cups']}: ERROR - {resultado['error']}")

           print(f"\nConsumo total de todos los suministros: {total_general:.2f} kWh")
           return resultados

Validación y Limpieza de Datos
-------------------------------

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1
   from datetime import datetime

   def validar_y_limpiar_datos(username, password, cups, distributor_code, fecha_inicio, fecha_fin):
       """Valida y limpia los datos obtenidos de la API"""

       with SimpleDatadisClientV1(username, password) as client:
           print("Obteniendo y validando datos...")

           consumo = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=fecha_inicio,
               date_to=fecha_fin
           )

           print(f"Datos originales: {len(consumo)} registros")

           # Validaciones
           datos_validos = []
           errores = {
               "consumo_negativo": 0,
               "fecha_invalida": 0,
               "valores_extremos": 0
           }

           for registro in consumo:
               try:
                   # Validar consumo no negativo
                   if registro.consumptionKWh and registro.consumptionKWh < 0:
                       errores["consumo_negativo"] += 1
                       continue

                   # Validar fecha válida
                   datetime.strptime(registro.date, "%Y/%m/%d %H:%M:%S")

                   # Validar valores no extremos (más de 100 kWh por hora es sospechoso)
                   if registro.consumptionKWh and registro.consumptionKWh > 100:
                       errores["valores_extremos"] += 1
                       continue

                   datos_validos.append(registro)

               except ValueError:
                   errores["fecha_invalida"] += 1
               except Exception:
                   continue

           # Resultados de validación
           print(f"Datos válidos: {len(datos_validos)}")
           print(f"Errores encontrados:")
           for tipo_error, cantidad in errores.items():
               if cantidad > 0:
                   print(f"  - {tipo_error}: {cantidad}")

           # Estadísticas de datos limpios
           if datos_validos:
               consumos = [d.consumption_kwh for d in datos_validos]
               print(f"\nEstadísticas de datos limpios:")
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
                   if resumen["distribuidores"] and resumen["distribuidores"][0].distributor_codes:
                       codigo_dist = resumen["distribuidores"][0].distributor_codes[0]
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
