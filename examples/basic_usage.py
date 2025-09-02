"""
Ejemplo básico de uso del SDK de Datadis (actualizado para API real)
"""

from datadis_python import DatadisClient
from datadis_python.exceptions import DatadisError, AuthenticationError

def main():
    # Configurar credenciales (mejor usar variables de entorno en producción)
    username = "tu_nif_datadis"  # NIF del usuario registrado en Datadis
    password = "tu_password_datadis"
    
    try:
        # Crear cliente
        with DatadisClient(username, password) as client:
            print("🔑 Cliente inicializado correctamente")
            
            # 1. Obtener distribuidores disponibles
            print("🏢 Obteniendo distribuidores disponibles...")
            distributors = client.get_distributors()
            print(f"✅ Encontrados {len(distributors)} distribuidores: {distributors}")
            
            # 2. Obtener puntos de suministro
            print("📍 Obteniendo puntos de suministro...")
            supplies = client.get_supplies()
            print(f"✅ Encontrados {len(supplies)} puntos de suministro")
            
            for supply in supplies:
                print(f"  - CUPS: {supply.cups}")
                print(f"    Dirección: {supply.address}")
                print(f"    Distribuidor: {supply.distributor} (Código: {supply.distributor_code})")
                print(f"    Tipo de punto: {supply.point_type}")
                print()
            
            # 3. Si hay suministros, obtener detalle del contrato del primero
            if supplies:
                supply = supplies[0]
                cups = supply.cups
                distributor_code = supply.distributor_code
                
                print(f"📋 Obteniendo detalle del contrato para CUPS: {cups}")
                contract = client.get_contract_detail(cups, distributor_code)
                
                if contract:
                    print("✅ Contrato encontrado:")
                    print(f"  - Comercializadora: {contract.marketer}")
                    print(f"  - Tarifa: {contract.access_fare}")
                    print(f"  - Potencia contratada: {contract.contracted_power_kw} kW")
                    print(f"  - Fecha inicio: {contract.start_date}")
                    print()
                
                # 4. Obtener consumos (últimos 2 meses)
                print(f"⚡ Obteniendo consumos para CUPS: {cups}")
                consumptions = client.get_consumption(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",  # Formato correcto: YYYY/MM
                    date_to="2024/02",
                    measurement_type=0,   # 0 = por horas
                    point_type=supply.point_type
                )
                
                print(f"✅ Encontrados {len(consumptions)} registros de consumo")
                
                # Mostrar algunos ejemplos
                for consumption in consumptions[:5]:  # Primeros 5
                    print(f"  - {consumption.date} {consumption.time}: "
                          f"{consumption.consumption_kwh} kWh "
                          f"({consumption.obtain_method})")
                
                # 5. Obtener potencias máximas
                print(f"⚡ Obteniendo potencias máximas para CUPS: {cups}")
                max_powers = client.get_max_power(
                    cups=cups,
                    distributor_code=distributor_code,
                    date_from="2024/01",
                    date_to="2024/02"
                )
                
                print(f"✅ Encontradas {len(max_powers)} mediciones de potencia máxima")
                
                for power in max_powers[:3]:  # Primeras 3
                    print(f"  - {power.date} {power.time}: "
                          f"{power.max_power} W ({power.period})")
    
    except AuthenticationError:
        print("❌ Error de autenticación. Verifica tu NIF y contraseña.")
    
    except DatadisError as e:
        print(f"❌ Error del SDK: {e}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()