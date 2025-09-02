Examples
========

This section provides practical examples of how to use the Datadis Python SDK for common tasks.

Basic Data Retrieval
---------------------

Simple Supply Point Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient

   client = DatadisClient(username="12345678A", password="password")

   # Get all supply points
   supplies = client.get_supplies()

   for supply in supplies:
       print(f"CUPS: {supply.cups}")
       print(f"Address: {supply.address}")
       print(f"Municipality: {supply.municipality}")
       print(f"Province: {supply.province}")
       print(f"Distributor: {supply.distributor}")
       print("-" * 50)

Consumption Analysis
--------------------

Monthly Consumption Report
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient
   from datetime import datetime, timedelta
   from collections import defaultdict

   def generate_monthly_report(client, cups, distributor_code, year, month):
       """Generate a monthly consumption report."""
       
       date_str = f"{year}/{month:02d}"
       
       consumptions = client.get_consumption(
           cups=cups,
           distributor_code=distributor_code,
           date_from=date_str,
           date_to=date_str,
           measurement_type=0  # Hourly data
       )
       
       # Group by day
       daily_consumption = defaultdict(float)
       
       for consumption in consumptions:
           day = consumption.date.split("/")[2]  # Extract day
           daily_consumption[day] += consumption.consumption_kwh
       
       # Print report
       print(f"Monthly Consumption Report - {year}/{month:02d}")
       print("=" * 50)
       print(f"CUPS: {cups}")
       print(f"Total records: {len(consumptions)}")
       print(f"Total consumption: {sum(daily_consumption.values()):.2f} kWh")
       print()
       
       # Daily breakdown
       for day in sorted(daily_consumption.keys(), key=int):
           print(f"Day {day}: {daily_consumption[day]:.2f} kWh")
       
       return daily_consumption

   # Usage
   client = DatadisClient(username="12345678A", password="password")
   supplies = client.get_supplies()
   
   if supplies:
       supply = supplies[0]
       report = generate_monthly_report(
           client, 
           supply.cups, 
           supply.distributor_code, 
           2024, 
           1
       )

Peak Hour Analysis
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient
   from collections import Counter

   def analyze_peak_hours(client, cups, distributor_code, date_from, date_to):
       """Analyze peak consumption hours."""
       
       consumptions = client.get_consumption(
           cups=cups,
           distributor_code=distributor_code,
           date_from=date_from,
           date_to=date_to,
           measurement_type=0
       )
       
       # Extract hours and consumption
       hourly_data = []
       for consumption in consumptions:
           hour = int(consumption.time.split(":")[0])
           hourly_data.append((hour, consumption.consumption_kwh))
       
       # Find peak hours
       hour_totals = Counter()
       hour_counts = Counter()
       
       for hour, consumption in hourly_data:
           hour_totals[hour] += consumption
           hour_counts[hour] += 1
       
       # Calculate averages
       hour_averages = {
           hour: hour_totals[hour] / hour_counts[hour] 
           for hour in hour_totals
       }
       
       # Sort by consumption
       sorted_hours = sorted(
           hour_averages.items(), 
           key=lambda x: x[1], 
           reverse=True
       )
       
       print("Peak Hours Analysis")
       print("=" * 30)
       print("Hour | Avg Consumption (kWh)")
       print("-" * 30)
       
       for hour, avg_consumption in sorted_hours[:5]:
           print(f"{hour:02d}:00 | {avg_consumption:.3f}")

   # Usage
   client = DatadisClient(username="12345678A", password="password")
   supplies = client.get_supplies()
   
   if supplies:
       supply = supplies[0]
       analyze_peak_hours(
           client,
           supply.cups,
           supply.distributor_code,
           "2024/01",
           "2024/01"
       )

Contract and Supply Management
------------------------------

Complete Supply Point Overview
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient

   def get_complete_supply_info(client, cups, distributor_code):
       """Get complete information for a supply point."""
       
       print(f"Supply Point Information: {cups}")
       print("=" * 60)
       
       # Get contract details
       contract = client.get_contract_detail(cups, distributor_code)
       
       if contract:
           print("CONTRACT INFORMATION")
           print(f"  Marketer: {contract.marketer or 'Not available'}")
           print(f"  Distributor: {contract.distributor}")
           print(f"  Tariff: {contract.access_fare}")
           print(f"  Contracted Power: {contract.contracted_power_kw} kW")
           print(f"  Start Date: {contract.start_date}")
           print(f"  End Date: {contract.end_date or 'Active'}")
           
           if contract.self_consumption_type_code:
               print(f"  Self-consumption: {contract.self_consumption_type_desc}")
           
           print()
       
       # Get recent consumption summary
       try:
           consumptions = client.get_consumption(
               cups=cups,
               distributor_code=distributor_code,
               date_from="2024/01",
               date_to="2024/01",
               measurement_type=0
           )
           
           if consumptions:
               total = sum(c.consumption_kwh for c in consumptions)
               avg_daily = total / 31  # January has 31 days
               
               print("RECENT CONSUMPTION (January 2024)")
               print(f"  Total: {total:.2f} kWh")
               print(f"  Daily Average: {avg_daily:.2f} kWh")
               print(f"  Records: {len(consumptions)}")
               
               # Method breakdown
               methods = {}
               for c in consumptions:
                   methods[c.obtain_method] = methods.get(c.obtain_method, 0) + 1
               
               print("  Data Quality:")
               for method, count in methods.items():
                   percentage = (count / len(consumptions)) * 100
                   print(f"    {method}: {count} records ({percentage:.1f}%)")
       
       except Exception as e:
           print(f"Could not retrieve consumption data: {e}")

   # Usage
   client = DatadisClient(username="12345678A", password="password")
   supplies = client.get_supplies()
   
   for supply in supplies:
       get_complete_supply_info(client, supply.cups, supply.distributor_code)
       print("\n" + "="*60 + "\n")

Error Handling Examples
-----------------------

Robust Data Retrieval
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datadis_python import DatadisClient
   from datadis_python.exceptions import (
       DatadisError, 
       AuthenticationError, 
       APIError, 
       ValidationError
   )
   import time

   def robust_get_consumption(client, cups, distributor_code, date_from, date_to, max_retries=3):
       """Get consumption data with robust error handling."""
       
       for attempt in range(max_retries):
           try:
               print(f"Attempt {attempt + 1}/{max_retries}")
               
               consumptions = client.get_consumption(
                   cups=cups,
                   distributor_code=distributor_code,
                   date_from=date_from,
                   date_to=date_to
               )
               
               print(f"✓ Successfully retrieved {len(consumptions)} records")
               return consumptions
               
           except AuthenticationError as e:
               print(f"✗ Authentication failed: {e}")
               # Don't retry authentication errors
               break
               
           except ValidationError as e:
               print(f"✗ Validation error: {e}")
               # Don't retry validation errors
               break
               
           except APIError as e:
               print(f"✗ API error: {e.message} (status: {e.status_code})")
               
               if e.status_code == 429:  # Rate limited
                   if attempt < max_retries - 1:
                       wait_time = 2 ** attempt  # Exponential backoff
                       print(f"  Rate limited. Waiting {wait_time} seconds...")
                       time.sleep(wait_time)
                       continue
               elif e.status_code >= 500:  # Server error
                   if attempt < max_retries - 1:
                       print(f"  Server error. Retrying in 5 seconds...")
                       time.sleep(5)
                       continue
               
               # Don't retry client errors (4xx except 429)
               break
               
           except DatadisError as e:
               print(f"✗ General error: {e}")
               if attempt < max_retries - 1:
                   print(f"  Retrying in 3 seconds...")
                   time.sleep(3)
                   continue
               break
       
       print("✗ Failed to retrieve data after all attempts")
       return []

   # Usage
   client = DatadisClient(username="12345678A", password="password")
   
   try:
       supplies = client.get_supplies()
       
       if supplies:
           supply = supplies[0]
           consumptions = robust_get_consumption(
               client,
               supply.cups,
               supply.distributor_code,
               "2024/01",
               "2024/01"
           )
           
           if consumptions:
               print(f"Final result: {len(consumptions)} consumption records")
   
   except Exception as e:
       print(f"Unexpected error: {e}")

Data Export
-----------

Export to CSV
^^^^^^^^^^^^^

.. code-block:: python

   import csv
   from datadis_python import DatadisClient

   def export_consumption_to_csv(client, cups, distributor_code, date_from, date_to, filename):
       """Export consumption data to CSV."""
       
       consumptions = client.get_consumption(
           cups=cups,
           distributor_code=distributor_code,
           date_from=date_from,
           date_to=date_to
       )
       
       with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
           fieldnames = [
               'cups', 'date', 'time', 'consumption_kwh', 'obtain_method',
               'surplus_energy_kwh', 'generation_energy_kwh', 'self_consumption_energy_kwh'
           ]
           
           writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
           writer.writeheader()
           
           for consumption in consumptions:
               writer.writerow({
                   'cups': consumption.cups,
                   'date': consumption.date,
                   'time': consumption.time,
                   'consumption_kwh': consumption.consumption_kwh,
                   'obtain_method': consumption.obtain_method,
                   'surplus_energy_kwh': consumption.surplus_energy_kwh or 0,
                   'generation_energy_kwh': consumption.generation_energy_kwh or 0,
                   'self_consumption_energy_kwh': consumption.self_consumption_energy_kwh or 0
               })
       
       print(f"Exported {len(consumptions)} records to {filename}")

   # Usage
   client = DatadisClient(username="12345678A", password="password")
   supplies = client.get_supplies()
   
   if supplies:
       supply = supplies[0]
       export_consumption_to_csv(
           client,
           supply.cups,
           supply.distributor_code,
           "2024/01",
           "2024/01",
           f"consumption_{supply.cups}_2024_01.csv"
       )