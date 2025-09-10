#!/usr/bin/env python3
"""
Test del cliente v1 simplificado
"""

import os
from dotenv import load_dotenv
from datadis_python.client.v1.simple_client import SimpleDatadisClientV1

load_dotenv()

USERNAME = os.getenv("DATADIS_CIF")
PASSWORD = os.getenv("DATADIS_PASSWORD")

def test_simple_v1():
    """Test del cliente v1 simplificado"""
    print("=== TEST CLIENTE V1 SIMPLIFICADO ===\n")
    
    if not USERNAME or not PASSWORD:
        print("❌ Variables de entorno no configuradas")
        return
    
    # Cliente con timeout alto y más reintentos
    with SimpleDatadisClientV1(USERNAME, PASSWORD, timeout=120, retries=3) as client:
        try:
            # Test get_supplies
            supplies = client.get_supplies()
            
            if supplies:
                print(f"✅ SUCCESS! {len(supplies)} suministros obtenidos")
                print(f"Primer CUPS: {supplies[0].get('cups', 'N/A')}")
                print(f"Primer distribuidor: {supplies[0].get('distributorCode', 'N/A')}")
                
                # Test contract detail si tenemos supplies
                if len(supplies) > 0:
                    first_supply = supplies[0]
                    cups = first_supply.get('cups')
                    distributor = first_supply.get('distributorCode')
                    
                    if cups and distributor:
                        print(f"\n📋 Probando contrato para {cups}...")
                        contract = client.get_contract_detail(cups, distributor)
                        print(f"Contrato obtenido: {len(contract)} campos")
                
            else:
                print("❌ No se obtuvieron suministros")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_v1()