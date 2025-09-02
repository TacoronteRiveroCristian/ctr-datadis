Quick Start Guide
=================

This guide will help you get started with the Datadis Python SDK quickly.

Prerequisites
-------------

Before using the SDK, you need:

1. A Datadis account (register at `datadis.es <https://datadis.es>`_)
2. Your NIF (National Identity Document) registered in Datadis
3. Your Datadis password

Basic Usage
-----------

Initialize the Client
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient

   client = DatadisClient(
       username="12345678A",  # Your NIF
       password="your_password"
   )

Get Available Distributors
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, check which distributors are available for your account:

.. code-block:: python

   distributors = client.get_distributors()
   print(f"Available distributors: {distributors}")
   # Output: ['2', '8']

Get Supply Points
^^^^^^^^^^^^^^^^^

Retrieve your supply points (CUPS):

.. code-block:: python

   supplies = client.get_supplies()
   
   for supply in supplies:
       print(f"CUPS: {supply.cups}")
       print(f"Address: {supply.address}")
       print(f"Distributor: {supply.distributor}")
       print(f"Distributor Code: {supply.distributor_code}")
       print("---")

Get Contract Information
^^^^^^^^^^^^^^^^^^^^^^^^

Get detailed contract information for a specific CUPS:

.. code-block:: python

   # Use the first supply point from previous step
   supply = supplies[0]
   
   contract = client.get_contract_detail(
       cups=supply.cups,
       distributor_code=supply.distributor_code
   )
   
   if contract:
       print(f"Marketer: {contract.marketer}")
       print(f"Contracted Power: {contract.contracted_power_kw} kW")
       print(f"Tariff: {contract.access_fare}")

Get Consumption Data
^^^^^^^^^^^^^^^^^^^^

Retrieve consumption data for a specific period:

.. code-block:: python

   consumptions = client.get_consumption(
       cups=supply.cups,
       distributor_code=supply.distributor_code,
       date_from="2024/01",  # YYYY/MM format
       date_to="2024/02",
       measurement_type=0,    # 0 for hourly, 1 for quarter-hourly
       point_type=supply.point_type
   )
   
   print(f"Found {len(consumptions)} consumption records")
   
   # Show first few records
   for consumption in consumptions[:5]:
       print(f"{consumption.date} {consumption.time}: "
             f"{consumption.consumption_kwh} kWh "
             f"({consumption.obtain_method})")

Get Maximum Power Data
^^^^^^^^^^^^^^^^^^^^^^

Retrieve maximum power demand data:

.. code-block:: python

   max_powers = client.get_max_power(
       cups=supply.cups,
       distributor_code=supply.distributor_code,
       date_from="2024/01",
       date_to="2024/02"
   )
   
   for power in max_powers:
       print(f"{power.date} {power.time}: "
             f"{power.max_power} W ({power.period})")

Error Handling
--------------

Always handle potential errors:

.. code-block:: python

   from datadis_python.exceptions import DatadisError, AuthenticationError, APIError

   try:
       supplies = client.get_supplies()
   except AuthenticationError:
       print("Authentication failed - check your credentials")
   except APIError as e:
       print(f"API error: {e.message} (status: {e.status_code})")
   except DatadisError as e:
       print(f"General error: {e}")

Complete Example
----------------

Here's a complete example that demonstrates the typical workflow:

.. code-block:: python

   from datadis_python import DatadisClient
   from datadis_python.exceptions import DatadisError, AuthenticationError

   def main():
       # Initialize client
       client = DatadisClient(
           username="12345678A",  # Replace with your NIF
           password="your_password"  # Replace with your password
       )
       
       try:
           # Get distributors
           print("Getting available distributors...")
           distributors = client.get_distributors()
           print(f"Available distributors: {distributors}")
           
           # Get supply points
           print("\nGetting supply points...")
           supplies = client.get_supplies()
           print(f"Found {len(supplies)} supply points")
           
           if supplies:
               supply = supplies[0]
               print(f"Using CUPS: {supply.cups}")
               
               # Get contract details
               print("\nGetting contract details...")
               contract = client.get_contract_detail(
                   cups=supply.cups,
                   distributor_code=supply.distributor_code
               )
               
               if contract:
                   print(f"Marketer: {contract.marketer}")
                   print(f"Tariff: {contract.access_fare}")
               
               # Get consumption data
               print("\nGetting consumption data...")
               consumptions = client.get_consumption(
                   cups=supply.cups,
                   distributor_code=supply.distributor_code,
                   date_from="2024/01",
                   date_to="2024/01",
                   point_type=supply.point_type
               )
               
               print(f"Found {len(consumptions)} consumption records")
               
               # Show summary
               if consumptions:
                   total_consumption = sum(c.consumption_kwh for c in consumptions)
                   print(f"Total consumption: {total_consumption:.2f} kWh")
       
       except AuthenticationError:
           print("❌ Authentication failed. Please check your credentials.")
       except DatadisError as e:
           print(f"❌ Error: {e}")

   if __name__ == "__main__":
       main()

Next Steps
----------

* Read the :doc:`api` documentation for detailed method descriptions
* Check out more :doc:`examples` for specific use cases
* Learn about error handling and best practices