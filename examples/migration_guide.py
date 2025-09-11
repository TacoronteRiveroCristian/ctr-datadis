#!/usr/bin/env python3
"""
Guía de migración del cliente legacy al nuevo SDK
"""

import os


def legacy_example():
    """Ejemplo usando el cliente legacy (deprecated)"""
    print("=== CLIENTE LEGACY (DEPRECATED) ===")

    from datadis_python import DatadisClientLegacy

    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Credenciales no configuradas")
        return

    # Cliente legacy (el original)
    client = DatadisClientLegacy(username, password)

    try:
        # Esto funciona como antes
        supplies = client.get_supplies()
        print(f"Legacy - Suministros: {len(supplies)}")

        if supplies:
            supply = supplies[0]
            print(f"Legacy - Primer CUPS: {supply.cups}")

    except Exception as e:
        print(f"Legacy error: {e}")
    finally:
        client.close()


def modern_v1_example():
    """Mismo resultado usando el nuevo cliente v1"""
    print("\n=== MIGRACIÓN A V1 (MISMO COMPORTAMIENTO) ===")

    from datadis_python import DatadisClientV1

    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Credenciales no configuradas")
        return

    # Nuevo cliente v1 - comportamiento similar al legacy pero más rápido
    client = DatadisClientV1(username, password)

    try:
        # Misma funcionalidad, respuestas raw
        supplies = client.get_supplies()
        print(f"V1 - Suministros: {len(supplies)}")

        if supplies:
            supply = supplies[0]  # Es un diccionario
            print(f"V1 - Primer CUPS: {supply['cups']}")

            # Nuevas funciones de conveniencia
            cups_list = client.get_cups_list()
            print(f"V1 - Solo CUPS: {len(cups_list)}")

    except Exception as e:
        print(f"V1 error: {e}")
    finally:
        client.close()


def modern_v2_example():
    """Versión moderna con tipos y validación"""
    print("\n=== MIGRACIÓN A V2 (MODERNO Y TIPADO) ===")

    from datadis_python import DatadisClientV2

    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Credenciales no configuradas")
        return

    # Nuevo cliente v2 - tipado y validado
    client = DatadisClientV2(username, password)

    try:
        # Misma función, respuesta tipada
        supplies = client.get_supplies()
        print(f"V2 - Suministros: {len(supplies)}")

        if supplies:
            supply = supplies[0]  # Es un objeto SupplyData
            print(f"V2 - Primer CUPS: {supply.cups}")
            print(f"V2 - Autocompletado: {supply.address}")

            # Nuevas funciones avanzadas
            summary = client.get_consumption_summary(
                supply.cups, supply.distributor_code, "2024/11", "2024/11"
            )
            print(f"V2 - Resumen consumo: {summary['total']:.2f} kWh")

    except Exception as e:
        print(f"V2 error: {e}")
    finally:
        client.close()


def unified_example():
    """Lo mejor de ambos mundos"""
    print("\n=== CLIENTE UNIFICADO (RECOMENDADO) ===")

    from datadis_python import DatadisClient

    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Credenciales no configuradas")
        return

    # Cliente unificado - acceso a ambas versiones
    client = DatadisClient(username, password)

    try:
        # Por defecto usa v2 (recomendado)
        supplies = client.get_supplies()
        print(f"Unificado - Suministros (v2): {len(supplies)}")

        # Acceso explícito a v1 cuando necesites velocidad
        supplies_raw = client.v1.get_supplies()
        print(f"Unificado - Suministros raw (v1): {len(supplies_raw)}")

        # Acceso explícito a v2 cuando necesites tipos
        supplies_typed = client.v2.get_supplies()
        print(f"Unificado - Suministros tipados (v2): {len(supplies_typed)}")

        # Métodos de conveniencia específicos
        cups_list = client.get_cups_list()  # De v1
        distributor_codes = client.get_distributor_codes()  # De v1

        print(f"Unificado - CUPS: {len(cups_list)}")
        print(f"Unificado - Distribuidores: {distributor_codes}")

    except Exception as e:
        print(f"Unificado error: {e}")
    finally:
        client.close()


def migration_recommendations():
    """Recomendaciones de migración"""
    print("\n=== RECOMENDACIONES DE MIGRACIÓN ===")

    recommendations = [
        "1. MIGRACIÓN INMEDIATA (sin cambios):",
        "   - Cambiar: from datadis_python import DatadisClient",
        "   - Por: from datadis_python import DatadisClientV1 as DatadisClient",
        "   - Tu código funcionará igual pero más rápido",
        "",
        "2. MIGRACIÓN GRADUAL (recomendada):",
        "   - Usar: from datadis_python import DatadisClient",
        "   - client.v1.get_supplies() para velocidad",
        "   - client.v2.get_supplies() para tipos",
        "   - client.get_supplies() usa v2 por defecto",
        "",
        "3. MIGRACIÓN COMPLETA (largo plazo):",
        "   - Usar: from datadis_python import DatadisClientV2",
        "   - Aprovechar tipos, validación y nuevas funciones",
        "   - Mejor experiencia de desarrollo",
        "",
        "4. CASOS DE USO ESPECÍFICOS:",
        "   - Scripts simples/rápidos: DatadisClientV1",
        "   - Aplicaciones con tipos: DatadisClientV2",
        "   - Librerías/frameworks: DatadisClient (unificado)",
        "",
        "5. COMPATIBILIDAD:",
        "   - DatadisClientLegacy seguirá funcionando",
        "   - Pero considera migrar para mejor rendimiento",
        "   - Nuevas funciones solo en v1/v2",
    ]

    for rec in recommendations:
        print(rec)


def main():
    """Ejecutar todos los ejemplos de migración"""

    # Verificar credenciales
    username = os.getenv("DATADIS_USERNAME")
    password = os.getenv("DATADIS_PASSWORD")

    if not username or not password:
        print("Para ejecutar los ejemplos, define:")
        print("export DATADIS_USERNAME='tu_nif'")
        print("export DATADIS_PASSWORD='tu_password'")
        print("\nMostrando solo las recomendaciones:")
        migration_recommendations()
        return

    # Ejecutar ejemplos
    legacy_example()
    modern_v1_example()
    modern_v2_example()
    unified_example()
    migration_recommendations()


if __name__ == "__main__":
    main()
