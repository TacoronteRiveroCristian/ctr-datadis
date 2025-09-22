"""
Cliente HTTP robusto y reutilizable para el SDK de Datadis.

Este módulo proporciona una clase ``HTTPClient`` especializada para realizar peticiones
HTTP a la API de Datadis con funcionalidades avanzadas como reintentos automáticos,
manejo de timeouts, gestión de headers y procesamiento de respuestas.

La clase está optimizada específicamente para las características de la API de Datadis:
- Timeouts largos debido a la lentitud característica del servicio
- Reintentos automáticos con backoff exponencial para manejar inestabilidad
- Soporte para autenticación Bearer Token
- Manejo especial de diferentes tipos de contenido (JSON, form-data, texto plano)
- Procesamiento de respuestas con normalización de texto para caracteres especiales

Características principales:
    - **Gestión automática de reintentos**: Backoff exponencial para timeouts y errores de red
    - **Flexibilidad de contenido**: Soporte para JSON y form-data según el endpoint
    - **Manejo robusto de errores**: Clasificación inteligente de errores HTTP
    - **Integración con Pydantic**: Preparado para validación de datos
    - **Rate limiting integrado**: Delays automáticos para evitar sobrecarga del servidor

Example:
    Uso básico del cliente HTTP::

        from datadis_python.utils.http import HTTPClient

        # Inicializar con configuración personalizada
        client = HTTPClient(timeout=120, retries=5)

        # Petición GET simple
        response = client.make_request(
            method="GET",
            url="https://api.example.com/data",
            params={"param1": "value1"}
        )

        # Petición POST con autenticación
        client.set_auth_header("bearer_token_here")
        response = client.make_request(
            method="POST",
            url="https://api.example.com/auth",
            data={"username": "user", "password": "pass"},
            use_form_data=True
        )

        # Cerrar recursos
        client.close()

    Uso como context manager (recomendado)::

        with HTTPClient(timeout=90, retries=3) as client:
            client.set_auth_header("token")
            response = client.make_request("GET", "https://api.example.com/data")
            # El cliente se cierra automáticamente

Warning:
    Este cliente está específicamente optimizado para la API de Datadis. Para uso
    general, considere usar directamente la biblioteca ``requests`` o un cliente
    HTTP más genérico.

:author: TacoronteRiveroCristian
"""

import time
from typing import Any, Dict, Optional, Union

import requests

from ..exceptions import APIError, AuthenticationError, DatadisError


class HTTPClient:
    """
    Cliente HTTP robusto especializado para la API de Datadis.

    Esta clase proporciona una interfaz de alto nivel para realizar peticiones HTTP
    con características específicamente optimizadas para interactuar con la API de Datadis.
    Incluye manejo automático de reintentos, timeouts largos, gestión de autenticación
    y procesamiento especializado de respuestas.

    Optimizaciones para Datadis:
        - **Timeouts largos**: Por defecto 60s, recomendado 90-120s para Datadis
        - **Reintentos robustos**: Backoff exponencial con hasta 5 reintentos
        - **Rate limiting**: Delays automáticos para evitar sobrecarga del servidor
        - **Manejo de encoding**: Desactiva compresión gzip para evitar problemas
        - **Procesamiento de texto**: Normalización automática de caracteres especiales

    Estrategia de reintentos:
        - **Errores de red y timeouts**: Se reintentan automáticamente
        - **Errores HTTP 4xx/5xx**: Se propagan inmediatamente (no reintentos)
        - **Backoff exponencial**: 2s → 4s → 8s → 16s → 32s (máximo 10s para timeouts)
        - **Error 401**: Se propaga para permitir renovación de token

    Example:
        Configuración típica para Datadis::

            # Configuración robusta para API lenta de Datadis
            client = HTTPClient(timeout=120, retries=5)

            # Autenticación Bearer Token
            client.set_auth_header("jwt_token_from_datadis")

            # Petición con gestión automática de errores
            response = client.make_request(
                method="GET",
                url="https://datadis.es/api-private/api/get-supplies",
                params={"distributor_code": "2"}
            )

        Diferentes tipos de contenido::

            # Para autenticación (form-data)
            auth_response = client.make_request(
                method="POST",
                url="https://datadis.es/nikola-auth/tokens/login",
                data={"username": "12345678A", "password": "password"},
                use_form_data=True
            )

            # Para endpoints de datos (JSON, por defecto)
            data_response = client.make_request(
                method="GET",
                url="https://datadis.es/api-private/api/get-consumption-data",
                params={"cups": "ES001234567890123456AB"}
            )

    :param timeout: Timeout para peticiones HTTP en segundos. Recomendado: 90-120s para Datadis
    :type timeout: int
    :param retries: Número máximo de reintentos automáticos para errores de red/timeouts
    :type retries: int

    .. note::
       La API de Datadis puede ser muy lenta (60-90 segundos) al procesar consultas
       complejas que requieren agregar datos de múltiples distribuidoras eléctricas.

    .. seealso::
       - :class:`SimpleDatadisClientV1` y :class:`SimpleDatadisClientV2` para uso de alto nivel
       - Documentación oficial de Datadis para límites de rate limiting
    """

    def __init__(self, timeout: int = 60, retries: int = 3):
        """
        Inicializa el cliente HTTP con configuración optimizada para Datadis.

        Configura una sesión HTTP persistente con headers optimizados y timeouts
        apropiados para la API de Datadis. La configuración por defecto está pensada
        para un uso general, pero se recomienda ajustar los valores para Datadis.

        Configuración recomendada para Datadis:
            - timeout: 90-120 segundos (la API puede ser muy lenta)
            - retries: 3-5 reintentos (para manejar inestabilidad ocasional)

        :param timeout: Timeout para peticiones HTTP en segundos.
                       Para Datadis se recomienda 90-120s debido a la lentitud del servicio
        :type timeout: int
        :param retries: Número máximo de reintentos automáticos para errores de red.
                       3-5 reintentos recomendados para Datadis por su inestabilidad ocasional
        :type retries: int

        Example:
            Configuraciones típicas::

                # Configuración conservadora (rápida, pocos reintentos)
                client = HTTPClient(timeout=60, retries=2)

                # Configuración robusta para Datadis (recomendada)
                client = HTTPClient(timeout=120, retries=5)

                # Configuración para desarrollo/testing (muy paciente)
                client = HTTPClient(timeout=180, retries=3)
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

        # Headers optimizados para Datadis
        # IMPORTANTE: Desactivar compresión gzip para evitar problemas con algunos endpoints
        self.session.headers.update(
            {
                "User-Agent": "datadis-python-sdk/0.1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "identity",  # Desactivar compresión para evitar problemas
            }
        )

    def make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_form_data: bool = False,
    ) -> Union[Dict[str, Any], str, list]:
        """
        Realiza una petición HTTP robusta con reintentos automáticos y manejo de errores.

        Este método es el núcleo del cliente HTTP y maneja toda la lógica de peticiones
        incluyendo reintentos con backoff exponencial, manejo de diferentes tipos de
        contenido, rate limiting automático y procesamiento especializado de respuestas.

        Flujo de operación:
            1. **Rate limiting**: Delay automático de 0.1s (excepto para autenticación)
            2. **Configuración de headers**: Combina headers por defecto con personalizados
            3. **Selección de formato**: JSON o form-data según ``use_form_data``
            4. **Ejecución con reintentos**: Hasta ``self.retries`` intentos con backoff exponencial
            5. **Procesamiento de respuesta**: Manejo especializado según tipo de contenido

        Estrategia de reintentos:
            - **Errores de red/timeout**: Reintentos con backoff: 2s → 4s → 8s → 16s...
            - **Errores HTTP**: Propagación inmediata sin reintentos
            - **Máximo wait**: 10 segundos entre reintentos para evitar timeouts excesivos

        Tipos de contenido soportados:
            - **JSON** (por defecto): Para la mayoría de endpoints de datos
            - **Form-data**: Para autenticación y algunos endpoints legacy
            - **Detección automática**: Basada en el parámetro ``use_form_data``

        :param method: Método HTTP a usar (GET, POST, PUT, DELETE, etc.)
        :type method: str
        :param url: URL completa del endpoint a consultar
        :type url: str
        :param data: Datos a enviar en el cuerpo de la petición.
                    Para GET se ignora, para POST se usa según ``use_form_data``
        :type data: Optional[Dict[str, Any]]
        :param params: Parámetros de query string a añadir a la URL
        :type params: Optional[Dict[str, Any]]
        :param headers: Headers HTTP adicionales a combinar con los por defecto.
                       Los headers personalizados tienen prioridad sobre los por defecto
        :type headers: Optional[Dict[str, str]]
        :param use_form_data: Si ``True``, envía datos como application/x-www-form-urlencoded.
                             Si ``False`` (por defecto), envía como application/json
        :type use_form_data: bool

        :return: Respuesta procesada del servidor. El tipo depende del endpoint:

                - **JWT tokens**: ``str`` (para endpoints de autenticación)
                - **Datos JSON**: ``Dict[str, Any]`` o ``List[Any]`` (para endpoints de datos)
                - **Respuestas de texto**: ``str`` (para endpoints que no devuelven JSON)

        :rtype: Union[Dict[str, Any], str, list]

        :raises DatadisError: Si se agotan todos los reintentos por errores de red/timeouts
        :raises AuthenticationError: Si hay errores de autenticación (401)
        :raises APIError: Si la API devuelve errores HTTP (400, 403, 404, 500, etc.)

        Example:
            Diferentes tipos de peticiones::

                # GET con parámetros de query
                response = client.make_request(
                    method="GET",
                    url="https://datadis.es/api-private/api/get-supplies",
                    params={"distributor_code": "2", "authorized_nif": "12345678A"}
                )

                # POST con autenticación (form-data)
                token = client.make_request(
                    method="POST",
                    url="https://datadis.es/nikola-auth/tokens/login",
                    data={"username": "12345678A", "password": "mi_password"},
                    use_form_data=True
                )

                # GET con headers personalizados
                response = client.make_request(
                    method="GET",
                    url="https://datadis.es/api-private/api/get-consumption-data",
                    params={"cups": "ES001234567890123456AB"},
                    headers={"Authorization": f"Bearer {token}"}
                )

        Note:
            El rate limiting automático (delay de 0.1s) se aplica a todas las peticiones
            excepto las de autenticación para evitar sobrecargar los servidores de Datadis
            que pueden tener límites de rate restrictivos.

        .. seealso::
           - :meth:`_handle_response` para detalles del procesamiento de respuestas
           - La normalización de texto se realiza automáticamente en respuestas JSON
        """
        # Rate limiting automático para evitar sobrecargar el servidor de Datadis
        # Excepción: endpoints de autenticación no necesitan delay
        if "/nikola-auth" not in url:
            time.sleep(0.1)  # Delay reducido pero efectivo

        # Intentar la petición con reintentos automáticos
        for attempt in range(self.retries + 1):
            try:
                # Configurar headers específicos para esta petición
                if headers:
                    request_headers = {**self.session.headers, **headers}
                else:
                    request_headers = dict(self.session.headers)

                # Ejecutar petición según el tipo de datos requerido
                if use_form_data and data:
                    # Para autenticación usar form-data (Content-Type: application/x-www-form-urlencoded)
                    response = requests.request(
                        method=method,
                        url=url,
                        data=data,  # Datos como formulario
                        params=params,
                        headers=request_headers,
                        timeout=self.timeout,
                    )
                else:
                    # Para peticiones normales usar JSON (Content-Type: application/json)
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,  # Datos como JSON
                        params=params,
                        timeout=self.timeout,
                    )

                # Procesar respuesta y retornar resultado
                return self._handle_response(response, url)

            except requests.RequestException as e:
                # Si es el último intento, propagar el error
                if attempt == self.retries:
                    raise DatadisError(
                        f"Error de conexión después de {self.retries + 1} intentos: {str(e)}"
                    )

                # Calcular tiempo de espera con backoff exponencial (máximo 10s)
                wait_time = min(10, (2**attempt) * 2)
                print(
                    f"⚠️  Intento {attempt + 1}/{self.retries + 1} falló. "
                    f"Reintentando en {wait_time}s... (Error: {str(e)})"
                )
                time.sleep(wait_time)

        # Este punto nunca debería alcanzarse debido a la lógica de reintentos,
        # pero se incluye para satisfacer el análisis estático de tipos
        raise DatadisError(
            "Error inesperado: se agotaron todos los reintentos sin lanzar excepción"
        )

    def _handle_response(
        self, response: requests.Response, url: str
    ) -> Union[Dict[str, Any], str, list]:
        """
        Procesa y maneja respuestas HTTP de la API de Datadis con lógica especializada.

        Este método interno procesa las respuestas HTTP aplicando lógica específica
        para diferentes tipos de endpoints de Datadis. Maneja tanto respuestas exitosas
        como errores, aplicando normalización de texto y conversión de tipos según sea necesario.

        Lógica de procesamiento por tipo de endpoint:
            - **Autenticación** (``/nikola-auth``): Retorna JWT token como string
            - **Datos JSON**: Parsea JSON y aplica normalización de caracteres especiales
            - **Respuestas de texto**: Retorna contenido raw como string
            - **Respuestas vacías**: Maneja respuestas sin contenido adecuadamente

        Manejo de errores HTTP:
            - **200 OK**: Procesamiento normal según tipo de contenido
            - **401 Unauthorized**: Error de autenticación (token inválido/expirado)
            - **429 Too Many Requests**: Rate limiting excedido
            - **4xx/5xx**: Otros errores HTTP con extracción de mensaje detallado

        Normalización de caracteres:
            Las respuestas JSON se procesan automáticamente para corregir problemas
            de encoding que son comunes en la API de Datadis (caracteres especiales
            españoles como ñ, ç, acentos, etc.).

        :param response: Objeto Response de requests con la respuesta HTTP
        :type response: requests.Response
        :param url: URL original de la petición (para contexto en logs/errores)
        :type url: str

        :return: Respuesta procesada según el tipo de endpoint:

                - **Token JWT**: ``str`` para endpoints de autenticación
                - **Datos estructurados**: ``Dict[str, Any]`` o ``List[Any]`` para datos
                - **Contenido de texto**: ``str`` para respuestas no-JSON

        :rtype: Union[Dict[str, Any], str, list]

        :raises AuthenticationError: Para errores 401 (credenciales inválidas/token expirado)
        :raises APIError: Para errores HTTP 4xx/5xx con código y mensaje detallado

        Example:
            Diferentes tipos de respuestas procesadas::

                # Autenticación → JWT token como string
                token_response = client._handle_response(auth_response, "/nikola-auth/tokens/login")
                # Resultado: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

                # Datos JSON → Dict/List normalizado
                supplies_response = client._handle_response(data_response, "/get-supplies")
                # Resultado: [{"cups": "ES001...", "address": "CALLE EJEMPLO"}, ...]

                # Error HTTP → Exception con detalles
                try:
                    client._handle_response(error_response, "/invalid-endpoint")
                except APIError as e:
                    print(f"Error {e.status_code}: {e.message}")

        Note:
            Este método es interno y normalmente no se llama directamente. Es invocado
            automáticamente por :meth:`make_request` para procesar todas las respuestas.

        .. seealso::
           - :func:`datadis_python.utils.text_utils.normalize_api_response` para normalización de texto
           - Documentación de la API de Datadis para códigos de error específicos
        """
        if response.status_code == 200:
            # Procesamiento exitoso - determinar tipo de respuesta

            if "/nikola-auth" in url:
                # Endpoints de autenticación retornan JWT token como texto plano
                return response.text.strip()

            # Para otros endpoints, intentar parsear como JSON
            try:
                json_response = response.json()
                # Aplicar normalización automática de caracteres especiales
                # Esta normalización es crucial para Datadis debido a problemas comunes
                # con caracteres españoles (ñ, acentos, ç, etc.)
                from ..utils.text_utils import normalize_api_response

                return normalize_api_response(json_response)

            except ValueError:
                # Si no es JSON válido, retornar como texto plano
                # Esto puede ocurrir en algunos endpoints legacy o en errores específicos
                return response.text

        elif response.status_code == 401:
            # Error de autenticación - credenciales inválidas o token expirado
            raise AuthenticationError(
                "Credenciales inválidas o token expirado. "
                "Verifique sus credenciales o reautentíquese."
            )

        elif response.status_code == 429:
            # Rate limiting - demasiadas peticiones
            raise APIError(
                "Límite de peticiones excedido. Reduzca la frecuencia de consultas.",
                429,
            )

        else:
            # Otros errores HTTP - extraer mensaje detallado si está disponible
            error_msg = f"Error HTTP {response.status_code}"

            try:
                # Intentar extraer mensaje de error del JSON de respuesta
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
                elif "error" in error_data:
                    error_msg = error_data["error"]
                elif "description" in error_data:
                    error_msg = error_data["description"]

            except ValueError:
                # Si no es JSON, usar el texto de respuesta si está disponible
                if response.text:
                    error_msg = response.text[
                        :200
                    ]  # Limitar longitud para evitar logs excesivos

            # Lanzar error con código de estado y mensaje detallado
            raise APIError(error_msg, response.status_code)

    def close(self) -> None:
        """
        Cierra la sesión HTTP y libera recursos asociados.

        Cierra explícitamente la sesión HTTP subyacente, liberando conexiones
        de red y otros recursos. Es una buena práctica llamar este método
        cuando se termina de usar el cliente, especialmente en aplicaciones
        de larga duración.

        Este método es seguro de llamar múltiples veces y no genera errores
        si la sesión ya está cerrada.

        Example:
            Uso manual de cierre::

                client = HTTPClient(timeout=120, retries=5)
                try:
                    # Usar cliente para peticiones...
                    response = client.make_request("GET", "https://example.com")
                finally:
                    # Asegurar limpieza de recursos
                    client.close()

            Uso como context manager (recomendado)::

                with HTTPClient(timeout=120, retries=5) as client:
                    # Usar cliente...
                    response = client.make_request("GET", "https://example.com")
                    # client.close() se llama automáticamente

        Note:
            Cuando se usa el cliente como context manager (``with`` statement),
            este método se llama automáticamente al salir del bloque, por lo
            que no es necesario llamarlo manualmente.
        """
        if self.session:
            self.session.close()

    def set_auth_header(self, token: str) -> None:
        """
        Establece el header de autorización Bearer Token para todas las peticiones futuras.

        Configura el token de autenticación que se añadirá automáticamente a todas
        las peticiones HTTP subsecuentes. Este método es típicamente llamado después
        de una autenticación exitosa para configurar el cliente para peticiones autenticadas.

        El token se almacena en los headers de la sesión persistent, por lo que se
        aplicará automáticamente a todas las peticiones realizadas con este cliente
        hasta que se reemplace con un nuevo token o se elimine.

        :param token: Token JWT obtenido del endpoint de autenticación de Datadis.
                     Debe ser un token válido sin el prefijo "Bearer " (se añade automáticamente)
        :type token: str

        Example:
            Configurar autenticación después del login::

                client = HTTPClient(timeout=120, retries=5)

                # Autenticar y obtener token
                token = client.make_request(
                    method="POST",
                    url="https://datadis.es/nikola-auth/tokens/login",
                    data={"username": "12345678A", "password": "mi_password"},
                    use_form_data=True
                )

                # Configurar token para peticiones futuras
                client.set_auth_header(token)

                # Ahora todas las peticiones incluirán el header Authorization
                response = client.make_request(
                    method="GET",
                    url="https://datadis.es/api-private/api/get-supplies"
                )

        Note:
            El token se prefija automáticamente con "Bearer " según el estándar RFC 6750.
            No incluya este prefijo en el parámetro ``token``.

        .. seealso::
           - :meth:`remove_auth_header` para eliminar la autenticación
           - RFC 6750 para especificación completa de Bearer Token
        """
        self.session.headers["Authorization"] = f"Bearer {token}"

    def remove_auth_header(self) -> None:
        """
        Elimina el header de autorización de todas las peticiones futuras.

        Remueve el token de autenticación de los headers de la sesión, haciendo que
        las peticiones subsecuentes se realicen sin autenticación. Esto es útil para
        limpiar credenciales cuando se cambia de usuario o cuando se quiere realizar
        peticiones no autenticadas.

        Esta operación es segura y no genera errores si no existe un header de
        autorización configurado.

        Example:
            Limpiar autenticación para cambio de usuario::

                # Usuario 1 autenticado
                client.set_auth_header(token_user1)
                data_user1 = client.make_request("GET", "/get-supplies")

                # Cambiar a usuario 2
                client.remove_auth_header()  # Limpiar credenciales anteriores
                token_user2 = client.make_request(
                    "POST", "/nikola-auth/tokens/login",
                    data={"username": "87654321B", "password": "other_password"},
                    use_form_data=True
                )
                client.set_auth_header(token_user2)
                data_user2 = client.make_request("GET", "/get-supplies")

            Peticiones sin autenticación::

                client.remove_auth_header()
                # Ahora las peticiones no incluirán Authorization header
                public_data = client.make_request("GET", "/public-endpoint")

        Note:
            Después de llamar este método, las peticiones a endpoints que requieren
            autenticación fallarán con error 401 hasta que se establezca un nuevo
            token con :meth:`set_auth_header`.

        .. seealso::
           - :meth:`set_auth_header` para establecer nuevo token de autenticación
        """
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    def __enter__(self):
        """
        Método de entrada para context manager.

        Permite usar el HTTPClient con la declaración ``with`` de Python para
        gestión automática de recursos. Al entrar en el bloque ``with``, retorna
        la instancia del cliente lista para usar.

        :return: La instancia del cliente HTTP configurada
        :rtype: HTTPClient

        Example:
            Uso como context manager::

                with HTTPClient(timeout=120, retries=5) as client:
                    # Configurar autenticación
                    token = client.make_request(
                        "POST", "/auth",
                        data={"user": "12345678A", "pass": "password"},
                        use_form_data=True
                    )
                    client.set_auth_header(token)

                    # Realizar peticiones
                    data = client.make_request("GET", "/api/data")

                # client.close() se llama automáticamente aquí

        Note:
            El uso como context manager es la forma recomendada de usar HTTPClient
            ya que garantiza la liberación adecuada de recursos de red.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método de salida para context manager.

        Se llama automáticamente al salir del bloque ``with``, garantizando que
        los recursos del cliente HTTP se liberen adecuadamente, independientemente
        de si el bloque se completó exitosamente o se produjo una excepción.

        :param exc_type: Tipo de excepción si ocurrió una excepción, None en caso contrario
        :param exc_val: Valor de la excepción si ocurrió una excepción, None en caso contrario
        :param exc_tb: Traceback de la excepción si ocurrió una excepción, None en caso contrario

        Note:
            Este método siempre retorna None, lo que significa que no suprime ninguna
            excepción que pueda haber ocurrido dentro del bloque ``with``. Las excepciones
            se propagan normalmente después de la limpieza de recursos.
        """
        self.close()
