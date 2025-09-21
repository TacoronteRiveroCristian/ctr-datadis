Instalación
===========

Requisitos
-----------

- Python 3.8 o superior
- pip (incluido con Python)
- Acceso a internet para instalar dependencias

Instalación desde PyPI
-----------------------

La forma más sencilla de instalar ``ctr-datadis`` es usando pip:

.. code-block:: bash

   pip install ctr-datadis

Instalación desde código fuente
--------------------------------

Si deseas instalar la versión más reciente desde el repositorio:

.. code-block:: bash

   git clone https://github.com/TacoronteRiveroCristian/datadis.git
   cd datadis
   pip install .

Instalación para desarrollo
----------------------------

Si planeas contribuir al proyecto:

.. code-block:: bash

   git clone https://github.com/TacoronteRiveroCristian/datadis.git
   cd datadis
   poetry install --with dev

Esto instalará todas las dependencias de desarrollo incluyendo herramientas de testing y linting.

Verificación de la instalación
-------------------------------

Para verificar que la instalación fue exitosa:

.. code-block:: python

   import datadis_python
   print(datadis_python.__version__)

Dependencias
------------

Las principales dependencias del proyecto son:

- **requests**: Para realizar peticiones HTTP a la API de Datadis
- **pydantic**: Para validación y serialización de datos
- **typing-extensions**: Para soporte de tipos en Python 3.8+

Todas las dependencias se instalan automáticamente con el paquete.
