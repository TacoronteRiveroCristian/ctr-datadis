Ejemplos de Uso
===============

Esta sección muestra ejemplos prácticos para casos de uso comunes con ambas versiones del cliente.

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
           print(f"Consumo total anual: {total_anual:.2f} kWh")
           print(f"Promedio mensual: {promedio_mensual:.2f} kWh")
           print(f"Mes de mayor consumo: {mes_mayor_consumo} ({consumo_mensual.get(mes_mayor_consumo, 0):.2f} kWh)")
           print(f"Mes de menor consumo: {mes_menor_consumo} ({consumo_mensual.get(mes_menor_consumo, 0):.2f} kWh)")
           print(f"Registros procesados: {len(consumption)}")

           return {
               "total_anual": total_anual,
               "promedio_mensual": promedio_mensual,
               "consumo_mensual": consumo_mensual,
               "mes_mayor_consumo": mes_mayor_consumo,
               "mes_menor_consumo": mes_menor_consumo,
               "registros_totales": len(consumption)
           }

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

           # Verificar errores por distribuidor
           if consumption_response.distributor_error:
               print("Errores encontrados:")
               for error in consumption_response.distributor_error:
                   print(f"- {error.distributorName}: {error.errorDescription}")

           consumption = consumption_response.time_curve
           if not consumption:
               print("No se encontraron datos de consumo")
               return None

           # Análisis detallado
           consumo_mensual = {}
           datos_por_metodo = {"Real": 0, "Estimada": 0}

           for registro in consumption:
               mes = registro.date[:7]
               if mes not in consumo_mensual:
                   consumo_mensual[mes] = {
                       "consumo": 0,
                       "excedentes": 0,
                       "autoconsumo": 0,
                       "registros": 0
                   }

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

Iteración de Todas las CUPS
----------------------------

Script Completo para Procesar Múltiples Suministros
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2
   from datetime import datetime
   import csv
   import json

   def procesar_todas_las_cups(username, password, year="2024", export_format="json"):
       """
       Procesa todas las CUPS disponibles y genera un informe completo

       Args:
           username: NIF del usuario
           password: Contraseña
           year: Año a analizar (formato "YYYY")
           export_format: "json" o "csv" para el formato de exportación
       """

       resultados = []
       errores_globales = []

       with SimpleDatadisClientV2(username, password) as client:
           try:
               # 1. Obtener todos los suministros
               print("Obteniendo lista de suministros...")
               supplies_response = client.get_supplies()

               if supplies_response.distributor_error:
                   print("Errores al obtener suministros:")
                   for error in supplies_response.distributor_error:
                       print(f"- {error.distributorName}: {error.errorDescription}")
                       errores_globales.append({
                           "tipo": "supplies",
                           "distribuidor": error.distributorName,
                           "error": error.errorDescription
                       })

               supplies = supplies_response.supplies
               if not supplies:
                   print("No se encontraron suministros")
                   return None

               print(f"Procesando {len(supplies)} puntos de suministro...")

               # 2. Procesar cada CUPS
               for i, supply in enumerate(supplies, 1):
                   print(f"\nProcesando {i}/{len(supplies)}: {supply.cups}")

                   resultado_cups = {
                       "cups": supply.cups,
                       "direccion": supply.address,
                       "provincia": supply.province,
                       "codigo_postal": supply.postalCode,
                       "distribuidor": supply.distributor,
                       "codigo_distribuidor": supply.distributorCode,
                       "tipo_punto": supply.pointType,
                       "fecha_procesamiento": datetime.now().isoformat()
                   }

                   try:
                       # Obtener datos de consumo
                       print(f"  Obteniendo consumo {year}...")
                       consumption_response = client.get_consumption(
                           cups=supply.cups,
                           distributor_code=supply.distributorCode,
                           date_from=f"{year}/01",
                           date_to=f"{year}/12"
                       )

                       if consumption_response.distributor_error:
                           for error in consumption_response.distributor_error:
                               errores_globales.append({
                                   "tipo": "consumption",
                                   "cups": supply.cups,
                                   "distribuidor": error.distributorName,
                                   "error": error.errorDescription
                               })

                       # Analizar consumo
                       consumption = consumption_response.time_curve
                       if consumption:
                           total_consumo = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
                           total_excedentes = sum(c.surplusEnergyKWh for c in consumption if c.surplusEnergyKWh)
                           registros_reales = len([c for c in consumption if c.obtainMethod == "Real"])

                           resultado_cups.update({
                               "consumo_total_kwh": round(total_consumo, 2),
                               "excedentes_total_kwh": round(total_excedentes, 2),
                               "registros_totales": len(consumption),
                               "registros_reales": registros_reales,
                               "tiene_autoconsumo": any(c.selfConsumptionKWh for c in consumption)
                           })
                       else:
                           resultado_cups.update({
                               "consumo_total_kwh": 0,
                               "excedentes_total_kwh": 0,
                               "registros_totales": 0,
                               "registros_reales": 0,
                               "tiene_autoconsumo": False,
                               "nota": "Sin datos de consumo"
                           })

                       # Obtener potencia máxima
                       print(f"  Obteniendo potencia máxima...")
                       max_power_response = client.get_max_power(
                           cups=supply.cups,
                           distributor_code=supply.distributorCode,
                           date_from=f"{year}/01",
                           date_to=f"{year}/12"
                       )

                       if max_power_response.max_power:
                           potencias = [p.maxPower for p in max_power_response.max_power]
                           resultado_cups["potencia_maxima_w"] = max(potencias)
                           resultado_cups["potencia_maxima_kw"] = round(max(potencias) / 1000, 2)
                       else:
                           resultado_cups["potencia_maxima_w"] = 0
                           resultado_cups["potencia_maxima_kw"] = 0

                       # Intentar obtener energía reactiva (solo V2)
                       try:
                           print(f"  Obteniendo energía reactiva...")
                           reactive_data = client.get_reactive_data(
                               cups=supply.cups,
                               distributor_code=supply.distributorCode,
                               date_from=f"{year}/01",
                               date_to=f"{year}/12"
                           )
                           resultado_cups["tiene_energia_reactiva"] = len(reactive_data) > 0
                           resultado_cups["registros_reactiva"] = len(reactive_data)
                       except Exception as e:
                           resultado_cups["tiene_energia_reactiva"] = False
                           resultado_cups["registros_reactiva"] = 0
                           resultado_cups["error_reactiva"] = str(e)

                       resultado_cups["estado"] = "procesado_exitosamente"
                       print(f"  Completado: {resultado_cups['consumo_total_kwh']} kWh")

                   except Exception as e:
                       print(f"  Error procesando {supply.cups}: {e}")
                       resultado_cups.update({
                           "estado": "error",
                           "error": str(e),
                           "consumo_total_kwh": 0,
                           "registros_totales": 0
                       })

                   resultados.append(resultado_cups)

               # 3. Generar resumen
               cups_exitosas = [r for r in resultados if r["estado"] == "procesado_exitosamente"]
               consumo_total_usuario = sum(r["consumo_total_kwh"] for r in cups_exitosas)

               resumen = {
                   "fecha_procesamiento": datetime.now().isoformat(),
                   "usuario": username,
                   "year_analizado": year,
                   "total_cups_procesadas": len(resultados),
                   "cups_exitosas": len(cups_exitosas),
                   "cups_con_errores": len(resultados) - len(cups_exitosas),
                   "consumo_total_usuario_kwh": round(consumo_total_usuario, 2),
                   "errores_globales": len(errores_globales)
               }

               print(f"\nResumen del procesamiento:")
               print(f"CUPS procesadas: {resumen['total_cups_procesadas']}")
               print(f"CUPS exitosas: {resumen['cups_exitosas']}")
               print(f"CUPS con errores: {resumen['cups_con_errores']}")
               print(f"Consumo total del usuario: {resumen['consumo_total_usuario_kwh']} kWh")

               # 4. Exportar resultados
               datos_export = {
                   "resumen": resumen,
                   "cups_detalle": resultados,
                   "errores_detalle": errores_globales
               }

               if export_format == "json":
                   filename = f"datadis_reporte_completo_{username}_{year}.json"
                   with open(filename, 'w', encoding='utf-8') as f:
                       json.dump(datos_export, f, indent=2, ensure_ascii=False)
                   print(f"Reporte exportado a: {filename}")

               elif export_format == "csv":
                   filename = f"datadis_cups_{username}_{year}.csv"
                   with open(filename, 'w', newline='', encoding='utf-8') as f:
                       if resultados:
                           writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
                           writer.writeheader()
                           writer.writerows(resultados)
                   print(f"Datos de CUPS exportados a: {filename}")

               return datos_export

           except Exception as e:
               print(f"Error crítico en el procesamiento: {e}")
               return None

   # Ejemplo de uso
   if __name__ == "__main__":
       # Procesar todas las CUPS del usuario para 2024
       reporte = procesar_todas_las_cups(
           username="tu_nif",
           password="tu_contraseña",
           year="2024",
           export_format="json"
       )

Análisis Comparativo Entre Años
--------------------------------

.. code-block:: python

   def comparar_consumo_entre_years(username, password, cups, distributor_code, years=["2023", "2024"]):
       """Compara el consumo entre diferentes años"""

       with SimpleDatadisClientV2(username, password) as client:
           resultados_comparacion = {}

           for year in years:
               print(f"Analizando año {year}...")

               consumption_response = client.get_consumption(
                   cups=cups,
                   distributor_code=distributor_code,
                   date_from=f"{year}/01",
                   date_to=f"{year}/12"
               )

               if consumption_response.time_curve:
                   consumption = consumption_response.time_curve

                   # Análisis por trimestres
                   trimestres = {
                       "Q1": {"meses": ["01", "02", "03"], "consumo": 0},
                       "Q2": {"meses": ["04", "05", "06"], "consumo": 0},
                       "Q3": {"meses": ["07", "08", "09"], "consumo": 0},
                       "Q4": {"meses": ["10", "11", "12"], "consumo": 0}
                   }

                   total_year = 0
                   for registro in consumption:
                       if registro.consumptionKWh:
                           mes = registro.date[5:7]  # MM
                           total_year += registro.consumptionKWh

                           for trimestre, data in trimestres.items():
                               if mes in data["meses"]:
                                   data["consumo"] += registro.consumptionKWh

                   resultados_comparacion[year] = {
                       "total_anual": round(total_year, 2),
                       "trimestres": {k: round(v["consumo"], 2) for k, v in trimestres.items()},
                       "promedio_mensual": round(total_year / 12, 2),
                       "registros": len(consumption)
                   }
               else:
                   resultados_comparacion[year] = {
                       "total_anual": 0,
                       "error": "Sin datos disponibles"
                   }

           # Calcular diferencias
           if len(years) == 2 and all(year in resultados_comparacion for year in years):
               year1, year2 = years[0], years[1]
               total1 = resultados_comparacion[year1].get("total_anual", 0)
               total2 = resultados_comparacion[year2].get("total_anual", 0)

               if total1 > 0:
                   diferencia_absoluta = total2 - total1
                   diferencia_porcentual = (diferencia_absoluta / total1) * 100

                   print(f"Comparación {year1} vs {year2}:")
                   print(f"Consumo {year1}: {total1} kWh")
                   print(f"Consumo {year2}: {total2} kWh")
                   print(f"Diferencia: {diferencia_absoluta:+.2f} kWh ({diferencia_porcentual:+.1f}%)")

                   resultados_comparacion["comparacion"] = {
                       "diferencia_absoluta": round(diferencia_absoluta, 2),
                       "diferencia_porcentual": round(diferencia_porcentual, 1),
                       "tendencia": "incremento" if diferencia_absoluta > 0 else "reducción"
                   }

           return resultados_comparacion

Generación de Informes Detallados
----------------------------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import pandas as pd

   def generar_informe_detallado(username, password, cups, distributor_code, year="2024"):
       """Genera un informe detallado con gráficos y estadísticas"""

       with SimpleDatadisClientV2(username, password) as client:
           # Obtener todos los datos
           print("Recopilando datos...")

           consumption_response = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",
               date_to=f"{year}/12"
           )

           max_power_response = client.get_max_power(
               cups=cups,
               distributor_code=distributor_code,
               date_from=f"{year}/01",
               date_to=f"{year}/12"
           )

           contract_response = client.get_contract_detail(
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

           # Crear DataFrame para análisis
           df = pd.DataFrame(datos_consumo)
           df['fecha'] = pd.to_datetime(df['fecha'])
           df['mes'] = df['fecha'].dt.to_period('M')

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

           # Gráfico 2: Comparación consumo vs excedentes
           resumen_mensual[['consumo_kwh', 'excedentes_kwh']].plot(kind='bar', ax=axes[0,1])
           axes[0,1].set_title('Consumo vs Excedentes')
           axes[0,1].set_ylabel('kWh')

           # Gráfico 3: Evolución temporal del consumo
           df.set_index('fecha')['consumo_kwh'].resample('W').sum().plot(ax=axes[1,0], color='green')
           axes[1,0].set_title('Evolución Semanal del Consumo')
           axes[1,0].set_ylabel('kWh')

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

           # Resumen estadístico
           estadisticas = {
               "periodo_analizado": f"{year}",
               "cups": cups,
               "total_registros": len(df),
               "consumo_total_kwh": round(df['consumo_kwh'].sum(), 2),
               "consumo_promedio_mensual": round(df['consumo_kwh'].sum() / 12, 2),
               "mes_mayor_consumo": str(resumen_mensual['consumo_kwh'].idxmax()),
               "mes_menor_consumo": str(resumen_mensual['consumo_kwh'].idxmin()),
               "tiene_autoconsumo": df['autoconsumo_kwh'].sum() > 0,
               "total_excedentes_kwh": round(df['excedentes_kwh'].sum(), 2),
               "contrato": contrato_info
           }

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

       # Obtener CUPS disponibles
       with SimpleDatadisClientV2(USERNAME, PASSWORD) as client:
           supplies_response = client.get_supplies()

           if supplies_response.supplies:
               primera_cups = supplies_response.supplies[0]
               print(f"Analizando CUPS: {primera_cups.cups}")

               # Generar informe detallado
               informe = generar_informe_detallado(
                   USERNAME,
                   PASSWORD,
                   primera_cups.cups,
                   primera_cups.distributorCode,
                   YEAR
               )
