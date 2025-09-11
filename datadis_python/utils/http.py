"""
Utilidades HTTP comunes para clientes Datadis
"""

import time
from typing import Optional, Dict, Any, Union
import requests

from ..exceptions import DatadisError, AuthenticationError, APIError


class HTTPClient:
    """Cliente HTTP base con funcionalidades comunes"""
    
    def __init__(self, timeout: int = 60, retries: int = 3):
        """
        Inicializa el cliente HTTP
        
        Args:
            timeout: Timeout para requests en segundos
            retries: Número de reintentos automáticos
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        
        # Headers por defecto
        self.session.headers.update({
            'User-Agent': 'datadis-python-sdk/0.1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_form_data: bool = False
    ) -> Union[Dict[str, Any], str, list]:
        """
        Realiza una petición HTTP con reintentos automáticos
        
        Args:
            method: Método HTTP (GET, POST)
            url: URL completa
            data: Datos para el body de la petición
            params: Parámetros de query string
            headers: Headers adicionales
            use_form_data: Si usar form data en lugar de JSON
            
        Returns:
            Respuesta JSON, texto plano o lista
        """
        # Delay para evitar rate limiting (excepto para auth)
        if '/nikola-auth' not in url:
            time.sleep(0.1)  # Reducir delay de 0.5s a 0.1s
        
        # Reintentos automáticos
        for attempt in range(self.retries + 1):
            try:
                # Configurar headers específicos si se necesitan
                if headers:
                    request_headers = {**self.session.headers, **headers}
                else:
                    request_headers = self.session.headers
                
                # Configurar la petición según el tipo de datos
                if use_form_data and data:
                    # Para autenticación usar form data
                    response = requests.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        headers=request_headers,
                        timeout=self.timeout
                    )
                else:
                    # Para peticiones normales usar JSON
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        params=params,
                        timeout=self.timeout
                    )
                
                return self._handle_response(response, url)
                
            except requests.RequestException as e:
                if attempt == self.retries:
                    raise DatadisError(f"Error de conexión: {str(e)}")
                # Esperar más tiempo antes del siguiente intento
                wait_time = min(10, (2 ** attempt) * 2)  # Backoff exponencial
                print(f"Reintento {attempt + 1}/{self.retries + 1} después de {wait_time}s...")
                time.sleep(wait_time)
    
    def _handle_response(self, response: requests.Response, url: str) -> Union[Dict[str, Any], str, list]:
        """
        Maneja la respuesta HTTP
        
        Args:
            response: Respuesta HTTP
            url: URL de la petición
            
        Returns:
            Respuesta procesada
        """
        if response.status_code == 200:
            # Para autenticación, la respuesta es texto plano (JWT)
            if '/nikola-auth' in url:
                return response.text.strip()
            
            # Para otras peticiones, esperamos JSON
            try:
                json_response = response.json()
                # Normalizar texto para evitar problemas de caracteres especiales
                from ..utils.text_utils import normalize_api_response
                return normalize_api_response(json_response)
            except ValueError:
                # Si no es JSON válido, devolver como texto
                return response.text
                
        elif response.status_code == 401:
            raise AuthenticationError("Credenciales inválidas o token expirado")
        elif response.status_code == 429:
            raise APIError("Límite de peticiones excedido", 429)
        else:
            # Otros errores HTTP
            error_msg = f"Error HTTP {response.status_code}"
            try:
                error_data = response.json()
                if 'message' in error_data:
                    error_msg = error_data['message']
                elif 'error' in error_data:
                    error_msg = error_data['error']
            except ValueError:
                # Si no es JSON, usar el texto de la respuesta
                if response.text:
                    error_msg = response.text
            
            raise APIError(error_msg, response.status_code)
    
    def close(self) -> None:
        """Cierra la sesión HTTP"""
        if self.session:
            self.session.close()
    
    def set_auth_header(self, token: str) -> None:
        """Establece el header de autorización"""
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def remove_auth_header(self) -> None:
        """Remueve el header de autorización"""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]