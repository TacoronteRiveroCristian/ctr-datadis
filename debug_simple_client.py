#!/usr/bin/env python3
"""
Cliente simple para debug - implementación minimalista que debe funcionar
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("DATADIS_CIF")
PASSWORD = os.getenv("DATADIS_PASSWORD")

class SimpleDatadisClient:
    """Cliente minimalista para debug"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # Headers básicos
        self.session.headers.update({
            'User-Agent': 'datadis-python-sdk/0.1.0'
        })
    
    def authenticate(self):
        """Autenticación simple"""
        print("Autenticando...")
        
        # Headers específicos para auth
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'User-Agent': 'datadis-python-sdk/0.1.0'
        }
        
        data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(
                url="https://datadis.es/nikola-auth/tokens/login",
                data=data,  # form data, no json
                headers=headers,
                timeout=30
            )
            
            print(f"Auth status: {response.status_code}")
            
            if response.status_code == 200:
                self.token = response.text.strip()
                print(f"Token obtenido: {self.token[:20]}...")
                
                # Configurar header de auth para futuras peticiones
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                return True
            else:
                print(f"Error auth: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error en authenticate: {e}")
            return False
    
    def get_supplies(self):
        """Obtener supplies"""
        if not self.token:
            if not self.authenticate():
                return None
        
        print("Obteniendo supplies...")
        
        try:
            # NO agregar delay aquí para debug
            response = self.session.get(
                url="https://datadis.es/api-private/api/get-supplies",
                timeout=30
            )
            
            print(f"Supplies status: {response.status_code}")
            
            if response.status_code == 200:
                supplies = response.json()
                print(f"Supplies obtenidos: {len(supplies)}")
                return supplies
            else:
                print(f"Error supplies: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error en get_supplies: {e}")
            return None
    
    def close(self):
        """Cerrar sesión"""
        if self.session:
            self.session.close()

def test_simple_client():
    """Test del cliente simple"""
    print("=== CLIENTE SIMPLE DEBUG ===")
    
    if not USERNAME or not PASSWORD:
        print("Error: Variables de entorno no configuradas")
        return
    
    client = SimpleDatadisClient(USERNAME, PASSWORD)
    
    try:
        # Test paso a paso
        print("1. Autenticando...")
        if client.authenticate():
            print("✅ Autenticación exitosa")
            
            print("2. Obteniendo supplies...")
            supplies = client.get_supplies()
            
            if supplies:
                print(f"✅ Supplies obtenidos: {len(supplies)}")
                print(f"Primer CUPS: {supplies[0].get('cups', 'N/A')}")
            else:
                print("❌ Error obteniendo supplies")
        else:
            print("❌ Error en autenticación")
            
    finally:
        client.close()

if __name__ == "__main__":
    test_simple_client()