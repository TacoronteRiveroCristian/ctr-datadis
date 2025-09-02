Datadis Python SDK Documentation
=================================

A comprehensive Python SDK for interacting with the official Datadis API (Distribuidora de Información de Suministros de España).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   changelog

Overview
--------

Datadis is the official Spanish platform that provides electricity supply data access. This SDK provides a simple and robust interface to interact with the Datadis API v2, allowing developers to retrieve consumption data, contract information, supply points, and more.

Features
--------

* **Automatic Authentication**: Token-based authentication with automatic renewal
* **Complete API Coverage**: Access to all Datadis API v2 endpoints
* **Type Safety**: Full type hints and Pydantic models for data validation
* **Error Handling**: Comprehensive error handling with custom exceptions
* **Rate Limiting**: Built-in retry logic and rate limit handling
* **Python 3.8+**: Compatible with modern Python versions

Quick Example
-------------

.. code-block:: python

   from datadis_python import DatadisClient

   # Initialize client
   client = DatadisClient(
       username="12345678A",  # Your NIF
       password="your_password"
   )

   # Get supply points
   supplies = client.get_supplies()
   
   # Get consumption data
   consumptions = client.get_consumption(
       cups="ES001234567890123456AB",
       distributor_code="2",
       date_from="2024/01",
       date_to="2024/02"
   )

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`