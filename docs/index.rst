ctr-datadis Documentation
=========================

**ctr-datadis** es un SDK completo de Python para interactuar con la API oficial de Datadis, la plataforma española de datos de suministro eléctrico. Proporciona acceso type-safe a datos de consumo eléctrico, información de suministro y utilidades relacionadas para consumidores de energía españoles.

Características principales:

* **Dos versiones de API**: Soporte completo para V1 y V2 de la API de Datadis
* **Type-safe**: Modelos Pydantic para validación automática de datos
* **Manejo robusto de errores**: V2 incluye manejo específico de errores por distribuidor
* **Fácil de usar**: API simple y pythónica con context managers
* **Reintentos automáticos**: Backoff exponencial para timeouts y errores de red
* **Completo**: Acceso a todos los endpoints incluyendo energía reactiva (V2)
* **Bien documentado**: Documentación completa con ejemplos didácticos

Inicio Rápido
--------------

.. code-block:: bash

   pip install ctr-datadis

Cliente V1 (Básico)
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   # Inicializar cliente V1
   with SimpleDatadisClientV1("tu_nif", "tu_contraseña") as client:
       # Obtener puntos de suministro
       supplies = client.get_supplies()

       if supplies:
           # Obtener datos de consumo (formato mensual requerido)
           consumption = client.get_consumption(
               cups=supplies[0].cups,
               distributor_code=supplies[0].distributorCode,
               date_from="2024/01",  # Solo formato mensual YYYY/MM
               date_to="2024/12"
           )

           total_kwh = sum(c.consumptionKWh for c in consumption if c.consumptionKWh)
           print(f"Consumo total 2024: {total_kwh:.2f} kWh")

Cliente V2 (Recomendado - con manejo de errores mejorado)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datadis_python.client.v2.simple_client import SimpleDatadisClientV2

   # Inicializar cliente V2
   with SimpleDatadisClientV2("tu_nif", "tu_contraseña") as client:
       # Obtener puntos de suministro con manejo de errores
       supplies_response = client.get_supplies()

       print(f"Suministros obtenidos: {len(supplies_response.supplies)}")

       # Verificar errores por distribuidor
       if supplies_response.distributor_error:
           for error in supplies_response.distributor_error:
               print(f"Error en {error.distributorName}: {error.errorDescription}")

       if supplies_response.supplies:
           supply = supplies_response.supplies[0]

           # Obtener consumo con manejo robusto de errores
           consumption_response = client.get_consumption(
               cups=supply.cups,
               distributor_code=supply.distributorCode,
               date_from="2024/01",
               date_to="2024/12"
           )

           if consumption_response.time_curve:
               total_kwh = sum(c.consumptionKWh for c in consumption_response.time_curve
                             if c.consumptionKWh)
               print(f"Consumo total 2024: {total_kwh:.2f} kWh")

           # Funcionalidad exclusiva V2: Energía reactiva
           reactive_data = client.get_reactive_data(
               cups=supply.cups,
               distributor_code=supply.distributorCode,
               date_from="2024/01",
               date_to="2024/12"
           )
           print(f"Datos de energía reactiva: {len(reactive_data)} registros")

Documentación
=============

.. toctree::
   :maxdepth: 2
   :caption: Guía del Usuario

   installation
   quickstart
   examples
   models
   exceptions
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Referencia de la API

   api
   modules

* :ref:`search`

Licencia
========

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

Contribuir
==========

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

Soporte
=======

- **Documentación**: https://ctr-datadis.readthedocs.io
- **Issues**: https://github.com/TacoronteRiveroCristian/datadis/issues
- **PyPI**: https://pypi.org/project/ctr-datadis
