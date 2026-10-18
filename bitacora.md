# 📓 Bitácora de Desarrollo — PJ-67 Kanban & Docs MCP

## 📌 Visión del Proyecto
Construir una alternativa autónoma, privada y sin costo de suscripción a herramientas como Trello y Notion, empaquetada en un único contenedor Docker para ejecutarse en una **Raspberry Pi** y accesible de forma segura a través de **Tailscale**. 

Además, incorpora soporte nativo para **Model Context Protocol (MCP)** sobre HTTP/SSE, permitiendo a asistentes de Inteligencia Artificial (Claude, Cursor, Antigravity) interactuar directamente con el tablero y la base de conocimiento personal.

---

## 🛠️ Decisiones de Arquitectura

### 1. ¿Por qué Raspberry Pi + Tailscale en lugar de Hosting Compartido?
- **Procesos persistentes para MCP:** Los servidores MCP remotos requieren conexiones HTTP/SSE de larga duración y listeners activos, difíciles o imposibles de mantener en hostings compartidos basados exclusivamente en PHP-FPM.
- **Privacidad estricta:** Al enrutar el tráfico mediante Tailscale, la instancia nunca se expone a internet público ni requiere abrir puertos en el router.
- **Optimización de recursos:** Se integra con **Traefik** como reverse proxy y **Sablier** para hibernación automática de contenedores cuando no se utilizan, liberando memoria RAM en la Raspberry Pi.

### 2. ¿Por qué SQLite como motor de persistencia?
- **Cero mantenimiento:** Base de datos embebida en un único archivo (`/data/kanban.db`).
- **Respaldo atómico trivial:** Permite hacer backups simples mediante copia de archivo o sincronización a almacenamiento secundario.
- **Rendimiento:** Excelente velocidad para lecturas y escrituras simultáneas en entornos personales o de equipo pequeño bajo modo WAL (`Write-Ahead Logging`).

### 3. ¿Por qué Model Context Protocol (MCP) vía SSE?
- **Protocolo Abierto:** Estandarizado por Anthropic para dotar a los LLMs de capacidades y contexto dinámico.
- **Transporte SSE (Server-Sent Events):** Permite exponer herramientas de gestión del tablero a través de la red local/Tailscale hacia clientes de IA remotos sin requerir accesos SSH ni comandos directos en la shell.
- **Desacoplamiento de Seguridad:** El agente solo tiene acceso a las herramientas declaradas (`create_task`, `list_tasks`, `search_notes`); el código ejecutable y las transacciones SQL son gobernadas enteramente por el servidor.

---

## 📅 Registro de Avances

### [Fase 1] — Inicialización y Definición del Stack
- [x] Creación de repositorio y estructura base.
- [x] Configuración de variables de entorno (`.env` y `.env.example`).
- [x] Definición de `dockerfile` multi-arquitectura (ARM64 para Raspberry Pi y AMD64).
- [x] Creación de documentación de portafolio (`Readme.md`).
- [x] Definición de modelos de datos (Tableros, Columnas, Tarjetas/Documentos, Tags).
- [x] Implementación de servidor FastAPI con endpoints REST y servidor MCP (SSE).
- [x] Interfaz web responsiva con drag & drop y editor Markdown estilo Notion.
- [x] Configuración de etiquetas para Traefik y Sablier en `docker-compose.yml`.

### [Fase 2] — Multi-Proyecto, Scrum, Wiki de Documentación y Monocromático
- [x] Soporte Multi-Proyecto (tablas `projects` y selector interactivo).
- [x] Metodología Scrum (Sprints, Story Points y Product Backlog).
- [x] Sección de Documentación Wiki (`project_docs` con Markdown).
- [x] Bitácora de Actualizaciones (`project_updates` / Changelog).
- [x] Dashboard de Métricas Scrum (Velocidad, Tasa de cumplimiento, KPIs).
- [x] Rediseño de interfaz monocromática profesional con iconos vectoriales SVG sin emojis.
- [x] Expansión del catálogo de tools MCP (13 herramientas para IA).

### [Fase 3] — Interfaz Jira AI-Native, Bootstrap 5 Local y Modo Claro/Oscuro
- [x] Descarga de Bootstrap 5.3.3, Marked y Mermaid directamente en `static/vendor/` para ejecución 100% offline dentro del contenedor.
- [x] Soporte nativo para alternancia de **Modo Claro / Modo Oscuro** con persistencia en `localStorage`.
- [x] Interfaz inspirada en Jira SDLC con IA (Atlassian Rovo style):
  - Tablero Kanban con creación rápida en línea (`+ What needs to be done?`).
  - Asignación de Agentes de IA (`Claude Agent`, `Cursor`, `Figma Agent`, `Rich`).
  - Vista jerárquica de **Work items** por Fases con dependencias.
  - Vista **Technical Plan** con renderizado de diagramas de arquitectura Mermaid.
  - Panel lateral colapsable **AI Planner** conectado al servidor MCP para sugerir tareas y chatear con la IA.
