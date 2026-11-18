import sqlite3
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from src.database import db
from src.models import (
    UserResponse, UserCreate, UserUpdate,
    ProjectResponse, ProjectCreate, ProjectUpdate, ProjectReadmeUpdate,
    SprintResponse, SprintCreate, SprintUpdate, SprintBase,
    BoardViewResponse,
    TaskResponse, TaskCreate, TaskUpdate, TaskMove,
    DocResponse, DocCreate, DocUpdate, DocBase,
    UpdateLogResponse, UpdateLogCreate, UpdateLogBase,
    ProjectMetricsResponse,
    BitacoraEntryResponse, BitacoraEntryCreate, BitacoraEntryUpdate,
    BackupInfoResponse, ActivityListResponse, PhaseRenameRequest
)

router = APIRouter(prefix="/api", tags=["Kanban & Scrum API"])

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "PJ-67 Agile Platform & MCP"}

# ==========================================
# Usuarios / Equipo
# ==========================================

@router.get("/users", response_model=List[UserResponse])
def list_users(include_inactive: bool = Query(False)):
    return db.list_users(include_inactive=include_inactive)

@router.post("/users", response_model=UserResponse)
def create_user(payload: UserCreate):
    try:
        return db.create_user(
            name=payload.name,
            email=payload.email or "",
            role=payload.role or "Miembro",
            area=payload.area or "",
            color=payload.color or "#0c66e4",
            is_active=True if payload.is_active is None else payload.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese nombre")

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        u = db.update_user(user_id, **update_data)
        if not u:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return u
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe otro usuario con ese nombre")

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    ok = db.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"status": "success", "message": f"Usuario {user_id} eliminado"}

# ==========================================
# Proyectos
# ==========================================

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects():
    return db.list_projects()

@router.post("/projects", response_model=ProjectResponse)
def create_project(payload: ProjectCreate):
    return db.create_project(
        name=payload.name,
        description=payload.description or "",
        github_url=payload.github_url or "",
        folder_url=payload.folder_url or "",
        readme_markdown=payload.readme_markdown or "",
        difficulty=payload.difficulty or 3,
        priority=payload.priority or "Media",
        theme=payload.theme or "",
        area=payload.area or payload.theme or "",
        axis=payload.axis or "Abierto",
        status=payload.status or "En tiempo",
        stakeholder=payload.stakeholder or "",
        area_key_user=payload.area_key_user or "",
        owner=payload.owner or "",
        start_date=payload.start_date or "",
        due_date=payload.due_date or "",
        next_step=payload.next_step or "",
        risks_blockers=payload.risks_blockers or "",
        is_visible=True if payload.is_visible is None else payload.is_visible,
        extra_data=payload.extra_data or "{}"
    )

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    p = db.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return p

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    p = db.update_project(project_id, **update_data)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return p

@router.delete("/projects/{project_id}")
def delete_project(project_id: int):
    ok = db.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"status": "success", "message": f"Proyecto {project_id} eliminado exitosamente"}

@router.get("/projects/{project_id}/readme")
def get_project_readme(project_id: int):
    p = db.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"project_id": project_id, "readme_markdown": p.get("readme_markdown") or ""}

@router.put("/projects/{project_id}/readme")
def update_project_readme(project_id: int, payload: ProjectReadmeUpdate):
    p = db.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.update_project_readme(project_id, payload.readme_markdown)
    return {"project_id": project_id, "readme_markdown": payload.readme_markdown}

@router.get("/projects/{project_id}/backlog", response_model=List[TaskResponse])
def get_project_backlog(project_id: int):
    return db.get_backlog_tasks(project_id)

# ==========================================
# Tablero y Sprints
# ==========================================

@router.get("/projects/{project_id}/board", response_model=BoardViewResponse)
def get_project_board(project_id: int, sprint_id: Optional[int] = Query(-1)):
    """
    sprint_id = -1 -> Sprint Activo
    sprint_id = 0  -> Product Backlog
    sprint_id > 0  -> Sprint específico
    """
    board = db.get_project_board(project_id, sprint_id)
    if not board:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return board

@router.get("/projects/{project_id}/sprints", response_model=List[SprintResponse])
def list_sprints(project_id: int):
    return db.list_sprints(project_id)

@router.post("/projects/{project_id}/sprints", response_model=SprintResponse)
def create_sprint(project_id: int, payload: SprintBase):
    return db.create_sprint(
        project_id=project_id,
        name=payload.name,
        goal=payload.goal or "",
        start_date=payload.start_date or "",
        end_date=payload.end_date or "",
        target_points=payload.target_points or 0
    )

@router.put("/sprints/{sprint_id}/complete", response_model=SprintResponse)
def complete_sprint(sprint_id: int):
    s = db.complete_sprint(sprint_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return s

# ==========================================
# Tareas
# ==========================================

@router.post("/tasks", response_model=TaskResponse)
def create_task(payload: TaskCreate):
    return db.create_task(
        project_id=payload.project_id,
        column_id=payload.column_id,
        title=payload.title,
        description=payload.description or "",
        priority=payload.priority or "medium",
        story_points=payload.story_points,
        sprint_id=payload.sprint_id,
        tags=payload.tags or [],
        assignee=payload.assignee or "Sin asignar",
        assignee_id=payload.assignee_id,
        phase=payload.phase or "Base",
        dependency=payload.dependency or ""
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    task = db.update_task(task_id, **update_data)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.put("/tasks/{task_id}/move", response_model=TaskResponse)
def move_task(task_id: int, payload: TaskMove):
    task = db.move_task(task_id, payload.column_id, payload.new_position)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    success = db.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"success": True, "message": f"Tarea {task_id} eliminada"}

@router.post("/tasks/{task_id}/move-to-sprint", response_model=TaskResponse)
def move_task_to_sprint(task_id: int, sprint_id: Optional[int] = None):
    task = db.move_task_to_sprint(task_id, sprint_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.post("/tasks/{task_id}/move-to-backlog", response_model=TaskResponse)
def move_task_to_backlog(task_id: int):
    task = db.move_task_to_backlog(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

# ==========================================
# Documentación Wiki
# ==========================================

@router.get("/projects/{project_id}/docs", response_model=List[DocResponse])
def list_project_docs(project_id: int):
    return db.list_docs(project_id)

@router.post("/projects/{project_id}/docs", response_model=DocResponse)
def create_project_doc(project_id: int, payload: DocBase):
    return db.create_doc(
        project_id=project_id,
        title=payload.title,
        category=payload.category or "General",
        content_markdown=payload.content_markdown or ""
    )

@router.get("/docs/{doc_id}", response_model=DocResponse)
def get_doc(doc_id: int):
    d = db.get_doc(doc_id)
    if not d:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return d

@router.put("/docs/{doc_id}", response_model=DocResponse)
def update_doc(doc_id: int, payload: DocUpdate):
    d = db.update_doc(
        doc_id=doc_id,
        title=payload.title,
        category=payload.category,
        content_markdown=payload.content_markdown
    )
    if not d:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return d

@router.delete("/docs/{doc_id}")
def delete_doc(doc_id: int):
    success = db.delete_doc(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {"success": True, "message": f"Documento {doc_id} eliminado"}

# ==========================================
# Bitácora de Actualizaciones (Changelog)
# ==========================================

@router.get("/projects/{project_id}/updates", response_model=List[UpdateLogResponse])
def list_project_updates(project_id: int):
    return db.list_updates(project_id)

@router.post("/projects/{project_id}/updates", response_model=UpdateLogResponse)
def create_project_update(project_id: int, payload: UpdateLogBase, sprint_id: Optional[int] = None):
    return db.create_update(
        project_id=project_id,
        version_tag=payload.version_tag,
        title=payload.title,
        content_markdown=payload.content_markdown,
        sprint_id=sprint_id
    )

# ==========================================
# Métricas y Estadísticas
# ==========================================

@router.get("/projects/{project_id}/metrics", response_model=ProjectMetricsResponse)
def get_project_metrics(project_id: int):
    metrics = db.get_project_metrics(project_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return metrics

# ==========================================
# Bitácora Interactiva (Notebook Markdown)
# ==========================================

@router.get("/projects/{project_id}/bitacora", response_model=List[BitacoraEntryResponse])
def list_project_bitacora(project_id: int):
    return db.list_bitacora_entries(project_id)

@router.post("/projects/{project_id}/bitacora", response_model=BitacoraEntryResponse)
def create_project_bitacora(project_id: int, payload: BitacoraEntryCreate):
    return db.create_bitacora_entry(
        project_id=project_id,
        content_markdown=payload.content_markdown,
        title=payload.title or "",
        entry_date=payload.entry_date or ""
    )

@router.put("/bitacora/{entry_id}", response_model=BitacoraEntryResponse)
def update_bitacora_entry(entry_id: int, payload: BitacoraEntryUpdate):
    entry = db.update_bitacora_entry(
        entry_id=entry_id,
        content_markdown=payload.content_markdown,
        title=payload.title,
        entry_date=payload.entry_date
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada de bitácora no encontrada")
    return entry

@router.delete("/bitacora/{entry_id}")
def delete_bitacora_entry(entry_id: int):
    success = db.delete_bitacora_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrada de bitácora no encontrada")
    return {"success": True, "message": f"Entrada {entry_id} eliminada"}

# ==========================================
# Respaldos Atómicos WAL y Registro Histórico de Actividad
# ==========================================

@router.get("/backups", response_model=List[BackupInfoResponse])
def list_backups():
    return db.list_backups()

@router.post("/backups", response_model=BackupInfoResponse)
def create_backup():
    try:
        return db.create_backup(backup_type="manual")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo generar el respaldo: {str(e)}")

@router.get("/backups/{filename}/download")
def download_backup(filename: str):
    if "/" in filename or "\\" in filename or ".." in filename or not filename.endswith(".db"):
        raise HTTPException(status_code=400, detail="Nombre de respaldo inválido")
    path = db.get_backup_path(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Respaldo no encontrado")
    return FileResponse(
        path=str(path),
        media_type="application/octet-stream",
        filename=path.name,
    )

@router.get("/activity", response_model=ActivityListResponse)
def list_activity_logs(
    project_id: Optional[int] = Query(None),
    start_iso: Optional[str] = Query(None),
    end_iso: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1, le=365),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=500),
):
    return db.list_activity_logs(
        project_id=project_id,
        start_iso=start_iso,
        end_iso=end_iso,
        days=days,
        entity_type=entity_type,
        action=action,
        limit=limit,
    )

@router.put("/projects/{project_id}/phases/rename")
def rename_project_phase(project_id: int, payload: PhaseRenameRequest):
    old_name = (payload.old_phase or "").strip()
    new_name = (payload.new_phase or "").strip()
    if not old_name or not new_name:
        raise HTTPException(status_code=400, detail="El nombre de etapa no puede estar vacío")
    updated_count = db.rename_project_phase(project_id, old_name, new_name)
    return {"success": True, "updated_count": updated_count, "old_phase": old_name, "new_phase": new_name}
