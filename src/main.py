import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from src.config import settings
from src.database import db
from src.api.routes import router as api_router
from src.mcp_server import router as mcp_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de tablas y datos semilla al arrancar el contenedor
    db.init_db()
    db.ensure_daily_backup()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Kanban Board + Native Model Context Protocol (MCP) server",
    version="1.0.0",
    lifespan=lifespan
)

# CORS para acceso local y red interna
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(api_router)
app.include_router(mcp_router)

# Montar archivos estáticos para la interfaz web (CSS, JS)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/home", status_code=307)

@app.get("/home")
async def serve_home():
    home_path = os.path.join(static_dir, "home.html")
    if os.path.exists(home_path):
        return FileResponse(home_path)
    return {"message": "Higgings Platform is running. Home UI not found."}

@app.get("/project/{project_id}")
async def serve_project(project_id: int):
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Higgings Platform is running. Project UI not found."}

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
