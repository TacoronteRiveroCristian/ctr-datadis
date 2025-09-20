Referencia de la API
====================

Esta sección documenta todas las clases y métodos disponibles en el SDK de Datadis.

Cliente Principal
-----------------

Cliente V1 (Recomendado)
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.client.v1.simple_client.SimpleDatadisClientV1
   :members:
   :undoc-members:
   :show-inheritance:

Cliente V2 (Experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.client.v2.simple_client.SimpleDatadisClientV2
   :members:
   :undoc-members:
   :show-inheritance:

Modelos de Datos
-----------------

Datos de Consumo
~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.consumption.ConsumptionData
   :members:
   :undoc-members:
   :show-inheritance:

Datos de Suministro
~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.supply.SupplyData
   :members:
   :undoc-members:
   :show-inheritance:

Datos de Contrato
~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.contract.ContractData
   :members:
   :undoc-members:
   :show-inheritance:

Datos de Distribuidor
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.distributor.DistributorData
   :members:
   :undoc-members:
   :show-inheritance:

Datos de Potencia Máxima
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.max_power.MaxPowerData
   :members:
   :undoc-members:
   :show-inheritance:

Datos de Energía Reactiva
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.reactive.ReactiveData
   :members:
   :undoc-members:
   :show-inheritance:

Respuestas de la API
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: datadis_python.models.responses.DatadisResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: datadis_python.models.responses.ErrorResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: datadis_python.models.responses.PaginatedResponse
   :members:
   :undoc-members:
   :show-inheritance:

Excepciones
-----------

.. automodule:: datadis_python.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Utilidades
----------

Validadores
~~~~~~~~~~~

.. automodule:: datadis_python.utils.validators
   :members:
   :undoc-members:
   :show-inheritance:

Utilidades HTTP
~~~~~~~~~~~~~~~

.. automodule:: datadis_python.utils.http
   :members:
   :undoc-members:
   :show-inheritance:

Utilidades de Texto
~~~~~~~~~~~~~~~~~~~

.. automodule:: datadis_python.utils.text_utils
   :members:
   :undoc-members:
   :show-inheritance:

Constantes
~~~~~~~~~~

.. automodule:: datadis_python.utils.constants
   :members:
   :undoc-members:
   :show-inheritance:

Cliente Base (Avanzado)
-----------------------

.. autoclass:: datadis_python.client.base.BaseDatadisClient
   :members:
   :undoc-members:
   :show-inheritance:

Cliente Unificado (Futuro)
---------------------------

.. autoclass:: datadis_python.client.unified.UnifiedDatadisClient
   :members:
   :undoc-members:
   :show-inheritance: