/**
 * Huggins Agile & MCP Platform — Frontend Logic
 */

let currentProjectId = null;
let currentProjectData = null;
let currentTab = 'home';
let currentBoardData = null;
let currentTaskId = null;
let currentDocId = null;

// Bootstrap Modal Instances
let taskModalInstance = null;
let releaseModalInstance = null;
let projectSettingsModalInstance = null;
let portfolioModalInstance = null;

// ==========================================
// 1. Inicialización & Modo Claro / Oscuro
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  const taskModalEl = document.getElementById('task-modal');
  if (taskModalEl) taskModalInstance = new bootstrap.Modal(taskModalEl);
  const releaseModalEl = document.getElementById('release-modal');
  if (releaseModalEl) releaseModalInstance = new bootstrap.Modal(releaseModalEl);
  const projSettingsModalEl = document.getElementById('project-settings-modal');
  if (projSettingsModalEl) projectSettingsModalInstance = new bootstrap.Modal(projSettingsModalEl);
  const portfolioModalEl = document.getElementById('portfolio-modal');
  if (portfolioModalEl) portfolioModalInstance = new bootstrap.Modal(portfolioModalEl);

  await loadProjects();
  setupEventListeners();
  initMermaid();
});

function initTheme() {
  const savedTheme = localStorage.getItem('pj67-theme') || 'dark';
  applyTheme(savedTheme);

  document.getElementById('btn-theme-toggle').addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-bs-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
  localStorage.setItem('pj67-theme', theme);
  const themeText = document.getElementById('theme-text');
  if (themeText) {
    themeText.textContent = theme === 'dark' ? 'Oscuro' : 'Claro';
  }
}

function initMermaid() {
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: false,
      theme: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'default',
      securityLevel: 'loose'
    });
  }
}

// ==========================================
// 2. Gestión de Proyectos
// ==========================================

async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error('Error cargando proyectos');
    const projects = await res.json();
    const sel = document.getElementById('project-selector');
    sel.innerHTML = '';

    projects.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      sel.appendChild(opt);
    });

    if (projects.length > 0) {
      currentProjectId = currentProjectId || projects[0].id;
      sel.value = currentProjectId;
      await switchProject(currentProjectId);
    }
  } catch (err) {
    console.error('Projects error:', err);
  }
}

async function switchProject(projectId) {
  currentProjectId = parseInt(projectId);
  try {
    const res = await fetch(`/api/projects/${currentProjectId}`);
    if (res.ok) {
      currentProjectData = await res.json();
      document.getElementById('current-project-title').textContent = currentProjectData.name;
      updateProjectGitHubLink(currentProjectData.github_url);
    }
  } catch (err) {
    console.error('Switch project error:', err);
  }

  await refreshActiveView();
}

function updateProjectGitHubLink(url) {
  const ghLink = document.getElementById('project-github-link');
  const ghLabel = document.getElementById('project-github-label');
  if (!ghLink) return;

  if (url && url.trim()) {
    ghLink.href = url.trim();
    ghLink.target = '_blank';
    ghLink.title = `Abrir repositorio en GitHub: ${url.trim()}`;
    ghLink.classList.remove('btn-outline-warning');
    ghLink.classList.add('btn-outline-secondary');
    if (ghLabel) ghLabel.textContent = 'GitHub';
  } else {
    ghLink.href = '#';
    ghLink.target = '_self';
    ghLink.title = 'Configurar URL de GitHub para este proyecto';
    ghLink.classList.remove('btn-outline-secondary');
    ghLink.classList.add('btn-outline-warning');
    if (ghLabel) ghLabel.textContent = '+ GitHub';
  }
}

// ==========================================
// 3. Navegación por Pestañas (Jira Subheader)
// ==========================================

function setupEventListeners() {
  // Selector de proyecto
  document.getElementById('project-selector').addEventListener('change', (e) => {
    switchProject(e.target.value);
  });

  // Botón nuevo proyecto
  document.getElementById('btn-add-project').addEventListener('click', async () => {
    const name = prompt('Nombre del nuevo proyecto (ej. Summer Campaign, Mobile App):');
    if (!name) return;
    const github_url = prompt('URL del repositorio GitHub (opcional):') || '';
    const res = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, github_url })
    });
    if (res.ok) {
      const p = await res.json();
      currentProjectId = p.id;
      await loadProjects();
    }
  });

  // Clic en el título del proyecto para abrir modal de edición completo
  document.getElementById('current-project-title')?.addEventListener('click', () => {
    openEditProjectModal(currentProjectData);
  });

  // Clic en enlace GitHub: si no tiene URL, solicitar ingresarla
  document.getElementById('project-github-link')?.addEventListener('click', async (e) => {
    if (!currentProjectData?.github_url || !currentProjectData.github_url.trim()) {
      e.preventDefault();
      const url = prompt('Introduce la URL del repositorio GitHub para este proyecto:');
      if (url) {
        await saveProjectDetails(currentProjectData.name, url, currentProjectData.description || '');
      }
    }
  });

  // Clic secundario en GitHub para editar la URL en cualquier momento
  document.getElementById('project-github-link')?.addEventListener('contextmenu', async (e) => {
    e.preventDefault();
    const url = prompt('Editar URL del repositorio GitHub:', currentProjectData?.github_url || '');
    if (url !== null) {
      await saveProjectDetails(currentProjectData.name, url, currentProjectData.description || '');
    }
  });

  // Tabs de navegación
  document.querySelectorAll('.jira-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.jira-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const tabId = tab.dataset.tab;
      switchTab(tabId);
    });
  });

  // Búsqueda en vivo
  document.getElementById('jira-search-input')?.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    filterContent(q);
  });

  // Setup Modals
  setupTaskModalActions();
  setupReleaseModalActions();
  setupBitacoraActions();
  setupPortfolioActions();

  // Botón refrescar métricas
  document.getElementById('btn-refresh-metrics')?.addEventListener('click', () => {
    renderMetrics();
  });

  // Acciones Home (README Markdown)
  document.getElementById('btn-edit-readme')?.addEventListener('click', () => {
    const textarea = document.getElementById('readme-editor-textarea');
    if (textarea) textarea.value = currentReadmeContent;
    toggleReadmeMode(true);
  });

  document.getElementById('btn-cancel-readme')?.addEventListener('click', () => {
    toggleReadmeMode(false);
  });

  document.getElementById('btn-save-readme')?.addEventListener('click', async () => {
    const textarea = document.getElementById('readme-editor-textarea');
    if (!textarea) return;
    const content = textarea.value;
    try {
      const res = await fetch(`/api/projects/${currentProjectId}/readme`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ readme_markdown: content })
      });
      if (res.ok) {
        currentReadmeContent = content;
        await renderHomeReadme();
      } else {
        alert('Error al guardar el README');
      }
    } catch (err) {
      console.error('Save readme error:', err);
    }
  });
}

async function saveProjectDetails(name, github_url, description) {
  if (!currentProjectId) return;
  try {
    const res = await fetch(`/api/projects/${currentProjectId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, github_url, description })
    });
    if (res.ok) {
      currentProjectData = await res.json();
      document.getElementById('current-project-title').textContent = currentProjectData.name;
      updateProjectGitHubLink(currentProjectData.github_url);
      await loadProjects();
    }
  } catch (err) {
    console.error('Save project error:', err);
  }
}

async function switchTab(tabId) {
  currentTab = tabId;
  const viewMap = {
    'home': 'view-home',
    'bitacora': 'view-bitacora',
    'board': 'view-board',
    'work-items': 'view-work-items',
    'changelog': 'view-changelog',
    'metrics': 'view-metrics'
  };

  Object.values(viewMap).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });

  const activeEl = document.getElementById(viewMap[tabId]);
  if (activeEl) {
    activeEl.style.display = (tabId === 'board') ? 'flex' : 'block';
  }

  await refreshActiveView();
}

async function refreshActiveView() {
  if (!currentProjectId) return;

  if (currentTab === 'home') {
    await renderHomeReadme();
  } else if (currentTab === 'board') {
    await renderBoard();
  } else if (currentTab === 'work-items') {
    await renderWorkItems();
  } else if (currentTab === 'changelog') {
    await renderChangelog();
  } else if (currentTab === 'bitacora') {
    await renderBitacora();
  } else if (currentTab === 'metrics') {
    await renderMetrics();
  }
}

// ==========================================
// 3.1. Home / README Markdown del Proyecto
// ==========================================

let currentReadmeContent = '';

async function renderHomeReadme() {
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/readme`);
    if (!res.ok) throw new Error('Error al obtener README');
    const data = await res.json();
    currentReadmeContent = data.readme_markdown || '';

    const titleEl = document.getElementById('home-readme-title');
    if (titleEl && currentProjectData) {
      titleEl.textContent = `${currentProjectData.name} — README`;
    }

    const renderedEl = document.getElementById('readme-rendered-content');
    const textareaEl = document.getElementById('readme-editor-textarea');

    if (textareaEl) {
      textareaEl.value = currentReadmeContent;
    }

    if (renderedEl) {
      if (currentReadmeContent.trim()) {
        renderedEl.innerHTML = (typeof marked !== 'undefined' && marked.parse)
          ? marked.parse(currentReadmeContent)
          : `<pre>${escapeHtml(currentReadmeContent)}</pre>`;
      } else {
        renderedEl.innerHTML = '<p class="text-muted fst-italic">Este proyecto no tiene un README aún. Haz clic en <strong>Editar Readme</strong> para redactar la documentación.</p>';
      }
    }

    toggleReadmeMode(false);

  } catch (err) {
    console.error('Error renderHomeReadme:', err);
  }
}

function toggleReadmeMode(isEditing) {
  const viewContainer = document.getElementById('readme-view-container');
  const editContainer = document.getElementById('readme-edit-container');
  const btnEdit = document.getElementById('btn-edit-readme');
  const btnSave = document.getElementById('btn-save-readme');
  const btnCancel = document.getElementById('btn-cancel-readme');

  if (viewContainer) viewContainer.style.display = isEditing ? 'none' : 'block';
  if (editContainer) editContainer.style.display = isEditing ? 'block' : 'none';
  if (btnEdit) btnEdit.style.display = isEditing ? 'none' : 'inline-block';
  if (btnSave) btnSave.style.display = isEditing ? 'inline-block' : 'none';
  if (btnCancel) btnCancel.style.display = isEditing ? 'inline-block' : 'none';
}

// ==========================================
// 4. Tablero Kanban con Backlog Integrado
// ==========================================

async function renderBoard() {
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/board?sprint_id=-1`);
    if (!res.ok) throw new Error('Error cargando tablero');
    currentBoardData = await res.json();

    if (currentBoardData.active_sprint) {
      document.getElementById('active-sprint-badge').textContent = `${currentBoardData.active_sprint.name} (${currentBoardData.active_sprint.completed_points}/${currentBoardData.active_sprint.total_points} pts)`;
    } else {
      document.getElementById('active-sprint-badge').textContent = 'Product Backlog';
    }

    const container = document.getElementById('board-columns-container');
    container.innerHTML = '';

    currentBoardData.columns.forEach(col => {
      const colEl = document.createElement('div');
      colEl.className = 'jira-column';
      colEl.dataset.columnId = col.id;

      colEl.innerHTML = `
        <div class="jira-col-header">
          <h4 class="jira-col-title">
            <span>${escapeHtml(col.title)}</span>
            <span class="badge bg-body-secondary text-secondary border rounded-pill">${col.tasks.length}</span>
          </h4>
        </div>
        <div class="quick-create-box">
          <input type="text" class="quick-create-input" placeholder="+ What needs to be done?" data-column-id="${col.id}">
        </div>
        <div class="jira-card-list" data-column-id="${col.id}"></div>
      `;

      // Quick create on Enter
      const quickInput = colEl.querySelector('.quick-create-input');
      quickInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && quickInput.value.trim()) {
          const title = quickInput.value.trim();
          quickInput.value = '';
          await createQuickTask(col.id, title);
        }
      });

      // Card list drag & drop
      const cardList = colEl.querySelector('.jira-card-list');
      cardList.addEventListener('dragover', (e) => { e.preventDefault(); cardList.classList.add('drag-over'); });
      cardList.addEventListener('dragleave', () => cardList.classList.remove('drag-over'));
      cardList.addEventListener('drop', async (e) => {
        e.preventDefault();
        cardList.classList.remove('drag-over');
        const taskId = e.dataTransfer.getData('text/plain');
        if (taskId) {
          await moveTask(parseInt(taskId), col.id);
        }
      });

      col.tasks.forEach(task => {
        cardList.appendChild(createJiraCardElement(task));
      });

      container.appendChild(colEl);
    });

  } catch (err) {
    console.error('Board render error:', err);
  }
}

function createJiraCardElement(task) {
  const card = document.createElement('div');
  card.className = 'jira-card';
  card.draggable = true;
  card.dataset.taskId = task.id;

  const agentClasses = {
    'Claude Agent': 'agent-claude',
    'Cursor': 'agent-cursor',
    'Figma Agent': 'agent-figma',
    'Rich (Humano)': 'agent-rich',
    'Rich': 'agent-rich'
  };
  const agentClass = agentClasses[task.assignee] || 'agent-default';

  card.innerHTML = `
    <div class="card-title-text">${escapeHtml(task.title)}</div>
    <div class="card-key-row">
      <div class="d-flex align-items-center gap-1">
        <span class="card-key">PJ67-${task.id}</span>
        <span class="badge bg-body-tertiary text-muted border" style="font-size:10px;">${task.story_points || 1} pt</span>
      </div>
      <span class="card-agent-badge ${agentClass}">
        ${escapeHtml(task.assignee || 'Claude Agent')}
      </span>
    </div>
  `;

  card.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', task.id);
    card.classList.add('dragging');
  });
  card.addEventListener('dragend', () => card.classList.remove('dragging'));
  card.addEventListener('click', () => openTaskModalForEdit(task));

  return card;
}

async function createQuickTask(columnId, title) {
  try {
    const isBacklog = (parseInt(columnId) === 0);
    const activeSprintId = (!isBacklog && currentBoardData && currentBoardData.active_sprint)
      ? currentBoardData.active_sprint.id
      : null;

    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: currentProjectId,
        column_id: columnId,
        sprint_id: activeSprintId,
        title: title,
        story_points: 2,
        assignee: 'Claude Agent',
        phase: 'Phase 1'
      })
    });
    await renderBoard();
  } catch (err) {
    console.error('Quick task error:', err);
  }
}

async function moveTask(taskId, columnId) {
  try {
    await fetch(`/api/tasks/${taskId}/move`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ column_id: columnId, new_position: 999 })
    });
    await renderBoard();
  } catch (err) {
    console.error('Move error:', err);
  }
}

// ==========================================
// 5. Work Items View (Imagen 4)
// ==========================================

async function renderWorkItems() {
  const container = document.getElementById('work-items-container');
  container.innerHTML = '';

  try {
    const res = await fetch(`/api/projects/${currentProjectId}/board?sprint_id=-1`);
    const data = await res.json();

    const allTasks = [];
    data.columns.forEach(c => {
      c.tasks.forEach(t => allTasks.push({ ...t, column_title: c.title }));
    });

    const phases = ['Phase 1', 'Phase 2', 'Phase 3'];

    phases.forEach(phaseName => {
      const phaseTasks = allTasks.filter(t => (t.phase || 'Phase 1') === phaseName);

      const groupEl = document.createElement('div');
      groupEl.className = 'phase-group';

      let rowsHtml = '';
      if (phaseTasks.length === 0) {
        rowsHtml = `<tr><td colspan="5" class="text-muted text-center py-3 small">No work items in ${phaseName}.</td></tr>`;
      } else {
        phaseTasks.forEach(task => {
          rowsHtml += `
            <tr style="cursor:pointer;" onclick="openTaskModalById(${task.id})">
              <td class="font-monospace fw-bold text-primary" style="width:110px;">PJ67-${task.id}</td>
              <td class="fw-semibold text-body">${escapeHtml(task.title)}</td>
              <td style="width:130px;"><span class="badge bg-secondary-subtle text-body border">${escapeHtml(task.column_title)}</span></td>
              <td style="width:160px;"><span class="badge bg-body-secondary text-body">${escapeHtml(task.assignee || 'Claude Agent')}</span></td>
              <td class="text-muted small" style="width:150px;">${task.dependency ? escapeHtml(task.dependency) : '<span class="text-secondary opacity-50">—</span>'}</td>
            </tr>
          `;
        });
      }

      groupEl.innerHTML = `
        <div class="phase-header">
          <span>▼ ${phaseName}</span>
          <span class="badge bg-body text-secondary border">${phaseTasks.length} items</span>
        </div>
        <table class="items-table">
          <thead>
            <tr>
              <th>Key</th>
              <th>Description</th>
              <th>Status</th>
              <th>Assignee</th>
              <th>Dependency</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      `;

      container.appendChild(groupEl);
    });

  } catch (err) {
    console.error('Work items error:', err);
  }
}


// ==========================================
// 7. Releases / Changelog
// ==========================================

async function renderChangelog() {
  const container = document.getElementById('releases-container');
  container.innerHTML = '';

  try {
    const res = await fetch(`/api/projects/${currentProjectId}/updates`);
    const updates = await res.json();

    if (updates.length === 0) {
      container.innerHTML = '<div class="alert alert-secondary small text-center">No releases logged yet.</div>';
      return;
    }

    updates.forEach(u => {
      const card = document.createElement('div');
      card.className = 'card border shadow-sm mb-3';
      const rendered = typeof marked !== 'undefined' ? marked.parse(u.content_markdown) : u.content_markdown;

      card.innerHTML = `
        <div class="card-header bg-body-tertiary d-flex justify-content-between align-items-center py-2">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-primary font-monospace">${escapeHtml(u.version_tag)}</span>
            <span class="fw-bold">${escapeHtml(u.title)}</span>
          </div>
          <span class="text-muted small">${u.created_at.split(' ')[0]}</span>
        </div>
        <div class="card-body small lh-base">${rendered}</div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Changelog error:', err);
  }
}

// ==========================================
// 8. Métricas Generales del Proyecto & Scrum
// ==========================================

async function renderMetrics() {
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/metrics`);
    if (!res.ok) throw new Error('Error al consultar métricas');
    const m = await res.json();

    // 1. KPI Cards
    const totalEl = document.getElementById('metric-total-tasks');
    if (totalEl) totalEl.textContent = m.total_tasks || 0;

    const breakdownEl = document.getElementById('metric-tasks-breakdown');
    if (breakdownEl) {
      const pending = (m.total_tasks || 0) - (m.completed_tasks || 0);
      breakdownEl.textContent = `${m.completed_tasks || 0} completadas · ${pending} pendientes`;
    }

    const velocityEl = document.getElementById('metric-velocity');
    if (velocityEl) velocityEl.textContent = `${m.velocity_points_completed || 0} pts`;

    const pointsBreakdownEl = document.getElementById('metric-points-breakdown');
    if (pointsBreakdownEl) {
      pointsBreakdownEl.textContent = `${m.completed_points || 0} de ${m.total_points || 0} story points totales`;
    }

    const completionEl = document.getElementById('metric-completion');
    if (completionEl) completionEl.textContent = `${m.completion_rate || 0}%`;

    const barEl = document.getElementById('metric-completion-bar');
    if (barEl) barEl.style.width = `${Math.min(m.completion_rate || 0, 100)}%`;

    const inProgEl = document.getElementById('metric-in-progress');
    if (inProgEl) inProgEl.textContent = m.in_progress_tasks || 0;

    // 2. Distribución por Estado / Columnas
    const statusContainer = document.getElementById('status-distribution-container');
    if (statusContainer) {
      statusContainer.innerHTML = '';
      const statusEntries = Object.entries(m.tasks_by_status || {});
      if (statusEntries.length === 0) {
        statusContainer.innerHTML = '<span class="text-muted small">Sin tareas registradas.</span>';
      } else {
        statusEntries.forEach(([status, count]) => {
          const pct = m.total_tasks > 0 ? Math.round((count / m.total_tasks) * 100) : 0;
          const isDone = status.toLowerCase().includes('terminado') || status.toLowerCase().includes('done');
          const isProg = status.toLowerCase().includes('progreso') || status.toLowerCase().includes('progress');
          const colorClass = isDone ? 'bg-success' : (isProg ? 'bg-primary' : 'bg-secondary');

          const row = document.createElement('div');
          row.innerHTML = `
            <div class="d-flex align-items-center justify-content-between small mb-1">
              <span class="fw-medium">${escapeHtml(status)}</span>
              <span class="text-muted fw-semibold">${count} tareas (${pct}%)</span>
            </div>
            <div class="progress" style="height: 6px;">
              <div class="progress-bar ${colorClass}" style="width: ${pct}%;"></div>
            </div>
          `;
          statusContainer.appendChild(row);
        });
      }
    }

    // 3. Distribución por Prioridad
    const prioContainer = document.getElementById('priority-distribution-container');
    if (prioContainer) {
      prioContainer.innerHTML = '';
      const prioLabels = { 'urgent': 'Urgente', 'high': 'Alta', 'medium': 'Media', 'low': 'Baja' };
      const prioColors = { 'urgent': 'bg-danger', 'high': 'bg-warning', 'medium': 'bg-primary', 'low': 'bg-secondary' };
      const priorities = ['urgent', 'high', 'medium', 'low'];

      priorities.forEach(p => {
        const pts = (m.points_by_priority && m.points_by_priority[p]) || 0;
        const pct = m.total_points > 0 ? Math.round((pts / m.total_points) * 100) : 0;
        const row = document.createElement('div');
        row.innerHTML = `
          <div class="d-flex align-items-center justify-content-between small mb-1">
            <span class="fw-medium">${prioLabels[p] || p}</span>
            <span class="text-muted fw-semibold">${pts} pts (${pct}%)</span>
          </div>
          <div class="progress" style="height: 6px;">
            <div class="progress-bar ${prioColors[p] || 'bg-secondary'}" style="width: ${pct}%;"></div>
          </div>
        `;
        prioContainer.appendChild(row);
      });
    }

    // 4. Carga de Trabajo por Responsable / Miembro
    const assigneesContainer = document.getElementById('assignees-distribution-bars');
    if (assigneesContainer) {
      assigneesContainer.innerHTML = '';
      const assigneeEntries = Object.entries(m.tasks_by_assignee || {});
      if (assigneeEntries.length === 0) {
        assigneesContainer.innerHTML = '<span class="text-muted small">Sin asignaciones registradas.</span>';
      } else {
        assigneeEntries.forEach(([assignee, data]) => {
          const pts = data.points || 0;
          const tasks = data.tasks || 0;
          const pct = m.total_points > 0 ? Math.round((pts / m.total_points) * 100) : 0;

          const row = document.createElement('div');
          row.innerHTML = `
            <div class="d-flex align-items-center justify-content-between small mb-1">
              <span class="fw-semibold text-body">${escapeHtml(assignee)}</span>
              <span class="text-muted">${tasks} tareas · <strong class="text-body">${pts} pts</strong> (${pct}%)</span>
            </div>
            <div class="progress" style="height: 7px;">
              <div class="progress-bar bg-info" style="width: ${pct}%;"></div>
            </div>
          `;
          assigneesContainer.appendChild(row);
        });
      }
    }

  } catch (err) {
    console.error('Metrics error:', err);
  }
}



// ==========================================
// 10. Modales de Tarea
// ==========================================

function setupTaskModalActions() {
  document.getElementById('btn-modal-save-task').addEventListener('click', async () => {
    const title = document.getElementById('modal-task-title').value.trim();
    if (!title) return;

    const columnId = parseInt(document.getElementById('modal-task-column').value);
    const assignee = document.getElementById('modal-task-assignee').value;
    const storyPoints = parseInt(document.getElementById('modal-task-points').value);
    const phase = document.getElementById('modal-task-phase').value;
    const priority = document.getElementById('modal-task-priority').value;
    const tags = document.getElementById('modal-task-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    const description = document.getElementById('modal-task-desc').value;

    const sprintSelect = document.getElementById('modal-task-sprint');
    const sprintVal = sprintSelect ? sprintSelect.value : 'active';
    let targetSprintId = null;
    if (sprintVal === 'backlog') {
      targetSprintId = null;
    } else if (sprintVal === 'active') {
      targetSprintId = currentBoardData && currentBoardData.active_sprint ? currentBoardData.active_sprint.id : null;
    } else if (!isNaN(parseInt(sprintVal))) {
      targetSprintId = parseInt(sprintVal);
    }

    if (currentTaskId) {
      await fetch(`/api/tasks/${currentTaskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title, column_id: columnId, sprint_id: targetSprintId, assignee, story_points: storyPoints, phase, priority, tags, description
        })
      });
    } else {
      await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProjectId,
          column_id: columnId,
          sprint_id: targetSprintId,
          title,
          assignee,
          story_points: storyPoints,
          phase,
          priority,
          tags,
          description
        })
      });
    }

    taskModalInstance.hide();
    await refreshActiveView();
  });

  document.getElementById('btn-modal-delete-task').addEventListener('click', async () => {
    if (!currentTaskId || !confirm('¿Eliminar esta tarea?')) return;
    await fetch(`/api/tasks/${currentTaskId}`, { method: 'DELETE' });
    taskModalInstance.hide();
    await refreshActiveView();
  });
}

function populateModalSprintSelect(selectedSprintId) {
  const sel = document.getElementById('modal-task-sprint');
  if (!sel) return;
  sel.innerHTML = '';

  const activeSprint = currentBoardData && currentBoardData.active_sprint;
  if (activeSprint) {
    const optSprint = document.createElement('option');
    optSprint.value = activeSprint.id;
    optSprint.textContent = `${activeSprint.name} (Sprint Activo)`;
    sel.appendChild(optSprint);
  }

  const optBacklog = document.createElement('option');
  optBacklog.value = 'backlog';
  optBacklog.textContent = 'Product Backlog (Sin Sprint / Ideas)';
  sel.appendChild(optBacklog);

  if (selectedSprintId === null || selectedSprintId === undefined || selectedSprintId === 0) {
    sel.value = 'backlog';
  } else if (activeSprint && selectedSprintId === activeSprint.id) {
    sel.value = activeSprint.id;
  } else {
    sel.value = selectedSprintId || 'backlog';
  }
}

function openTaskModalForCreate() {
  currentTaskId = null;
  document.getElementById('modal-task-title').value = '';
  document.getElementById('modal-task-desc').value = '';
  document.getElementById('modal-task-tags').value = '';
  document.getElementById('modal-task-points').value = '2';
  document.getElementById('modal-task-assignee').value = 'Claude Agent';
  document.getElementById('modal-task-phase').value = 'Phase 1';
  document.getElementById('btn-modal-delete-task').style.display = 'none';

  populateModalColumnSelect();
  populateModalSprintSelect(currentTab === 'backlog' ? null : (currentBoardData?.active_sprint?.id || null));
  taskModalInstance.show();
}

function openTaskModalForEdit(task) {
  currentTaskId = task.id;
  document.getElementById('modal-task-title').value = task.title;
  document.getElementById('modal-task-desc').value = task.description || '';
  document.getElementById('modal-task-tags').value = (task.tags || []).join(', ');
  document.getElementById('modal-task-points').value = task.story_points || 1;
  document.getElementById('modal-task-assignee').value = task.assignee || 'Claude Agent';
  document.getElementById('modal-task-phase').value = task.phase || 'Phase 1';
  document.getElementById('modal-task-priority').value = task.priority || 'medium';
  document.getElementById('btn-modal-delete-task').style.display = 'block';

  populateModalColumnSelect();
  populateModalSprintSelect(task.sprint_id);
  document.getElementById('modal-task-column').value = task.column_id;
  taskModalInstance.show();
}

window.openTaskModalById = async function(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}`);
    const task = await res.json();
    openTaskModalForEdit(task);
  } catch (e) {
    console.error('Open task error:', e);
  }
};

function populateModalColumnSelect() {
  const sel = document.getElementById('modal-task-column');
  sel.innerHTML = '';
  if (currentBoardData && currentBoardData.columns) {
    currentBoardData.columns.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.title;
      sel.appendChild(opt);
    });
  }
}

// Filtro de contenido global
function filterContent(q) {
  if (currentTab === 'board') {
    document.querySelectorAll('.jira-card').forEach(c => {
      c.style.display = !q || c.textContent.toLowerCase().includes(q) ? 'flex' : 'none';
    });
  } else if (currentTab === 'work-items') {
    document.querySelectorAll('.items-table tbody tr').forEach(r => {
      r.style.display = !q || r.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  }
}

function setupReleaseModalActions() {
  document.getElementById('btn-add-release')?.addEventListener('click', () => {
    document.getElementById('modal-release-tag').value = '';
    document.getElementById('modal-release-title').value = '';
    document.getElementById('modal-release-notes').value = '';
    if (releaseModalInstance) releaseModalInstance.show();
  });

  document.getElementById('btn-modal-save-release')?.addEventListener('click', async () => {
    const tag = document.getElementById('modal-release-tag').value.trim();
    const title = document.getElementById('modal-release-title').value.trim();
    const notes = document.getElementById('modal-release-notes').value.trim();

    if (!tag || !title) {
      alert('Por favor especifica al menos la versión (tag) y el título del release.');
      return;
    }

    try {
      const res = await fetch(`/api/projects/${currentProjectId}/updates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProjectId,
          version_tag: tag,
          title: title,
          content_markdown: notes
        })
      });

      if (res.ok) {
        if (releaseModalInstance) releaseModalInstance.hide();
        await renderChangelog();
      } else {
        const err = await res.json();
        alert('Error guardando release: ' + (err.detail || 'Error desconocido'));
      }
    } catch (err) {
      alert('Error de conexión: ' + err.message);
    }
  });
}

// ==========================================
// 3.4. Bitácora del Proyecto (Markdown Notebook)
// ==========================================

const DEFAULT_BITACORA_TEMPLATE = `**Proyecto:**  
PJ-XX (Nombre del Proyecto)

**Actividades:**  
[Descripción de actividades realizadas]

**Herramientas/IA:**  
[Herramientas, librerías, modelos o IA usadas]

**Aprendí:**  
[Lecciones técnicas o metodológicas aprendidas]

**Resultado:**  
[Métricas, entregables o estado alcanzado]

**Siguiente:**  
[Siguientes pasos o fases]`;

function setupBitacoraActions() {
  const btnAdd = document.getElementById('btn-add-bitacora-entry');
  const cardNew = document.getElementById('new-bitacora-entry-card');
  const btnClose = document.getElementById('btn-close-new-bitacora');
  const btnCancel = document.getElementById('btn-cancel-new-bitacora');
  const btnSave = document.getElementById('btn-save-new-bitacora');
  const inputTitle = document.getElementById('new-bitacora-title');
  const inputDate = document.getElementById('new-bitacora-date');
  const textareaContent = document.getElementById('new-bitacora-content');

  const closeForm = () => {
    if (cardNew) cardNew.style.display = 'none';
  };

  btnAdd?.addEventListener('click', () => {
    if (!cardNew) return;
    const isVisible = cardNew.style.display !== 'none';
    if (isVisible) {
      closeForm();
    } else {
      cardNew.style.display = 'block';
      if (inputDate && !inputDate.value) {
        inputDate.value = new Date().toISOString().split('T')[0];
      }
      if (textareaContent && !textareaContent.value.trim()) {
        const projName = currentProjectData ? `${currentProjectData.id ? 'PJ-' + currentProjectData.id : ''} (${currentProjectData.name})` : 'PJ-XX';
        textareaContent.value = DEFAULT_BITACORA_TEMPLATE.replace('PJ-XX (Nombre del Proyecto)', projName);
      }
      inputTitle?.focus();
    }
  });

  btnClose?.addEventListener('click', closeForm);
  btnCancel?.addEventListener('click', closeForm);

  btnSave?.addEventListener('click', async () => {
    if (!currentProjectId) return;
    const title = inputTitle?.value.trim() || 'Entrada de Bitácora';
    const entryDate = inputDate?.value || new Date().toISOString().split('T')[0];
    const content = textareaContent?.value.trim();

    if (!content) {
      alert('El contenido no puede estar vacío.');
      return;
    }

    try {
      const res = await fetch(`/api/projects/${currentProjectId}/bitacora`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title,
          entry_date: entryDate,
          content_markdown: content
        })
      });

      if (res.ok) {
        if (inputTitle) inputTitle.value = '';
        if (textareaContent) textareaContent.value = '';
        closeForm();
        await renderBitacora();
      } else {
        const err = await res.json();
        alert('Error al guardar la entrada: ' + (err.detail || 'Error desconocido'));
      }
    } catch (err) {
      console.error('Error saving bitacora entry:', err);
      alert('Error de conexión al guardar entrada.');
    }
  });
}

async function renderBitacora() {
  if (!currentProjectId) return;
  const headerTitle = document.getElementById('bitacora-header-title');
  if (headerTitle && currentProjectData) {
    headerTitle.textContent = `Bitácora — ${currentProjectData.name}`;
  }

  const listEl = document.getElementById('bitacora-entries-list');
  if (!listEl) return;

  try {
    const res = await fetch(`/api/projects/${currentProjectId}/bitacora`);
    if (!res.ok) throw new Error('Error al cargar bitácora');
    const entries = await res.json();

    if (entries.length === 0) {
      listEl.innerHTML = `
        <div class="text-center py-5 text-muted border rounded-3 bg-body-tertiary">
          <i class="bi bi-journal-text fs-1 d-block mb-2 text-secondary opacity-50"></i>
          <p class="mb-2 fw-medium">No hay entradas en la bitácora todavía.</p>
          <p class="small text-secondary mb-0">Haz clic en <strong>+ Nueva Entrada</strong> para registrar una entrada con formato de notebook.</p>
        </div>`;
      return;
    }

    listEl.innerHTML = '';
    entries.forEach((entry, idx) => {
      const card = document.createElement('div');
      card.className = 'bitacora-block card border shadow-sm';
      card.id = `bitacora-entry-${entry.id}`;

      const dateFormatted = entry.entry_date || (entry.created_at ? entry.created_at.split('T')[0] : '');

      card.innerHTML = `
        <div class="bitacora-block-header card-header d-flex justify-content-between align-items-center py-2 px-3 bg-body-secondary bg-opacity-50">
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1 font-monospace">
              #${entries.length - idx} &bull; ${escapeHtml(dateFormatted)}
            </span>
            <span class="fw-bold fs-6 text-body entry-view-title" id="entry-title-view-${entry.id}">
              ${escapeHtml(entry.title)}
            </span>
            <input type="text" class="form-control form-control-sm entry-edit-title" id="entry-title-edit-${entry.id}" value="${escapeHtml(entry.title)}" style="display:none; max-width: 320px;">
            <input type="date" class="form-control form-control-sm entry-edit-date" id="entry-date-edit-${entry.id}" value="${escapeHtml(dateFormatted)}" style="display:none; max-width: 150px;">
          </div>
          <div class="d-flex align-items-center gap-1">
            <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-edit-entry" id="btn-edit-${entry.id}" title="Editar bloque">
              <i class="bi bi-pencil"></i> <span class="d-none d-sm-inline">Editar</span>
            </button>
            <button class="btn btn-sm btn-success py-0 px-2 btn-save-entry" id="btn-save-${entry.id}" style="display:none;" title="Guardar cambios">
              <i class="bi bi-check-lg"></i> <span class="d-none d-sm-inline">Guardar</span>
            </button>
            <button class="btn btn-sm btn-secondary py-0 px-2 btn-cancel-entry" id="btn-cancel-${entry.id}" style="display:none;" title="Cancelar edición">
              <i class="bi bi-x-lg"></i> <span class="d-none d-sm-inline">Cancelar</span>
            </button>
            <button class="btn btn-sm btn-outline-danger py-0 px-2 btn-delete-entry" id="btn-delete-${entry.id}" title="Eliminar entrada">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
        <div class="card-body p-3">
          <div class="bitacora-block-body markdown-rendered" id="entry-view-content-${entry.id}">
            ${(typeof marked !== 'undefined' && marked.parse) ? marked.parse(entry.content_markdown || '') : `<pre>${escapeHtml(entry.content_markdown || '')}</pre>`}
          </div>
          <div class="entry-editor-container" id="entry-edit-container-${entry.id}" style="display:none;">
            <textarea class="form-control font-monospace" id="entry-textarea-${entry.id}" rows="12">${escapeHtml(entry.content_markdown || '')}</textarea>
          </div>
        </div>
      `;

      listEl.appendChild(card);

      const btnEdit = card.querySelector(`#btn-edit-${entry.id}`);
      const btnSave = card.querySelector(`#btn-save-${entry.id}`);
      const btnCancel = card.querySelector(`#btn-cancel-${entry.id}`);
      const btnDelete = card.querySelector(`#btn-delete-${entry.id}`);
      const viewTitle = card.querySelector(`#entry-title-view-${entry.id}`);
      const editTitle = card.querySelector(`#entry-title-edit-${entry.id}`);
      const editDate = card.querySelector(`#entry-date-edit-${entry.id}`);
      const viewContent = card.querySelector(`#entry-view-content-${entry.id}`);
      const editContainer = card.querySelector(`#entry-edit-container-${entry.id}`);
      const textarea = card.querySelector(`#entry-textarea-${entry.id}`);

      const toggleEditMode = (editing) => {
        btnEdit.style.display = editing ? 'none' : 'inline-block';
        btnSave.style.display = editing ? 'inline-block' : 'none';
        btnCancel.style.display = editing ? 'inline-block' : 'none';
        viewTitle.style.display = editing ? 'none' : 'inline-block';
        editTitle.style.display = editing ? 'inline-block' : 'none';
        editDate.style.display = editing ? 'inline-block' : 'none';
        viewContent.style.display = editing ? 'none' : 'block';
        editContainer.style.display = editing ? 'block' : 'none';
      };

      btnEdit.addEventListener('click', () => {
        toggleEditMode(true);
        textarea.focus();
      });

      btnCancel.addEventListener('click', () => {
        editTitle.value = entry.title;
        editDate.value = dateFormatted;
        textarea.value = entry.content_markdown || '';
        toggleEditMode(false);
      });

      btnSave.addEventListener('click', async () => {
        const newTitle = editTitle.value.trim() || 'Entrada de Bitácora';
        const newDate = editDate.value || dateFormatted;
        const newContent = textarea.value.trim();

        if (!newContent) {
          alert('El contenido no puede estar vacío.');
          return;
        }

        try {
          const updateRes = await fetch(`/api/bitacora/${entry.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              title: newTitle,
              entry_date: newDate,
              content_markdown: newContent
            })
          });

          if (updateRes.ok) {
            entry.title = newTitle;
            entry.entry_date = newDate;
            entry.content_markdown = newContent;

            viewTitle.textContent = newTitle;
            viewContent.innerHTML = (typeof marked !== 'undefined' && marked.parse)
              ? marked.parse(newContent)
              : `<pre>${escapeHtml(newContent)}</pre>`;
            toggleEditMode(false);
          } else {
            const err = await updateRes.json();
            alert('Error al actualizar entrada: ' + (err.detail || 'Error desconocido'));
          }
        } catch (err) {
          console.error('Error updating bitacora entry:', err);
          alert('Error de conexión al actualizar entrada.');
        }
      });

      btnDelete.addEventListener('click', async () => {
        if (!confirm(`¿Eliminar la entrada "${entry.title}"?`)) return;
        try {
          const delRes = await fetch(`/api/bitacora/${entry.id}`, { method: 'DELETE' });
          if (delRes.ok) {
            await renderBitacora();
          } else {
            alert('Error al eliminar la entrada.');
          }
        } catch (err) {
          console.error('Error deleting entry:', err);
          alert('Error de conexión al eliminar entrada.');
        }
      });
    });

  } catch (err) {
    console.error('Error rendering bitacora:', err);
    listEl.innerHTML = `<div class="alert alert-danger">Error al cargar la bitácora: ${escapeHtml(err.message)}</div>`;
  }
}

// ==========================================
// 3.5. Portafolio de Proyectos (Vista Hub)
// ==========================================

let allPortfolioProjects = [];

function setupPortfolioActions() {
  const btnOpen = document.getElementById('btn-open-portfolio');
  const searchInput = document.getElementById('portfolio-filter-search');
  const themeSelect = document.getElementById('portfolio-filter-theme');
  const diffSelect = document.getElementById('portfolio-filter-difficulty');
  const statusSelect = document.getElementById('portfolio-filter-status');
  const btnReset = document.getElementById('btn-portfolio-reset-filters');
  const btnNewProj = document.getElementById('btn-portfolio-new-project');

  btnOpen?.addEventListener('click', async () => {
    await renderPortfolio();
    if (portfolioModalInstance) portfolioModalInstance.show();
  });

  searchInput?.addEventListener('input', applyPortfolioFilters);
  themeSelect?.addEventListener('change', applyPortfolioFilters);
  diffSelect?.addEventListener('change', applyPortfolioFilters);
  statusSelect?.addEventListener('change', applyPortfolioFilters);

  btnReset?.addEventListener('click', () => {
    if (searchInput) searchInput.value = '';
    if (themeSelect) themeSelect.value = '';
    if (diffSelect) diffSelect.value = '';
    if (statusSelect) statusSelect.value = '';
    renderPortfolioRows(allPortfolioProjects);
  });

  btnNewProj?.addEventListener('click', async () => {
    const name = prompt('Nombre del nuevo proyecto (ej. PJ-68 Machine Learning):');
    if (!name || !name.trim()) return;
    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim() })
      });
      if (res.ok) {
        await loadProjects();
        await renderPortfolio();
      }
    } catch (e) {
      console.error('Error creating project:', e);
    }
  });

  // Guardar desde el modal de edición de proyecto
  document.getElementById('btn-modal-save-proj')?.addEventListener('click', async () => {
    const idInput = document.getElementById('modal-proj-id');
    const targetId = idInput?.value ? parseInt(idInput.value) : currentProjectId;
    if (!targetId) return;

    const name = document.getElementById('modal-proj-name')?.value.trim();
    const theme = document.getElementById('modal-proj-theme')?.value.trim();
    const axis = document.getElementById('modal-proj-axis')?.value.trim();
    const difficulty = parseInt(document.getElementById('modal-proj-difficulty')?.value || '3');
    const status = document.getElementById('modal-proj-status')?.value || 'Planeación';
    const github_url = document.getElementById('modal-proj-github')?.value.trim();
    const description = document.getElementById('modal-proj-desc')?.value.trim();

    if (!name) {
      alert('El nombre del proyecto es obligatorio.');
      return;
    }

    try {
      const res = await fetch(`/api/projects/${targetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          theme,
          axis,
          difficulty,
          status,
          github_url,
          description
        })
      });

      if (res.ok) {
        if (projectSettingsModalInstance) projectSettingsModalInstance.hide();
        await loadProjects();
        if (targetId === currentProjectId) {
          await switchProject(targetId);
        }
        if (currentTab === 'portfolio') {
          await renderPortfolio();
        }
      } else {
        const err = await res.json();
        alert('Error al guardar proyecto: ' + (err.detail || 'Error desconocido'));
      }
    } catch (err) {
      console.error('Error saving project:', err);
      alert('Error de conexión al guardar proyecto.');
    }
  });
}

function openEditProjectModal(project) {
  const p = project || currentProjectData;
  if (!p) return;

  const idInput = document.getElementById('modal-proj-id');
  if (idInput) idInput.value = p.id;

  const nameInput = document.getElementById('modal-proj-name');
  if (nameInput) nameInput.value = p.name || '';

  const themeInput = document.getElementById('modal-proj-theme');
  if (themeInput) themeInput.value = p.theme || '';

  const axisInput = document.getElementById('modal-proj-axis');
  if (axisInput) axisInput.value = p.axis || 'Abierto';

  const diffInput = document.getElementById('modal-proj-difficulty');
  if (diffInput) diffInput.value = p.difficulty || 3;

  const statusInput = document.getElementById('modal-proj-status');
  if (statusInput) statusInput.value = p.status || 'Planeación';

  const githubInput = document.getElementById('modal-proj-github');
  if (githubInput) githubInput.value = p.github_url || '';

  const descInput = document.getElementById('modal-proj-desc');
  if (descInput) descInput.value = p.description || '';

  if (projectSettingsModalInstance) projectSettingsModalInstance.show();
}

async function renderPortfolio() {
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error('Error al obtener lista de proyectos');
    allPortfolioProjects = await res.json();

    const countBadge = document.getElementById('portfolio-total-count');
    if (countBadge) countBadge.textContent = `${allPortfolioProjects.length} proyectos`;

    // Poblar dropdown de temas únicos
    const themeSelect = document.getElementById('portfolio-filter-theme');
    if (themeSelect) {
      const currentSelectedTheme = themeSelect.value;
      const themes = Array.from(new Set(allPortfolioProjects.map(p => p.theme).filter(Boolean))).sort();
      themeSelect.innerHTML = '<option value="">Todos los Temas</option>';
      themes.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = t;
        themeSelect.appendChild(opt);
      });
      themeSelect.value = currentSelectedTheme;
    }

    applyPortfolioFilters();
  } catch (err) {
    console.error('Error in renderPortfolio:', err);
  }
}

function applyPortfolioFilters() {
  const search = (document.getElementById('portfolio-filter-search')?.value || '').toLowerCase().trim();
  const theme = document.getElementById('portfolio-filter-theme')?.value || '';
  const diff = document.getElementById('portfolio-filter-difficulty')?.value || '';
  const status = document.getElementById('portfolio-filter-status')?.value || '';

  let filtered = allPortfolioProjects.filter(p => {
    if (search) {
      const matchName = (p.name || '').toLowerCase().includes(search);
      const matchDesc = (p.description || '').toLowerCase().includes(search);
      const matchTheme = (p.theme || '').toLowerCase().includes(search);
      const matchId = `pj-${p.id}`.includes(search);
      if (!matchName && !matchDesc && !matchTheme && !matchId) return false;
    }
    if (theme && p.theme !== theme) return false;
    if (diff && p.difficulty !== parseInt(diff)) return false;
    if (status && p.status !== status) return false;
    return true;
  });

  renderPortfolioRows(filtered);
}

function renderPortfolioRows(projects) {
  const tbody = document.getElementById('portfolio-table-body');
  if (!tbody) return;

  if (projects.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-5 text-muted">
          No se encontraron proyectos con los filtros aplicados.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = '';
  projects.forEach(p => {
    const tr = document.createElement('tr');
    tr.className = 'portfolio-row-clickable';

    const starCount = Math.max(1, Math.min(5, p.difficulty || 3));
    const starsStr = '★'.repeat(starCount) + '☆'.repeat(5 - starCount);

    let statusClass = 'bg-secondary-subtle text-secondary';
    if (p.status === 'Terminado') statusClass = 'bg-success-subtle text-success border border-success-subtle';
    else if (p.status === 'En Curso') statusClass = 'bg-primary-subtle text-primary border border-primary-subtle';
    else if (p.status === 'Planeación') statusClass = 'bg-warning-subtle text-warning border border-warning-subtle';

    const pct = p.progress_percent || 0;
    const completed = p.completed_tasks || 0;
    const total = p.total_tasks || 0;
    const bitacoraDate = p.last_bitacora_date || '—';

    tr.innerHTML = `
      <td>
        <span class="badge bg-body-secondary text-body border font-monospace">PJ-${p.id}</span>
      </td>
      <td>
        <div class="fw-bold text-body project-link-title" style="cursor: pointer;" title="Ir a este proyecto">
          ${escapeHtml(p.name)}
        </div>
        ${p.description ? `<div class="small text-muted text-truncate" style="max-width: 320px;" title="${escapeHtml(p.description)}">${escapeHtml(p.description)}</div>` : ''}
      </td>
      <td>
        ${p.theme ? `<span class="badge bg-info-subtle text-info border border-info-subtle me-1">${escapeHtml(p.theme)}</span>` : '<span class="text-muted small">—</span>'}
        ${p.axis ? `<span class="badge bg-light text-secondary border small">${escapeHtml(p.axis)}</span>` : ''}
      </td>
      <td>
        <span class="portfolio-stars" title="${starCount} de 5 estrellas">${starsStr}</span>
      </td>
      <td>
        <span class="badge ${statusClass}">${escapeHtml(p.status || 'Planeación')}</span>
      </td>
      <td>
        <div class="d-flex align-items-center gap-2">
          <div class="progress flex-grow-1 portfolio-progress-bar" style="background: var(--border-subtle); height: 6px;">
            <div class="progress-bar ${pct === 100 ? 'bg-success' : 'bg-primary'}" role="progressbar" style="width: ${pct}%"></div>
          </div>
          <span class="small text-muted font-monospace" style="min-width: 45px;">${completed}/${total}</span>
        </div>
      </td>
      <td>
        <span class="small font-monospace ${p.last_bitacora_date ? 'text-primary fw-medium' : 'text-muted'}">${escapeHtml(bitacoraDate)}</span>
      </td>
      <td class="text-end">
        <div class="d-flex justify-content-end gap-1">
          <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-portfolio-edit" title="Editar proyecto">
            Editar
          </button>
          <button class="btn btn-sm btn-outline-primary py-0 px-2 btn-portfolio-open" title="Abrir tablero">
            Abrir
          </button>
        </div>
      </td>
    `;

    tr.querySelector('.btn-portfolio-edit')?.addEventListener('click', (e) => {
      e.stopPropagation();
      openEditProjectModal(p);
    });

    const openProject = async () => {
      if (portfolioModalInstance) portfolioModalInstance.hide();
      document.getElementById('project-selector').value = p.id;
      await switchProject(p.id);
      document.querySelectorAll('.jira-tab').forEach(t => t.classList.remove('active'));
      document.querySelector('.jira-tab[data-tab="board"]')?.classList.add('active');
      switchTab('board');
    };

    tr.querySelector('.btn-portfolio-open')?.addEventListener('click', (e) => {
      e.stopPropagation();
      openProject();
    });

    tr.querySelector('.project-link-title')?.addEventListener('click', openProject);

    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

