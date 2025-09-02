"""
Cliente principal para la API de Datadis
"""

import time
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime

from ..exceptions import DatadisError, AuthenticationError, APIError
from ..utils.constants import DATADIS_BASE_URL, API_ENDPOINTS, DEFAULT_TIMEOUT, MAX_RETRIES
from ..utils.validators import (
    validate_cups, 
    validate_date_range, 
    validate_measurement_type,
    validate_point_type
)
from ..models.consumption import ConsumptionData, ConsumptionResponse
from ..models.contract import ContractData
from ..models.supply import SupplyData


class DatadisClient:
    """
    Cliente para interactuar con la API de Datadis
    
    Proporciona métodos sencillos para obtener datos de consumo, contratos,
    facturas y otros datos disponibles en la plataforma Datadis.
    """
    
    def __init__(
        self, 
        username: str, 
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = MAX_RETRIES
    ):
        """
        Inicializa el cliente de Datadis
        
        Args:
            username: Nombre de usuario de Datadis
            password: Contraseña de Datadis
            timeout: Timeout para requests en segundos
            retries: Número de reintentos automáticos
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.base_url = DATADIS_BASE_URL
        self.session = requests.Session()
        self.token = None
        self.token_expiry = None
        
        # Headers por defecto
        self.session.headers.update({
            'User-Agent': 'datadis-python-sdk/0.1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        authenticated: bool = True
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a la API
        
        Args:
            method: Método HTTP (GET, POST)
            endpoint: Endpoint de la API
            data: Datos para el body de la petición
            params: Parámetros de query string
            authenticated: Si requiere autenticación
            
        Returns:
            Respuesta JSON de la API
            
        Raises:
            APIError: Error en la respuesta de la API
            AuthenticationError: Error de autenticación
        """
        if authenticated:
            self._ensure_authenticated()
        
        url = f"{self.base_url}{endpoint}"
        
        # Reintentos automáticos
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                
                # Manejar respuestas de la API
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError:
                        # Respuesta no es JSON válido
                        raise APIError(
                            f"Respuesta no válida del servidor: {response.text}",
                            response.status_code
                        )
                elif response.status_code == 401:
                    # Token expirado, intentar renovar
                    self.token = None
                    if authenticated:
                        self._authenticate()
                        continue
                    else:
                        raise AuthenticationError("Credenciales inválidas")
                elif response.status_code == 429:
                    # Rate limiting, esperar antes de reintentar
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)  # Backoff exponencial
                        continue
                    raise APIError("Límite de peticiones excedido", 429)
                else:
                    # Otros errores HTTP
                    error_msg = f"Error HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'message' in error_data:
                            error_msg = error_data['message']
                    except ValueError:
                        pass
                    
                    raise APIError(error_msg, response.status_code)
                    
            except requests.RequestException as e:
                if attempt == self.retries:
                    raise DatadisError(f"Error de conexión: {str(e)}")
                time.sleep(1)  # Esperar antes de reintentar
    
    def _authenticate(self) -> None:
        """
        Autentica con la API y obtiene token de acceso
        
        Raises:
            AuthenticationError: Si las credenciales son inválidas
        """
        login_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self._make_request(
                "POST", 
                API_ENDPOINTS["login"], 
                data=login_data,
                authenticated=False
            )
            
            if "token" in response:
                self.token = response["token"]
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                # Asumir que el token expira en 1 hora
                self.token_expiry = time.time() + 3600
            else:
                raise AuthenticationError("No se recibió token en la respuesta")
                
        except APIError as e:
            if e.status_code == 401:
                raise AuthenticationError("Credenciales inválidas")
            raise
    
    def _ensure_authenticated(self) -> None:
        """
        Asegura que el cliente está autenticado con un token válido
        """
        if (not self.token or 
            (self.token_expiry and time.time() >= self.token_expiry - 300)):  # Renovar 5 min antes
            self._authenticate()
    
    def get_contracts(self) -> List[ContractData]:
        """
        Obtiene la lista de contratos disponibles
        
        Returns:
            Lista de datos de contratos
        """
        response = self._make_request("GET", API_ENDPOINTS["contracts"])
        
        contracts = []
        if isinstance(response, list):
            for contract_data in response:
                contracts.append(ContractData(**contract_data))
        elif isinstance(response, dict) and "contracts" in response:
            for contract_data in response["contracts"]:
                contracts.append(ContractData(**contract_data))
        
        return contracts
    
    def get_supplies(self) -> List[SupplyData]:
        """
        Obtiene la lista de puntos de suministro disponibles
        
        Returns:
            Lista de datos de suministros
        """
        response = self._make_request("GET", API_ENDPOINTS["supplies"])
        
        supplies = []
        if isinstance(response, list):
            for supply_data in response:
                supplies.append(SupplyData(**supply_data))
        elif isinstance(response, dict) and "supplies" in response:
            for supply_data in response["supplies"]:
                supplies.append(SupplyData(**supply_data))
        
        return supplies
    
    def get_consumption(
        self,
        cups: str,
        date_from: str,
        date_to: str,
        measurement_type: Optional[int] = None,
        point_type: Optional[int] = None
    ) -> List[ConsumptionData]:
        """
        Obtiene datos de consumo para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            date_from: Fecha inicial (YYYY-MM-DD)
            date_to: Fecha final (YYYY-MM-DD) 
            measurement_type: Tipo de medida (0=consumo, 1=generación)
            point_type: Tipo de punto (1=frontera, 2=consumo, 3=generación, 4=aux)
            
        Returns:
            Lista de datos de consumo
        """
        # Validar parámetros
        cups = validate_cups(cups)
        date_from, date_to = validate_date_range(date_from, date_to)
        measurement_type = validate_measurement_type(measurement_type)
        point_type = validate_point_type(point_type)
        
        params = {
            "cups": cups,
            "dateFrom": date_from,
            "dateTo": date_to,
            "measurementType": measurement_type,
            "pointType": point_type
        }
        
        response = self._make_request("GET", API_ENDPOINTS["consumption"], params=params)
        
        consumptions = []
        if isinstance(response, list):
            for consumption_data in response:
                consumptions.append(ConsumptionData(**consumption_data))
        elif isinstance(response, dict):
            # Si la respuesta tiene estructura anidada
            if "consumptionData" in response:
                for consumption_data in response["consumptionData"]:
                    consumptions.append(ConsumptionData(**consumption_data))
        
        return consumptions
    
    def get_invoices(
        self,
        cups: str,
        date_from: str, 
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene datos de facturación para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            date_from: Fecha inicial (YYYY-MM-DD)
            date_to: Fecha final (YYYY-MM-DD)
            
        Returns:
            Lista de datos de facturación
        """
        # Validar parámetros
        cups = validate_cups(cups)
        date_from, date_to = validate_date_range(date_from, date_to)
        
        params = {
            "cups": cups,
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        response = self._make_request("GET", API_ENDPOINTS["invoices"], params=params)
        
        # Por ahora devolver respuesta raw hasta definir modelo específico
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "invoices" in response:
            return response["invoices"]
        else:
            return []
    
    def close(self) -> None:
        """
        Cierra la sesión y libera recursos
        """
        if self.session:
            self.session.close()
        self.token = None
        self.token_expiry = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()