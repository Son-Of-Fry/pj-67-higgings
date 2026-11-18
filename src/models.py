from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Modelos de Usuarios / Equipo
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field("", max_length=150)
    role: Optional[str] = Field("Miembro", max_length=80)
    area: Optional[str] = Field("", max_length=100)
    color: Optional[str] = Field("#0c66e4", max_length=20)
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    area: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: str

# Modelos de Proyecto
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field("", max_length=500)
    github_url: Optional[str] = Field("", description="URL directa al repositorio GitHub")
    folder_url: Optional[str] = Field("", description="URL de carpeta compartida (SharePoint, Google Drive, OneDrive)")
    readme_markdown: Optional[str] = Field("", description="Documento Home/README en Markdown")
    priority: Optional[str] = Field("Media", description="Prioridad del proyecto (Baja, Media, Alta, Crítica)")
    area: Optional[str] = Field("", description="Área del proyecto (ej: Riesgo de Crédito, Finanzas)")
    axis: Optional[str] = Field("Abierto", description="Eje del proyecto")
    status: Optional[str] = Field("En tiempo", description="Estado general (En tiempo, En riesgo, Retrasado, Pausado, En mantenimiento, Completado)")
    stakeholder: Optional[str] = Field("", max_length=150, description="Interesado o área solicitante del proyecto")
    area_key_user: Optional[str] = Field("", max_length=150, description="Responsable del Área (Area Key User)")
    owner: Optional[str] = Field("", max_length=100, description="Responsable asignado al proyecto")
    start_date: Optional[str] = Field("", description="Fecha de inicio (YYYY-MM-DD)")
    due_date: Optional[str] = Field("", description="Fecha límite (YYYY-MM-DD)")
    next_step: Optional[str] = Field("", description="Siguiente paso inmediato para seguimiento")
    risks_blockers: Optional[str] = Field("", description="Riesgos o bloqueos detectados")
    is_visible: Optional[bool] = Field(True, description="Indica si el proyecto es visible en la lista desplegable")
    difficulty: Optional[int] = Field(3, description="Campo legacy de dificultad (1-5)")
    theme: Optional[str] = Field("", description="Campo legacy de tema (sincronizado con area)")
    extra_data: Optional[str] = Field("{}", description="Metadatos adicionales en JSON")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    folder_url: Optional[str] = None
    readme_markdown: Optional[str] = None
    priority: Optional[str] = None
    area: Optional[str] = None
    axis: Optional[str] = None
    status: Optional[str] = None
    stakeholder: Optional[str] = None
    area_key_user: Optional[str] = None
    owner: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    next_step: Optional[str] = None
    risks_blockers: Optional[str] = None
    is_visible: Optional[bool] = None
    difficulty: Optional[int] = None
    theme: Optional[str] = None
    extra_data: Optional[str] = None

class ProjectReadmeUpdate(BaseModel):
    readme_markdown: str

class ProjectResponse(ProjectBase):
    id: int
    created_at: str
    active_sprint_name: Optional[str] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    progress_percent: int = 0
    last_bitacora_date: Optional[str] = None
    total_docs: int = 0

# Modelos de Sprints (Scrum)
class SprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    goal: Optional[str] = Field("", max_length=500)
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    target_points: Optional[int] = 0

class SprintCreate(SprintBase):
    project_id: int

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None # planned, active, completed
    target_points: Optional[int] = None

class SprintResponse(SprintBase):
    id: int
    project_id: int
    status: str
    completed_points: int = 0
    total_points: int = 0
    created_at: str

# Modelos de Tareas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", description="Documento de la tarea en Markdown")
    priority: str = Field("medium", description="low, medium, high, urgent")
    story_points: int = Field(1, ge=0, le=55, description="Puntos de historia Scrum (1, 2, 3, 5, 8...)")
    assignee: Optional[str] = Field("Sin asignar", description="Usuario o responsable asignado")
    assignee_id: Optional[int] = Field(None, description="ID opcional del usuario asignado")
    phase: Optional[str] = Field("Base", description="Etapa o fase de entrega (por defecto Base)")
    dependency: Optional[str] = Field("", description="Dependencia con otra tarea (ej. Requiere PJ-67-1)")
    tags: List[str] = Field(default_factory=list)

class TaskCreate(TaskBase):
    project_id: int
    column_id: int
    sprint_id: Optional[int] = None # Si es None, va al Product Backlog

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    story_points: Optional[int] = None
    assignee: Optional[str] = None
    assignee_id: Optional[int] = None
    phase: Optional[str] = None
    dependency: Optional[str] = None
    tags: Optional[List[str]] = None
    column_id: Optional[int] = None
    sprint_id: Optional[int] = None
    position: Optional[int] = None

class TaskMove(BaseModel):
    column_id: int
    new_position: int

class TaskResponse(BaseModel):
    id: int
    project_id: int
    column_id: int
    sprint_id: Optional[int] = None
    title: str
    description: str
    priority: str
    story_points: int
    assignee: str = "Sin asignar"
    assignee_id: Optional[int] = None
    effective_status: Optional[str] = None
    phase: str = "Base"
    dependency: str = ""
    position: int
    tags: List[str]
    created_at: str
    updated_at: str

# Columnas y Tablero
class ColumnResponse(BaseModel):
    id: int
    project_id: int
    title: str
    position: int
    is_backlog: bool = False
    tasks: List[TaskResponse] = []

class BoardViewResponse(BaseModel):
    project: ProjectResponse
    active_sprint: Optional[SprintResponse] = None
    columns: List[ColumnResponse] = []
    backlog_count: int = 0

# Documentación Wiki del Proyecto
class DocBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field("General", max_length=50)
    content_markdown: str = Field("", description="Contenido completo del artículo Wiki en Markdown")

class DocCreate(DocBase):
    project_id: int

class DocUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content_markdown: Optional[str] = None

class DocResponse(DocBase):
    id: int
    project_id: int
    created_at: str
    updated_at: str

# Bitácora de Actualizaciones (Changelog)
class UpdateLogBase(BaseModel):
    version_tag: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    content_markdown: str = Field(..., description="Notas de la versión en Markdown")

class UpdateLogCreate(UpdateLogBase):
    project_id: int
    sprint_id: Optional[int] = None

class UpdateLogResponse(UpdateLogBase):
    id: int
    project_id: int
    sprint_id: Optional[int] = None
    created_at: str

# Métricas Scrum Generales del Proyecto
class ProjectMetricsResponse(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int = 0
    todo_tasks: int = 0
    backlog_tasks: int = 0
    completion_rate: float
    total_points: int
    completed_points: int
    velocity_points_completed: int
    points_by_priority: Dict[str, int]
    tasks_by_priority: Dict[str, int] = {}
    tasks_by_status: Dict[str, int] = {}
    tasks_by_assignee: Dict[str, Dict[str, Any]] = {}
    tasks_by_tag: Dict[str, int]

# Modelos de Bitácora (Notebook Markdown)
class BitacoraEntryBase(BaseModel):
    title: Optional[str] = Field("", max_length=200)
    content_markdown: str = Field(..., min_length=1)
    entry_date: Optional[str] = ""

class BitacoraEntryCreate(BitacoraEntryBase):
    pass

class BitacoraEntryUpdate(BaseModel):
    title: Optional[str] = None
    content_markdown: Optional[str] = None
    entry_date: Optional[str] = None

class BitacoraEntryResponse(BitacoraEntryBase):
    id: int
    project_id: int
    position: int = 0
    created_at: str
    updated_at: str

# Modelos de Respaldos y Registro Histórico de Actividad
class BackupInfoResponse(BaseModel):
    filename: str
    backup_type: str  # auto | manual
    size_bytes: int
    size_human: str
    created_at: str

class ActivityLogItem(BaseModel):
    id: int
    project_id: Optional[int] = None
    project_name: str = ""
    task_id: Optional[int] = None
    entity_type: str
    action: str
    field_name: str = ""
    old_value: str = ""
    new_value: str = ""
    actor: str = "Usuario Web"
    summary: str
    created_at: str

class ActivitySummary(BaseModel):
    total_events: int = 0
    tasks_created: int = 0
    tasks_completed: int = 0
    moved_from_backlog: int = 0
    projects_updated: int = 0
    blockers_logged: int = 0

class ActivityListResponse(BaseModel):
    summary: ActivitySummary
    events: List[ActivityLogItem] = []

class PhaseRenameRequest(BaseModel):
    old_phase: str = Field(..., min_length=1, max_length=100)
    new_phase: str = Field(..., min_length=1, max_length=100)
