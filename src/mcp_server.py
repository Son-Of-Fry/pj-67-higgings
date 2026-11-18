import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from src.database import db

router = APIRouter(tags=["MCP Server"])

active_sessions: Dict[str, asyncio.Queue] = {}

_PROJECT_PROPERTIES_SCHEMA = {
    "name": {"type": "string", "description": "Nombre del proyecto"},
    "description": {"type": "string", "description": "Descripción general del propósito del proyecto"},
    "area": {"type": "string", "description": "Área del proyecto (ej. 'Riesgo de Crédito', 'Operaciones')"},
    "axis": {"type": "string", "description": "Eje estratégico del proyecto"},
    "priority": {
        "type": "string",
        "enum": ["Baja", "Media", "Alta", "Crítica"],
        "description": "Prioridad del proyecto"
    },
    "status": {
        "type": "string",
        "enum": ["En tiempo", "En riesgo", "Retrasado", "Pausado", "En mantenimiento", "Completado"],
        "description": "Estado general del proyecto"
    },
    "stakeholder": {"type": "string", "description": "Interesado o área solicitante"},
    "area_key_user": {"type": "string", "description": "Responsable del Área (Area Key User)"},
    "owner": {"type": "string", "description": "Responsable asignado del proyecto"},
    "start_date": {"type": "string", "description": "Fecha de inicio (YYYY-MM-DD)"},
    "due_date": {"type": "string", "description": "Fecha límite (YYYY-MM-DD)"},
    "next_step": {"type": "string", "description": "Siguiente paso inmediato para seguimiento"},
    "risks_blockers": {"type": "string", "description": "Riesgos o bloqueos detectados"},
    "folder_url": {"type": "string", "description": "URL a la carpeta compartida (SharePoint, Drive, OneDrive)"},
    "github_url": {"type": "string", "description": "URL al repositorio de GitHub"},
    "is_visible": {"type": "boolean", "description": "Visible en el selector superior"}
}

MCP_TOOLS = [
    {
        "name": "list_projects",
        "description": "Lista todos los proyectos registrados en Higgings, con su sprint activo y conteo de tareas.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_project",
        "description": "Obtiene la información y metadatos de un proyecto específico.",
        "inputSchema": {
            "type": "object",
            "required": ["project_id"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto a consultar"
                }
            }
        }
    },
    {
        "name": "list_users",
        "description": "Lista los usuarios del equipo registrados en Higgings para asignar tareas o proyectos.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "create_user",
        "description": "Registra un nuevo usuario en el catálogo de equipo de Higgings.",
        "inputSchema": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "description": "Nombre completo del usuario"},
                "email": {"type": "string", "description": "Correo electrónico"},
                "role": {"type": "string", "description": "Rol (ej. Responsable, Analista, Desarrollador)"},
                "area": {"type": "string", "description": "Área o departamento"}
            }
        }
    },
    {
        "name": "create_project",
        "description": "Crea un nuevo proyecto en Higgings con su tablero Kanban estándar y Sprint 1.",
        "inputSchema": {
            "type": "object",
            "required": ["name"],
            "properties": _PROJECT_PROPERTIES_SCHEMA
        }
    },
    {
        "name": "update_project",
        "description": "Actualiza metadatos ejecutivos de un proyecto existente (estado, prioridad, área, responsables, fechas, siguiente paso, bloqueos, enlaces y visibilidad).",
        "inputSchema": {
            "type": "object",
            "required": ["project_id"],
            "properties": {
                "project_id": {"type": "integer", "description": "ID del proyecto a actualizar"},
                **_PROJECT_PROPERTIES_SCHEMA
            }
        }
    },
    {
        "name": "get_board_state",
        "description": "Obtiene el estado COMPLETO del tablero Kanban de un proyecto (todas las columnas con sus tareas, responsables, story points, fases y prioridades).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 1)",
                    "default": 1
                },
                "sprint_id": {
                    "type": "integer",
                    "description": "ID del Sprint a filtrar (-1 para sprint activo, 0 para backlog, o ID específico)",
                    "default": -1
                }
            }
        }
    },
    {
        "name": "get_board_summary",
        "description": "Obtiene un resumen rápido de conteo de tareas por columna y backlog de un proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 1)",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "get_task",
        "description": "Obtiene los detalles completos de una tarea específica (título, descripción Markdown, asignado, story points, fase, tags, prioridad).",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID de la tarea a consultar"
                }
            }
        }
    },
    {
        "name": "create_task",
        "description": "Crea una nueva historia de usuario o tarea Scrum con Story Points, usuario asignado, fase, prioridad y notas Markdown.",
        "inputSchema": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto",
                    "default": 1
                },
                "title": {
                    "type": "string",
                    "description": "Título breve y conciso de la tarea"
                },
                "description": {
                    "type": "string",
                    "description": "Detalles técnicos, notas o checklists en formato Markdown"
                },
                "column_title": {
                    "type": "string",
                    "description": "Columna destino ('Backlog', 'Por Hacer', 'En Progreso', 'En Revisión', 'Terminado'). Por defecto: 'Por Hacer'",
                    "default": "Por Hacer"
                },
                "story_points": {
                    "type": "integer",
                    "description": "Estimación de esfuerzo Scrum en escala Fibonacci (1, 2, 3, 5, 8, 13). Por defecto: 1",
                    "default": 1
                },
                "assignee": {
                    "type": "string",
                    "description": "Usuario asignado (del catálogo de usuarios o 'Sin asignar')",
                    "default": "Sin asignar"
                },
                "phase": {
                    "type": "string",
                    "description": "Etapa o fase del proyecto (por defecto 'Base'; ej. 'Base', 'Mejoras', 'Mantenimiento')",
                    "default": "Base"
                },
                "dependency": {
                    "type": "string",
                    "description": "Dependencias técnicas o prerequisitos para iniciar esta tarea"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Nivel de prioridad",
                    "default": "medium"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Etiquetas de categorización (ej. ['Backend', 'SQLite'])"
                },
                "assign_to_active_sprint": {
                    "type": "boolean",
                    "description": "Si es True, la asigna al Sprint activo; si es False, la coloca en el Product Backlog.",
                    "default": True
                }
            }
        }
    },
    {
        "name": "batch_create_tasks",
        "description": "Crea múltiples tareas en una sola llamada.",
        "inputSchema": {
            "type": "object",
            "required": ["project_id", "tasks"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto"
                },
                "tasks": {
                    "type": "array",
                    "description": "Lista de tareas a crear",
                    "items": {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "column_title": {"type": "string", "default": "Por Hacer"},
                            "story_points": {"type": "integer", "default": 1},
                            "assignee": {"type": "string", "default": "Sin asignar"},
                            "phase": {"type": "string", "default": "Base"},
                            "priority": {"type": "string", "default": "medium"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    },
    {
        "name": "update_task",
        "description": "Actualiza cualquier campo de una tarea existente (título, descripción, asignado, story points, fase, prioridad, columna).",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID de la tarea a modificar"
                },
                "title": {"type": "string"},
                "description": {"type": "string"},
                "assignee": {"type": "string"},
                "phase": {"type": "string"},
                "dependency": {"type": "string"},
                "story_points": {"type": "integer"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "column_title": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    {
        "name": "update_task_status",
        "description": "Mueve una tarea a otra columna del tablero Kanban (ej. de 'En Progreso' a 'Terminado').",
        "inputSchema": {
            "type": "object",
            "required": ["task_id", "new_column_title"],
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID de la tarea a mover"
                },
                "new_column_title": {
                    "type": "string",
                    "description": "Nueva columna destino ('Por Hacer', 'En Progreso', 'En Revisión', 'Terminado')"
                }
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Elimina una tarea del tablero o backlog permanentemente.",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID de la tarea a eliminar"
                }
            }
        }
    },
    {
        "name": "list_sprints",
        "description": "Lista todos los Sprints de un proyecto con sus objetivos, fechas de entrega y estado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "create_sprint",
        "description": "Crea y planifica un nuevo ciclo Sprint para un proyecto.",
        "inputSchema": {
            "type": "object",
            "required": ["project_id", "name"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto"
                },
                "name": {
                    "type": "string",
                    "description": "Nombre del Sprint (ej. 'Sprint 2 — Autenticación')"
                },
                "goal": {
                    "type": "string",
                    "description": "Objetivo clave a entregar en este ciclo"
                },
                "target_points": {
                    "type": "integer",
                    "description": "Meta de Story Points a completar",
                    "default": 14
                }
            }
        }
    },
    {
        "name": "complete_sprint",
        "description": "Cierra y marca como completado el Sprint activo actual de un proyecto.",
        "inputSchema": {
            "type": "object",
            "required": ["sprint_id"],
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID del Sprint a completar"
                }
            }
        }
    },
    {
        "name": "log_project_release",
        "description": "Registra una entrega/versión en la Bitácora de Releases (Changelog) del proyecto.",
        "inputSchema": {
            "type": "object",
            "required": ["project_id", "version_tag", "title", "content_markdown"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto"
                },
                "version_tag": {
                    "type": "string",
                    "description": "Etiqueta de versión (ej. 'v1.0.0' o 'v0.2.0-beta')"
                },
                "title": {
                    "type": "string",
                    "description": "Título descriptivo del release"
                },
                "content_markdown": {
                    "type": "string",
                    "description": "Notas completas de la versión en formato Markdown"
                },
                "sprint_id": {
                    "type": "integer",
                    "description": "ID opcional del Sprint asociado a la entrega"
                }
            }
        }
    },
    {
        "name": "list_releases",
        "description": "Lista el histórico de versiones y notas de release de un proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "get_project_metrics",
        "description": "Obtiene las métricas generales de gestión ágil (velocidad de sprint, tasa de cumplimiento, distribución por estado y carga por miembro).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "search_tasks",
        "description": "Busca tareas en un proyecto por palabra clave en títulos, descripciones o tags.",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto",
                    "default": 1
                },
                "query": {
                    "type": "string",
                    "description": "Término de búsqueda"
                }
            }
        }
    },
    {
        "name": "get_project_readme",
        "description": "Obtiene el contenido Markdown del documento Home / README del proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 1)",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "update_project_readme",
        "description": "Actualiza el contenido Markdown del documento Home / README del proyecto.",
        "inputSchema": {
            "type": "object",
            "required": ["readme_markdown"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 1)",
                    "default": 1
                },
                "readme_markdown": {
                    "type": "string",
                    "description": "Nuevo contenido del README en formato Markdown"
                }
            }
        }
    },
    {
        "name": "list_bitacora_entries",
        "description": "Consulta todas las entradas de la bitácora estilo notebook de un proyecto.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 1)",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "add_bitacora_entry",
        "description": "Añade una nueva entrada a la bitácora del proyecto en Markdown. OBLIGATORIO: El campo 'content_markdown' DEBE seguir estrictamente esta plantilla de 6 bloques:\n**Proyecto:** [Clave y nombre]\n**Actividades:** [Qué se hizo]\n**Herramientas/IA:** [Herramientas, librerías o agentes usados]\n**Aprendí:** [Hallazgo técnico, causa raíz o decisión de arquitectura]\n**Resultado:** [Impacto o estado funcional logrado]\n**Siguiente:** [Próximos pasos]",
        "inputSchema": {
            "type": "object",
            "required": ["content_markdown"],
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID del proyecto (por defecto 67 para Higgings Platform)",
                    "default": 67
                },
                "title": {
                    "type": "string",
                    "description": "Título o encabezado de la entrada"
                },
                "content_markdown": {
                    "type": "string",
                    "description": "Contenido en Markdown siguiendo estrictamente la plantilla: **Proyecto:**, **Actividades:**, **Herramientas/IA:**, **Aprendí:**, **Resultado:**, **Siguiente:**"
                },
                "entry_date": {
                    "type": "string",
                    "description": "Fecha de la entrada en formato YYYY-MM-DD (por defecto hoy)"
                }
            }
        }
    },
    {
        "name": "update_bitacora_entry",
        "description": "Modifica una entrada existente de la bitácora por su ID. El campo 'content_markdown' debe mantener la plantilla: **Proyecto:**, **Actividades:**, **Herramientas/IA:**, **Aprendí:**, **Resultado:**, **Siguiente:**",
        "inputSchema": {
            "type": "object",
            "required": ["entry_id", "content_markdown"],
            "properties": {
                "entry_id": {
                    "type": "integer",
                    "description": "ID de la entrada de bitácora a modificar"
                },
                "title": {
                    "type": "string",
                    "description": "Nuevo título opcional"
                },
                "content_markdown": {
                    "type": "string",
                    "description": "Nuevo contenido Markdown siguiendo estrictamente la plantilla de 6 bloques"
                }
            }
        }
    },
    {
        "name": "get_activity_log",
        "description": "Consulta el registro histórico de actividad (qué tareas pasaron de Backlog a sprint o Terminado, cambios de estado en proyectos, bloqueos, releases y bitácora) con resumen de métricas y listado cronológico.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "Opcional. Filtra la actividad a un proyecto específico"
                },
                "days": {
                    "type": "integer",
                    "description": "Cantidad de días hacia atrás a consultar (ej. 1 para últimas 24h, 7 para última semana)",
                    "default": 7
                },
                "entity_type": {
                    "type": "string",
                    "enum": ["task", "project", "sprint", "release", "bitacora"],
                    "description": "Opcional. Filtrar por tipo de entidad"
                },
                "limit": {
                    "type": "integer",
                    "description": "Máximo de eventos a devolver (por defecto 100, máx 500)",
                    "default": 100
                }
            }
        }
    }
]

def _resolve_column_id(project_id: int, column_title: str) -> int:
    clean = (column_title or "").strip().lower()
    if clean in ("backlog", "backlog (ideas)", "ideas", "product backlog"):
        return 0
    board = db.get_project_board(project_id)
    if not board:
        return 1
    for col in board.get("columns", []):
        if col["title"].lower() == clean:
            return col["id"]
    for col in board.get("columns", []):
        if not col.get("is_backlog"):
            return col["id"]
    return 1

def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    try:
        if tool_name == "list_users":
            users = db.list_users(include_inactive=False)
            return json.dumps(users, indent=2, ensure_ascii=False)

        elif tool_name == "create_user":
            u = db.create_user(
                name=arguments["name"],
                email=arguments.get("email", ""),
                role=arguments.get("role", "Miembro"),
                area=arguments.get("area", "")
            )
            return f"✅ Usuario #{u['id']} '{u['name']}' registrado exitosamente."

        elif tool_name == "list_projects":
            projects = db.list_projects()
            return json.dumps(projects, indent=2, ensure_ascii=False)

        elif tool_name == "get_project":
            pid = arguments["project_id"]
            p = db.get_project(pid)
            if not p:
                return f"Error: Proyecto #{pid} no encontrado."
            active_sprint = db.get_active_sprint(pid)
            p["active_sprint"] = active_sprint
            return json.dumps(p, indent=2, ensure_ascii=False)

        elif tool_name == "create_project":
            p = db.create_project(
                name=arguments["name"],
                description=arguments.get("description", ""),
                github_url=arguments.get("github_url", ""),
                folder_url=arguments.get("folder_url", ""),
                area=arguments.get("area", ""),
                axis=arguments.get("axis", "Abierto"),
                priority=arguments.get("priority", "Media"),
                status=arguments.get("status", "En tiempo"),
                stakeholder=arguments.get("stakeholder", ""),
                area_key_user=arguments.get("area_key_user", ""),
                owner=arguments.get("owner", ""),
                start_date=arguments.get("start_date", ""),
                due_date=arguments.get("due_date", ""),
                next_step=arguments.get("next_step", ""),
                risks_blockers=arguments.get("risks_blockers", ""),
                is_visible=arguments.get("is_visible", True),
                actor="MCP"
            )
            return f"✅ Proyecto #{p['id']} '{p['name']}' creado exitosamente en Higgings con su tablero y Sprint 1."

        elif tool_name == "update_project":
            pid = arguments["project_id"]
            update_fields = {k: arguments[k] for k in _PROJECT_PROPERTIES_SCHEMA.keys() if k in arguments}
            p = db.update_project(pid, actor="MCP", **update_fields)
            if not p:
                return f"Error: Proyecto #{pid} no encontrado."
            return f"✅ Proyecto #{pid} ('{p['name']}') actualizado exitosamente."

        elif tool_name == "get_board_state":
            pid = arguments.get("project_id", 1)
            sprint_id = arguments.get("sprint_id", -1)
            board = db.get_project_board(pid, sprint_id=sprint_id)
            if not board:
                return f"Error: Proyecto #{pid} no encontrado."
            return json.dumps(board, indent=2, ensure_ascii=False)

        elif tool_name == "get_board_summary":
            pid = arguments.get("project_id", 1)
            board = db.get_project_board(pid)
            if not board:
                return f"Error: Proyecto #{pid} no encontrado."
            summary = {
                "project": board["project"]["name"],
                "active_sprint": board["active_sprint"]["name"] if board["active_sprint"] else "Sin Sprint Activo",
                "backlog_tasks": board["backlog_count"],
                "columns": {col["title"]: len(col["tasks"]) for col in board["columns"]}
            }
            return json.dumps(summary, indent=2, ensure_ascii=False)

        elif tool_name == "get_task":
            task_id = arguments["task_id"]
            task = db.get_task(task_id)
            if not task:
                return f"Error: Tarea #{task_id} no encontrada."
            return json.dumps(task, indent=2, ensure_ascii=False)

        elif tool_name == "create_task":
            pid = arguments.get("project_id", 1)
            title = arguments["title"]
            col_name = arguments.get("column_title", "Por Hacer")
            column_id = _resolve_column_id(pid, col_name)
            points = arguments.get("story_points", 1)
            assign_sprint = arguments.get("assign_to_active_sprint", True)

            sprint_id = None
            if assign_sprint and column_id != 0:
                active_sprint = db.get_active_sprint(pid)
                if active_sprint:
                    sprint_id = active_sprint["id"]

            task = db.create_task(
                project_id=pid,
                column_id=column_id,
                title=title,
                description=arguments.get("description", ""),
                priority=arguments.get("priority", "medium"),
                story_points=points,
                sprint_id=sprint_id,
                tags=arguments.get("tags", []),
                assignee=arguments.get("assignee", "Sin asignar"),
                phase=arguments.get("phase", "Base"),
                dependency=arguments.get("dependency", ""),
                actor="MCP"
            )
            location = f"al Sprint #{sprint_id}" if task.get("sprint_id") else "al Product Backlog"
            return f"✅ Tarea #{task['id']} ('{title}') creada y asignada a [{task['assignee']}] con {points} Story Points en {location}."

        elif tool_name == "batch_create_tasks":
            pid = arguments["project_id"]
            tasks_input = arguments.get("tasks", [])
            active_sprint = db.get_active_sprint(pid)
            default_sprint_id = active_sprint["id"] if active_sprint else None

            created_tasks = []
            for item in tasks_input:
                col_name = item.get("column_title", "Por Hacer")
                column_id = _resolve_column_id(pid, col_name)
                sprint_id = None if column_id == 0 else default_sprint_id
                t = db.create_task(
                    project_id=pid,
                    column_id=column_id,
                    title=item["title"],
                    description=item.get("description", ""),
                    priority=item.get("priority", "medium"),
                    story_points=item.get("story_points", 1),
                    sprint_id=sprint_id,
                    tags=item.get("tags", []),
                    assignee=item.get("assignee", "Sin asignar"),
                    phase=item.get("phase", "Base"),
                    dependency=item.get("dependency", ""),
                    actor="MCP"
                )
                created_tasks.append(f"#{t['id']} {t['title']} ({t['story_points']} pts)")

            return f"✅ Se crearon exitosamente {len(created_tasks)} tareas en el proyecto #{pid}:\n" + "\n".join(f"- {ct}" for ct in created_tasks)

        elif tool_name == "update_task":
            task_id = arguments["task_id"]
            task = db.get_task(task_id)
            if not task:
                return f"Error: No se encontró la tarea #{task_id}"

            update_data = {}
            for k in ["title", "description", "assignee", "phase", "dependency", "story_points", "priority", "tags", "sprint_id"]:
                if k in arguments:
                    update_data[k] = arguments[k]

            if "column_title" in arguments:
                col_id = _resolve_column_id(task["project_id"], arguments["column_title"])
                update_data["column_id"] = col_id

            updated = db.update_task(task_id, actor="MCP", **update_data)
            return f"✅ Tarea #{task_id} actualizada correctamente."

        elif tool_name == "update_task_status":
            task_id = arguments["task_id"]
            new_col_name = arguments["new_column_title"]
            task = db.get_task(task_id)
            if not task:
                return f"Error: No se encontró la tarea #{task_id}"

            new_col_id = _resolve_column_id(task["project_id"], new_col_name)
            db.move_task(task_id, new_col_id, 999, actor="MCP")
            return f"✅ Tarea #{task_id} movida a la columna '{new_col_name}'."

        elif tool_name == "delete_task":
            task_id = arguments["task_id"]
            ok = db.delete_task(task_id, actor="MCP")
            if ok:
                return f"✅ Tarea #{task_id} eliminada exitosamente."
            return f"Error: No se pudo eliminar la tarea #{task_id}."

        elif tool_name == "list_sprints":
            sprints = db.list_sprints(arguments.get("project_id", 1))
            return json.dumps(sprints, indent=2, ensure_ascii=False)

        elif tool_name == "create_sprint":
            sprint = db.create_sprint(
                project_id=arguments["project_id"],
                name=arguments["name"],
                goal=arguments.get("goal", ""),
                target_points=arguments.get("target_points", 14)
            )
            return f"✅ Sprint #{sprint['id']} '{sprint['name']}' planificado exitosamente."

        elif tool_name == "complete_sprint":
            sprint = db.complete_sprint(arguments["sprint_id"], actor="MCP")
            if not sprint:
                return "Error: Sprint no encontrado."
            return f"✅ Sprint #{sprint['id']} '{sprint['name']}' completado. Puntos conseguidos: {sprint['completed_points']} de {sprint['total_points']}."

        elif tool_name == "log_project_release":
            update = db.create_update(
                project_id=arguments["project_id"],
                version_tag=arguments["version_tag"],
                title=arguments["title"],
                content_markdown=arguments["content_markdown"],
                sprint_id=arguments.get("sprint_id"),
                actor="MCP"
            )
            return f"✅ Release registrado en Higgings: [{update['version_tag']}] {update['title']}"

        elif tool_name == "list_releases":
            updates = db.list_updates(arguments.get("project_id", 1))
            return json.dumps(updates, indent=2, ensure_ascii=False)

        elif tool_name == "get_project_metrics":
            metrics = db.get_project_metrics(arguments.get("project_id", 1))
            return json.dumps(metrics, indent=2, ensure_ascii=False)

        elif tool_name == "search_tasks":
            pid = arguments.get("project_id", 1)
            q = arguments["query"].lower().strip()
            board = db.get_project_board(pid, sprint_id=-1)
            results = []
            if board:
                for col in board.get("columns", []):
                    for t in col.get("tasks", []):
                        title = t.get("title", "").lower()
                        desc = t.get("description", "").lower()
                        tags_str = str(t.get("tags", "")).lower()
                        if q in title or q in desc or q in tags_str:
                            results.append({
                                "id": t["id"],
                                "title": t["title"],
                                "column": col["title"],
                                "story_points": t["story_points"],
                                "assignee": t["assignee"],
                                "priority": t["priority"]
                            })
            return json.dumps(results, indent=2, ensure_ascii=False)

        elif tool_name == "get_project_readme":
            pid = arguments.get("project_id", 1)
            readme = db.get_project_readme(pid)
            return json.dumps({"project_id": pid, "readme_markdown": readme}, indent=2, ensure_ascii=False)

        elif tool_name == "update_project_readme":
            pid = arguments.get("project_id", 1)
            content = arguments.get("readme_markdown", "")
            ok = db.update_project_readme(pid, content)
            if ok:
                return f"README del proyecto #{pid} actualizado exitosamente."
            else:
                return f"Error: No se pudo actualizar el README del proyecto #{pid}."

        elif tool_name == "list_bitacora_entries":
            pid = arguments.get("project_id", 1)
            entries = db.list_bitacora_entries(pid)
            return json.dumps(entries, indent=2, ensure_ascii=False)

        elif tool_name == "add_bitacora_entry":
            pid = arguments.get("project_id", 1)
            content = arguments.get("content_markdown", "")
            title = arguments.get("title", "")
            date_str = arguments.get("entry_date", "")
            entry = db.create_bitacora_entry(pid, content, title, date_str, actor="MCP")
            return json.dumps({"status": "created", "entry": entry}, indent=2, ensure_ascii=False)

        elif tool_name == "update_bitacora_entry":
            eid = arguments["entry_id"]
            content = arguments.get("content_markdown", "")
            title = arguments.get("title")
            entry = db.update_bitacora_entry(eid, content, title)
            if entry:
                return json.dumps({"status": "updated", "entry": entry}, indent=2, ensure_ascii=False)
            return f"Error: No se encontró la entrada de bitácora #{eid}."

        elif tool_name == "get_activity_log":
            result = db.list_activity_logs(
                project_id=arguments.get("project_id"),
                days=arguments.get("days", 7),
                entity_type=arguments.get("entity_type"),
                limit=arguments.get("limit", 100),
            )
            return json.dumps(result, indent=2, ensure_ascii=False)

        else:
            return f"Error: Herramienta desconocida '{tool_name}'"

    except Exception as e:
        return f"Error ejecutando herramienta {tool_name}: {str(e)}"

def process_jsonrpc(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "higgings-agile-mcp",
                    "version": "2.1.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": MCP_TOOLS
            }
        }

    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        output = handle_tool_call(tool_name, args)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": output
                    }
                ],
                "isError": False
            }
        }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        }

    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        return None

@router.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    active_sessions[session_id] = queue

    async def event_generator():
        yield f"event: endpoint\ndata: /messages?session_id={session_id}\n\n"
        try:
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            pass
        finally:
            active_sessions.pop(session_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/messages")
@router.post("/sse")
@router.post("/mcp")
async def post_messages(request: Request, session_id: Optional[str] = None):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not session_id:
        session_id = request.query_params.get("session_id")

    # Identificar la sesión SSE correspondiente
    target_queue = None
    if session_id and session_id in active_sessions:
        target_queue = active_sessions[session_id]
    elif len(active_sessions) == 1:
        target_queue = next(iter(active_sessions.values()))
    elif len(active_sessions) > 1:
        target_queue = list(active_sessions.values())[-1]

    response = process_jsonrpc(body)

    # Si hay respuesta y stream SSE activo, enviar inmediatamente al canal SSE
    if target_queue and response:
        await target_queue.put(response)

    if response:
        return JSONResponse(response)
    return JSONResponse({"status": "acknowledged"})
