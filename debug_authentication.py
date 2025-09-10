#!/usr/bin/env python3
"""
Script de debug para comparar autenticación manual vs clientes v1/v2
"""

import os
import requests
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

USERNAME = os.getenv("DATADIS_CIF") 
PASSWORD = os.getenv("DATADIS_PASSWORD")

if not USERNAME or not PASSWORD:
    print("Error: Define DATADIS_CIF y DATLADIS_PASSWORD")
    exit(1)

print("=== DEBUG AUTENTICACIÓN DATADIS ===\n")

def test_manual_authentication():
    """Probar autenticación manual (tu método que funciona)"""
    print("1. AUTENTICACIÓN MANUAL (método que funciona)")
    
    try:
        # Headers para autenticación
        auth_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'User-Agent': 'datadis-python-sdk/0.1.0'
        }
        
        # Datos de login
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        print(f"  URL: https://datadis.es/nikola-auth/tokens/login")
        print(f"  Headers: {auth_headers}")
        print(f"  Data: username={USERNAME[:3]}***, password=***")
        
        # Petición de autenticación
        auth_response = requests.post(
            url="https://datadis.es/nikola-auth/tokens/login",
            data=login_data,
            headers=auth_headers,
            timeout=30
        )
        
        print(f"  Status: {auth_response.status_code}")
        print(f"  Response length: {len(auth_response.text)}")
        
        if auth_response.status_code == 200:
            token = auth_response.text.strip()
            print(f"  Token obtenido: {token[:20]}...")
            
            # Probar get_supplies
            print("\n  Probando get_supplies...")
            supplies_response = requests.get(
                url="https://datadis.es/api-private/api/get-supplies",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            
            print(f"  Supplies status: {supplies_response.status_code}")
            print(f"  Supplies length: {len(supplies_response.text)}")
            
            if supplies_response.status_code == 200:
                import json
                supplies = supplies_response.json()
                print(f"  Supplies count: {len(supplies)}")
                print(f"  ✅ MANUAL FUNCIONA!")
                return token
            else:
                print(f"  ❌ Error en supplies: {supplies_response.text}")
                return None
        else:
            print(f"  ❌ Error en auth: {auth_response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error manual: {e}")
        return None

def test_base_client():
    """Probar cliente base paso a paso"""
    print("\n2. CLIENTE BASE (paso a paso)")
    
    try:
        from datadis_python.client.base import BaseDatadisClient
        from datadis_python.client.v1.client import DatadisClientV1
        
        print("  Creando cliente v1...")
        client = DatadisClientV1(USERNAME, PASSWORD)
        
        print("  Autenticando manualmente...")
        client.authenticate()
        
        print(f"  Token obtenido: {client.token[:20] if client.token else 'None'}...")
        
        if client.token:
            print("  Probando petición autenticada...")
            response = client.make_authenticated_request("GET", "/get-supplies")
            print(f"  Response type: {type(response)}")
            print(f"  Response length: {len(response) if isinstance(response, list) else 'N/A'}")
            print(f"  ✅ CLIENTE BASE FUNCIONA!")
        else:
            print(f"  ❌ No se obtuvo token")
            
    except Exception as e:
        print(f"  ❌ Error cliente base: {e}")
        import traceback
        traceback.print_exc()

def test_http_client():
    """Probar HTTPClient directamente"""
    print("\n3. HTTP CLIENT (utilidad HTTP)")
    
    try:
        from datadis_python.utils.http import HTTPClient
        
        http_client = HTTPClient(timeout=30, retries=3)
        
        print("  Autenticando con HTTPClient...")
        
        auth_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'User-Agent': 'datadis-python-sdk/0.1.0'
        }
        
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        token = http_client.make_request(
            method="POST",
            url="https://datadis.es/nikola-auth/tokens/login",
            data=login_data,
            headers=auth_headers,
            use_form_data=True
        )
        
        print(f"  Token: {token[:20] if isinstance(token, str) else 'Error'}...")
        
        if isinstance(token, str):
            http_client.set_auth_header(token)
            
            supplies = http_client.make_request(
                method="GET",
                url="https://datadis.es/api-private/api/get-supplies"
            )
            
            print(f"  Supplies: {len(supplies) if isinstance(supplies, list) else 'Error'}")
            print(f"  ✅ HTTP CLIENT FUNCIONA!")
        else:
            print(f"  ❌ Token inválido: {token}")
            
    except Exception as e:
        print(f"  ❌ Error HTTP client: {e}")
        import traceback
        traceback.print_exc()

def test_v1_client():
    """Probar DatadisClientV1 completo"""
    print("\n4. DATADIS CLIENT V1 (completo)")
    
    try:
        from datadis_python.client.v1.client import DatadisClientV1
        
        print("  Creando cliente...")
        client = DatadisClientV1(USERNAME, PASSWORD)
        
        print("  Llamando get_supplies()...")
        start_time = time.time()
        supplies = client.get_supplies()
        end_time = time.time()
        
        print(f"  Tiempo: {end_time - start_time:.2f}s")
        print(f"  Supplies: {len(supplies) if isinstance(supplies, list) else 'Error'}")
        print(f"  ✅ CLIENT V1 FUNCIONA!")
        
        client.close()
        
    except Exception as e:
        print(f"  ❌ Error client v1: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Ejecutar todos los tests de debug"""
    
    # Test 1: Manual (baseline que funciona)
    manual_token = test_manual_authentication()
    
    # Test 2: Cliente base
    test_base_client()
    
    # Test 3: HTTP Client
    test_http_client()
    
    # Test 4: Cliente V1 completo
    test_v1_client()
    
    print("\n=== RESUMEN ===")
    print("Si manual funciona pero los clientes no, el problema está en:")
    print("1. Implementación de autenticación")
    print("2. Manejo de headers")
    print("3. Timeouts o reintentos")
    print("4. URLs o endpoints")

if __name__ == "__main__":
    main()