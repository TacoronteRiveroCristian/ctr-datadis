ctr-datadis Documentation
=========================

A comprehensive Python SDK for interacting with the official Datadis API (Spanish electricity supply data platform).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Installation
------------

.. code-block:: bash

   pip install ctr-datadis

Quick Start
-----------

.. code-block:: python

   from datadis_python.client.v1.simple_client import DatadisClient

   # Initialize client
   client = DatadisClient(username="your_nif", password="your_password")

   # Get supply points
   supplies = client.get_supplies()

   # Get consumption data
   consumption = client.get_consumption(
       cups="ES1234000000000001JN0F",
       distributor_code="2", 
       start_date="2024/01",
       end_date="2024/02"
   )

API Reference
=============

.. toctree::
   :maxdepth: 4

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`