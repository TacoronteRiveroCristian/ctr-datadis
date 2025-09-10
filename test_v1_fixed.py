#!/usr/bin/env python3
"""
Test del cliente v1 corregido (importación normal)
"""

import os
from dotenv import load_dotenv
from datadis_python import DatadisClientV1

load_dotenv()

USERNAME = os.getenv("DATADIS_CIF")
PASSWORD = os.getenv("DATADIS_PASSWORD")

def test_v1_fixed():
    """Test del cliente v1 corregido"""
    print("=== TEST CLIENTE V1 CORREGIDO ===\n")
    
    if not USERNAME or not PASSWORD:
        print("❌ Variables de entorno no configuradas")
        return
    
    # Ahora DatadisClientV1 usa la implementación simplificada
    with DatadisClientV1(USERNAME, PASSWORD) as client:
        try:
            # Test get_supplies
            print("🧪 Probando get_supplies()...")
            supplies = client.get_supplies()
            
            if supplies:
                print(f"✅ SUCCESS! {len(supplies)} suministros")
                
                # Mostrar primer suministro
                first = supplies[0]
                print(f"📍 Primer suministro:")
                print(f"   CUPS: {first.get('cups')}")
                print(f"   Dirección: {first.get('address')}")
                print(f"   Distribuidor: {first.get('distributorCode')}")
                print(f"   Tipo punto: {first.get('pointType')}")
                
                # Test distribuidores
                print(f"\n🧪 Probando get_distributors()...")
                distributors = client.get_distributors()
                print(f"✅ {len(distributors)} distribuidores obtenidos")
                
                # Test consumo (último mes)
                print(f"\n🧪 Probando get_consumption()...")
                consumption = client.get_consumption(
                    cups=first.get('cups'),
                    distributor_code=first.get('distributorCode'),
                    date_from="2024/11",
                    date_to="2024/11"
                )
                print(f"✅ {len(consumption)} registros de consumo")
                
                if consumption:
                    first_record = consumption[0]
                    print(f"📊 Primer registro:")
                    print(f"   Fecha: {first_record.get('date')}")
                    print(f"   Hora: {first_record.get('time')}")
                    print(f"   Consumo: {first_record.get('obtainedMeasure')} kWh")
                
                print(f"\n🎉 TODOS LOS TESTS PASARON!")
                
            else:
                print("❌ No se obtuvieron suministros")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_v1_fixed()