"""
Cliente V1 simplificado y robusto para Datadis
"""

import time
import requests
from typing import List, Dict, Any, Optional

from ...utils.constants import API_V1_ENDPOINTS, AUTH_ENDPOINTS, DATADIS_BASE_URL, DATADIS_API_BASE
from ...utils.text_utils import normalize_api_response
from ...exceptions import DatadisError, AuthenticationError, APIError


class SimpleDatadisClientV1:
    """
    Cliente V1 simplificado que maneja mejor los timeouts de Datadis
    """
    
    def __init__(self, username: str, password: str, timeout: int = 120, retries: int = 3):
        """
        Inicializa el cliente simplificado
        
        Args:
            username: NIF del usuario
            password: Contraseña
            timeout: Timeout en segundos (120s por defecto para Datadis)
            retries: Número de reintentos
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.token = None
        self.session = requests.Session()
        
        # Headers básicos (desactivar compresión para evitar problemas de gzip)
        self.session.headers.update({
            'User-Agent': 'datadis-python-sdk/0.2.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'identity'  # Desactivar compresión gzip
        })
    
    def authenticate(self) -> bool:
        """
        Autentica con la API de Datadis
        
        Returns:
            True si la autenticación fue exitosa
        """
        print("🔐 Autenticando con Datadis...")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'User-Agent': 'datadis-python-sdk/0.2.0'
        }
        
        data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(
                url=f"{DATADIS_BASE_URL}{AUTH_ENDPOINTS['login']}",
                data=data,
                headers=headers,
                timeout=30  # Auth timeout más corto
            )
            
            if response.status_code == 200:
                self.token = response.text.strip()
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Autenticación exitosa")
                return True
            else:
                raise AuthenticationError(f"Error de autenticación: {response.status_code}")
                
        except requests.Timeout:
            raise AuthenticationError("Timeout en autenticación")
        except Exception as e:
            raise AuthenticationError(f"Error en autenticación: {e}")
    
    def _make_authenticated_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Realiza una petición autenticada con manejo robusto de timeouts
        
        Args:
            endpoint: Endpoint de la API (ej: '/get-supplies')
            params: Parámetros de query
            
        Returns:
            Respuesta de la API
        """
        if not self.token:
            if not self.authenticate():
                raise AuthenticationError("No se pudo autenticar")
        
        url = f"{DATADIS_API_BASE}{endpoint}"
        
        for attempt in range(self.retries + 1):
            try:
                print(f"📡 Petición a {endpoint} (intento {attempt + 1}/{self.retries + 1})...")
                
                response = self.session.get(
                    url=url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    print(f"✅ Respuesta exitosa ({len(response.text)} chars)")
                    json_response = response.json()
                    # Normalizar texto para evitar problemas de caracteres especiales
                    return normalize_api_response(json_response)
                elif response.status_code == 401:
                    # Token expirado, renovar
                    print("🔄 Token expirado, renovando...")
                    self.token = None
                    if self.authenticate():
                        continue
                    else:
                        raise AuthenticationError("No se pudo renovar el token")
                else:
                    raise APIError(f"Error HTTP {response.status_code}: {response.text}", response.status_code)
                    
            except requests.Timeout:
                if attempt < self.retries:
                    wait_time = min(30, (2 ** attempt) * 5)
                    print(f"⏰ Timeout. Esperando {wait_time}s antes del siguiente intento...")
                    time.sleep(wait_time)
                else:
                    raise DatadisError(f"Timeout después de {self.retries + 1} intentos. La API de Datadis puede estar lenta.")
            except Exception as e:
                if attempt < self.retries:
                    wait_time = (2 ** attempt) * 2
                    print(f"❌ Error: {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise DatadisError(f"Error después de {self.retries + 1} intentos: {e}")
        
        raise DatadisError("Se agotaron todos los reintentos")
    
    def get_supplies(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de puntos de suministro
        
        Returns:
            Lista de suministros como diccionarios
        """
        print("🏠 Obteniendo lista de suministros...")
        response = self._make_authenticated_request(API_V1_ENDPOINTS["supplies"])
        
        if isinstance(response, list):
            print(f"✅ {len(response)} suministros obtenidos")
            return response
        elif isinstance(response, dict) and "supplies" in response:
            supplies = response["supplies"]
            print(f"✅ {len(supplies)} suministros obtenidos")
            return supplies
        else:
            print("⚠️ Respuesta inesperada de la API")
            return []
    
    def get_distributors(self) -> List[Dict[str, Any]]:
        """Obtiene distribuidores"""
        print("🔌 Obteniendo distribuidores...")
        response = self._make_authenticated_request(API_V1_ENDPOINTS["distributors"])
        
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return [response] if response else []
        return []
    
    def get_contract_detail(self, cups: str, distributor_code: str) -> List[Dict[str, Any]]:
        """Obtiene detalle del contrato - devuelve lista de diccionarios según API spec"""
        print(f"📋 Obteniendo contrato para {cups}...")
        params = {"cups": cups, "distributorCode": distributor_code}
        response = self._make_authenticated_request(API_V1_ENDPOINTS["contracts"], params)
        
        # Según la documentación de la API, siempre debe devolver una lista de diccionarios
        if isinstance(response, list):
            # Ya es una lista, devolverla directamente
            return response
        elif isinstance(response, dict):
            # Si viene un objeto, envolverlo en una lista
            if response:  # Solo si tiene contenido
                return [response]
        
        # Si no hay datos válidos, devolver lista vacía
        return []
    
    def get_consumption(
        self, 
        cups: str, 
        distributor_code: str, 
        date_from: str, 
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene datos de consumo"""
        print(f"⚡ Obteniendo consumo para {cups} ({date_from} - {date_to})...")
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type)
        }
        
        if point_type is not None:
            params["pointType"] = str(point_type)
        
        response = self._make_authenticated_request(API_V1_ENDPOINTS["consumption"], params)
        
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "timeCurve" in response:
            return response["timeCurve"]
        return []
    
    def get_max_power(
        self, 
        cups: str, 
        distributor_code: str, 
        date_from: str, 
        date_to: str
    ) -> List[Dict[str, Any]]:
        """Obtiene datos de potencia máxima"""
        print(f"🔋 Obteniendo potencia máxima para {cups} ({date_from} - {date_to})...")
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to
        }
        
        response = self._make_authenticated_request(API_V1_ENDPOINTS["max_power"], params)
        
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "maxPower" in response:
            return response["maxPower"]
        return []
    
    def close(self):
        """Cierra la sesión"""
        if self.session:
            self.session.close()
        self.token = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()