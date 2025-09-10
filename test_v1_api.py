#!/usr/bin/env python3
"""
Script de prueba para verificar que el cliente funciona con API v1
"""

import os
import sys
from datadis_python.client.datadis_client import DatadisClient

def test_v1_api():
    """Prueba el cliente con API v1"""
    
    # Obtener credenciales del entorno
    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")
    
    if not username or not password:
        print("Error: Define DATADIS_USERNAME y DATADIS_PASSWORD en las variables de entorno")
        return False
    
    try:
        # Crear cliente
        print("Creando cliente...")
        client = DatadisClient(username, password)
        
        # Probar get_supplies (API v1)
        print("Probando get_supplies...")
        supplies = client.get_supplies()
        print(f"Resultado get_supplies: {len(supplies)} suministros encontrados")
        
        if supplies:
            print("Primer suministro:")
            print(supplies[0])
            
            # Probar get_distributors
            print("\nProbando get_distributors...")
            distributors = client.get_distributors()
            print(f"Resultado get_distributors: {len(distributors)} distribuidores")
            
            if distributors:
                print("Primer distribuidor:")
                print(distributors[0])
        
        client.close()
        print("\nPrueba completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_v1_api()
    sys.exit(0 if success else 1)