ctr-datadis Documentation
=========================

**ctr-datadis** es un SDK completo de Python para interactuar con la API oficial de Datadis, la plataforma española de datos de suministro eléctrico. Proporciona acceso type-safe a datos de consumo eléctrico, información de suministro y utilidades relacionadas para consumidores de energía españoles.

Características principales:

* **Type-safe**: Modelos Pydantic para validación automática de datos
* **Fácil de usar**: API simple y pythónica
* **Robusto**: Manejo automático de errores y reintentos
* **Completo**: Acceso a todos los endpoints de Datadis
* **Bien documentado**: Documentación completa con ejemplos

Inicio Rápido
--------------

.. code-block:: bash

   pip install ctr-datadis

.. code-block:: python

   from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

   # Inicializar cliente
   with SimpleDatadisClientV1("tu_nif", "tu_contraseña") as client:
       # Obtener puntos de suministro
       supplies = client.get_supplies()

       # Obtener datos de consumo
       consumption = client.get_consumption(
           cups="ES1234000000000001JN0F",
           distributor_code="2",
           date_from="2024/01/01",
           date_to="2024/01/31"
       )

       print(f"Consumo total: {sum(c.consumption_kwh for c in consumption)} kWh")

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
