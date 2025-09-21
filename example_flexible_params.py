#!/usr/bin/env python3
"""
Ejemplo demostrando los parámetros flexibles en el SDK de Datadis.

Este ejemplo muestra cómo ahora puedes usar tipos más pythónicos:
- datetime objects para fechas
- int/float para números
- int para distributor_code
"""

from datetime import date, datetime

from datadis_python.client.v1.simple_client import SimpleDatadisClientV1


def demo_flexible_parameters():
    """Demostración de los nuevos parámetros flexibles."""
    print("🚀 Demostración de Parámetros Flexibles en Datadis SDK")
    print("=" * 60)

    # Crear cliente (no se ejecutará realmente)
    # client = SimpleDatadisClientV1("test_user", "test_pass")

    # Ejemplo 1: Fechas como datetime objects
    print("\n📅 Ejemplo 1: Usando datetime objects para fechas")
    fecha_inicio = datetime(2024, 1, 1)
    fecha_fin = date(2024, 1, 31)
    print(f"   Fecha inicio: {fecha_inicio} (datetime)")
    print(f"   Fecha fin: {fecha_fin} (date)")
    print("   ✅ Antes: Solo strings como '2024/01/01'")
    print("   ✅ Ahora: datetime(2024, 1, 1) o date(2024, 1, 31)")

    # Ejemplo 2: Distributor code como int
    print("\n🏢 Ejemplo 2: Usando int para distributor_code")
    distributor_code = 2  # E-distribución
    print(f"   Distributor code: {distributor_code} (int)")
    print("   ✅ Antes: Solo string como '2'")
    print("   ✅ Ahora: int como 2 o string '2'")

    # Ejemplo 3: Measurement type como diferentes tipos
    print("\n📊 Ejemplo 3: Usando diferentes tipos para measurement_type")
    measurement_type_int = 0
    measurement_type_float = 1.0
    measurement_type_str = "0"
    print(f"   Como int: {measurement_type_int}")
    print(f"   Como float: {measurement_type_float}")
    print(f"   Como string: {measurement_type_str}")
    print("   ✅ Todos son válidos ahora!")

    # Los métodos ahora aceptan estos tipos flexibles:
    # client.get_consumption(
    #     cups="ES0031607515707001RC0F",
    #     distributor_code=2,  # int en lugar de "2"
    #     date_from=datetime(2024, 1, 1),  # datetime en lugar de "2024/01/01"
    #     date_to=date(2024, 1, 31),  # date en lugar de "2024/01/31"
    #     measurement_type=0,  # int en lugar de "0"
    #     point_type=1  # int en lugar de "1"
    # )

    print("\n🎉 Beneficios de los parámetros flexibles:")
    print("   • Más pythónico y natural")
    print("   • Menos conversiones manuales")
    print("   • Mejor integración con datetime")
    print("   • Mantiene compatibilidad total con código existente")
    print("   • Validación automática de tipos")


if __name__ == "__main__":
    demo_flexible_parameters()
