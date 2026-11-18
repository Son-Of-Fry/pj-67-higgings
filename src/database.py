import os
import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from src.config import settings

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.sqlite_db_path
        self._backup_lock = threading.Lock()
        self._last_backup_date: Optional[str] = None

    @staticmethod
    def _utc_iso_now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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

            # 0. Usuarios / Equipo
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                email TEXT DEFAULT '',
                role TEXT DEFAULT 'Miembro',
                area TEXT DEFAULT '',
                color TEXT DEFAULT '#0c66e4',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 1. Proyectos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                github_url TEXT DEFAULT '',
                folder_url TEXT DEFAULT '',
                readme_markdown TEXT DEFAULT '',
                difficulty INTEGER DEFAULT 3,
                priority TEXT DEFAULT 'Media',
                theme TEXT DEFAULT '',
                area TEXT DEFAULT '',
                axis TEXT DEFAULT 'Abierto',
                status TEXT DEFAULT 'En tiempo',
                stakeholder TEXT DEFAULT '',
                area_key_user TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                start_date TEXT DEFAULT '',
                due_date TEXT DEFAULT '',
                next_step TEXT DEFAULT '',
                risks_blockers TEXT DEFAULT '',
                is_visible INTEGER DEFAULT 1,
                extra_data TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Auto-migraciones para proyectos existentes
            cursor.execute("PRAGMA table_info(projects)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            added_area = "area" not in existing_cols
            added_priority = "priority" not in existing_cols
            for col_name, col_type in [
                ("folder_url", "TEXT DEFAULT ''"),
                ("readme_markdown", "TEXT DEFAULT ''"),
                ("difficulty", "INTEGER DEFAULT 3"),
                ("priority", "TEXT DEFAULT 'Media'"),
                ("theme", "TEXT DEFAULT ''"),
                ("area", "TEXT DEFAULT ''"),
                ("axis", "TEXT DEFAULT 'Abierto'"),
                ("status", "TEXT DEFAULT 'En tiempo'"),
                ("stakeholder", "TEXT DEFAULT ''"),
                ("area_key_user", "TEXT DEFAULT ''"),
                ("owner", "TEXT DEFAULT ''"),
                ("start_date", "TEXT DEFAULT ''"),
                ("due_date", "TEXT DEFAULT ''"),
                ("next_step", "TEXT DEFAULT ''"),
                ("risks_blockers", "TEXT DEFAULT ''"),
                ("is_visible", "INTEGER DEFAULT 1"),
                ("extra_data", "TEXT DEFAULT '{}'"),
                ("created_at", "TEXT DEFAULT ''"),
                ("updated_at", "TEXT DEFAULT ''")
            ]:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")

            if added_area:
                cursor.execute("UPDATE projects SET area = theme WHERE theme IS NOT NULL AND theme != '' AND (area IS NULL OR area = '')")
            if added_priority:
                cursor.execute("""
                    UPDATE projects
                    SET priority = CASE
                        WHEN difficulty >= 5 THEN 'Crítica'
                        WHEN difficulty = 4 THEN 'Alta'
                        WHEN difficulty IN (1, 2) THEN 'Baja'
                        ELSE 'Media'
                    END
                """)
            cursor.execute("UPDATE projects SET status = 'En tiempo' WHERE status IN ('Planeación', 'En Curso', '') OR status IS NULL")
            cursor.execute("UPDATE projects SET status = 'Completado' WHERE status = 'Terminado'")

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
                assignee TEXT DEFAULT 'Sin asignar',
                assignee_id INTEGER,
                phase TEXT DEFAULT 'Base',
                dependency TEXT DEFAULT '',
                position INTEGER NOT NULL,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (column_id) REFERENCES columns (id) ON DELETE CASCADE,
                FOREIGN KEY (sprint_id) REFERENCES sprints (id) ON DELETE SET NULL,
                FOREIGN KEY (assignee_id) REFERENCES users (id) ON DELETE SET NULL
            );
            """)

            # Migración automática de columnas para bases existentes
            cursor.execute("PRAGMA table_info(tasks)")
            task_col_names = [r["name"] for r in cursor.fetchall()]
            if task_col_names:
                if "assignee" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN assignee TEXT DEFAULT 'Sin asignar'")
                if "assignee_id" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN assignee_id INTEGER")
                if "phase" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN phase TEXT DEFAULT 'Base'")
                if "dependency" not in task_col_names:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN dependency TEXT DEFAULT ''")

                # Unificar etapas legacy ('Phase 1/2/3' o vacías) a 'Base'
                cursor.execute("""
                    UPDATE tasks
                    SET phase = 'Base'
                    WHERE phase IN ('Phase 1', 'Phase 2', 'Phase 3', '') OR phase IS NULL
                """)

                # Limpiar asignaciones legacy de agentes IA a 'Sin asignar'
                cursor.execute("""
                    UPDATE tasks
                    SET assignee = 'Sin asignar', assignee_id = NULL
                    WHERE assignee IN ('Claude Agent', 'Cursor', 'Figma Agent', 'Rich (Humano)', '')
                       OR assignee IS NULL
                       OR (assignee = 'Rich' AND NOT EXISTS (SELECT 1 FROM users WHERE name = 'Rich'))
                """)

                # Reparar tareas huérfanas con column_id = 0 asignándolas a 'Por Hacer' en Backlog
                cursor.execute("""
                    UPDATE tasks
                    SET sprint_id = NULL,
                        column_id = COALESCE(
                            (SELECT id FROM columns WHERE project_id = tasks.project_id AND title = 'Por Hacer' LIMIT 1),
                            column_id
                        )
                    WHERE column_id = 0 OR column_id NOT IN (SELECT id FROM columns)
                """)
                conn.commit()

            # Migración automática de projects para columna github_url y readme_markdown
            cursor.execute("PRAGMA table_info(projects)")
            proj_col_names = [r["name"] for r in cursor.fetchall()]
            if proj_col_names and "github_url" not in proj_col_names:
                cursor.execute("ALTER TABLE projects ADD COLUMN github_url TEXT DEFAULT ''")
                cursor.execute("UPDATE projects SET github_url = 'https://github.com/Son-Of-Fry/pj-67-higgings' WHERE name LIKE '%PJ-00%' OR name LIKE '%PJ-67%'")
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

            # 8. Registro Histórico de Actividad (Audit Log)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                project_name TEXT DEFAULT '',
                task_id INTEGER,
                entity_type TEXT NOT NULL,
                action TEXT NOT NULL,
                field_name TEXT DEFAULT '',
                old_value TEXT DEFAULT '',
                new_value TEXT DEFAULT '',
                actor TEXT DEFAULT 'Usuario Web',
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_logs (created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_project ON activity_logs (project_id, created_at DESC)")

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

            # Semilla inicial para Bitácora si está vacía
            cursor.execute("SELECT COUNT(*) FROM bitacora_entries")
            if cursor.fetchone()[0] == 0:
                self._seed_bitacora_entries(cursor)
                conn.commit()

    def _seed_tutorial_project(self, cursor: sqlite3.Cursor):
        # Proyecto 0: PJ-00 Tutorial (Onboarding)
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-00 Tutorial", "Proyecto interactivo de bienvenida y tutorial guiado para aprender el flujo Scrum, gestión ágil y conexión con agentes MCP.", "https://github.com/Son-Of-Fry/pj-67-higgings")
        )
        p0_id = cursor.lastrowid

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
        """, (p0_id, "Sprint 1 — Onboarding & Tour", "Comprender las vistas Scrum, estimación de Story Points y flujo de tareas", now, now, "active", 14))
        sprint_id = cursor.lastrowid

        # Tareas Tutorial
        t1_desc = """### Bienvenido a tu plataforma de proyectos
Esta herramienta combina gestión ágil visual con soporte para automatización e IA mediante **Model Context Protocol (MCP)**.

#### ¿Cómo usar este tablero?
1. **Arrastra y suelta (Drag & Drop):** Toma cualquier tarjeta y muévela entre columnas para cambiar su estado en tiempo real.
2. **Creación rápida:** En la parte superior de cada columna escribe una tarea en `+ What needs to be done?` y presiona **Enter**.
3. **Edición completa:** Haz clic sobre cualquier tarjeta para editar su descripción en Markdown, asignar un responsable desde tu equipo, definir puntos de historia y fase de entrega."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Terminado"], sprint_id,
            "¡Bienvenido a Higgings! Conoce el flujo Scrum & MCP",
            t1_desc, "medium", 1, "Sin asignar", "Base", 1, json.dumps(["Bienvenida", "Tutorial"])
        ))

        t2_desc = """### Conoce cada una de las vistas disponibles:

- **Tablero (Board):** Tablero Kanban visual con Product Backlog integrado, columnas de flujo ágil y soporte para drag & drop.
- **Work items (Lista):** Vista en lista jerárquica organizada por etapas / fases de desarrollo y estado real.
- **Releases & Updates:** Registro histórico de entregas y notas de versión.
- **Métricas del Proyecto:** Métricas generales del proyecto, tasa de cumplimiento y distribución por responsable."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Terminado"], sprint_id,
            "Navega por las pestañas del proyecto",
            t2_desc, "low", 2, "Sin asignar", "Base", 2, json.dumps(["Navegación", "Guía"])
        ))

        t3_desc = """### Conexión con Clientes MCP
El servidor MCP de Higgings corre en segundo plano y expone el protocolo oficial por **Server-Sent Events (SSE)** en el puerto configurado.

#### ¿Qué puede hacer un cliente MCP conectado?
- `get_board_state`: Leer las columnas, sprints y tareas actuales.
- `create_task`: Crear nuevas historias con story points, fase y tags.
- `update_task_status`: Mover historias a 'En Progreso' o 'Terminado'.
- `update_project_readme`: Escribir o actualizar la documentación del proyecto."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["En Progreso"], sprint_id,
            "Configurar usuarios del equipo y conectar clientes MCP",
            t3_desc, "high", 3, "Sin asignar", "Base", 1, json.dumps(["MCP", "SSE"])
        ))

        t4_desc = """### Metodología Scrum: Story Points
Los Story Points miden el esfuerzo y complejidad relativa de una tarea (usando la escala Fibonacci: 1, 2, 3, 5, 8, 13).

- **1-2 pts:** Tareas triviales o ajustes rápidos.
- **3-5 pts:** Features con lógica de backend o componentes nuevos.
- **8-13 pts:** Módulos complejos que convendría desglosar en subtareas.

*Los puntos completados alimentan automáticamente el cálculo de velocidad en la pestaña de **Métricas**.*"""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Por Hacer"], sprint_id,
            "Estimar historias con Story Points (Fibonacci)",
            t4_desc, "medium", 5, "Sin asignar", "Base", 1, json.dumps(["Scrum", "Estimación"])
        ))

        t5_desc = """### Soporte Multi-Proyecto
Puedes gestionar tantos proyectos como necesites:
1. Haz clic en el botón `+` junto al selector de proyecto en la barra superior o en Inicio.
2. Ingresa el nombre, responsable, interesado y fechas de tu proyecto.
3. Cada proyecto tiene su propio tablero, sprints, bitácora, documentación y changelog independientes."""

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p0_id, col_ids["Por Hacer"], sprint_id,
            "Crear tu primer proyecto real con el botón '+'",
            t5_desc, "medium", 3, "Sin asignar", "Base", 2, json.dumps(["Multi-Proyecto"])
        ))

        # Wiki inicial para el tutorial
        wiki_md = """# Manual de Inicio Rápido & Arquitectura — PJ-00

¡Bienvenido a la plataforma ágil Higgings! Esta guía explica cómo trabajar en tus proyectos combinando metodologías ágiles (Scrum), control ejecutivo y automatización mediante MCP.

## Ciclo de Desarrollo Ágil

```mermaid
graph TD
    A[Idea de Negocio / Feature] --> B[Definir Plan y Fechas]
    B --> C[Desglosar en Work Items y Fases]
    C --> D[Sprint Backlog y Estimacion]
    D --> E[Implementacion por Responsable]
    E --> F[Pruebas y Revision]
    F --> G[Release en Changelog]
    G --> H[Analisis de Metricas]
```

## Buenas Prácticas Recomendadas

1. **Fases Claras:** Organiza tu trabajo en `Phase 1` (Arquitectura & Core), `Phase 2` (Features Principales) y `Phase 3` (Hardening & Releases).
2. **Story Points Realistas:** No sobrecargues un sprint; la suma de puntos objetivo debe rondar entre 13 y 21 puntos para mantener un ritmo sostenible.
3. **Documentación Viva:** Mantén este documento actualizado."""

        cursor.execute("""
            INSERT INTO project_docs (project_id, title, category, content_markdown)
            VALUES (?, ?, ?, ?)
        """, (p0_id, "Guía Rápida & Arquitectura — Tutorial PJ-00", "Guía", wiki_md))

        # Actualización de release en Changelog
        update_md = """### Bienvenido al Proyecto Tutorial PJ-00
- Tablero Kanban preconfigurado con ejemplos de tareas y flujo ágil.
- Soporte completo para asignación de responsables del equipo.
- Configuración lista para conectar clientes externos mediante el protocolo MCP (SSE)."""

        cursor.execute("""
            INSERT INTO project_updates (project_id, sprint_id, version_tag, title, content_markdown)
            VALUES (?, ?, ?, ?, ?)
        """, (p0_id, sprint_id, "v0.1.0-tutorial", "Lanzamiento del Proyecto Tutorial", update_md))

    def _seed_bitacora_entries(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT id, name FROM projects")
        projects = {row["name"]: row["id"] for row in cursor.fetchall()}

        pj67_id = None
        pj65_id = None
        pj00_id = None
        for name, pid in projects.items():
            if "PJ-67" in name or "Higgings" in name:
                pj67_id = pid
            elif "PJ-65" in name:
                pj65_id = pid
            elif "PJ-00" in name:
                pj00_id = pid

        pj67_entry = """**Proyecto:**  
PJ-67 (Higgings — AI-Native Agile Management Platform & MCP Server)

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
            """, (pj67_id, "Despliegue inicial Higgings & Servidor MCP con Scale-to-Zero", pj67_entry, "2026-10-17", 1, now_str, now_str))

        if pj65_id:
            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pj65_id, "Integración DVC + MLflow & Modelado Fase 2", pj65_entry, "2026-10-17", 1, now_str, now_str))

        if pj00_id:
            cursor.execute("""
                INSERT INTO bitacora_entries (project_id, title, content_markdown, entry_date, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pj00_id, "Despliegue inicial Higgings & Servidor MCP con Scale-to-Zero", pj67_entry, "2026-10-17", 1, now_str, now_str))

    def _seed_initial_data(self, cursor: sqlite3.Cursor):
        # Proyecto 1: PJ-67
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-67 Platform", "Sistema autónomo de gestión ágil de proyectos con Scrum y Model Context Protocol", "https://github.com/Son-Of-Fry/pj-67-higgings")
        )
        p1_id = cursor.lastrowid

        # Proyecto 2: PJ-65
        cursor.execute(
            "INSERT INTO projects (name, description, github_url) VALUES (?, ?, ?)",
            ("PJ-65 Retail MLOps", "Motor de pricing dinámico con DVC, MLflow y salvaguarda financiera", "")
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
            "high", 3, "Sin asignar", "Base", 1, json.dumps(["DevOps", "Docker"])
        ))

        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p1_id, col_ids["En Progreso"], sprint1_id,
            "Implementar soporte Multi-Proyecto y Scrum",
            "### Requerimientos\n1. Sprints con Story Points.\n2. Product Backlog independiente.\n3. Wiki de Documentación.",
            "urgent", 5, "Sin asignar", "Base", 1, json.dumps(["Scrum", "FastAPI"])
        ))

        # Tarea en Backlog (sprint_id = None)
        cursor.execute("""
            INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, phase, position, tags)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p1_id, col_ids["Por Hacer"],
            "Integrar gráficos avanzados de métricas con Canvas",
            "Requisito futuro para proyectar la velocidad de sprints históricos.",
            "low", 2, "Sin asignar", "Base", 1, json.dumps(["Frontend", "UI"])
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
    # Operaciones de Usuarios / Equipo
    # ==========================================

    def list_users(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM users ORDER BY name ASC")
            else:
                cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY name ASC")
            users = []
            for r in cursor.fetchall():
                d = dict(r)
                d["is_active"] = bool(d.get("is_active", 1))
                users.append(d)
            return users

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["is_active"] = bool(d.get("is_active", 1))
            return d

    def create_user(self, name: str, email: str = "", role: str = "Miembro", area: str = "", color: str = "#0c66e4", is_active: bool = True) -> Dict[str, Any]:
        clean_name = name.strip()
        if not clean_name or clean_name.lower() == "sin asignar":
            raise ValueError("El nombre de usuario no es válido.")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT INTO users (name, email, role, area, color, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (clean_name, email.strip(), role.strip() or "Miembro", area.strip(), color or "#0c66e4", 1 if is_active else 0, now)
            )
            user_id = cursor.lastrowid
            # Enlazar tareas existentes que tuvieran ese nombre asignado manualmente
            cursor.execute("UPDATE tasks SET assignee_id = ? WHERE assignee = ?", (user_id, clean_name))
            conn.commit()
            return self.get_user(user_id)

    def update_user(self, user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        current = self.get_user(user_id)
        if not current:
            return None

        fields = []
        values = []
        new_name = None
        for key in ["name", "email", "role", "area", "color", "is_active"]:
            if key in kwargs and kwargs[key] is not None:
                val = kwargs[key]
                if key == "name":
                    val = val.strip()
                    if not val or val.lower() == "sin asignar":
                        raise ValueError("El nombre de usuario no es válido.")
                    new_name = val
                elif key in ("email", "role", "area") and isinstance(val, str):
                    val = val.strip()
                elif key == "is_active" and isinstance(val, bool):
                    val = 1 if val else 0
                fields.append(f"{key} = ?")
                values.append(val)

        if not fields:
            return current

        values.append(user_id)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(values))
            if new_name and new_name != current["name"]:
                cursor.execute(
                    "UPDATE tasks SET assignee = ?, assignee_id = ? WHERE assignee_id = ? OR assignee = ?",
                    (new_name, user_id, user_id, current["name"])
                )
                cursor.execute(
                    "UPDATE projects SET owner = ? WHERE owner = ?",
                    (new_name, current["name"])
                )
            conn.commit()

        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        current = self.get_user(user_id)
        if not current:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET assignee = 'Sin asignar', assignee_id = NULL WHERE assignee_id = ? OR assignee = ?",
                (user_id, current["name"])
            )
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # Operaciones de Proyectos
    # ==========================================

    @staticmethod
    def _hydrate_project(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        total = d.get("total_tasks") or 0
        completed = d.get("completed_tasks") or 0
        d["progress_percent"] = round((completed / total) * 100) if total > 0 else 0
        d["is_visible"] = bool(d["is_visible"]) if d.get("is_visible") is not None else True
        for text_col in (
            "stakeholder", "area_key_user", "owner", "start_date", "due_date",
            "area", "theme", "description", "github_url", "folder_url",
            "readme_markdown", "next_step", "risks_blockers"
        ):
            if d.get(text_col) is None:
                d[text_col] = ""
        if not d["area"] and d["theme"]:
            d["area"] = d["theme"]
        if not d.get("priority"):
            d["priority"] = "Media"
        if not d.get("status"):
            d["status"] = "En tiempo"
        return d

    def list_projects(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*,
                       (SELECT name FROM sprints WHERE project_id = p.id AND status = 'active' LIMIT 1) as active_sprint_name,
                       (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks,
                       (SELECT COUNT(*) FROM tasks t JOIN columns c ON t.column_id = c.id WHERE t.project_id = p.id AND c.title = 'Terminado' AND t.sprint_id IS NOT NULL) as completed_tasks,
                       (SELECT entry_date FROM bitacora_entries WHERE project_id = p.id ORDER BY entry_date DESC, id DESC LIMIT 1) as last_bitacora_date,
                       (SELECT COUNT(*) FROM project_docs WHERE project_id = p.id) as total_docs
                FROM projects p
                ORDER BY p.id ASC
            """)
            return [self._hydrate_project(r) for r in cursor.fetchall()]

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*,
                       (SELECT name FROM sprints WHERE project_id = p.id AND status = 'active' LIMIT 1) as active_sprint_name,
                       (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks,
                       (SELECT COUNT(*) FROM tasks t JOIN columns c ON t.column_id = c.id WHERE t.project_id = p.id AND c.title = 'Terminado' AND t.sprint_id IS NOT NULL) as completed_tasks,
                       (SELECT entry_date FROM bitacora_entries WHERE project_id = p.id ORDER BY entry_date DESC, id DESC LIMIT 1) as last_bitacora_date,
                       (SELECT COUNT(*) FROM project_docs WHERE project_id = p.id) as total_docs
                FROM projects p WHERE p.id = ?
            """, (project_id,))
            row = cursor.fetchone()
            return self._hydrate_project(row) if row else None

    def create_project(
        self,
        name: str,
        description: str = "",
        github_url: str = "",
        folder_url: str = "",
        readme_markdown: str = "",
        difficulty: int = 3,
        priority: str = "Media",
        theme: str = "",
        area: str = "",
        axis: str = "Abierto",
        status: str = "En tiempo",
        stakeholder: str = "",
        area_key_user: str = "",
        owner: str = "",
        start_date: str = "",
        due_date: str = "",
        next_step: str = "",
        risks_blockers: str = "",
        is_visible: bool = True,
        extra_data: str = "{}",
        actor: str = "Usuario Web"
    ) -> Dict[str, Any]:
        resolved_area = area or theme
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT INTO projects 
                   (name, description, github_url, folder_url, readme_markdown, difficulty, priority, theme, area, axis, status, stakeholder, area_key_user, owner, start_date, due_date, next_step, risks_blockers, is_visible, extra_data, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, description, github_url, folder_url, readme_markdown, difficulty, priority, resolved_area, resolved_area, axis, status, stakeholder, area_key_user, owner, start_date, due_date, next_step, risks_blockers, 1 if is_visible else 0, extra_data, now, now)
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

            self._log_activity(
                cursor,
                project_id=project_id,
                project_name=name,
                entity_type="project",
                action="created",
                new_value=status,
                actor=actor,
                summary=f"Proyecto creado: {name}",
            )

            conn.commit()
        self._maybe_daily_backup()
        return self.get_project(project_id)

    def update_project(self, project_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        actor = kwargs.pop("actor", "Usuario Web") or "Usuario Web"
        current = self.get_project(project_id)
        if not current:
            return None

        if "area" in kwargs and kwargs["area"] is not None:
            kwargs["theme"] = kwargs["area"]
        elif "theme" in kwargs and kwargs["theme"] is not None:
            kwargs["area"] = kwargs["theme"]

        fields = []
        values = []
        changed_items = []
        allowed = [
            "name", "description", "github_url", "folder_url", "readme_markdown",
            "difficulty", "priority", "theme", "area", "axis", "status",
            "stakeholder", "area_key_user", "owner", "start_date", "due_date",
            "next_step", "risks_blockers", "is_visible", "extra_data"
        ]
        for key in allowed:
            if key in kwargs and kwargs[key] is not None:
                fields.append(f"{key} = ?")
                val = kwargs[key]
                if key == "is_visible" and isinstance(val, bool):
                    val = 1 if val else 0
                values.append(val)

                old_raw = current.get(key)
                if key == "is_visible":
                    old_cmp = 1 if old_raw else 0
                    new_cmp = 1 if val else 0
                else:
                    old_cmp = str(old_raw if old_raw is not None else "")
                    new_cmp = str(val)

                if old_cmp != new_cmp:
                    changed_items.append((key, old_cmp, new_cmp))

        if not fields:
            return current

        fields.append("updated_at = ?")
        values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(project_id)

        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
        project_name = str(kwargs.get("name") or current.get("name") or "")
        tracked_fields = {
            "status": "Estado",
            "risks_blockers": "Bloqueo",
            "next_step": "Siguiente paso",
            "priority": "Prioridad",
            "owner": "Responsable",
            "due_date": "Fecha límite",
            "area": "Área",
        }
        other_changed = []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))

            for key, old_val, new_val in changed_items:
                if key == "theme":
                    continue
                if key in tracked_fields:
                    if key == "risks_blockers":
                        summary = (
                            f"Bloqueo registrado: {new_val[:120]}"
                            if new_val.strip()
                            else "Bloqueo resuelto / limpiado"
                        )
                    elif key == "next_step":
                        summary = (
                            f"Siguiente paso: {new_val[:120]}"
                            if new_val.strip()
                            else "Siguiente paso limpiado"
                        )
                    else:
                        label = tracked_fields[key]
                        summary = f"{label}: '{old_val or 'Sin definir'}' -> '{new_val or 'Sin definir'}'"
                    self._log_activity(
                        cursor,
                        project_id=project_id,
                        project_name=project_name,
                        entity_type="project",
                        action="updated",
                        field_name=key,
                        old_value=old_val,
                        new_value=new_val,
                        actor=actor,
                        summary=summary,
                    )
                else:
                    other_changed.append(key)

            if other_changed:
                if other_changed == ["readme_markdown"]:
                    summary = "Documentación README actualizada"
                    fname = "readme_markdown"
                else:
                    summary = f"Ficha de proyecto actualizada ({', '.join(other_changed[:4])})"
                    fname = other_changed[0]
                self._log_activity(
                    cursor,
                    project_id=project_id,
                    project_name=project_name,
                    entity_type="project",
                    action="updated",
                    field_name=fname,
                    actor=actor,
                    summary=summary,
                )

            conn.commit()

        if changed_items:
            self._maybe_daily_backup()
        return self.get_project(project_id)

    def delete_project(self, project_id: int, actor: str = "Usuario Web") -> bool:
        project = self.get_project(project_id)
        if not project:
            return False
        pname = project.get("name") or f"PJ-{project_id}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM columns WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM sprints WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM project_docs WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM bitacora_entries WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM project_updates WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                self._log_activity(
                    cursor,
                    project_id=project_id,
                    project_name=pname,
                    entity_type="project",
                    action="deleted",
                    old_value=str(project.get("status") or ""),
                    actor=actor,
                    summary=f"Proyecto eliminado: {pname}",
                )
            conn.commit()
        if deleted:
            self._maybe_daily_backup()
        return deleted

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

    def complete_sprint(self, sprint_id: int, actor: str = "Usuario Web") -> Optional[Dict[str, Any]]:
        sprint = self.get_sprint(sprint_id)
        if not sprint:
            return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sprints SET status = 'completed' WHERE id = ?", (sprint_id,))
            self._log_activity(
                cursor,
                project_id=sprint["project_id"],
                entity_type="sprint",
                action="completed",
                field_name="status",
                old_value=str(sprint.get("status") or "active"),
                new_value="completed",
                actor=actor,
                summary=f"Sprint completado: {sprint.get('name') or f'#{sprint_id}'}",
            )
            conn.commit()
        self._maybe_daily_backup()
        return self.get_sprint(sprint_id)

    # ==========================================
    # Tablero Kanban y Tareas
    # ==========================================

    @staticmethod
    def _hydrate_task(row: sqlite3.Row, column_title: Optional[str] = None) -> Dict[str, Any]:
        td = dict(row)
        try:
            td["tags"] = json.loads(td["tags"]) if td["tags"] else []
        except Exception:
            td["tags"] = []
        td["assignee"] = td.get("assignee") or "Sin asignar"
        td["phase"] = (td.get("phase") or "").strip() or "Base"
        resolved_col = column_title or td.get("column_title") or "Por Hacer"
        td["effective_status"] = "Backlog" if td.get("sprint_id") is None else resolved_col
        return td

    @staticmethod
    def _get_todo_column_id(cursor: sqlite3.Cursor, project_id: int, fallback: int = 1) -> int:
        cursor.execute(
            "SELECT id FROM columns WHERE project_id = ? AND title = 'Por Hacer' LIMIT 1",
            (project_id,)
        )
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute(
            "SELECT id FROM columns WHERE project_id = ? ORDER BY position ASC LIMIT 1",
            (project_id,)
        )
        first_row = cursor.fetchone()
        return first_row["id"] if first_row else fallback

    @staticmethod
    def _resolve_assignee(cursor: sqlite3.Cursor, assignee: Optional[str], assignee_id: Optional[int]) -> tuple[str, Optional[int]]:
        if assignee_id is not None:
            cursor.execute("SELECT id, name FROM users WHERE id = ?", (assignee_id,))
            urow = cursor.fetchone()
            if urow:
                return urow["name"], urow["id"]
        clean_name = (assignee or "").strip()
        if not clean_name or clean_name.lower() == "sin asignar":
            return "Sin asignar", None
        cursor.execute("SELECT id, name FROM users WHERE name = ?", (clean_name,))
        urow = cursor.fetchone()
        if urow:
            return urow["name"], urow["id"]
        return clean_name, None

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
            backlog_tasks = [self._hydrate_task(t, "Backlog") for t in cursor.fetchall()]

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
                col_dict["is_backlog"] = False
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE column_id = ? AND sprint_id = ?
                    ORDER BY position ASC, id DESC
                """, (col["id"], target_sprint_id))
                col_dict["tasks"] = [self._hydrate_task(t, col["title"]) for t in cursor.fetchall()]
                columns.append(col_dict)

            return {
                "project": project,
                "active_sprint": active_sprint,
                "columns": columns,
                "backlog_count": len(backlog_tasks)
            }

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, c.title as column_title
                FROM tasks t
                LEFT JOIN columns c ON t.column_id = c.id
                WHERE t.id = ?
            """, (task_id,))
            row = cursor.fetchone()
            return self._hydrate_task(row) if row else None

    def create_task(self, project_id: int, column_id: int, title: str, description: str = "", priority: str = "medium", story_points: int = 1, sprint_id: Optional[int] = None, tags: Optional[List[str]] = None, assignee: str = "Sin asignar", assignee_id: Optional[int] = None, phase: str = "Base", dependency: str = "", actor: str = "Usuario Web") -> Dict[str, Any]:
        tags_json = json.dumps(tags or [])
        clean_phase = (phase or "").strip() or "Base"
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            actual_col_id = column_id
            actual_sprint_id = sprint_id
            if column_id == 0:
                actual_col_id = self._get_todo_column_id(cursor, project_id)
                actual_sprint_id = None

            resolved_name, resolved_id = self._resolve_assignee(cursor, assignee, assignee_id)

            cursor.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM tasks WHERE column_id = ?", (actual_col_id,))
            pos = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO tasks (project_id, column_id, sprint_id, title, description, priority, story_points, assignee, assignee_id, phase, dependency, position, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, actual_col_id, actual_sprint_id, title, description, priority, story_points, resolved_name, resolved_id, clean_phase, dependency, pos, tags_json, now, now))
            task_id = cursor.lastrowid
            status_label = self._task_status_label(cursor, actual_sprint_id, actual_col_id)
            self._log_activity(
                cursor,
                project_id=project_id,
                task_id=task_id,
                entity_type="task",
                action="created",
                field_name="estado",
                old_value="",
                new_value=status_label,
                actor=actor,
                summary=f"Tarea creada en {status_label}: {title}",
            )
            conn.commit()

        self._maybe_daily_backup()
        return self.get_task(task_id)

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        actor = kwargs.pop("actor", "Usuario Web") or "Usuario Web"
        current = self.get_task(task_id)
        if not current:
            return None

        if "phase" in kwargs:
            kwargs["phase"] = (kwargs["phase"] or "").strip() or "Base"

        fields = []
        values = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            old_status = self._task_status_label(cursor, current.get("sprint_id"), current.get("column_id"))

            # Sincronizar coherencia entre Backlog (column_id=0 / sprint_id=None) y Tablero
            req_col = kwargs.get("column_id")
            sprint_explicit = "sprint_id" in kwargs
            req_sprint = kwargs.get("sprint_id")

            if req_col == 0:
                kwargs["column_id"] = self._get_todo_column_id(cursor, current["project_id"], current["column_id"])
                kwargs["sprint_id"] = None
            elif sprint_explicit and (req_sprint is None or req_sprint == 0):
                kwargs["sprint_id"] = None
                if "column_id" not in kwargs or req_col is None:
                    kwargs["column_id"] = self._get_todo_column_id(cursor, current["project_id"], current["column_id"])
            elif req_col is not None and req_col > 0 and not sprint_explicit and current.get("sprint_id") is None:
                active_sprint = self.get_active_sprint(current["project_id"])
                if active_sprint:
                    kwargs["sprint_id"] = active_sprint["id"]

            # Sincronizar assignee / assignee_id si alguno viene en kwargs
            if "assignee" in kwargs or "assignee_id" in kwargs:
                resolved_name, resolved_id = self._resolve_assignee(
                    cursor,
                    kwargs.get("assignee", current.get("assignee")),
                    kwargs.get("assignee_id")
                )
                kwargs["assignee"] = resolved_name
                kwargs["assignee_id"] = resolved_id

            for key, val in kwargs.items():
                if key == "tags" and isinstance(val, list):
                    fields.append("tags = ?")
                    values.append(json.dumps(val))
                elif key in ["title", "description", "priority", "story_points", "assignee", "assignee_id", "phase", "dependency", "column_id", "sprint_id", "position"]:
                    fields.append(f"{key} = ?")
                    values.append(val)

            if not fields:
                return current

            fields.append("updated_at = ?")
            values.append(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            values.append(task_id)

            query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, tuple(values))

            new_sprint_id = kwargs["sprint_id"] if "sprint_id" in kwargs else current.get("sprint_id")
            new_col_id = kwargs["column_id"] if "column_id" in kwargs else current.get("column_id")
            new_status = self._task_status_label(cursor, new_sprint_id, new_col_id)
            task_title = str(kwargs.get("title") or current.get("title") or f"Tarea #{task_id}")
            logged_specific = False

            if old_status != new_status:
                self._log_activity(
                    cursor,
                    project_id=current["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="moved",
                    field_name="estado",
                    old_value=old_status,
                    new_value=new_status,
                    actor=actor,
                    summary=f"'{task_title}' pasó de {old_status} a {new_status}",
                )
                logged_specific = True

            if "assignee" in kwargs and str(kwargs["assignee"] or "Sin asignar") != str(current.get("assignee") or "Sin asignar"):
                old_assignee = str(current.get("assignee") or "Sin asignar")
                new_assignee = str(kwargs["assignee"] or "Sin asignar")
                self._log_activity(
                    cursor,
                    project_id=current["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="assigned",
                    field_name="assignee",
                    old_value=old_assignee,
                    new_value=new_assignee,
                    actor=actor,
                    summary=f"'{task_title}' asignada: {old_assignee} -> {new_assignee}",
                )
                logged_specific = True

            if "priority" in kwargs and str(kwargs["priority"] or "") != str(current.get("priority") or ""):
                self._log_activity(
                    cursor,
                    project_id=current["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="updated",
                    field_name="priority",
                    old_value=str(current.get("priority") or ""),
                    new_value=str(kwargs["priority"] or ""),
                    actor=actor,
                    summary=f"Prioridad de '{task_title}': {current.get('priority') or ''} -> {kwargs['priority']}",
                )
                logged_specific = True

            if "phase" in kwargs and str(kwargs["phase"]) != str(current.get("phase") or "Base"):
                self._log_activity(
                    cursor,
                    project_id=current["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="updated",
                    field_name="phase",
                    old_value=str(current.get("phase") or "Base"),
                    new_value=str(kwargs["phase"]),
                    actor=actor,
                    summary=f"Etapa de '{task_title}': {current.get('phase') or 'Base'} -> {kwargs['phase']}",
                )
                logged_specific = True

            if not logged_specific:
                other_changed = []
                for k in ["title", "description", "story_points", "phase", "dependency", "tags"]:
                    if k in kwargs and kwargs[k] != current.get(k):
                        other_changed.append(k)
                if other_changed:
                    self._log_activity(
                        cursor,
                        project_id=current["project_id"],
                        task_id=task_id,
                        entity_type="task",
                        action="updated",
                        field_name=other_changed[0],
                        actor=actor,
                        summary=f"Tarea actualizada: {task_title}",
                    )

            conn.commit()

        self._maybe_daily_backup()
        return self.get_task(task_id)

    def move_task(self, task_id: int, new_column_id: int, new_position: int, actor: str = "Usuario Web") -> Optional[Dict[str, Any]]:
        current_task = self.get_task(task_id)
        if not current_task:
            return None

        moved_status = False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            old_status = self._task_status_label(cursor, current_task.get("sprint_id"), current_task.get("column_id"))

            if new_column_id == 0:
                target_col_id = self._get_todo_column_id(cursor, current_task["project_id"], current_task["column_id"])
                target_sprint_id = None
                cursor.execute("""
                    UPDATE tasks 
                    SET column_id = ?, sprint_id = NULL, position = ?, updated_at = ?
                    WHERE id = ?
                """, (target_col_id, new_position, now, task_id))
            else:
                target_sprint_id = current_task.get("sprint_id")
                if target_sprint_id is None:
                    active_sprint = self.get_active_sprint(current_task["project_id"])
                    if active_sprint:
                        target_sprint_id = active_sprint["id"]
                target_col_id = new_column_id

                cursor.execute("""
                    UPDATE tasks 
                    SET column_id = ?, sprint_id = ?, position = ?, updated_at = ?
                    WHERE id = ?
                """, (target_col_id, target_sprint_id, new_position, now, task_id))

            new_status = self._task_status_label(cursor, target_sprint_id, target_col_id)
            if old_status != new_status:
                moved_status = True
                self._log_activity(
                    cursor,
                    project_id=current_task["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="moved",
                    field_name="estado",
                    old_value=old_status,
                    new_value=new_status,
                    actor=actor,
                    summary=f"'{current_task['title']}' pasó de {old_status} a {new_status}",
                )

            conn.commit()
        if moved_status:
            self._maybe_daily_backup()
        return self.get_task(task_id)

    def delete_task(self, task_id: int, actor: str = "Usuario Web") -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            old_status = self._task_status_label(cursor, task.get("sprint_id"), task.get("column_id"))
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                self._log_activity(
                    cursor,
                    project_id=task["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="deleted",
                    field_name="estado",
                    old_value=old_status,
                    new_value="",
                    actor=actor,
                    summary=f"Tarea eliminada ({old_status}): {task['title']}",
                )
            conn.commit()
        if deleted:
            self._maybe_daily_backup()
        return deleted

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
            return [self._hydrate_task(r, "Backlog") for r in cursor.fetchall()]

    def move_task_to_sprint(self, task_id: int, sprint_id: Optional[int] = None, actor: str = "Usuario Web") -> Optional[Dict[str, Any]]:
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
            old_status = self._task_status_label(cursor, task.get("sprint_id"), task.get("column_id"))
            col_id = self._get_todo_column_id(cursor, task["project_id"], task["column_id"])

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE tasks 
                SET sprint_id = ?, column_id = ?, updated_at = ?
                WHERE id = ?
            """, (target_sprint_id, col_id, now, task_id))
            new_status = self._task_status_label(cursor, target_sprint_id, col_id)
            if old_status != new_status or task.get("sprint_id") != target_sprint_id:
                summary = (
                    f"'{task['title']}' pasó de {old_status} a {new_status}"
                    if old_status != new_status
                    else f"'{task['title']}' movida a sprint #{target_sprint_id}"
                )
                self._log_activity(
                    cursor,
                    project_id=task["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="moved",
                    field_name="estado",
                    old_value=old_status,
                    new_value=new_status,
                    actor=actor,
                    summary=summary,
                )
            conn.commit()

        self._maybe_daily_backup()
        return self.get_task(task_id)

    def move_task_to_backlog(self, task_id: int, actor: str = "Usuario Web") -> Optional[Dict[str, Any]]:
        task = self.get_task(task_id)
        if not task:
            return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            old_status = self._task_status_label(cursor, task.get("sprint_id"), task.get("column_id"))
            col_id = self._get_todo_column_id(cursor, task["project_id"], task["column_id"])
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE tasks SET column_id = ?, sprint_id = NULL, updated_at = ? WHERE id = ?", (col_id, now, task_id))
            if old_status != "Backlog":
                self._log_activity(
                    cursor,
                    project_id=task["project_id"],
                    task_id=task_id,
                    entity_type="task",
                    action="moved",
                    field_name="estado",
                    old_value=old_status,
                    new_value="Backlog",
                    actor=actor,
                    summary=f"'{task['title']}' devuelta de {old_status} a Backlog",
                )
            conn.commit()
        self._maybe_daily_backup()
        return self.get_task(task_id)

    def rename_project_phase(self, project_id: int, old_phase: str, new_phase: str, actor: str = "Usuario Web") -> int:
        clean_old = (old_phase or "").strip() or "Base"
        clean_new = (new_phase or "").strip() or "Base"
        if clean_old == clean_new:
            return 0
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET phase = ?, updated_at = ? WHERE project_id = ? AND phase = ?",
                (clean_new, now, project_id, clean_old)
            )
            count = cursor.rowcount
            if count > 0:
                self._log_activity(
                    cursor,
                    project_id=project_id,
                    entity_type="project",
                    action="updated",
                    field_name="phase",
                    old_value=clean_old,
                    new_value=clean_new,
                    actor=actor,
                    summary=f"Etapa renombrada en {count} tarea(s): '{clean_old}' -> '{clean_new}'",
                )
            conn.commit()
        if count > 0:
            self._maybe_daily_backup()
        return count

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

    def create_update(self, project_id: int, version_tag: str, title: str, content_markdown: str, sprint_id: Optional[int] = None, actor: str = "Usuario Web") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO project_updates (project_id, sprint_id, version_tag, title, content_markdown, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, sprint_id, version_tag, title, content_markdown, now))
            update_id = cursor.lastrowid
            self._log_activity(
                cursor,
                project_id=project_id,
                entity_type="release",
                action="created",
                new_value=version_tag,
                actor=actor,
                summary=f"Release {version_tag}: {title}",
            )
            conn.commit()
            cursor.execute("SELECT * FROM project_updates WHERE id = ?", (update_id,))
            row = dict(cursor.fetchone())
        self._maybe_daily_backup()
        return row

    # ==========================================
    # Métricas y Estadísticas Scrum
    # ==========================================

    def get_project_metrics(self, project_id: int) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            project = self.get_project(project_id)
            if not project:
                return {}

            # Total tareas, en progreso y completadas (excluyendo backlog del conteo de columnas activas)
            cursor.execute("""
                SELECT 
                    COUNT(t.id) as total_tasks,
                    SUM(CASE WHEN t.sprint_id IS NOT NULL AND (c.title LIKE '%Terminado%' OR c.title LIKE '%Done%') THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN t.sprint_id IS NOT NULL AND (c.title LIKE '%Progreso%' OR c.title LIKE '%Progress%') THEN 1 ELSE 0 END) as in_progress_tasks,
                    SUM(CASE WHEN t.sprint_id IS NOT NULL AND (c.title LIKE '%Hacer%' OR c.title LIKE '%To Do%') THEN 1 ELSE 0 END) as todo_tasks,
                    COALESCE(SUM(t.story_points), 0) as total_points,
                    COALESCE(SUM(CASE WHEN t.sprint_id IS NOT NULL AND (c.title LIKE '%Terminado%' OR c.title LIKE '%Done%') THEN t.story_points ELSE 0 END), 0) as completed_points
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

            # Distribución por columna / estado (incluyendo Backlog separado)
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND sprint_id IS NULL", (project_id,))
            backlog_count = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT c.title as column_title, COUNT(t.id) as task_count
                FROM columns c
                LEFT JOIN tasks t ON c.id = t.column_id AND t.project_id = ? AND t.sprint_id IS NOT NULL
                WHERE c.project_id = ?
                GROUP BY c.id, c.title
                ORDER BY c.position
            """, (project_id, project_id))
            tasks_by_status = {"Backlog (Ideas)": backlog_count}
            for r in cursor.fetchall():
                tasks_by_status[r["column_title"]] = r["task_count"]

            # Distribución por miembro / asignado
            cursor.execute("""
                SELECT COALESCE(NULLIF(TRIM(t.assignee), ''), 'Sin asignar') as member,
                       COUNT(t.id) as task_count,
                       COALESCE(SUM(t.story_points), 0) as points
                FROM tasks t
                WHERE t.project_id = ?
                GROUP BY member
                ORDER BY points DESC
            """, (project_id,))
            tasks_by_assignee = {
                r["member"]: {"tasks": r["task_count"], "points": r["points"]}
                for r in cursor.fetchall()
            }

            # Puntos y tareas por prioridad
            cursor.execute("""
                SELECT priority,
                       COALESCE(SUM(story_points), 0) as points,
                       COUNT(id) as task_count
                FROM tasks
                WHERE project_id = ?
                GROUP BY priority
            """, (project_id,))
            prio_rows = cursor.fetchall()
            points_by_priority = {r["priority"]: r["points"] for r in prio_rows}
            tasks_by_priority = {r["priority"]: r["task_count"] for r in prio_rows}

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
                "backlog_tasks": backlog_count,
                "completion_rate": completion_rate,
                "total_points": total_points,
                "completed_points": completed_points,
                "velocity_points_completed": completed_points,
                "points_by_priority": points_by_priority,
                "tasks_by_priority": tasks_by_priority,
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

    def create_bitacora_entry(self, project_id: int, content_markdown: str, title: str = "", entry_date: str = "", actor: str = "Usuario Web") -> Dict[str, Any]:
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
            preview = title.strip() or (content_markdown.strip().splitlines()[0][:80] if content_markdown.strip() else entry_date)
            self._log_activity(
                cursor,
                project_id=project_id,
                entity_type="bitacora",
                action="created",
                new_value=entry_date,
                actor=actor,
                summary=f"Entrada en bitácora: {preview}",
            )
            conn.commit()
        self._maybe_daily_backup()
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

    # ==========================================
    # Registro Histórico de Actividad (Audit Log)
    # ==========================================

    @staticmethod
    def _column_title_by_id(cursor: sqlite3.Cursor, col_id: Optional[int]) -> str:
        if not col_id:
            return "Por Hacer"
        cursor.execute("SELECT title FROM columns WHERE id = ?", (col_id,))
        row = cursor.fetchone()
        return row["title"] if row else "Por Hacer"

    def _task_status_label(self, cursor: sqlite3.Cursor, sprint_id: Optional[int], column_id: Optional[int]) -> str:
        if sprint_id is None:
            return "Backlog"
        return self._column_title_by_id(cursor, column_id)

    def _log_activity(
        self,
        cursor: sqlite3.Cursor,
        *,
        project_id: Optional[int],
        project_name: str = "",
        task_id: Optional[int] = None,
        entity_type: str,
        action: str,
        field_name: str = "",
        old_value: str = "",
        new_value: str = "",
        actor: str = "Usuario Web",
        summary: str = ""
    ):
        resolved_pname = project_name
        if not resolved_pname and project_id is not None:
            cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,))
            prow = cursor.fetchone()
            if prow:
                resolved_pname = prow["name"]

        cursor.execute(
            """INSERT INTO activity_logs
               (project_id, project_name, task_id, entity_type, action, field_name, old_value, new_value, actor, summary, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                resolved_pname,
                task_id,
                entity_type,
                action,
                field_name,
                str(old_value or ""),
                str(new_value or ""),
                actor or "Usuario Web",
                summary,
                self._utc_iso_now()
            )
        )

    def list_activity_logs(
        self,
        project_id: Optional[int] = None,
        start_iso: Optional[str] = None,
        end_iso: Optional[str] = None,
        days: Optional[int] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        where = ["1=1"]
        params: List[Any] = []

        if project_id is not None:
            where.append("project_id = ?")
            params.append(project_id)

        if not start_iso and days is not None and days > 0:
            start_iso = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

        if start_iso:
            where.append("created_at >= ?")
            params.append(start_iso)
        if end_iso:
            where.append("created_at <= ?")
            params.append(end_iso)
        if entity_type:
            where.append("entity_type = ?")
            params.append(entity_type)
        if action:
            where.append("action = ?")
            params.append(action)

        where_sql = " AND ".join(where)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT
                    COUNT(*) as total_events,
                    SUM(CASE WHEN entity_type = 'task' AND action = 'created' THEN 1 ELSE 0 END) as tasks_created,
                    SUM(CASE WHEN entity_type = 'task' AND action IN ('created', 'moved') AND field_name = 'estado' AND (new_value LIKE '%Terminado%' OR new_value LIKE '%Done%') THEN 1 ELSE 0 END) as tasks_completed,
                    SUM(CASE WHEN entity_type = 'task' AND action = 'moved' AND field_name = 'estado' AND old_value = 'Backlog' AND new_value != 'Backlog' AND new_value != '' THEN 1 ELSE 0 END) as moved_from_backlog,
                    SUM(CASE WHEN entity_type = 'project' THEN 1 ELSE 0 END) as projects_updated,
                    SUM(CASE WHEN entity_type = 'project' AND field_name = 'risks_blockers' AND new_value != '' THEN 1 ELSE 0 END) as blockers_logged
                FROM activity_logs
                WHERE {where_sql}
            """, tuple(params))
            srow = cursor.fetchone()
            summary = {
                "total_events": srow["total_events"] or 0,
                "tasks_created": srow["tasks_created"] or 0,
                "tasks_completed": srow["tasks_completed"] or 0,
                "moved_from_backlog": srow["moved_from_backlog"] or 0,
                "projects_updated": srow["projects_updated"] or 0,
                "blockers_logged": srow["blockers_logged"] or 0
            }

            safe_limit = max(1, min(limit, 500))
            cursor.execute(
                f"SELECT * FROM activity_logs WHERE {where_sql} ORDER BY created_at DESC, id DESC LIMIT ?",
                tuple(params + [safe_limit])
            )
            events = [dict(r) for r in cursor.fetchall()]

        return {"summary": summary, "events": events}

    # ==========================================
    # Respaldos Atómicos WAL (Online SQLite Backup)
    # ==========================================

    def _backups_dir(self) -> Optional[Path]:
        if not self.db_path or self.db_path == ":memory:":
            return None
        bdir = Path(self.db_path).parent / "backups"
        bdir.mkdir(parents=True, exist_ok=True)
        return bdir

    @staticmethod
    def _format_bytes(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.2f} MB"

    def _prune_auto_backups(self, bdir: Path, keep_count: int = 14):
        auto_files = sorted(bdir.glob("kanban_auto_*.db"), reverse=True)
        for old_file in auto_files[keep_count:]:
            try:
                old_file.unlink()
            except OSError:
                pass

    def _backup_metadata(self, path: Path) -> Dict[str, Any]:
        stat = path.stat()
        btype = "auto" if path.name.startswith("kanban_auto_") else "manual"
        created = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "filename": path.name,
            "backup_type": btype,
            "size_bytes": stat.st_size,
            "size_human": self._format_bytes(stat.st_size),
            "created_at": created
        }

    def create_backup(self, backup_type: str = "manual", keep_auto: int = 14) -> Dict[str, Any]:
        bdir = self._backups_dir()
        if not bdir:
            raise ValueError("Respaldo en disco no disponible para bases en memoria")

        now_local = datetime.now()
        if backup_type == "auto":
            filename = f"kanban_auto_{now_local.strftime('%Y%m%d')}.db"
        else:
            filename = f"kanban_manual_{now_local.strftime('%Y%m%d_%H%M%S')}.db"

        dest_path = bdir / filename
        tmp_path = bdir / f".{filename}.tmp"

        with self._backup_lock:
            src_conn = self._get_connection()
            try:
                dest_conn = sqlite3.connect(str(tmp_path))
                try:
                    src_conn.backup(dest_conn)
                finally:
                    dest_conn.close()
            finally:
                src_conn.close()

            os.replace(tmp_path, dest_path)
            if backup_type == "auto":
                self._prune_auto_backups(bdir, keep_count=keep_auto)
                self._last_backup_date = now_local.strftime("%Y-%m-%d")

        return self._backup_metadata(dest_path)

    def ensure_daily_backup(self, keep_auto: int = 14) -> Optional[Dict[str, Any]]:
        bdir = self._backups_dir()
        if not bdir:
            return None
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_file = bdir / f"kanban_auto_{datetime.now().strftime('%Y%m%d')}.db"
        if today_file.exists():
            self._last_backup_date = today_str
            return None
        return self.create_backup(backup_type="auto", keep_auto=keep_auto)

    def _maybe_daily_backup(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self._last_backup_date != today_str:
            try:
                self.ensure_daily_backup()
            except Exception:
                pass

    def list_backups(self) -> List[Dict[str, Any]]:
        bdir = self._backups_dir()
        if not bdir:
            return []
        files = [f for f in bdir.glob("*.db") if not f.name.startswith(".")]
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return [self._backup_metadata(f) for f in files]

    def get_backup_path(self, filename: str) -> Optional[Path]:
        bdir = self._backups_dir()
        if not bdir:
            return None
        if "/" in filename or "\\" in filename or ".." in filename or not filename.endswith(".db"):
            return None
        candidate = (bdir / filename).resolve()
        if candidate.parent != bdir.resolve() or not candidate.is_file():
            return None
        return candidate

db = Database()
