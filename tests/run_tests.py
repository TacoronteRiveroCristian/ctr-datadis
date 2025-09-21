#!/usr/bin/env python3
"""
Script para ejecutar tests del SDK de Datadis con diferentes configuraciones.

Este script proporciona diferentes modos de ejecución de tests:
- Tests rápidos (solo unit tests)
- Tests completos (unit + integration)
- Tests con coverage
- Tests específicos por componente
- Tests de performance
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y maneja errores."""
    print(f"\n{'='*60}")
    print(f"EJECUTANDO: {description}")
    print(f"COMANDO: {' '.join(command)}")
    print(f"{'='*60}")

    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"[OK] {description} - EXITOSO")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} - FALLÓ con código {e.returncode}")
        return False


def run_fast_tests():
    """Ejecuta solo tests unitarios rápidos."""
    command = ["poetry", "run", "pytest", "-m", "unit and not slow", "--tb=short", "-q"]
    return run_command(command, "Tests unitarios rápidos")


def run_full_tests():
    """Ejecuta todos los tests (unit + integration)."""
    command = ["poetry", "run", "pytest", "--tb=short"]
    return run_command(command, "Tests completos (unit + integration)")


def run_coverage_tests():
    """Ejecuta tests con coverage."""
    command = [
        "poetry",
        "run",
        "pytest",
        "--cov=datadis_python",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=json:coverage.json",
        "--cov-fail-under=90",
    ]
    return run_command(command, "Tests con coverage")


def run_specific_tests(component):
    """Ejecuta tests específicos de un componente."""
    test_map = {
        "auth": "-m auth",
        "models": "-m models",
        "client_v1": "-m client_v1",
        "client_v2": "-m client_v2",
        "utils": "-m utils",
        "errors": "-m errors",
        "integration": "-m integration",
    }

    if component not in test_map:
        print(f"[ERROR] Componente desconocido: {component}")
        print(f"Componentes disponibles: {', '.join(test_map.keys())}")
        return False

    command = ["poetry", "run", "pytest", test_map[component], "--tb=short"]
    return run_command(command, f"Tests de {component}")


def run_performance_tests():
    """Ejecuta tests de performance."""
    command = ["poetry", "run", "pytest", "-m", "slow", "--tb=short", "--durations=0"]
    return run_command(command, "Tests de performance")


def run_quality_checks():
    """Ejecuta checks de calidad de código."""
    checks = [
        (
            ["poetry", "run", "black", "--check", "datadis_python/"],
            "Black format check",
        ),
        (
            ["poetry", "run", "isort", "--check-only", "datladis_python/"],
            "Import sorting check",
        ),
        (["poetry", "run", "flake8", "datadis_python/"], "Flake8 linting"),
        (["poetry", "run", "mypy", "datadis_python/"], "Type checking"),
    ]

    all_passed = True
    for command, description in checks:
        try:
            # Fix typo in isort command
            if "datladis_python" in command:
                command = [
                    cmd.replace("datladis_python", "datadis_python") for cmd in command
                ]

            success = run_command(command, description)
            if not success:
                all_passed = False
        except Exception as e:
            print(f"[ERROR] Error ejecutando {description}: {e}")
            all_passed = False

    return all_passed


def run_test_validation():
    """Valida que los tests están bien escritos."""
    command = ["poetry", "run", "pytest", "tests/test_coverage_and_quality.py", "-v"]
    return run_command(command, "Validación de calidad de tests")


def main():
    """Execute main test runner logic."""
    parser = argparse.ArgumentParser(
        description="Ejecutor de tests para el SDK de Datadis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py --fast                    # Tests rápidos
  python run_tests.py --full                    # Tests completos
  python run_tests.py --coverage                # Tests con coverage
  python run_tests.py --component auth          # Tests de autenticación
  python run_tests.py --performance             # Tests de performance
  python run_tests.py --quality                 # Checks de calidad
  python run_tests.py --validate                # Validar tests
  python run_tests.py --all                     # Todo lo anterior
        """,
    )

    # Argumentos mutuamente excluyentes para diferentes tipos de ejecución
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fast", action="store_true", help="Ejecutar solo tests unitarios rápidos"
    )
    group.add_argument("--full", action="store_true", help="Ejecutar todos los tests")
    group.add_argument(
        "--coverage", action="store_true", help="Ejecutar tests con reporte de coverage"
    )
    group.add_argument(
        "--component", type=str, help="Ejecutar tests de un componente específico"
    )
    group.add_argument(
        "--performance", action="store_true", help="Ejecutar tests de performance"
    )
    group.add_argument(
        "--quality", action="store_true", help="Ejecutar checks de calidad de código"
    )
    group.add_argument(
        "--validate",
        action="store_true",
        help="Validar que los tests están bien escritos",
    )
    group.add_argument(
        "--all", action="store_true", help="Ejecutar todos los tipos de tests y checks"
    )

    # Argumentos adicionales
    parser.add_argument(
        "--fail-fast", action="store_true", help="Detener en el primer fallo"
    )
    parser.add_argument("--verbose", action="store_true", help="Output verboso")

    args = parser.parse_args()

    # Verificar que estamos en el directorio correcto
    if not Path("pyproject.toml").exists():
        print("[ERROR] Error: Ejecutar desde el directorio raíz del proyecto")
        sys.exit(1)

    success = True

    try:
        if args.fast:
            success = run_fast_tests()

        elif args.full:
            success = run_full_tests()

        elif args.coverage:
            success = run_coverage_tests()
            if success:
                print(f"\n[INFO] Reporte de coverage generado en: htmlcov/index.html")

        elif args.component:
            success = run_specific_tests(args.component)

        elif args.performance:
            success = run_performance_tests()

        elif args.quality:
            success = run_quality_checks()

        elif args.validate:
            success = run_test_validation()

        elif args.all:
            print("\n[INFO] EJECUTANDO SUITE COMPLETA DE TESTS Y CHECKS")

            steps = [
                ("Tests rápidos", run_fast_tests),
                ("Validación de tests", run_test_validation),
                ("Checks de calidad", run_quality_checks),
                ("Tests completos", run_full_tests),
                ("Tests con coverage", run_coverage_tests),
                ("Tests de performance", run_performance_tests),
            ]

            results = {}
            for step_name, step_func in steps:
                if args.fail_fast and not success:
                    break

                step_success = step_func()
                results[step_name] = step_success
                if not step_success:
                    success = False

            # Resumen final
            print(f"\n{'='*60}")
            print("RESUMEN DE EJECUCIÓN")
            print(f"{'='*60}")
            for step_name, step_success in results.items():
                status = "[OK] PASÓ" if step_success else "[ERROR] FALLÓ"
                print(f"{step_name}: {status}")
            print(f"{'='*60}")

            if success:
                print("[SUCCESS] TODOS LOS CHECKS PASARON")
                print("[INFO] Reporte de coverage en: htmlcov/index.html")
            else:
                print("[FAIL] ALGUNOS CHECKS FALLARON")

    except KeyboardInterrupt:
        print("\n[WARNING] Ejecución interrumpida por el usuario")
        success = False

    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        success = False

    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
