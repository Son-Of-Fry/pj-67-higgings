import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.config import settings

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.sqlite_db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Migración automática si existe una base de datos con el esquema de la v1
            cursor.execute("PRAGMA table_info(columns)")
            col_info = [r["name"] for r in cursor.fetchall()]
            if col_info and "project_id" not in col_info:
                cursor.execute("DROP TABLE IF EXISTS tasks")
                cursor.execute("DROP TABLE IF EXISTS columns")
                cursor.execute("DROP TABLE IF EXISTS boards")
                cursor.execute("DROP TABLE IF EXISTS sprints")
                cursor.execute("DROP TABLE IF EXISTS project_docs")
                cursor.execute("DROP TABLE IF EXISTS project_updates")
                conn.commit()

            # 1. Proyectos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                github_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Sprints (Scrum)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                goal TEXT DEFAULT '',
                start_date TEXT DEFAULT '',
                end_date TEXT DEFAULT '',
                status TEXT DEFAULT 'active', -- planned, active, completed
                target_points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            );
            """)

            # 3. Columnas del Tablero Kanban por proyecto
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            );
            """)

            # 4. Tareas (Historias de usuario / Tareas Scrum)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                column_id INTEGER NOT NULL,
                sprint_id INTEGER, -- NULL indica que está en el Product Backlog
                title TEXT NOT NULL,
                description TEXT DEFAULT '', -- Markdown
                priority TEXT DEFAULT 'medium',
                story_points INTEGER DEFAULT 1,
                assignee TEXT DEFAULT 'Claude Agent',
                phase TEXT DEFAULT 'Phase 1',
                dependency TEXT DEFAULT '',
                position INTEGER NOT NULL,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (column_id) REFERENCES columns (id) ON DELETE CASCADE,
                FOREIGN KEY (sprint_id) REFERENCES sprints (id) ON DELETE SET NULL
            );
            """)

            # Migración automática de columnas para bases existentes
            cursor.execute("PRAGMA table_info(tasks)")
            task_col_names = [r["name"] for r in cursor.fetchall()]
            if task_col_names:
                if "assignee" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN assignee TEXT DEFAULT 'Claude Agent'")
                if "phase" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN phase TEXT DEFAULT 'Phase 1'")
                if "dependency" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN dependency TEXT DEFAULT ''")
                conn.commit()

            # Migración automática de projects para columna github_url y readme_markdown
            cursor.execute("PRAGMA table_info(projects)")
            proj_col_names = [r["name"] for r in cursor.fetchall()]
            if proj_col_names and "github_url" not in proj_col_names:
                cursor.execute("ALTER TABLE projects ADD COLUMN github_url TEXT DEFAULT ''")
                cursor.execute("UPDATE projects SET github_url = 'https://github.com/rich/huggins-tutorial' WHERE name LIKE '%PJ-00%'")
                cursor.execute("UPDATE projects SET github_url = 'https://github.com/rich/huggins-pj67' WHERE name LIKE '%PJ-67%'")
                cursor.execute("UPDATE projects SET github_url = 'https://github.com/rich/retail-mlops' WHERE name LIKE '%PJ-65%'")
                conn.commit()

            if proj_col_names and "readme_markdown" not in proj_col_names:
                cursor.execute("ALTER TABLE projects ADD COLUMN readme_markdown TEXT DEFAULT ''")
                p0_readme = """# Guía del Proyecto (README)

Bienvenido a la documentación principal del proyecto.

Este documento está escrito en formato **Markdown** y puedes editarlo en cualquier momento haciendo clic en el botón **Editar Readme**.

---

### Objetivos y Alcance
- **Flujo Scrum Visual:** Tablero ágil con Story Points, estimaciones y fases.
- **Product Backlog Integrado:** Columna 0 para incubar y refinar ideas antes de comprometerlas al sprint.
- **Soporte MCP para IA:** Permite a Claude Desktop o Cursor inspeccionar historias y modificar este README automáticamente.

---

### Herramientas MCP Disponibles
- `get_project_readme`: Obtiene el contenido de este README.
- `update_project_readme`: Actualiza el contenido de este README directamente desde un agente.
"""
                cursor.execute("UPDATE projects SET readme_markdown = ? WHERE name LIKE '%PJ-00%'", (p0_readme,))
                conn.commit()

            # 5. Documentación Wiki del Proyecto
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                content_markdown TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            );
            """)

            # 6. Bitácora de Actualizaciones (Changelog / Releases)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                sprint_id INTEGER,
                version_tag TEXT DEFAULT 'v1.0.0',
                title TEXT NOT NULL,
                content_markdown TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (sprint_id) REFERENCES sprints (id) ON DELETE SET NULL
            );
            """)

            # 7. Bitácora Interactiva tipo Notebook Markdown
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bitacora_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT DEFAULT '',
                content_markdown TEXT NOT NULL,
                entry_date TEXT DEFAULT '',
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            );
            """)

            conn.commit()

            # Semilla inicial para Bitácora si está vacía
            cursor.execute("SELECT COUNT(*) FROM bitacora_entries")
            if cursor.fetchone()[0] == 0:
                self._seed_bitacora_entries(cursor)
                conn.commit()

            # Semilla inicial si no hay proyectos
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                self._seed_tutorial_project(cursor)
                self._seed_initial_data(cursor)
                conn.commit()
            else:
                # Si ya existen proyectos pero falta PJ-00 Tutorial, agregarlo al inicio
                cursor.execute("SELECT COUNT(*) FROM projects WHERE name LIKE '%PJ-00%'")
                if cursor.fetchone()[0] == 0:
                    self._seed_tutorial_project(cursor)
                    conn.commit()

    def _seed_tutorial_project(self, cursor: sqlite3.Cursor):
        # Proyecto 0: PJ-00 Tutorial (Onboarding)
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-00 Tutorial", "Proyecto interactivo de bienvenida y tutorial guiado para aprender el flujo Scrum, gestión ágil y conexión con agentes MCP.", "https://github.com/rich/huggins-tutorial")
        )
        p0_id = cursor.lastrowid

    def _seed_bitacora_entries(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT id, name FROM projects")
        projects = {row["name"]: row["id"] for row in cursor.fetchall()}

        pj67_id = None
        pj65_id = None
        pj00_id = None
        for name, pid in projects.items():
            if "PJ-67" in name or "Huggins" in name:
                pj67_id = pid
            elif "PJ-65" in name:
                pj65_id = pid
            elif "PJ-00" in name:
                pj00_id = pid

        pj67_entry = """**Proyecto:**  
PJ-67 (Huggins — AI-Native Agile Management Platform & MCP Server)

**Actividades:**  
Integración y despliegue de servidor MCP SSE nativo en Docker sobre Raspberry Pi vía Tailscale, Product Backlog en el tablero, Home (README) interactivo y soporte de Scale-to-Zero con Sablier y Traefik.

**Herramientas/IA:**  
FastAPI, SQLite (modo WAL), Bootstrap 5, Vanilla JS, Marked.js, Docker, Traefik, Sablier, Claude Desktop, Cursor y Antigravity AI.

**Aprendí:**  
Los clientes MCP en Go (como Antigravity) envían `POST` directo a `/sse` sin `session_id`, mientras que Claude Desktop sigue el flujo de dos canales hacia `/messages?session_id=...`. Responder en ambos canales garantiza compatibilidad universal.

**Resultado:**  
Plataforma completa operativa en `:28945`, con persistencia SQLite, Scale-to-Zero (0 MB RAM en reposo), Home (README) dinámico y catálogo de 20 herramientas MCP probadas exitosamente desde Antigravity y Claude.

**Siguiente:**  
Fase 4: Bitácora interactiva tipo Notebook Markdown por proyecto y carga masiva de proyectos desde Excel."""

        pj65_entry = """**Proyecto:**  
PJ-65 (Retail Dynamic Pricing & Automated Valuation System)

**Actividades:**  
Integración y despliegue de DVC y MLflow en Docker sobre Raspberry Pi vía Tailscale, versionado del dataset en Fase 1 y registro de modelos en Fase 2.

**Herramientas/IA:**  
DVC (dvc-ssh), MLflow, Docker, Tailscale, Streamlit, LightGBM, Python, Jupyter y Antigravity AI.

**Aprendí:**  
DVC desacopla datos pesados de Git usando punteros `.dvc` (hashes MD5) hacia almacenamiento remoto, y MLflow gestiona experimentos requiriendo configuración CORS para accesos remotos vía FastAPI.

**Resultado:**  
Dataset de 1M de filas (38.75 MB) respaldado en la Raspberry Pi con Dashboard interactivo en Streamlit, y 2 modelos LightGBM con métricas y SHAP registrados en MLflow.

**Siguiente:**  
Fase 3: Implementar reglas de salvaguarda financiera (costo + CAC + margen mínimo) y schemas Pydantic v2 en la API de inferencia."""

        now_str = "2026-10-17 19:30:00"

        if pj67_id:
            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pj67_id, "Despliegue inicial Huggins & Servidor MCP con Scale-to-Zero", pj67_entry, "2026-10-17", 1, now_str, now_str))

        if pj65_id:
            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pj65_id, "Integración DVC + MLflow & Modelado Fase 2", pj65_entry, "2026-10-17", 1, now_str, now_str))

        if pj00_id:
            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pj00_id, "Despliegue inicial Huggins & Servidor MCP con Scale-to-Zero", pj67_entry, "2026-10-17", 1, now_str, now_str))

        # Columnas estándar
        columns = [("Por Hacer", 1), ("En Progreso", 2), ("En Revisión", 3), ("Terminado", 4)]
        col_ids = {}
        for title, pos in columns:
            cursor.execute(
                "INSERT INTO columns (project_id, title, position) VALUES (?, ?, ?)",
                (p0_id, title, pos)
            )
            col_ids[title] = cursor.lastrowid

        # Sprint 1 Tutorial
        now = datetime.utcnow().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO sprints (project_id, name, goal, start_date, end_date, status, target_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (p0_id, "Sprint 1 — Onboarding & Tour", "Comprender las vistas Scrum, estimación de Story Points y uso de agentes de IA", now, now, "active", 14))
        sprint_id = cursor.lastrowid

        # Tareas Tutorial
        t1_desc = """### 👋 ¡Hola! Te damos la bienvenida a tu plataforma de proyectos
Esta herramienta está inspirada en **Jira + Confluence** con soporte nativo para agentes de Inteligencia Artificial mediante **Model Context Protocol (MCP)**.

#### 🎯 ¿Cómo usar este tablero?
1. **Arrastra y suelta (Drag & Drop):** Toma cualquier tarjeta y muévela entre columnas para cambiar su estado en tiempo real.
2. **Creación rápida:** En la parte superior de cada columna escribe una tarea en `+ What needs to be done?` y presiona **Enter**.
3. **Edición completa:** Haz clic sobre cualquier tarjeta para editar su descripción en Markdown, asignar un agente (Claude, Cursor, Rich), definir puntos de historia y fase de entrega."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Terminado"], sprint_id,
            "¡Bienvenido a PJ-67! Conoce el flujo Scrum & MCP",
            t1_desc, "medium", 1, "Rich (Humano)", "Phase 1", 1, json.dumps(["Bienvenida", "Tutorial"])
        ))

        t2_desc = """### Conoce cada una de las 4 vistas disponibles:

- **Tablero (Board):** Tablero Kanban visual con Product Backlog integrado, columnas de flujo ágil y soporte para drag & drop.
- **Work items (Lista):** Vista en lista jerárquica organizada por fases (Phase 1, Phase 2, Phase 3) para seguimiento detallado.
- **Releases & Updates:** Registro histórico de entregas, notas de versión y retrospectivas de cada sprint.
- **Métricas del Proyecto:** Métricas generales del proyecto, velocidad de sprint, tasa de cumplimiento y distribución por responsable."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Terminado"], sprint_id,
            "Navega por las 4 pestañas del proyecto",
            t2_desc, "low", 2, "Claude Agent", "Phase 1", 2, json.dumps(["Navegación", "Guía"])
        ))

        t3_desc = """### 🤖 Conexión con Agentes de Inteligencia Artificial
El servidor MCP de PJ-67 corre en segundo plano y expone el protocolo oficial por **Server-Sent Events (SSE)** en el puerto `28945`.

#### Configuración para Claude Desktop:
Agrega esto en tu archivo `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "pj67-scrum": {
      "url": "http://localhost:28945/sse"
    }
  }
}
```

#### ¿Qué puede hacer el agente con las herramientas MCP?
- `get_board_state`: Leer las columnas, sprints y tareas actuales.
- `create_task`: Crear nuevas historias con story points, fase y tags.
- `move_task_column`: Mover historias a 'En Progreso' o 'Terminado' tras codificar.
- `update_technical_plan`: Escribir o actualizar la wiki de arquitectura."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["En Progreso"], sprint_id,
            "Conectar Claude Desktop o Cursor al Servidor MCP",
            t3_desc, "high", 3, "Claude Agent", "Phase 2", 1, json.dumps(["MCP", "IA", "SSE"])
        ))

        t4_desc = """### 📐 Metodología Scrum: Story Points
Los Story Points miden el esfuerzo y complejidad relativa de una tarea (usando la escala Fibonacci: 1, 2, 3, 5, 8, 13).

- **1-2 pts:** Tareas triviales o ajustes rápidos de UI/texto.
- **3-5 pts:** Features con lógica de backend o componentes nuevos.
- **8-13 pts:** Módulos complejos que convendría desglosar en subtareas.

*Los puntos completados alimentan automáticamente el cálculo de velocidad en la pestaña **DX & AI Metrics**.*"""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Por Hacer"], sprint_id,
            "Estimar historias con Story Points (Fibonacci)",
            t4_desc, "medium", 5, "Rich (Humano)", "Phase 2", 1, json.dumps(["Scrum", "Estimación"])
        ))

        t5_desc = """### 📁 Soporte Multi-Proyecto
Puedes gestionar tantos proyectos como necesites:
1. Haz clic en el botón `+` junto al selector de proyecto en la barra superior.
2. Ingresa el nombre de tu nuevo proyecto (ej. `Sistema de Facturación`, `App Móvil`).
3. El nuevo proyecto tendrá su propio tablero, sprints, wiki de documentación y changelog independientes."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Por Hacer"], sprint_id,
            "Crear tu primer proyecto real con el botón '+'",
            t5_desc, "medium", 3, "Cursor", "Phase 3", 2, json.dumps(["Multi-Proyecto"])
        ))

        # Wiki inicial para el tutorial
        wiki_md = """# 📚 Manual de Inicio Rápido & Arquitectura — PJ-00

¡Bienvenido a la plataforma ágil PJ-67! Esta guía explica cómo trabajar en tus proyectos combinando metodologías ágiles (Scrum) y agentes autónomos de IA mediante MCP.

## 🔄 Ciclo de Desarrollo Ágil Asistido por IA

```mermaid
graph TD
    A[💡 Idea de Negocio / Feature] --> B[📐 Redactar Technical Plan]
    B --> C[📑 Desglosar en Work Items & Fases]
    C --> D[📋 Sprint Backlog & Estimación]
    D --> E[🤖 Claude Agent / Cursor: Implementación]
    E --> F[🧪 Pruebas & Revisión]
    F --> G[🚀 Release en Changelog]
    G --> H[📊 Análisis de Métricas DX]
```

## 🛠️ Buenas Prácticas Recomendadas

1. **Fases Claras:** Organiza tu trabajo en `Phase 1` (Arquitectura & Core), `Phase 2` (Features Principales) y `Phase 3` (Hardening & Releases).
2. **Story Points Realistas:** No sobrecargues un sprint; la suma de puntos objetivo debe rondar entre 13 y 21 puntos para mantener un ritmo sostenible.
3. **Documentación Viva:** Mantén este documento actualizado; los agentes MCP leen este plan técnico para proponer tareas coherentes con tus requerimientos.

---
*Nota: Puedes editar este documento en cualquier momento haciendo clic en el botón **Editar Plan**.*"""

        cursor.execute("""
            INSERT INTO project_docs (project_id, title, category, content_markdown)
            VALUES (?, ?, ?, ?)
        """, (p0_id, "Guía Rápida & Arquitectura — Tutorial PJ-00", "Guía", wiki_md))

        # Actualización de release en Changelog
        update_md = """### 🎉 Bienvenido al Proyecto Tutorial PJ-00
- Tablero Kanban preconfigurado con ejemplos de tareas y flujo ágil.
- Soporte completo para asignación a agentes de IA (`Claude Agent`, `Cursor`) y humanos (`Rich`).
- Configuración lista para conectar agentes externos mediante el protocolo MCP (SSE)."""

        cursor.execute("""
            INSERT INTO project_updates (project_id, sprint_id, version_tag, title, content_markdown)
            VALUES (?, ?, ?, ?, ?)
        """, (p0_id, sprint_id, "v0.1.0-tutorial", "Lanzamiento del Proyecto Tutorial", update_md))

    def _seed_initial_data(self, cursor: sqlite3.Cursor):
        # Proyecto 1: PJ-67
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-67 Platform", "Sistema autónomo de gestión ágil de proyectos con Scrum y Model Context Protocol", "https://github.com/rich/huggins-pj67")
        )
        p1_id = cursor.lastrowid

        # Proyecto 2: PJ-65
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-65 Retail MLOps", "Motor de pricing dinámico con DVC, MLflow y salvaguarda financiera", "https://github.com/rich/retail-mlops")
        )

        # Columnas estándar para PJ-67
        columns = [("Por Hacer", 1), ("En Progreso", 2), ("En Revisión", 3), ("Terminado", 4)]
        col_ids = {}
        for title, pos in columns:
            cursor.execute(
                "INSERT INTO columns (project_id, title, position) VALUES (?, ?, ?)",
                (p1_id, title, pos)
            )
            col_ids[title] = cursor.lastrowid

        # Sprint 1
        now = datetime.utcnow().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO sprints (project_id, name, goal, start_date, end_date, status, target_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (p1_id, "Sprint 1 — Core & MCP", "Construir motor Scrum, Documentación Wiki y servidor MCP", now, now, "active", 13))
        sprint1_id = cursor.lastrowid

        # Tareas del Sprint
        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p1_id, col_ids["Terminado"], sprint1_id,
            "Diseñar arquitectura SQLite y Docker",
            "### Resumen de Entrega\n* SQLite en WAL mode.\n* Dockerfile multi-arquitectura.",
            "high", 3, "Claude Agent", "Phase 1", 1, json.dumps(["DevOps", "Docker"])
        ))

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p1_id, col_ids["En Progreso"], sprint1_id,
            "Implementar soporte Multi-Proyecto y Scrum",
            "### Requerimientos\n1. Sprints con Story Points.\n2. Product Backlog independiente.\n3. Wiki de Documentación.",
            "urgent", 5, "Cursor", "Phase 2", 1, json.dumps(["Scrum", "FastAPI"])
        ))

        # Tarea en Backlog (sprint_id = None)
        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p1_id, col_ids["Por Hacer"],
            "Integrar gráficos avanzados de métricas con Canvas",
            "Requisito futuro para proyectar la velocidad de sprints históricos.",
            "low", 2, "Rich (Humano)", "Phase 3", 1, json.dumps(["Frontend", "UI"])
        ))

        # Documento inicial de Wiki
        wiki_md = """# 📚 Arquitectura del Sistema PJ-67

Bienvenido a la Wiki de documentación interna del proyecto.

## Componentes Técnicos
* **Backend:** FastAPI asíncrono sirviendo APIs REST y SSE.
* **Persistencia:** SQLite con modo WAL y transacciones atómicas.
* **MCP Server:** Transporte Server-Sent Events exponiendo herramientas de control Scrum a la IA.
* **Frontend:** Vanilla JS reactivo, CSS monocromático moderno sin frameworks pesados.
"""
        cursor.execute("""
            INSERT INTO project_docs (project_id, title, category, content_markdown)
            VALUES (?, ?, ?, ?)
        """, (p1_id, "Arquitectura del Sistema", "Arquitectura", wiki_md))

        # Actualización inicial en Changelog
        update_md = """### 🚀 Lanzamiento v1.0.0
- Configuración de persistencia en SQLite.
- Integración de servidor MCP con protocolo SSE oficial.
- Despliegue en contenedor Docker sin dependencias externas.
"""
        cursor.execute("""
            INSERT INTO project_updates (project_id, sprint_id, version_tag, title, content_markdown)
            VALUES (?, ?, ?, ?, ?)
        """, (p1_id, sprint1_id, "v1.0.0", "Lanzamiento Inicial del Sistema", update_md))

    # ==========================================
    # Operaciones de Proyectos
    # ==========================================

    def list_projects(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*,
                       (SELECT name FROM sprints WHERE project_id = p.id AND status = 'active' LIMIT 1) as active_sprint_name,
                       (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks,
                       (SELECT COUNT(*) FROM project_docs WHERE project_id = p.id) as total_docs
                FROM projects p
                ORDER BY p.id ASC
            """)
            return [dict(r) for r in cursor.fetchall()]

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*,
                       (SELECT name FROM sprints WHERE project_id = p.id AND status = 'active' LIMIT 1) as active_sprint_name,
                       (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks,
                       (SELECT COUNT(*) FROM project_docs WHERE project_id = p.id) as total_docs
                FROM projects p WHERE p.id = ?
            """, (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_project(self, name: str, description: str = "", github_url: str = "", readme_markdown: str = "") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO projects (name, description, github_url, readme_markdown, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (name, description, github_url, readme_markdown, now, now)
            )
            project_id = cursor.lastrowid

            # Crear columnas por defecto
            for title, pos in [("Por Hacer", 1), ("En Progreso", 2), ("En Revisión", 3), ("Terminado", 4)]:
                cursor.execute(
                    "INSERT INTO columns (project_id, title, position) VALUES (?, ?, ?)",
                    (project_id, title, pos)
                )

            # Crear Sprint 1 por defecto
            cursor.execute("""
                INSERT INTO sprints (project_id, name, goal, status, target_points)
                VALUES (?, ?, ?, 'active', 10)
            """, (project_id, "Sprint 1", "Sprint inicial"))

            conn.commit()
            return self.get_project(project_id)

    def update_project(self, project_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        current = self.get_project(project_id)
        if not current:
            return None

        fields = []
        values = []
        for key in ["name", "description", "github_url", "readme_markdown"]:
            if key in kwargs and kwargs[key] is not None:
                fields.append(f"{key} = ?")
                values.append(kwargs[key])

        if not fields:
            return current

        fields.append("updated_at = ?")
        values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(project_id)

        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))
            conn.commit()

        return self.get_project(project_id)

    def get_project_readme(self, project_id: int) -> str:
        p = self.get_project(project_id)
        return p.get("readme_markdown") or "" if p else ""

    def update_project_readme(self, project_id: int, readme_markdown: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE projects SET readme_markdown = ?, updated_at = ? WHERE id = ?",
                (readme_markdown, now, project_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # Operaciones de Sprints (Scrum)
    # ==========================================

    def list_sprints(self, project_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*,
                       COALESCE(SUM(CASE WHEN c.title = 'Terminado' THEN t.story_points ELSE 0 END), 0) as completed_points,
                       COALESCE(SUM(t.story_points), 0) as total_points
                FROM sprints s
                LEFT JOIN tasks t ON s.id = t.sprint_id
                LEFT JOIN columns c ON t.column_id = c.id
                WHERE s.project_id = ?
                GROUP BY s.id
                ORDER BY s.id DESC
            """, (project_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_active_sprint(self, project_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*,
                       COALESCE(SUM(CASE WHEN c.title = 'Terminado' THEN t.story_points ELSE 0 END), 0) as completed_points,
                       COALESCE(SUM(t.story_points), 0) as total_points
                FROM sprints s
                LEFT JOIN tasks t ON s.id = t.sprint_id
                LEFT JOIN columns c ON t.column_id = c.id
                WHERE s.project_id = ? AND s.status = 'active'
                GROUP BY s.id
                LIMIT 1
            """, (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_sprint(self, project_id: int, name: str, goal: str = "", start_date: str = "", end_date: str = "", target_points: int = 0) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sprints (project_id, name, goal, start_date, end_date, status, target_points)
                VALUES (?, ?, ?, ?, ?, 'planned', ?)
            """, (project_id, name, goal, start_date, end_date, target_points))
            sprint_id = cursor.lastrowid
            conn.commit()
            return self.get_sprint(sprint_id)

    def get_sprint(self, sprint_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*,
                       COALESCE(SUM(CASE WHEN c.title = 'Terminado' THEN t.story_points ELSE 0 END), 0) as completed_points,
                       COALESCE(SUM(t.story_points), 0) as total_points
                FROM sprints s
                LEFT JOIN tasks t ON s.id = t.sprint_id
                LEFT JOIN columns c ON t.column_id = c.id
                WHERE s.id = ?
                GROUP BY s.id
            """, (sprint_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def complete_sprint(self, sprint_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sprints SET status = 'completed' WHERE id = ?", (sprint_id,))
            conn.commit()
            return self.get_sprint(sprint_id)

    # ==========================================
    # Tablero Kanban y Tareas
    # ==========================================

    def get_project_board(self, project_id: int, sprint_id: Optional[int] = -1) -> Dict[str, Any]:
        """
        Si sprint_id == -1, se obtiene el sprint activo.
        Si sprint_id == 0 o None, se obtienen las tareas del Product Backlog (sprint_id IS NULL).
        Si sprint_id > 0, se obtienen las tareas de ese sprint específico.
        """
        project = self.get_project(project_id)
        if not project:
            return None

        active_sprint = self.get_active_sprint(project_id)
        target_sprint_id = active_sprint["id"] if (sprint_id == -1 and active_sprint) else sprint_id

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 0. Columna Backlog (Ideas no asignadas a un sprint)
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE project_id = ? AND sprint_id IS NULL
                ORDER BY position ASC, id DESC
            """, (project_id,))
            backlog_task_rows = cursor.fetchall()
            backlog_tasks = []
            for t in backlog_task_rows:
                td = dict(t)
                try:
                    td["tags"] = json.loads(td["tags"]) if td["tags"] else []
                except Exception:
                    td["tags"] = []
                backlog_tasks.append(td)

            backlog_count = len(backlog_tasks)

            columns = [{
                "id": 0,
                "project_id": project_id,
                "title": "Backlog (Ideas)",
                "position": 0,
                "is_backlog": True,
                "tasks": backlog_tasks
            }]

            cursor.execute("SELECT * FROM columns WHERE project_id = ? ORDER BY position ASC", (project_id,))
            col_rows = cursor.fetchall()

            for col in col_rows:
                col_dict = dict(col)
                # Mostrar tareas del sprint objetivo
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE column_id = ? AND sprint_id = ?
                    ORDER BY position ASC, id DESC
                """, (col["id"], target_sprint_id))

                task_rows = cursor.fetchall()
                tasks = []
                for t in task_rows:
                    td = dict(t)
                    try:
                        td["tags"] = json.loads(td["tags"]) if td["tags"] else []
                    except Exception:
                        td["tags"] = []
                    tasks.append(td)

                col_dict["tasks"] = tasks
                columns.append(col_dict)

            return {
                "project": project,
                "active_sprint": active_sprint,
                "columns": columns,
                "backlog_count": backlog_count
            }

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            try:
                data["tags"] = json.loads(data["tags"]) if data["tags"] else []
            except Exception:
                data["tags"] = []
            return data

    def create_task(self, project_id: int, column_id: int, title: str, description: str = "", priority: str = "medium", story_points: int = 1, sprint_id: Optional[int] = None, tags: Optional[List[str]] = None, assignee: str = "Claude Agent", phase: str = "Phase 1", dependency: str = "") -> Dict[str, Any]:
        tags_json = json.dumps(tags or [])
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            actual_col_id = column_id
            actual_sprint_id = sprint_id
            if column_id == 0:
                cursor.execute("SELECT id FROM columns WHERE project_id = ? AND title = 'Por Hacer' LIMIT 1", (project_id,))
                col_row = cursor.fetchone()
                actual_col_id = col_row["id"] if col_row else 1
                actual_sprint_id = None

            cursor.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM tasks WHERE column_id = ?", (actual_col_id,))
            pos = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, dependency, position, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, actual_col_id, actual_sprint_id, title, description, priority, story_points, assignee, phase, dependency, pos, tags_json, now, now))
            task_id = cursor.lastrowid
            conn.commit()

        return self.get_task(task_id)

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        current = self.get_task(task_id)
        if not current:
            return None

        fields = []
        values = []
        for key, val in kwargs.items():
            if key == "tags" and isinstance(val, list):
                fields.append("tags = ?")
                values.append(json.dumps(val))
            elif key in ["title", "description", "priority", "story_points", "assignee", "phase", "dependency", "column_id", "sprint_id", "position"]:
                fields.append(f"{key} = ?")
                values.append(val)

        if not fields:
            return current

        fields.append("updated_at = ?")
        values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(task_id)

        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))
            conn.commit()

        return self.get_task(task_id)

    def move_task(self, task_id: int, new_column_id: int, new_position: int) -> Optional[Dict[str, Any]]:
        current_task = self.get_task(task_id)
        if not current_task:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            if new_column_id == 0:
                # Movido a columna Backlog: sprint_id = NULL
                cursor.execute("""
                    UPDATE tasks 
                    SET sprint_id = NULL, position = ?, updated_at = ?
                    WHERE id = ?
                """, (new_position, now, task_id))
            else:
                # Movido a columna de Sprint: si venía de Backlog, asignarle el sprint activo
                sprint_id = current_task.get("sprint_id")
                if sprint_id is None:
                    active_sprint = self.get_active_sprint(current_task["project_id"])
                    if active_sprint:
                        sprint_id = active_sprint["id"]

                cursor.execute("""
                    UPDATE tasks 
                    SET column_id = ?, sprint_id = ?, position = ?, updated_at = ?
                    WHERE id = ?
                """, (new_column_id, sprint_id, new_position, now, task_id))

            conn.commit()
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_backlog_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, c.title as column_title
                FROM tasks t
                JOIN columns c ON t.column_id = c.id
                WHERE t.project_id = ? AND t.sprint_id IS NULL
                ORDER BY 
                    CASE t.priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    t.position ASC, t.id DESC
            """, (project_id,))
            rows = cursor.fetchall()
            tasks = []
            for r in rows:
                td = dict(r)
                try:
                    td["tags"] = json.loads(td["tags"]) if td["tags"] else []
                except Exception:
                    td["tags"] = []
                tasks.append(td)
            return tasks

    def move_task_to_sprint(self, task_id: int, sprint_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        task = self.get_task(task_id)
        if not task:
            return None

        target_sprint_id = sprint_id
        if target_sprint_id is None or target_sprint_id <= 0:
            active_sprint = self.get_active_sprint(task["project_id"])
            if active_sprint:
                target_sprint_id = active_sprint["id"]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Asegurar que la tarea esté en la columna 'Por Hacer' del proyecto si viene del backlog
            cursor.execute("SELECT id FROM columns WHERE project_id = ? AND title = 'Por Hacer' LIMIT 1", (task["project_id"],))
            col_row = cursor.fetchone()
            col_id = col_row["id"] if col_row else task["column_id"]

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE tasks 
                SET sprint_id = ?, column_id = ?, updated_at = ?
                WHERE id = ?
            """, (target_sprint_id, col_id, now, task_id))
            conn.commit()

        return self.get_task(task_id)

    def move_task_to_backlog(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE tasks SET sprint_id = NULL, updated_at = ? WHERE id = ?", (now, task_id))
            conn.commit()
        return self.get_task(task_id)

    # ==========================================
    # Documentación Wiki del Proyecto
    # ==========================================

    def list_docs(self, project_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM project_docs WHERE project_id = ? ORDER BY category ASC, title ASC", (project_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_doc(self, doc_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM project_docs WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_doc(self, project_id: int, title: str, category: str = "General", content_markdown: str = "") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO project_docs (project_id, title, category, content_markdown, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, title, category, content_markdown, now, now))
            doc_id = cursor.lastrowid
            conn.commit()
            return self.get_doc(doc_id)

    def update_doc(self, doc_id: int, title: Optional[str] = None, category: Optional[str] = None, content_markdown: Optional[str] = None) -> Optional[Dict[str, Any]]:
        doc = self.get_doc(doc_id)
        if not doc:
            return None
        fields = []
        values = []
        if title is not None:
            fields.append("title = ?")
            values.append(title)
        if category is not None:
            fields.append("category = ?")
            values.append(category)
        if content_markdown is not None:
            fields.append("content_markdown = ?")
            values.append(content_markdown)

        if fields:
            fields.append("updated_at = ?")
            values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            values.append(doc_id)
            query = f"UPDATE project_docs SET {', '.join(fields)} WHERE id = ?"
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(values))
                conn.commit()
        return self.get_doc(doc_id)

    def delete_doc(self, doc_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM project_docs WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # Bitácora de Actualizaciones (Changelog)
    # ==========================================

    def list_updates(self, project_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, s.name as sprint_name 
                FROM project_updates u
                LEFT JOIN sprints s ON u.sprint_id = s.id
                WHERE u.project_id = ?
                ORDER BY u.id DESC
            """, (project_id,))
            return [dict(r) for r in cursor.fetchall()]

    def create_update(self, project_id: int, version_tag: str, title: str, content_markdown: str, sprint_id: Optional[int] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO project_updates (project_id, sprint_id, version_tag, title, content_markdown, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, sprint_id, version_tag, title, content_markdown, now))
            update_id = cursor.lastrowid
            conn.commit()
            cursor.execute("SELECT * FROM project_updates WHERE id = ?", (update_id,))
            return dict(cursor.fetchone())

    # ==========================================
    # Métricas y Estadísticas Scrum
    # ==========================================

    def get_project_metrics(self, project_id: int) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            project = self.get_project(project_id)
            if not project:
                return {}

            # Total tareas, en progreso y completadas
            cursor.execute("""
                SELECT 
                    COUNT(t.id) as total_tasks,
                    SUM(CASE WHEN c.title LIKE '%Terminado%' OR c.title LIKE '%Done%' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN c.title LIKE '%Progreso%' OR c.title LIKE '%Progress%' THEN 1 ELSE 0 END) as in_progress_tasks,
                    SUM(CASE WHEN c.title LIKE '%Hacer%' OR c.title LIKE '%To Do%' THEN 1 ELSE 0 END) as todo_tasks,
                    COALESCE(SUM(t.story_points), 0) as total_points,
                    COALESCE(SUM(CASE WHEN c.title LIKE '%Terminado%' OR c.title LIKE '%Done%' THEN t.story_points ELSE 0 END), 0) as completed_points
                FROM tasks t
                JOIN columns c ON t.column_id = c.id
                WHERE t.project_id = ?
            """, (project_id,))
            summary_row = cursor.fetchone()
            total_tasks = summary_row["total_tasks"] or 0
            completed_tasks = summary_row["completed_tasks"] or 0
            in_progress_tasks = summary_row["in_progress_tasks"] or 0
            todo_tasks = summary_row["todo_tasks"] or 0
            total_points = summary_row["total_points"] or 0
            completed_points = summary_row["completed_points"] or 0
            completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

            # Distribución por columna / estado
            cursor.execute("""
                SELECT c.title as column_title, COUNT(t.id) as task_count
                FROM columns c
                LEFT JOIN tasks t ON c.id = t.column_id AND t.project_id = ?
                WHERE c.project_id = ?
                GROUP BY c.id, c.title
                ORDER BY c.position
            """, (project_id, project_id))
            tasks_by_status = {r["column_title"]: r["task_count"] for r in cursor.fetchall()}

            # Distribución por miembro / asignado
            cursor.execute("""
                SELECT t.assignee, COUNT(t.id) as task_count, COALESCE(SUM(t.story_points), 0) as points
                FROM tasks t
                WHERE t.project_id = ?
                GROUP BY t.assignee
                ORDER BY points DESC
            """, (project_id,))
            tasks_by_assignee = {
                (r["assignee"] or "Sin asignar"): {"tasks": r["task_count"], "points": r["points"]}
                for r in cursor.fetchall()
            }

            # Puntos por prioridad
            cursor.execute("""
                SELECT priority, COALESCE(SUM(story_points), 0) as points
                FROM tasks
                WHERE project_id = ?
                GROUP BY priority
            """, (project_id,))
            points_by_priority = {r["priority"]: r["points"] for r in cursor.fetchall()}

            # Tareas por tag
            cursor.execute("SELECT tags FROM tasks WHERE project_id = ?", (project_id,))
            tag_counts: Dict[str, int] = {}
            for row in cursor.fetchall():
                try:
                    tags = json.loads(row["tags"]) if row["tags"] else []
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                except Exception:
                    pass

            return {
                "project_id": project_id,
                "project_name": project["name"],
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "todo_tasks": todo_tasks,
                "completion_rate": completion_rate,
                "total_points": total_points,
                "completed_points": completed_points,
                "velocity_points_completed": completed_points,
                "points_by_priority": points_by_priority,
                "tasks_by_status": tasks_by_status,
                "tasks_by_assignee": tasks_by_assignee,
                "tasks_by_tag": tag_counts
            }

    # ==========================================
    # Bitácora Interactiva (Notebook Markdown)
    # ==========================================

    def list_bitacora_entries(self, project_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM bitacora_entries
                WHERE project_id = ?
                ORDER BY entry_date DESC, id DESC
            """, (project_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_bitacora_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bitacora_entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_bitacora_entry(self, project_id: int, content_markdown: str, title: str = "", entry_date: str = "") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            if not entry_date:
                entry_date = datetime.utcnow().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, title, content_markdown, entry_date, now, now))
            entry_id = cursor.lastrowid
            conn.commit()
            return self.get_bitacora_entry(entry_id)

    def update_bitacora_entry(self, entry_id: int, content_markdown: Optional[str] = None, title: Optional[str] = None, entry_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        current = self.get_bitacora_entry(entry_id)
        if not current:
            return None

        fields = []
        values = []
        if content_markdown is not None:
            fields.append("content_markdown = ?")
            values.append(content_markdown)
        if title is not None:
            fields.append("title = ?")
            values.append(title)
        if entry_date is not None:
            fields.append("entry_date = ?")
            values.append(entry_date)

        if not fields:
            return current

        fields.append("updated_at = ?")
        values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(entry_id)

        query = f"UPDATE bitacora_entries SET {', '.join(fields)} WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))
            conn.commit()
            return self.get_bitacora_entry(entry_id)

    def delete_bitacora_entry(self, entry_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bitacora_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

db = Database()
