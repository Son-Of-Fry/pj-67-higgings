import openpyxl
import json

wb = openpyxl.load_workbook('personal.xlsx')
ws = wb['proyectos']
rows = list(ws.iter_rows(values_only=True))

def esc(s):
    if s is None:
        return "''"
    return "'" + str(s).replace("'", "''") + "'"

lines = [
    "-- Re-alineación e importación exacta de proyectos en Huggins",
    "BEGIN TRANSACTION;",
    "",
    "-- 1. Re-alinear proyectos existentes para liberar IDs 1, 2, 3, 4",
    "UPDATE tasks SET project_id = 99 WHERE project_id = 4;",
    "UPDATE columns SET project_id = 99 WHERE project_id = 4;",
    "UPDATE sprints SET project_id = 99 WHERE project_id = 4;",
    "UPDATE project_docs SET project_id = 99 WHERE project_id = 4;",
    "UPDATE bitacora_entries SET project_id = 99 WHERE project_id = 4;",
    "UPDATE project_updates SET project_id = 99 WHERE project_id = 4;",
    "UPDATE projects SET id = 99, name = 'hojademaiz' WHERE id = 4;",
    "",
    "UPDATE tasks SET project_id = 65 WHERE project_id = 3;",
    "UPDATE columns SET project_id = 65 WHERE project_id = 3;",
    "UPDATE sprints SET project_id = 65 WHERE project_id = 3;",
    "UPDATE project_docs SET project_id = 65 WHERE project_id = 3;",
    "UPDATE bitacora_entries SET project_id = 65 WHERE project_id = 3;",
    "UPDATE project_updates SET project_id = 65 WHERE project_id = 3;",
    "UPDATE projects SET id = 65, name = 'Retail MLOps', theme = 'Machine Learning E2E (Pricing)', difficulty = 5, axis = 'E2E / MLOps' WHERE id = 3;",
    "",
    "UPDATE tasks SET project_id = 67 WHERE project_id = 2;",
    "UPDATE columns SET project_id = 67 WHERE project_id = 2;",
    "UPDATE sprints SET project_id = 67 WHERE project_id = 2;",
    "UPDATE project_docs SET project_id = 67 WHERE project_id = 2;",
    "UPDATE bitacora_entries SET project_id = 67 WHERE project_id = 2;",
    "UPDATE project_updates SET project_id = 67 WHERE project_id = 2;",
    "UPDATE projects SET id = 67, name = 'Platform', theme = 'Orquestación IA', difficulty = 4, axis = 'Plataforma / MCP' WHERE id = 2;",
    "",
    "UPDATE tasks SET project_id = 0 WHERE project_id = 1;",
    "UPDATE columns SET project_id = 0 WHERE project_id = 1;",
    "UPDATE sprints SET project_id = 0 WHERE project_id = 1;",
    "UPDATE project_docs SET project_id = 0 WHERE project_id = 1;",
    "UPDATE bitacora_entries SET project_id = 0 WHERE project_id = 1;",
    "UPDATE project_updates SET project_id = 0 WHERE project_id = 1;",
    "UPDATE projects SET id = 0, name = 'Tutorial' WHERE id = 1;",
    ""
]

now_str = '2026-10-18 20:00:00'

for r in rows[1:]:
    if not r or r[0] is None:
        continue
    pid = int(r[0])
    if pid in [65, 67]:
        continue

    diff_val = r[1]
    if isinstance(diff_val, str) and '★' in diff_val:
        diff = diff_val.count('★')
    elif isinstance(diff_val, (int, float)):
        diff = int(diff_val)
    else:
        diff = 3
    diff = max(1, min(5, diff))

    theme = str(r[2]).strip() if r[2] else ''
    axis = str(r[3]).strip() if r[3] else 'Abierto'
    raw_name = str(r[4]).strip() if r[4] else f'Proyecto {pid}'
    # El usuario pide: 'con el id exacto. pero olvida lo de colocarle al nombre ese id.'
    name = raw_name

    pregunta = str(r[5]).strip() if len(r) > 5 and r[5] else ''
    notas = str(r[6]).strip() if len(r) > 6 and r[6] else ''
    despliegue = str(r[7]).strip() if len(r) > 7 and r[7] else ''
    escalabilidad = str(r[8]).strip() if len(r) > 8 and r[8] else ''
    
    desc = notas[:490] if notas else pregunta[:490]

    stars = '★' * diff + '☆' * (5 - diff)
    readme = f"""# PJ-{pid:02d} — {raw_name}

> **Eje:** {axis} | **Tema:** {theme} | **Dificultad:** {stars}

---

## 1. Pregunta Central de Negocio
{pregunta}

## 2. Metodología y Enfoque Técnico
{notas}

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** {despliegue}
- **Escalabilidad:** {escalabilidad}

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
"""

    extra = json.dumps({'catalog_id': pid, 'pregunta_general': pregunta, 'despliegue': despliegue, 'escalabilidad': escalabilidad})

    sql_proj = f"""INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES ({pid}, {esc(name)}, {esc(desc)}, '', {esc(readme)}, {diff}, {esc(theme)}, {esc(axis)}, 'Planeación', {esc(extra)}, {esc(now_str)}, {esc(now_str)});"""

    sql_cols = f"""INSERT INTO columns (project_id, title, position) VALUES 
({pid}, 'Por Hacer', 1), ({pid}, 'En Progreso', 2), ({pid}, 'En Revisión', 3), ({pid}, 'Terminado', 4);"""

    sql_sprint = f"""INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
({pid}, 'Sprint 1', 'Sprint inicial', 'active', 10);"""

    lines.append(f"-- Proyecto {pid}: {name}")
    lines.append(sql_proj)
    lines.append(sql_cols)
    lines.append(sql_sprint)
    lines.append("")

lines.append("COMMIT;")

with open('import_projects.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("import_projects.sql generado exitosamente.")
