# Guía Rápida de Git Profesional

## 1. El Bloque Diario de Trabajo

Usa este bloque habitual en lugar del antiguo `git add . && git commit -m "actualizacion"`:

```bash
# 1. Inspeccionar qué cambió
git status -s

# 2. Agregar cambios verificados (evita agregar archivos accidentales como .xlsx o .env)
git add src/ static/ dockerfile

# 3. Guardar con mensaje descriptivo y tipo de cambio
git commit -m "feat: agregar modulo de portafolio con filtros interactivos"

# 4. Enviar a la rama principal
git push origin main
```

---

## 2. Tipos de Commit (Conventional Commits)

| Prefijo | Cuándo usarlo | Ejemplo |
| :--- | :--- | :--- |
| `feat:` | Nueva funcionalidad o módulo | `feat: agregar vista de portafolio` |
| `fix:` | Corrección de error o bug | `fix: solucionar cierre inesperado del modal` |
| `docs:` | Solo cambios de documentación | `docs: agregar guia de comandos git` |
| `refactor:` | Reorganización de código sin cambiar funcionalidad | `refactor: separar logica de filtros en app.js` |
| `chore:` | Tareas de configuración, Docker o librerías | `chore: actualizar dependencias en requirements.txt` |

---

## 3. Versionado con Etiquetas (Releases)

Cuando alcances una versión estable o hito del proyecto:

```bash
# Crear etiqueta anotada (-a) con mensaje (-m)
git tag -a v1.1.0 -m "Release v1.1.0: Hub de Portafolio y mejoras de UI"

# Enviar la etiqueta a GitHub
git push origin v1.1.0

# O enviar todas las etiquetas pendientes
git push origin --tags
```

### Regla SemVer (`vMAJOR.MINOR.PATCH`)
* **PATCH (`v1.0.1`):** Hotfix o bug menor.
* **MINOR (`v1.1.0`):** Nueva característica compatible.
* **MAJOR (`v2.0.0`):** Cambio radical o incompatible.

---

## 4. Comandos de Auxilio

* **Ver diferencias exactas antes de agregar:**
  ```bash
  git diff
  ```
* **Corregir el último commit (olvidaste un archivo o error en el texto):**
  ```bash
  git commit --amend -m "feat: nuevo texto corregido"
  ```
* **Descartar cambios no guardados en un archivo:**
  ```bash
  git restore static/index.html
  ```
* **Ver historial limpio y compacto:**
  ```bash
  git log --oneline -n 10
  ```


# 1. Revisar estado
git status -s

# 2. Agregar archivos
git add .

# 3. Guardar commit con mensaje descriptivo
git commit -m "feat: agregar portafolio interactivo y guia de git"

# 4. Crear etiqueta de versión anotada (-a) con mensaje (-m)
git tag -a v1.1.0 -m "Release v1.1.0: Portafolio de proyectos y filtros"

# 5. Enviar cambios y etiquetas a GitHub
git push origin main
git push origin --tags
