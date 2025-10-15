## Asunto: Incidencia API v2: Imposibilidad de obtener consumos para CUPS de terceros

**Cuerpo del Mensaje:**

Estimado equipo de soporte de Datadis,

Les escribo en representación del Instituto Tecnológico de Canarias (ITC) para informar de una incidencia que hemos detectado realizando llamadas directas a su API v2.

El problema es el siguiente: no estamos logrando obtener los datos de consumo horario para suministros de terceros autorizados.

El flujo que seguimos es el siguiente:
1.  Realizamos una petición `GET` al endpoint `/api-private/api/get-supplies-v2` utilizando el NIF de un cliente que nos ha autorizado. La llamada es exitosa y nos devuelve correctamente los datos de su suministro (CUPS, distribuidora, etc.).
2.  A continuación, con los datos obtenidos, realizamos una petición `GET` al endpoint `/api-private/api/get-consumption-data-v2` para ese mismo CUPS. La API responde con un código de estado 200 (OK), pero el array `timeCurve` en la respuesta JSON llega sistemáticamente vacío.

Queremos aclarar que las llamadas a ese mismo endpoint de consumo (`get-consumption-data-v2`) para nuestros CUPS propios (asociados a nuestro CIF de empresa) funcionan perfectamente, devolviendo los datos de consumo esperados.

El problema parece estar específicamente en la obtención de consumos para CUPS de terceros, a pesar de que la autorización para consultar sus datos de contrato es correcta.

Esta incidencia nos impide avanzar en la integración de servicios para nuestros clientes. Hemos documentado un caso de prueba detallado con las llamadas exactas y las respuestas obtenidas. Si nos facilitan un correo electrónico, podemos compartirlo para ayudarles a diagnosticar el problema.

Agradecemos su tiempo y quedamos a la espera de su respuesta.

Un saludo cordial,

[Tu Nombre/Departamento]
Instituto Tecnológico de Canarias (ITC)
