#!/usr/bin/env python3
"""
Debug específico del problema de supplies
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("DATADIS_CIF")
PASSWORD = os.getenv("DATADIS_PASSWORD")

def test_step_by_step():
    """Test paso a paso muy específico"""
    print("=== DEBUG ESPECÍFICO ===")
    
    # 1. Autenticación manual
    print("1. Autenticación...")
    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'User-Agent': 'datadis-python-sdk/0.1.0'
    }
    
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    auth_response = requests.post(
        url="https://datadis.es/nikola-auth/tokens/login",
        data=auth_data,
        headers=auth_headers,
        timeout=15  # Timeout más corto
    )
    
    print(f"Auth: {auth_response.status_code}")
    
    if auth_response.status_code != 200:
        print("❌ Auth falló")
        return
    
    token = auth_response.text.strip()
    print(f"Token: {token[:30]}...")
    
    # 2. Test con diferentes timeouts
    timeouts = [5, 10, 15, 30, 60]
    
    for timeout in timeouts:
        print(f"\n2. Probando supplies con timeout {timeout}s...")
        
        try:
            supplies_response = requests.get(
                url="https://datadis.es/api-private/api/get-supplies",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "User-Agent": "datadis-python-sdk/0.1.0"
                },
                timeout=timeout
            )
            
            print(f"  Status: {supplies_response.status_code}")
            print(f"  Content-Length: {len(supplies_response.text)}")
            
            if supplies_response.status_code == 200:
                supplies = supplies_response.json()
                print(f"  ✅ SUCCESS! {len(supplies)} supplies")
                return supplies
            else:
                print(f"  ❌ HTTP Error: {supplies_response.text[:100]}")
                
        except requests.Timeout:
            print(f"  ⏰ Timeout después de {timeout}s")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # 3. Test con otros endpoints
    print(f"\n3. Probando otros endpoints...")
    endpoints = [
        "/get-distributors-with-supplies",
        "/get-supplies-v2"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"  Probando {endpoint}...")
            response = requests.get(
                url=f"https://datadis.es/api-private/api{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"    Status: {response.status_code}")
        except requests.Timeout:
            print(f"    ⏰ Timeout en {endpoint}")
        except Exception as e:
            print(f"    ❌ Error: {e}")

if __name__ == "__main__":
    test_step_by_step()