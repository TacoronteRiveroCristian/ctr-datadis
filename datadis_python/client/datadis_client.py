"""
Cliente actualizado para la API de Datadis (versión corregida)
"""

import time
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime

from ..exceptions import DatadisError, AuthenticationError, APIError
from ..utils.constants import DATADIS_BASE_URL, DATADIS_API_BASE, API_ENDPOINTS, DEFAULT_TIMEOUT, MAX_RETRIES
from ..utils.validators import (
    validate_cups, 
    validate_date_range, 
    validate_measurement_type,
    validate_point_type,
    validate_distributor_code
)
from ..models import (
    ConsumptionData, ContractData, SupplyData, MaxPowerData,
    SuppliesResponse, ContractResponse, ConsumptionResponse, 
    MaxPowerResponse, DistributorsResponse
)


class DatadisClient:
    """
    Cliente actualizado para interactuar con la API de Datadis
    
    Basado en la documentación oficial de Datadis API v2
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
            username: NIF del usuario registrado en Datadis
            password: Contraseña de acceso a Datadis
            timeout: Timeout para requests en segundos
            retries: Número de reintentos automáticos
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.base_url = DATADIS_BASE_URL
        self.api_base = DATADIS_API_BASE
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
        """
        if authenticated:
            self._ensure_authenticated()
        
        # Usar URL base apropiada según el endpoint
        if endpoint.startswith('/nikola-auth'):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.api_base}{endpoint}"
        
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
                    # Rate limiting
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)
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
                time.sleep(1)
    
    def _authenticate(self) -> None:
        """
        Autentica con la API y obtiene token de acceso
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
    
    def get_distributors(self) -> List[str]:
        """
        Obtiene la lista de códigos de distribuidores disponibles
        
        Returns:
            Lista de códigos de distribuidoras
        """
        response = self._make_request("GET", API_ENDPOINTS["distributors_v2"])
        
        if isinstance(response, dict) and "distExistenceUser" in response:
            distributor_codes = response["distExistenceUser"].get("distributorCodes", [])
            return distributor_codes
        
        return []
    
    def get_supplies(self, distributor_code: Optional[str] = None) -> List[SupplyData]:
        """
        Obtiene la lista de puntos de suministro disponibles
        
        Args:
            distributor_code: Código del distribuidor (opcional)
            
        Returns:
            Lista de datos de suministros
        """
        params = {}
        if distributor_code:
            params["distributorCode"] = validate_distributor_code(distributor_code)
            
        response = self._make_request("GET", API_ENDPOINTS["supplies_v2"], params=params)
        
        supplies = []
        if isinstance(response, dict) and "supplies" in response:
            for supply_data in response["supplies"]:
                supplies.append(SupplyData(**supply_data))
        
        return supplies
    
    def get_contract_detail(
        self,
        cups: str,
        distributor_code: str
    ) -> Optional[ContractData]:
        """
        Obtiene el detalle del contrato para un CUPS específico
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            
        Returns:
            Datos del contrato o None si no se encuentra
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code
        }
        
        response = self._make_request("GET", API_ENDPOINTS["contracts_v2"], params=params)
        
        if isinstance(response, dict) and "contract" in response:
            contracts = response["contract"]
            if contracts:
                return ContractData(**contracts[0])
        
        return None
    
    def get_consumption(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str,
        measurement_type: int = 0,
        point_type: Optional[int] = None
    ) -> List[ConsumptionData]:
        """
        Obtiene datos de consumo para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            measurement_type: Tipo de medida (0=hora, 1=cuarto hora)
            point_type: Tipo de punto (obtenido de supplies)
            
        Returns:
            Lista de datos de consumo
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")
        measurement_type = validate_measurement_type(measurement_type)
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to,
            "measurementType": str(measurement_type)
        }
        
        if point_type is not None:
            params["pointType"] = str(validate_point_type(point_type))
        
        response = self._make_request("GET", API_ENDPOINTS["consumption_v2"], params=params)
        
        consumptions = []
        if isinstance(response, dict) and "timeCurve" in response:
            for consumption_data in response["timeCurve"]:
                consumptions.append(ConsumptionData(**consumption_data))
        
        return consumptions
    
    def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        date_from: str,
        date_to: str
    ) -> List[MaxPowerData]:
        """
        Obtiene datos de potencia máxima para un CUPS y rango de fechas
        
        Args:
            cups: Código CUPS del punto de suministro
            distributor_code: Código del distribuidor
            date_from: Fecha inicial (YYYY/MM)
            date_to: Fecha final (YYYY/MM)
            
        Returns:
            Lista de datos de potencia máxima
        """
        cups = validate_cups(cups)
        distributor_code = validate_distributor_code(distributor_code)
        date_from, date_to = validate_date_range(date_from, date_to, "monthly")
        
        params = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": date_from,
            "endDate": date_to
        }
        
        response = self._make_request("GET", API_ENDPOINTS["max_power_v2"], params=params)
        
        max_powers = []
        if isinstance(response, dict) and "maxPower" in response:
            for power_data in response["maxPower"]:
                max_powers.append(MaxPowerData(**power_data))
        
        return max_powers
    
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