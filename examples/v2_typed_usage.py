#!/usr/bin/env python3
"""
Ejemplo de uso del cliente Datadis API v2 (respuestas tipadas)
"""

import os

from datadis_python import DatadisClientV2


def main():
    """Ejemplo completo usando API v2"""

    # Credenciales desde variables de entorno
    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Error: Define DATADIS_USERNAME y DATADIS_PASSWORD")
        return

    # Crear cliente v2 (respuestas tipadas)
    client = DatadisClientV2(username, password)

    try:
        print("=== Cliente Datadis API v2 (Tipado) ===\n")

        # 1. Obtener suministros (objetos SupplyData)
        print("1. Obteniendo suministros...")
        supplies = client.get_supplies()
        print(f"Encontrados {len(supplies)} suministros")

        if supplies:
            first_supply = supplies[0]
            print(f"Primer suministro: {first_supply.cups}")
            print(f"Dirección: {first_supply.address}")
            print(f"Distribuidor: {first_supply.distributor_code}")
            print(f"Tipo de punto: {first_supply.point_type}")

            # Acceso tipado con autocompletado
            print(f"Provincia: {first_supply.province}")
            print(f"Municipio: {first_supply.municipality}")

            # 2. Obtener detalle del contrato (objeto ContractData o None)
            print("\n2. Obteniendo detalle del contrato...")
            contract = client.get_contract_detail(
                cups=first_supply.cups, distributor_code=first_supply.distributor_code
            )

            if contract:
                print(f"Contrato encontrado para {contract.cups}")
                print(
                    f"Tarifa: {contract.tariff if hasattr(contract, 'tariff') else 'N/A'}"
                )
            else:
                print("No se encontró contrato")

            # 3. Obtener consumo (lista de ConsumptionData)
            print("\n3. Obteniendo datos de consumo...")
            consumption_data = client.get_consumption(
                cups=first_supply.cups,
                distributor_code=first_supply.distributor_code,
                date_from="2024/11",
                date_to="2024/11",
            )
            print(f"Registros de consumo: {len(consumption_data)}")

            if consumption_data:
                first_record = consumption_data[0]
                print(f"Primer registro:")
                print(f"  Fecha: {first_record.date}")
                print(f"  Hora: {first_record.time}")
                print(f"  Consumo: {first_record.obtained_measure} kWh")

            # 4. Resumen de consumo (método exclusivo de v2)
            print("\n4. Obteniendo resumen de consumo...")
            summary = client.get_consumption_summary(
                cups=first_supply.cups,
                distributor_code=first_supply.distributor_code,
                date_from="2024/11",
                date_to="2024/11",
            )
            print(f"Resumen de consumo:")
            print(f"  Total: {summary['total']:.2f} kWh")
            print(f"  Promedio: {summary['average']:.2f} kWh")
            print(f"  Mínimo: {summary['min']:.2f} kWh")
            print(f"  Máximo: {summary['max']:.2f} kWh")
            print(f"  Registros: {summary['count']}")

            # 5. Obtener potencia máxima (lista de MaxPowerData)
            print("\n5. Obteniendo datos de potencia máxima...")
            max_power_data = client.get_max_power(
                cups=first_supply.cups,
                distributor_code=first_supply.distributor_code,
                date_from="2024/11",
                date_to="2024/11",
            )
            print(f"Registros de potencia: {len(max_power_data)}")

            if max_power_data:
                first_power = max_power_data[0]
                print(f"Primer registro de potencia:")
                print(f"  Fecha: {first_power.date}")
                print(f"  Potencia: {first_power.max_power} kW")

            # 6. Datos reactivos (solo disponible en v2)
            print("\n6. Obteniendo datos de energía reactiva...")
            try:
                reactive_data = client.get_reactive_data(
                    cups=first_supply.cups,
                    distributor_code=first_supply.distributor_code,
                    date_from="2024/11",
                    date_to="2024/11",
                )
                print(f"Registros de energía reactiva: {len(reactive_data)}")
            except Exception as e:
                print(f"Energía reactiva no disponible: {e}")

        # 7. Obtener distribuidores
        print("\n7. Obteniendo códigos de distribuidores...")
        distributor_codes = client.get_distributors()
        print(f"Códigos de distribuidores: {distributor_codes}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()
        print("\n=== Cliente cerrado ===")


if __name__ == "__main__":
    main()
