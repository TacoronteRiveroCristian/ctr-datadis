#!/usr/bin/env python3
"""
Ejemplo de uso del cliente Datadis API v1 (respuestas raw)
"""

import os
from datadis_python import DatadisClientV1

def main():
    """Ejemplo completo usando API v1"""
    
    # Credenciales desde variables de entorno
    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")
    
    if not username or not password:
        print("Error: Define DATADIS_USERNAME y DATADIS_PASSWORD")
        return
    
    # Crear cliente v1 (respuestas raw)
    client = DatadisClientV1(username, password)
    
    try:
        print("=== Cliente Datadis API v1 (Raw) ===\n")
        
        # 1. Obtener suministros (lista de diccionarios)
        print("1. Obteniendo suministros...")
        supplies = client.get_supplies()
        print(f"Encontrados {len(supplies)} suministros")
        
        if supplies:
            first_supply = supplies[0]
            print(f"Primer suministro: {first_supply['cups']}")
            print(f"Dirección: {first_supply['address']}")
            print(f"Distribuidor: {first_supply['distributorCode']}")
            
            # 2. Obtener detalle del contrato
            print("\n2. Obteniendo detalle del contrato...")
            contract = client.get_contract_detail(
                cups=first_supply['cups'],
                distributor_code=first_supply['distributorCode']
            )
            print(f"Contrato: {len(contract)} campos")
            
            # 3. Obtener consumo del último mes
            print("\n3. Obteniendo datos de consumo...")
            consumption = client.get_consumption(
                cups=first_supply['cups'],
                distributor_code=first_supply['distributorCode'],
                date_from="2024/11",
                date_to="2024/11"
            )
            print(f"Registros de consumo: {len(consumption)}")
            
            if consumption:
                print(f"Primer registro: {consumption[0]}")
            
            # 4. Métodos de conveniencia
            print("\n4. Usando métodos de conveniencia...")
            cups_list = client.get_cups_list()
            print(f"CUPS disponibles: {len(cups_list)}")
            
            distributor_codes = client.get_distributor_codes()
            print(f"Códigos de distribuidores: {distributor_codes}")
        
        # 5. Obtener distribuidores
        print("\n5. Obteniendo distribuidores...")
        distributors = client.get_distributors()
        print(f"Distribuidores: {len(distributors)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        client.close()
        print("\n=== Cliente cerrado ===")

if __name__ == "__main__":
    main()