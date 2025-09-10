#!/usr/bin/env python3
"""
Ejemplo de uso del cliente unificado Datadis (v1 + v2)
"""

import os
from datadis_python import DatadisClient

def main():
    """Ejemplo completo usando el cliente unificado"""
    
    # Credenciales desde variables de entorno
    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")
    
    if not username or not password:
        print("Error: Define DATADIS_USERNAME y DATADIS_PASSWORD")
        return
    
    # Crear cliente unificado
    client = DatadisClient(username, password)
    
    try:
        print("=== Cliente Datadis Unificado (v1 + v2) ===\n")
        
        # Información del cliente
        info = client.get_client_info()
        print(f"Estado del cliente: {info}")
        
        # ===============================
        # MÉTODOS DE CONVENIENCIA (usa v2)
        # ===============================
        print("\n--- Usando métodos de conveniencia (API v2) ---")
        
        # Por defecto usa v2 (tipado)
        supplies = client.get_supplies()
        print(f"Suministros (v2): {len(supplies)} objetos SupplyData")
        
        if supplies:
            first_supply = supplies[0]
            print(f"CUPS: {first_supply.cups}")
            print(f"Tipo: {type(first_supply).__name__}")
            
            # Consumo con resumen automático
            summary = client.get_consumption_summary(
                cups=first_supply.cups,
                distributor_code=first_supply.distributor_code,
                date_from="2024/11",
                date_to="2024/11"
            )
            print(f"Resumen consumo: {summary['total']:.2f} kWh total")
        
        # ===============================
        # USO ESPECÍFICO DE V1 (raw)
        # ===============================
        print("\n--- Usando API v1 específicamente (raw) ---")
        
        # Acceso directo a v1
        supplies_raw = client.v1.get_supplies()
        print(f"Suministros (v1): {len(supplies_raw)} diccionarios")
        
        if supplies_raw:
            first_raw = supplies_raw[0]
            print(f"CUPS: {first_raw['cups']}")
            print(f"Tipo: {type(first_raw).__name__}")
            
            # Métodos exclusivos de v1
            cups_list = client.v1.get_cups_list()
            print(f"Lista CUPS: {len(cups_list)} códigos")
            
            # Consumo raw
            consumption_raw = client.v1.get_consumption(
                cups=first_raw['cups'],
                distributor_code=first_raw['distributorCode'],
                date_from="2024/11",
                date_to="2024/11"
            )
            print(f"Consumo raw: {len(consumption_raw)} registros")
        
        # ===============================
        # USO ESPECÍFICO DE V2 (tipado)
        # ===============================
        print("\n--- Usando API v2 específicamente (tipado) ---")
        
        # Acceso directo a v2
        supplies_typed = client.v2.get_supplies()
        print(f"Suministros (v2): {len(supplies_typed)} objetos tipados")
        
        if supplies_typed:
            first_typed = supplies_typed[0]
            print(f"CUPS: {first_typed.cups}")
            print(f"Tipo: {type(first_typed).__name__}")
            
            # Funciones exclusivas de v2
            try:
                reactive = client.v2.get_reactive_data(
                    cups=first_typed.cups,
                    distributor_code=first_typed.distributor_code,
                    date_from="2024/11",
                    date_to="2024/11"
                )
                print(f"Datos reactivos: {len(reactive)} registros")
            except:
                print("Datos reactivos no disponibles")
        
        # ===============================
        # COMPARACIÓN DE RENDIMIENTO
        # ===============================
        print("\n--- Comparación de rendimiento ---")
        
        import time
        
        if supplies_raw:
            cups = supplies_raw[0]['cups']
            distributor = supplies_raw[0]['distributorCode']
            
            # Tiempo v1 (raw)
            start = time.time()
            consumption_v1 = client.v1.get_consumption(cups, distributor, "2024/11", "2024/11")
            time_v1 = time.time() - start
            
            # Tiempo v2 (tipado)
            start = time.time()
            consumption_v2 = client.v2.get_consumption(cups, distributor, "2024/11", "2024/11")
            time_v2 = time.time() - start
            
            print(f"V1 (raw): {time_v1:.3f}s, {len(consumption_v1)} registros")
            print(f"V2 (tipado): {time_v2:.3f}s, {len(consumption_v2)} registros")
            print(f"Diferencia: {abs(time_v2 - time_v1):.3f}s")
        
        # ===============================
        # MIGRACIÓN GRADUAL
        # ===============================
        print("\n--- Ejemplo de migración gradual ---")
        
        # Usar v1 para operaciones masivas (más rápido)
        all_cups = client.get_cups_list()  # Método de v1
        print(f"Todos los CUPS (v1): {len(all_cups)}")
        
        # Usar v2 para análisis detallado (más rico)
        if all_cups:
            for cups in all_cups[:2]:  # Solo los primeros 2
                distributor_codes = client.get_distributor_codes()  # v1
                if distributor_codes:
                    # Análisis tipado con v2
                    summary = client.v2.get_consumption_summary(
                        cups, distributor_codes[0], "2024/11", "2024/11"
                    )
                    print(f"CUPS {cups}: {summary['total']:.2f} kWh")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        client.close()
        print("\n=== Cliente cerrado ===")

if __name__ == "__main__":
    main()