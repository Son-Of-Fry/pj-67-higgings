# Higgings (PJ-67) - AI-Native Agile Management Platform & MCP Server

Plataforma de ingenieria y productividad agil inspirada en metodologias Scrum y SDLC moderno, empaquetada en un unico contenedor Docker para despliegue local o en Raspberry Pi, con Bootstrap 5 offline, persistencia en SQLite (WAL mode), soporte multi-proyecto con enlaces directos a GitHub, documentacion central Home/README editable en Markdown y servidor Model Context Protocol (MCP) nativo con 20 herramientas para agentes de Inteligencia Artificial.

---

## 1. Vision y Proposito

Las soluciones comerciales de gestion de proyectos (Jira, Linear, Monday, Notion) presentan dos inconvenientes principales en entornos de ingenieria independientes:

1. **Costos recurrentes y dependencia de la nube:** Tarifas mensuales por usuario con caracteristicas avanzadas bloqueadas tras suscripciones enterprise.
2. **Desconexion con agentes autonomos de IA:** Ausencia de una interfaz estandarizada y segura para que modelos de lenguaje (LLMs) inspeccionen el backlog, planifiquen sprints, actualicen estados de tareas y lean documentacion tecnica directamente sobre la infraestructura propia.

**Higgings** resuelve este reto mediante una solucion autoalojada y autocontenida que une la agilidad de Scrum con el estandar abierto **Model Context Protocol (MCP)**.

---

## 2. Principios de Diseno y Metodologia Scrum

### Product Backlog Integrado en el Tablero Kanban
Para maximizar la visibilidad y facilitar la priorización ágil:
- **Columna 0 - Backlog (Ideas):** Integrada directamente al inicio del tablero Kanban (`sprint_id IS NULL`). Permite registrar ideas y requerimientos rápidamente sin asignarlos aún al sprint.
- **Columnas de Sprint Activo:** Flujo de ejecución del sprint compuesto por *Por Hacer*, *En Progreso*, *En Revisión* y *Terminado*.
- **Transición fluida por Drag & Drop:** Arrastrar una tarjeta desde *Backlog (Ideas)* a *Por Hacer* la compromete inmediatamente en el sprint activo. Arrastrar de vuelta al backlog la libera del sprint.

### Soporte Multi-Proyecto y Enlaces a GitHub
- Cada proyecto cuenta con un tablero Kanban, backlog, changelog y metricas independientes.
- **Campo de repositorio GitHub:** Cada proyecto almacena su `github_url` en base de datos SQLite y expone un enlace directo en la barra superior de navegacion, permitiendo saltar al codigo fuente del repositorio asociado con un solo clic.

### Home / README Editable en Markdown
- Cada proyecto cuenta con su propia vista **Home (Readme)** que renderiza la documentación técnica y lineamientos del proyecto directamente en Markdown.
- Cuenta con un modo de edición integrado en la interfaz web para modificarlo en cualquier momento.
- Puede ser consultado y modificado por agentes de IA mediante las herramientas MCP `get_project_readme` y `update_project_readme`.

---

## 3. Arquitectura del Sistema

```
                      +----------------------------------------+
                      |            Red Privada                 |
                      |        Tailscale / VPN Local           |
                      +-------------------+--------------------+
                                          |
                                          v
                      +----------------------------------------+
                      |          Reverse Proxy                 |
                      |        Traefik / Sablier               |
                      |     (Wake-on-demand en host)           |
                      +-------------------+--------------------+
                                          |
                                          v
      +-----------------------------------------------------------------+
      |                 Contenedor Docker (Higgings)                     |
      |                                                                 |
      |   [ Web UI ]            [ API REST ]         [ Servidor MCP ]   |
      |  Bootstrap 5           FastAPI Core             Transporte      |
      |  Vanilla JS            16 Endpoints          Server-Sent Events |
      |  (Offline)             Scrum & Backlog           (/sse, /mcp)   |
      |        |                     |                       |          |
      |        +---------------------+-----------------------+          |
      |                              |                                  |
      |                              v                                  |
      |                [ Base de Datos SQLite (WAL) ]                   |
      |                      /data/kanban.db                            |
      +-----------------------------------------------------------------+
```

---

## 4. Servidor Model Context Protocol (MCP)

El **Model Context Protocol (MCP)** es el estandar abierto desarrollado por Anthropic para la comunicacion segura y bidireccional entre clientes de IA (Claude Desktop, Cursor, Antigravity) y servidores de contexto.

Higgings expone 18 herramientas especializadas a traves del endpoint SSE (`/sse`):

| Herramienta | Proposito | Parametros Principales |
| :--- | :--- | :--- |
| `list_projects` | Lista todos los proyectos con su sprint activo y conteo de tareas. | Ninguno |
| `get_project` | Retorna la informacion, descripcion y URL de GitHub de un proyecto. | `project_id` |
| `create_project` | Crea un proyecto nuevo con columnas Kanban por defecto y Sprint 1. | `name`, `description`, `github_url` |
| `get_board_state` | Retorna el estado completo del tablero de un proyecto y sprint. | `project_id`, `sprint_id` |
| `get_board_summary` | Resumen numerico rapido de tareas por columna y backlog. | `project_id` |
| `get_task` | Consulta el detalle completo de una tarea especifica. | `task_id` |
| `create_task` | Crea una tarea o historia de usuario asignada a un agente o humano. | `project_id`, `title`, `column_id`, `story_points`, `assignee`, `phase`, `priority` |
| `batch_create_tasks` | Creacion masiva de multiples tareas en una sola transaccion. | `project_id`, `tasks` (array) |
| `update_task` | Modifica cualquier atributo de una tarea existente. | `task_id`, campos a actualizar |
| `update_task_status` | Transiciona una tarea a una nueva columna (ej. Por Hacer -> En Progreso). | `task_id`, `column_name` |
| `delete_task` | Elimina una tarea por su identificador. | `task_id` |
| `list_sprints` | Lista el historial de sprints de un proyecto con sus puntos acumulados. | `project_id` |
| `create_sprint` | Planifica y apertura un nuevo sprint con objetivo y puntos meta. | `project_id`, `name`, `goal`, `target_points` |
| `complete_sprint` | Cierra el sprint activo marcandolo como completado. | `sprint_id` |
| `log_project_release` | Registra una version en la bitacora de entregas (Changelog). | `project_id`, `version_tag`, `title`, `content_markdown` |
| `list_releases` | Consulta las notas de version historicas de un proyecto. | `project_id` |
| `get_project_metrics` | Obtiene metricas de velocidad, cumplimiento y carga por miembro. | `project_id` |
| `search_tasks` | Busqueda por texto libre en titulos, descripciones y tags. | `project_id`, `query` |
| `get_project_readme` | Obtiene el contenido Markdown del documento Home / README del proyecto. | `project_id` |
| `update_project_readme` | Modifica el contenido Markdown del Home / README desde un agente MCP. | `project_id`, `readme_markdown` |

---

## 5. Requisitos y Despliegue con Docker

### Requisitos Previos
- Docker Engine 20.10+ o Docker Desktop.
- Arquitectura compatible: AMD64 o ARM64 (Raspberry Pi 4 / 5, servidores Linux, macOS o Windows).

### Variables de Entorno (.env)
El sistema cuenta con valores predeterminados listos para funcionar sin configuración previa. Si deseas personalizar puertos, tokens o rutas, copia la plantilla `.env.example`:

```bash
cp .env.example .env
```

Parámetros configurables en `.env`:
- `DATABASE_URL`: Conexión de base de datos (por defecto: `sqlite:////data/kanban.db`).
- `API_AUTH_TOKEN`: Token de autorización Bearer opcional para clientes MCP externos.
- `PORT`: Puerto interno de escucha de FastAPI (por defecto: `8000`).
- `ALLOWED_ORIGINS`: Dominios o IPs permitidas para CORS (por defecto: `*`).

> **Nota sobre `.dockerignore` vs `.env` en tiempo de ejecución:**
> El archivo `.dockerignore` **solo actúa al compilar la imagen** (`docker build`) para evitar que tu `.env` con contraseñas o tokens quede grabado permanentemente en las capas de la imagen. Al ejecutar el contenedor (`docker run`), tus variables se inyectan dinámicamente desde el directorio local `$(pwd)` usando la bandera `--env-file .env` o mediante Docker Compose.

### Construccion y Ejecucion del Contenedor

Para construir la imagen Docker localmente:

```bash
docker build -t higgings-platform -f dockerfile .
```

Para arrancar el contenedor en segundo plano con persistencia y variables montadas desde el directorio local actual (`$(pwd)`):

> **Respaldo y Portabilidad:** Al montar el volumen persistente como `$(pwd)/data`, la base de datos SQLite reside directamente en tu carpeta de trabajo. Esto simplifica los respaldos (basta con copiar o respaldar `./data`), facilita migraciones rápidas y asegura que los datos no se borren si el contenedor se reconstruye o detiene.

```bash
docker run -d \
  --name higgings-platform \
  -p 28945:8000 \
  --env-file .env \
  -v "$(pwd)/data":/data \
  --restart unless-stopped \
  higgings-platform
```

### Accesos Disponibles
- **Interfaz Web Higgings:** `http://localhost:28945`
- **Documentacion Interactiva Swagger API:** `http://localhost:28945/docs`
- **Endpoint MCP (SSE):** `http://localhost:28945/sse`

---

## 6. Configuracion en Clientes MCP

### Claude Desktop
Edita el archivo de configuracion `claude_desktop_config.json`:
- En macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- En Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "higgings": {
      "url": "http://localhost:28945/sse",
      "headers": {
        "Authorization": "Bearer your_secure_mcp_token_here"
      }
    }
  }
}
```

### Cursor
En la configuracion de Cursor (Settings -> Features -> MCP):
1. Anadir nuevo servidor MCP.
2. Nombre: `Higgings`
3. Tipo: `SSE`
4. URL: `http://localhost:28945/sse`

---

## 7. Estructura del Repositorio

```
.
|-- Readme.md                 # Documentacion general del sistema (sin iconos)
|-- dockerfile                # Definicion multi-stage de compilacion y ejecucion
|-- docker-compose.yml        # Orquestacion rapida con volumenes montados
|-- requirements.txt          # Dependencias Python (FastAPI, uvicorn, pydantic)
|-- src/                      # Codigo fuente backend
|   |-- main.py               # Punto de entrada FastAPI y montaje de estaticos
|   |-- config.py             # Configuracion centralizada y variables de entorno
|   |-- database.py           # Capa de datos SQLite en modo WAL y migraciones
|   |-- models.py             # Esquemas Pydantic v2
|   |-- mcp_server.py         # Servidor MCP y catalogo de 18 herramientas
|   `-- api/
|       `-- routes.py         # Rutas de la API REST para Kanban, Sprints y Backlog
`-- static/                   # Recursos frontend (Vanilla JS + Bootstrap 5 local)
    |-- index.html            # Interfaz principal de Higgings
    |-- css/
    |   `-- style.css         # Estilos dark/light mode y diseno tipo Atlassian
    |-- js/
    |   `-- app.js            # Logica de interaccion, drag & drop y gestion de vistas
    `-- vendor/               # Dependencias empaquetadas offline (Bootstrap, Marked)
```

---

## 8. Roadmap y Actualizaciones Futuras de Seguridad

Plan de mitigación y endurecimiento (hardening) de seguridad:

1. **Restricción Estricta de CORS:** Limitar `allow_origins` exclusivamente a los orígenes autorizados (`http://localhost:28945` o tu host seguro de red), eliminando el comodín abierto para prevenir ataques cross-site desde páginas externas en el navegador.
2. **Capa de Autenticación Interna (Zero-Trust):** Activar validación de token Bearer en el middleware de FastAPI para endpoints destructivos (`POST`, `PUT`, `DELETE`) y el servidor MCP, blindando el acceso contra dispositivos no autorizados en la Tailnet.
3. **Sanitización de Markdown contra XSS:** Integrar `DOMPurify` en el renderizado cliente de Markdown (`marked.parse`) para evitar inyección de scripts almacenados en bitácoras o documentos.
4. **Principio de Menor Privilegio en Docker:** Crear y declarar un usuario no privilegiado (`USER 1000:1000`) en el Dockerfile, evitando ejecutar el proceso Uvicorn como `root` con acceso de escritura al host.
5. **Aislamiento Estricto de Sesiones MCP:** Exigir `session_id` obligatorio en `/messages` y rechazar peticiones huérfanas con HTTP 400 para prevenir cruces o interceptación de eventos entre agentes concurrentes.

---

## 9. Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para mas detalles.
