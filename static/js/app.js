/**
 * Higgings Agile & MCP Platform — Project Workspace Logic (/project/{id})
 */

let currentProjectId = null;
let currentProjectData = null;
let loadedProjects = [];
let currentTab = 'board';
let currentBoardData = null;
let currentTaskId = null;
let currentTaskStoryPoints = 1;
let currentReadmeContent = '';

// Bootstrap Modal Instances
let taskModalInstance = null;
let releaseModalInstance = null;
let projectSettingsModalInstance = null;

// ==========================================
// 1. Inicialización
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
  const { initTheme, fetchUsersCatalog, setupUsersModal, setupActivityModal } = window.HiggingsCommon;

  initTheme();

  const taskModalEl = document.getElementById('task-modal');
  if (taskModalEl) taskModalInstance = new bootstrap.Modal(taskModalEl);
  const releaseModalEl = document.getElementById('release-modal');
  if (releaseModalEl) releaseModalInstance = new bootstrap.Modal(releaseModalEl);
  const projSettingsModalEl = document.getElementById('project-settings-modal');
  if (projSettingsModalEl) projectSettingsModalInstance = new bootstrap.Modal(projSettingsModalEl);

  currentProjectId = parseProjectIdFromUrl();
  if (currentProjectId === null) {
    window.location.href = '/home';
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  const validTabs = ['home', 'bitacora', 'board', 'work-items', 'changelog', 'metrics'];
  currentTab = validTabs.includes(tabParam) ? tabParam : 'board';

  await fetchUsersCatalog(true);

  setupUsersModal(async () => {
    await refreshProjectMetadata();
    await refreshActiveView();
  });

  setupActivityModal({
    defaultProjectId: () => currentProjectId,
    projectsGetter: () => (loadedProjects.length ? loadedProjects : (currentProjectData ? [currentProjectData] : []))
  });

  setupEventListeners();
  initMermaid();

  await loadProjectsSelector();
  await loadCurrentProject();
  activateTabUI(currentTab);
  await switchTab(currentTab, false);
});

function parseProjectIdFromUrl() {
  const match = window.location.pathname.match(/\/project\/(\d+)/);
  if (match) return parseInt(match[1], 10);
  return null;
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
// 2. Proyectos & Metadatos
// ==========================================

async function loadProjectsSelector() {
  const { formatProjectDisplay } = window.HiggingsCommon;
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error('Error cargando proyectos');
    const projects = await res.json();
    loadedProjects = projects;
    const sel = document.getElementById('project-selector');
    if (!sel) return;

    sel.innerHTML = '';
    projects.forEach(p => {
      if (p.is_visible === false && p.id !== currentProjectId) return;
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = formatProjectDisplay(p);
      sel.appendChild(opt);
    });

    sel.value = String(currentProjectId);
  } catch (err) {
    console.error('Projects selector error:', err);
  }
}

async function loadCurrentProject() {
  const {
    formatProjectDisplay,
    escapeHtml,
    isProjectOverdue,
    getStatusBadgeClass,
    getPriorityBadgeClass,
    renderBlockerAlertBadge
  } = window.HiggingsCommon;
  try {
    const res = await fetch(`/api/projects/${currentProjectId}`);
    if (!res.ok) {
      window.location.href = '/home';
      return;
    }
    currentProjectData = await res.json();

    const displayTitle = formatProjectDisplay(currentProjectData);
    document.title = `${displayTitle} — Higgings`;
    const titleEl = document.getElementById('current-project-title');
    if (titleEl) titleEl.textContent = displayTitle;

    updateProjectGitHubLink(currentProjectData.github_url);
    updateProjectFolderLink(currentProjectData.folder_url);

    const metaEl = document.getElementById('project-meta-summary');
    if (metaEl) {
      const parts = [];
      const statusBadge = `<span class="badge ${getStatusBadgeClass(currentProjectData.status)}">${escapeHtml(currentProjectData.status || 'En tiempo')}</span>`;
      const prioBadge = `<span class="badge ${getPriorityBadgeClass(currentProjectData.priority || 'Media')}">${escapeHtml(currentProjectData.priority || 'Media')}</span>`;
      const blockerBadge = renderBlockerAlertBadge(currentProjectData);
      parts.push(`${statusBadge} ${prioBadge}${blockerBadge}`);

      const areaVal = currentProjectData.area || currentProjectData.theme;
      if (areaVal) parts.push(`<strong>Área:</strong> ${escapeHtml(areaVal)}`);
      if (currentProjectData.owner) parts.push(`<strong>Responsable:</strong> ${escapeHtml(currentProjectData.owner)}`);
      if (currentProjectData.stakeholder) parts.push(`<strong>Interesado:</strong> ${escapeHtml(currentProjectData.stakeholder)}`);
      if (currentProjectData.area_key_user) parts.push(`<strong>Key User:</strong> ${escapeHtml(currentProjectData.area_key_user)}`);
      if (currentProjectData.start_date || currentProjectData.due_date) {
        const ini = currentProjectData.start_date || '—';
        const lim = currentProjectData.due_date || '—';
        const overdue = isProjectOverdue(currentProjectData);
        parts.push(`<span class="${overdue ? 'text-danger fw-semibold' : ''}"><strong>Fechas:</strong> ${escapeHtml(ini)} a ${escapeHtml(lim)}</span>`);
      }
      if (currentProjectData.next_step) {
        parts.push(`<span class="text-primary"><strong>Siguiente paso:</strong> ${escapeHtml(currentProjectData.next_step)}</span>`);
      }
      metaEl.innerHTML = parts.join(' &middot; ');
    }
  } catch (err) {
    console.error('Load project error:', err);
  }
}

async function refreshProjectMetadata() {
  await loadProjectsSelector();
  await loadCurrentProject();
}

function updateProjectFolderLink(url) {
  const folderLink = document.getElementById('project-folder-link');
  if (!folderLink) return;
  if (url && url.trim()) {
    folderLink.href = url.trim();
    folderLink.title = `Abrir carpeta compartida: ${url.trim()}`;
    folderLink.classList.remove('d-none');
    folderLink.classList.add('d-inline-flex');
  } else {
    folderLink.href = '#';
    folderLink.classList.add('d-none');
    folderLink.classList.remove('d-inline-flex');
  }
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
// 3. Navegación y Event Listeners
// ==========================================

function setupEventListeners() {
  const { populateProjectSettingsModal, submitProjectSettingsModal } = window.HiggingsCommon;

  // Cambio de proyecto en selector superior
  document.getElementById('project-selector')?.addEventListener('change', (e) => {
    const nextId = e.target.value;
    if (nextId !== '') {
      window.location.href = `/project/${nextId}?tab=${encodeURIComponent(currentTab)}`;
    }
  });

  // Botón '+' crea proyecto usando el modal unificado
  document.getElementById('btn-add-project')?.addEventListener('click', () => {
    populateProjectSettingsModal(null, projectSettingsModalInstance);
  });

  // Editar proyecto actual desde título o botón Configurar
  const openCurrentEdit = () => populateProjectSettingsModal(currentProjectData, projectSettingsModalInstance);
  document.getElementById('current-project-title')?.addEventListener('click', openCurrentEdit);
  document.getElementById('btn-edit-current-project')?.addEventListener('click', openCurrentEdit);

  // Guardar proyecto (creación o edición)
  document.getElementById('btn-modal-save-proj')?.addEventListener('click', async () => {
    await submitProjectSettingsModal(projectSettingsModalInstance, async (saved, isNew) => {
      if (isNew && saved?.id !== undefined) {
        window.location.href = `/project/${saved.id}`;
      } else {
        await refreshProjectMetadata();
      }
    });
  });

  // Clic en enlace GitHub vacío abre modal de configuración
  document.getElementById('project-github-link')?.addEventListener('click', (e) => {
    if (!currentProjectData?.github_url || !currentProjectData.github_url.trim()) {
      e.preventDefault();
      openCurrentEdit();
    }
  });

  // Tabs de navegación
  document.querySelectorAll('.jira-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.dataset.tab;
      activateTabUI(tabId);
      switchTab(tabId, true);
    });
  });

  // Búsqueda en vivo
  document.getElementById('jira-search-input')?.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    filterContent(q);
  });

  // Filtros del tablero Kanban
  ['board-filter-phase', 'board-filter-priority', 'board-filter-assignee', 'board-filter-tag'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', applyBoardFilters);
  });
  document.getElementById('btn-board-clear-filters')?.addEventListener('click', () => {
    ['board-filter-phase', 'board-filter-priority', 'board-filter-assignee', 'board-filter-tag'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    applyBoardFilters();
  });

  // Modales y vistas
  setupTaskModalActions();
  setupReleaseModalActions();
  setupBitacoraActions();

  document.getElementById('btn-add-work-item')?.addEventListener('click', openTaskModalForCreate);

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

function activateTabUI(tabId) {
  document.querySelectorAll('.jira-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.jira-tab[data-tab="${tabId}"]`)?.classList.add('active');
}

async function switchTab(tabId, updateHistory = true) {
  currentTab = tabId;

  if (updateHistory) {
    const newUrl = `/project/${currentProjectId}?tab=${encodeURIComponent(tabId)}`;
    window.history.replaceState({}, '', newUrl);
  }

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
  if (currentProjectId === null || currentProjectId === undefined) return;

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

async function renderHomeReadme() {
  const { escapeHtml } = window.HiggingsCommon;
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
    if (textareaEl) textareaEl.value = currentReadmeContent;

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

function getPhaseLabel(phase) {
  return (phase || '').trim() || 'Base';
}

function getProjectPhases(source) {
  const extraPhases = new Set();
  const items = Array.isArray(source) ? source : [];
  items.forEach(entry => {
    const tasksList = Array.isArray(entry?.tasks) ? entry.tasks : [entry];
    tasksList.forEach(t => {
      const ph = getPhaseLabel(t?.phase);
      if (ph && ph !== 'Base') {
        extraPhases.add(ph);
      }
    });
  });
  return ['Base', ...Array.from(extraPhases).sort((a, b) => a.localeCompare(b))];
}

function populatePhaseDatalist() {
  const dl = document.getElementById('modal-phase-suggestions');
  if (!dl) return;
  const projectPhases = getProjectPhases(currentBoardData?.columns || []);
  const suggestions = new Set(projectPhases);
  ['Base', 'Mejoras', 'Mantenimiento'].forEach(s => suggestions.add(s));
  dl.innerHTML = '';
  suggestions.forEach(ph => {
    const opt = document.createElement('option');
    opt.value = ph;
    dl.appendChild(opt);
  });
}

function getTaskPriorityBadge(priority) {
  const p = (priority || 'medium').toLowerCase();
  const map = {
    urgent: { label: 'Urgente', cls: 'bg-danger-subtle text-danger border-danger-subtle' },
    high: { label: 'Alta', cls: 'bg-warning-subtle text-warning border-warning-subtle' },
    medium: { label: 'Media', cls: 'bg-primary-subtle text-primary border-primary-subtle' },
    low: { label: 'Baja', cls: 'bg-secondary-subtle text-secondary border-secondary-subtle' }
  };
  return map[p] || map.medium;
}

function populateBoardFilters(columns) {
  const phaseSel = document.getElementById('board-filter-phase');
  const assigneeSel = document.getElementById('board-filter-assignee');
  const tagSel = document.getElementById('board-filter-tag');

  const projectPhases = getProjectPhases(columns || []);
  const phasesSet = new Set(projectPhases);
  const assigneesSet = new Set();
  const tagsSet = new Set();

  (columns || []).forEach(col => {
    (col.tasks || []).forEach(t => {
      assigneesSet.add(t.assignee || 'Sin asignar');
      (t.tags || []).forEach(tg => {
        if (tg && tg.trim()) tagsSet.add(tg.trim());
      });
    });
  });

  if (phaseSel) {
    const prev = phaseSel.value;
    phaseSel.innerHTML = '<option value="">Todas las etapas</option>';
    projectPhases.forEach(ph => {
      const opt = document.createElement('option');
      opt.value = ph;
      opt.textContent = ph;
      phaseSel.appendChild(opt);
    });
    if (prev && phasesSet.has(prev)) phaseSel.value = prev;
  }

  if (assigneeSel) {
    const prev = assigneeSel.value;
    assigneeSel.innerHTML = '<option value="">Todos los responsables</option>';
    Array.from(assigneesSet).sort((a, b) => a.localeCompare(b)).forEach(name => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      assigneeSel.appendChild(opt);
    });
    if (prev && assigneesSet.has(prev)) assigneeSel.value = prev;
  }

  if (tagSel) {
    const prev = tagSel.value;
    tagSel.innerHTML = '<option value="">Todos los tags</option>';
    Array.from(tagsSet).sort((a, b) => a.localeCompare(b)).forEach(tg => {
      const opt = document.createElement('option');
      opt.value = tg;
      opt.textContent = tg;
      tagSel.appendChild(opt);
    });
    if (prev && tagsSet.has(prev)) tagSel.value = prev;
  }
}

function applyBoardFilters() {
  const phaseVal = document.getElementById('board-filter-phase')?.value || '';
  const prioVal = document.getElementById('board-filter-priority')?.value || '';
  const assigneeVal = document.getElementById('board-filter-assignee')?.value || '';
  const tagVal = document.getElementById('board-filter-tag')?.value || '';
  const searchVal = (document.getElementById('jira-search-input')?.value || '').toLowerCase().trim();

  const hasSelectFilters = Boolean(phaseVal || prioVal || assigneeVal || tagVal);
  const hasAnyFilter = hasSelectFilters || Boolean(searchVal);

  let visibleTotal = 0;
  let allTotal = 0;

  document.querySelectorAll('#board-columns-container .jira-column').forEach(colEl => {
    const cards = colEl.querySelectorAll('.jira-card');
    let visibleCol = 0;
    cards.forEach(card => {
      allTotal += 1;
      const cPhase = card.dataset.phase || 'Base';
      const cPrio = card.dataset.priority || 'medium';
      const cAssignee = card.dataset.assignee || 'Sin asignar';
      let cTags = [];
      try { cTags = JSON.parse(card.dataset.tags || '[]'); } catch (e) {}

      const matches =
        (!phaseVal || cPhase === phaseVal) &&
        (!prioVal || cPrio === prioVal) &&
        (!assigneeVal || cAssignee === assigneeVal) &&
        (!tagVal || cTags.includes(tagVal)) &&
        (!searchVal || card.textContent.toLowerCase().includes(searchVal));

      card.style.display = matches ? 'flex' : 'none';
      if (matches) {
        visibleCol += 1;
        visibleTotal += 1;
      }
    });

    const badgeEl = colEl.querySelector('.jira-col-count');
    if (badgeEl) {
      badgeEl.textContent = hasAnyFilter ? `${visibleCol}/${cards.length}` : String(cards.length);
    }
  });

  const clearBtn = document.getElementById('btn-board-clear-filters');
  if (clearBtn) clearBtn.classList.toggle('d-none', !hasSelectFilters);

  const summaryEl = document.getElementById('board-filter-summary');
  if (summaryEl) {
    summaryEl.textContent = hasAnyFilter ? `Mostrando ${visibleTotal} de ${allTotal} tareas` : '';
  }
}

async function renderBoard() {
  const { escapeHtml } = window.HiggingsCommon;
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/board?sprint_id=-1`);
    if (!res.ok) throw new Error('Error cargando tablero');
    currentBoardData = await res.json();

    const backlogCount = currentBoardData.backlog_count || 0;
    const activeCount = (currentBoardData.columns || [])
      .filter(c => !c.is_backlog)
      .reduce((acc, c) => acc + (c.tasks ? c.tasks.length : 0), 0);

    const sprintBadge = document.getElementById('active-sprint-badge');
    if (sprintBadge) {
      sprintBadge.textContent = `Tablero Activo · ${activeCount} en curso · ${backlogCount} ideas`;
    }

    const container = document.getElementById('board-columns-container');
    container.innerHTML = '';

    currentBoardData.columns.forEach(col => {
      const colEl = document.createElement('div');
      colEl.className = (col.is_backlog || col.id === 0) ? 'jira-column jira-column-backlog' : 'jira-column';
      colEl.dataset.columnId = col.id;

      colEl.innerHTML = `
        <div class="jira-col-header">
          <h4 class="jira-col-title">
            <span>${escapeHtml(col.title)}</span>
            <span class="badge bg-body-secondary text-secondary border rounded-pill jira-col-count">${col.tasks.length}</span>
          </h4>
        </div>
        <div class="quick-create-box">
          <input type="text" class="quick-create-input" placeholder="+ Agregar tarea y Enter" data-column-id="${col.id}">
        </div>
        <div class="jira-card-list" data-column-id="${col.id}"></div>
      `;

      const quickInput = colEl.querySelector('.quick-create-input');
      quickInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && quickInput.value.trim()) {
          const title = quickInput.value.trim();
          quickInput.value = '';
          await createQuickTask(col.id, title);
        }
      });

      const cardList = colEl.querySelector('.jira-card-list');
      cardList.addEventListener('dragover', (e) => { e.preventDefault(); cardList.classList.add('drag-over'); });
      cardList.addEventListener('dragleave', () => cardList.classList.remove('drag-over'));
      cardList.addEventListener('drop', async (e) => {
        e.preventDefault();
        cardList.classList.remove('drag-over');
        const taskId = e.dataTransfer.getData('text/plain');
        if (taskId) {
          await moveTask(parseInt(taskId, 10), col.id);
        }
      });

      col.tasks.forEach(task => {
        cardList.appendChild(createJiraCardElement(task));
      });

      container.appendChild(colEl);
    });

    populateBoardFilters(currentBoardData.columns);
    applyBoardFilters();
  } catch (err) {
    console.error('Board render error:', err);
  }
}

function createJiraCardElement(task) {
  const { escapeHtml, getUserBadgeAttributes } = window.HiggingsCommon;
  const card = document.createElement('div');
  card.className = 'jira-card';
  card.draggable = true;
  card.dataset.taskId = task.id;

  const assigneeLabel = task.assignee || 'Sin asignar';
  const taskPhase = getPhaseLabel(task.phase);
  const taskPriority = (task.priority || 'medium').toLowerCase();
  const taskTags = Array.isArray(task.tags) ? task.tags : [];

  card.dataset.phase = taskPhase;
  card.dataset.priority = taskPriority;
  card.dataset.assignee = assigneeLabel;
  card.dataset.tags = JSON.stringify(taskTags);

  const badge = getUserBadgeAttributes(assigneeLabel);
  const prioBadge = getTaskPriorityBadge(taskPriority);

  const extraChips = [];
  if (taskPhase && taskPhase !== 'Base') {
    extraChips.push(`<span class="badge bg-info-subtle text-info border border-info-subtle" style="font-size:10px;">${escapeHtml(taskPhase)}</span>`);
  }
  taskTags.slice(0, 2).forEach(tg => {
    extraChips.push(`<span class="badge bg-body-secondary text-secondary border" style="font-size:10px;">${escapeHtml(tg)}</span>`);
  });
  const chipsRow = extraChips.length
    ? `<div class="d-flex flex-wrap gap-1 mb-1">${extraChips.join('')}</div>`
    : '';

  card.innerHTML = `
    <div class="card-title-text">${escapeHtml(task.title)}</div>
    ${chipsRow}
    <div class="card-key-row">
      <div class="d-flex align-items-center gap-1">
        <span class="card-key">PJ${currentProjectId}-${task.id}</span>
        <span class="badge border ${prioBadge.cls}" style="font-size:10px;">${escapeHtml(prioBadge.label)}</span>
      </div>
      <span class="card-agent-badge ${badge.className}" style="${badge.style}">
        ${escapeHtml(assigneeLabel)}
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
    const isBacklog = (parseInt(columnId, 10) === 0);
    const activeSprintId = (!isBacklog && currentBoardData && currentBoardData.active_sprint)
      ? currentBoardData.active_sprint.id
      : null;
    const selectedPhase = document.getElementById('board-filter-phase')?.value || 'Base';
    const selectedPrio = document.getElementById('board-filter-priority')?.value || 'medium';
    const selectedAssignee = document.getElementById('board-filter-assignee')?.value || 'Sin asignar';

    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: currentProjectId,
        column_id: parseInt(columnId, 10),
        sprint_id: activeSprintId,
        title: title,
        priority: selectedPrio,
        story_points: 1,
        assignee: selectedAssignee,
        phase: selectedPhase
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
      body: JSON.stringify({ column_id: parseInt(columnId, 10), new_position: 999 })
    });
    await renderBoard();
  } catch (err) {
    console.error('Move error:', err);
  }
}

// ==========================================
// 5. Work Items (Lista Jerárquica)
// ==========================================

async function renamePhasePrompt(oldPhase) {
  const nextName = prompt(`Nuevo nombre para la etapa "${oldPhase}":`, oldPhase);
  if (nextName === null) return;
  const trimmed = nextName.trim();
  if (!trimmed || trimmed === oldPhase) return;
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/phases/rename`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_phase: oldPhase, new_phase: trimmed })
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || 'No se pudo renombrar la etapa.');
      return;
    }
    await renderWorkItems();
  } catch (err) {
    console.error('Rename phase error:', err);
    alert('Error de conexión al renombrar etapa.');
  }
}

async function renderWorkItems() {
  const { escapeHtml, getUserBadgeAttributes } = window.HiggingsCommon;
  const container = document.getElementById('work-items-container');
  container.innerHTML = '';

  try {
    const res = await fetch(`/api/projects/${currentProjectId}/board?sprint_id=-1`);
    const data = await res.json();
    currentBoardData = data;

    const allTasks = [];
    data.columns.forEach(c => {
      c.tasks.forEach(t => {
        const statusLabel = t.effective_status || (c.is_backlog ? 'Backlog' : c.title);
        allTasks.push({ ...t, display_status: statusLabel });
      });
    });

    const phases = getProjectPhases(allTasks);

    phases.forEach(phaseName => {
      const phaseTasks = allTasks.filter(t => getPhaseLabel(t.phase) === phaseName);

      const groupEl = document.createElement('div');
      groupEl.className = 'phase-group';

      let rowsHtml = '';
      if (phaseTasks.length === 0) {
        rowsHtml = `<tr><td colspan="5" class="text-muted text-center py-3 small">No hay elementos en ${escapeHtml(phaseName)}.</td></tr>`;
      } else {
        phaseTasks.forEach(task => {
          const assigneeLabel = task.assignee || 'Sin asignar';
          const badge = getUserBadgeAttributes(assigneeLabel);
          rowsHtml += `
            <tr style="cursor:pointer;" onclick="openTaskModalById(${task.id})">
              <td class="font-monospace fw-bold text-primary" style="width:110px;">PJ${currentProjectId}-${task.id}</td>
              <td class="fw-semibold text-body">${escapeHtml(task.title)}</td>
              <td style="width:140px;"><span class="badge bg-secondary-subtle text-body border">${escapeHtml(task.display_status)}</span></td>
              <td style="width:170px;"><span class="badge ${badge.className}" style="${badge.style}">${escapeHtml(assigneeLabel)}</span></td>
              <td class="text-muted small" style="width:150px;">${task.dependency ? escapeHtml(task.dependency) : '<span class="text-secondary opacity-50">—</span>'}</td>
            </tr>
          `;
        });
      }

      const renameBtnHtml = phaseTasks.length > 0
        ? `<button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2 btn-rename-phase" style="font-size:11px;">Renombrar</button>`
        : '';

      groupEl.innerHTML = `
        <div class="phase-header">
          <span>${escapeHtml(phaseName)}</span>
          <div class="d-flex align-items-center gap-2">
            ${renameBtnHtml}
            <span class="badge bg-body text-secondary border">${phaseTasks.length} items</span>
          </div>
        </div>
        <table class="items-table">
          <thead>
            <tr>
              <th>Clave</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Responsable</th>
              <th>Dependencia</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      `;

      groupEl.querySelector('.btn-rename-phase')?.addEventListener('click', () => {
        renamePhasePrompt(phaseName);
      });

      container.appendChild(groupEl);
    });
  } catch (err) {
    console.error('Work items error:', err);
  }
}

// ==========================================
// 6. Releases / Changelog
// ==========================================

async function renderChangelog() {
  const { escapeHtml } = window.HiggingsCommon;
  const container = document.getElementById('releases-container');
  container.innerHTML = '';

  try {
    const res = await fetch(`/api/projects/${currentProjectId}/updates`);
    const updates = await res.json();

    if (updates.length === 0) {
      container.innerHTML = '<div class="alert alert-secondary small text-center">No hay releases registrados aún.</div>';
      return;
    }

    updates.forEach(u => {
      const card = document.createElement('div');
      card.className = 'card border shadow-sm mb-3';
      const rendered = typeof marked !== 'undefined' ? marked.parse(u.content_markdown) : escapeHtml(u.content_markdown);

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
// 7. Métricas Generales del Proyecto
// ==========================================

async function renderMetrics() {
  const { escapeHtml } = window.HiggingsCommon;
  try {
    const res = await fetch(`/api/projects/${currentProjectId}/metrics`);
    if (!res.ok) throw new Error('Error al consultar métricas');
    const m = await res.json();

    const totalEl = document.getElementById('metric-total-tasks');
    if (totalEl) totalEl.textContent = m.total_tasks || 0;

    const breakdownEl = document.getElementById('metric-tasks-breakdown');
    if (breakdownEl) {
      const pending = (m.total_tasks || 0) - (m.completed_tasks || 0);
      breakdownEl.textContent = `${m.completed_tasks || 0} completadas · ${pending} pendientes`;
    }

    const backlogCount = m.backlog_tasks ?? (m.tasks_by_status ? m.tasks_by_status['Backlog (Ideas)'] : 0) ?? 0;
    const velocityEl = document.getElementById('metric-velocity');
    if (velocityEl) velocityEl.textContent = String(backlogCount);

    const pointsBreakdownEl = document.getElementById('metric-points-breakdown');
    if (pointsBreakdownEl) {
      pointsBreakdownEl.textContent = `${m.todo_tasks || 0} por hacer en tablero`;
    }

    const completionEl = document.getElementById('metric-completion');
    if (completionEl) completionEl.textContent = `${m.completion_rate || 0}%`;

    const barEl = document.getElementById('metric-completion-bar');
    if (barEl) barEl.style.width = `${Math.min(m.completion_rate || 0, 100)}%`;

    const inProgEl = document.getElementById('metric-in-progress');
    if (inProgEl) inProgEl.textContent = m.in_progress_tasks || 0;

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

    const prioContainer = document.getElementById('priority-distribution-container');
    if (prioContainer) {
      prioContainer.innerHTML = '';
      const prioLabels = { 'urgent': 'Urgente', 'high': 'Alta', 'medium': 'Media', 'low': 'Baja' };
      const prioColors = { 'urgent': 'bg-danger', 'high': 'bg-warning', 'medium': 'bg-primary', 'low': 'bg-secondary' };
      const tasksByPrio = m.tasks_by_priority || m.points_by_priority || {};
      ['urgent', 'high', 'medium', 'low'].forEach(p => {
        const count = tasksByPrio[p] || 0;
        const pct = m.total_tasks > 0 ? Math.round((count / m.total_tasks) * 100) : 0;
        const row = document.createElement('div');
        row.innerHTML = `
          <div class="d-flex align-items-center justify-content-between small mb-1">
            <span class="fw-medium">${prioLabels[p] || p}</span>
            <span class="text-muted fw-semibold">${count} tareas (${pct}%)</span>
          </div>
          <div class="progress" style="height: 6px;">
            <div class="progress-bar ${prioColors[p] || 'bg-secondary'}" style="width: ${pct}%;"></div>
          </div>
        `;
        prioContainer.appendChild(row);
      });
    }

    const assigneesContainer = document.getElementById('assignees-distribution-bars');
    if (assigneesContainer) {
      assigneesContainer.innerHTML = '';
      const assigneeEntries = Object.entries(m.tasks_by_assignee || {});
      if (assigneeEntries.length === 0) {
        assigneesContainer.innerHTML = '<span class="text-muted small">Sin asignaciones registradas.</span>';
      } else {
        assigneeEntries.forEach(([assignee, data]) => {
          const tasks = data.tasks || 0;
          const pct = m.total_tasks > 0 ? Math.round((tasks / m.total_tasks) * 100) : 0;

          const row = document.createElement('div');
          row.innerHTML = `
            <div class="d-flex align-items-center justify-content-between small mb-1">
              <span class="fw-semibold text-body">${escapeHtml(assignee)}</span>
              <span class="text-muted"><strong class="text-body">${tasks} tareas</strong> (${pct}%)</span>
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
// 8. Modales de Tarea (Backlog y Usuarios sincronizados)
// ==========================================

function setupTaskModalActions() {
  const colSelect = document.getElementById('modal-task-column');
  const sprintSelect = document.getElementById('modal-task-sprint');

  // Sincronización bidireccional Columna <-> Aprobación (Idea/Autorizado)
  colSelect?.addEventListener('change', () => {
    const colVal = parseInt(colSelect.value, 10);
    if (!sprintSelect) return;
    if (colVal === 0) {
      sprintSelect.value = 'backlog';
    } else if (sprintSelect.value === 'backlog' && currentBoardData?.active_sprint) {
      sprintSelect.value = String(currentBoardData.active_sprint.id);
    }
  });

  sprintSelect?.addEventListener('change', () => {
    if (!colSelect) return;
    if (sprintSelect.value === 'backlog') {
      colSelect.value = '0';
    } else if (parseInt(colSelect.value, 10) === 0) {
      const firstBoardCol = currentBoardData?.columns?.find(c => !c.is_backlog && c.id > 0);
      if (firstBoardCol) colSelect.value = String(firstBoardCol.id);
    }
  });

  document.getElementById('btn-modal-save-task')?.addEventListener('click', async () => {
    const title = document.getElementById('modal-task-title').value.trim();
    if (!title) return;

    let columnId = parseInt(document.getElementById('modal-task-column').value, 10);
    const assignee = document.getElementById('modal-task-assignee').value || 'Sin asignar';
    const storyPoints = currentTaskStoryPoints || 1;
    const phase = (document.getElementById('modal-task-phase').value || '').trim() || 'Base';
    const priority = document.getElementById('modal-task-priority').value;
    const tags = document.getElementById('modal-task-tags').value.split(',').map(s => s.trim()).filter(Boolean);
    const description = document.getElementById('modal-task-desc').value;

    const sprintVal = sprintSelect ? sprintSelect.value : 'backlog';
    let targetSprintId = null;
    if (columnId === 0 || sprintVal === 'backlog') {
      columnId = 0;
      targetSprintId = null;
    } else if (sprintVal === 'active') {
      targetSprintId = currentBoardData && currentBoardData.active_sprint ? currentBoardData.active_sprint.id : null;
    } else if (!isNaN(parseInt(sprintVal, 10))) {
      targetSprintId = parseInt(sprintVal, 10);
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

  document.getElementById('btn-modal-delete-task')?.addEventListener('click', async () => {
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
    const optActive = document.createElement('option');
    optActive.value = String(activeSprint.id);
    optActive.textContent = 'Autorizado (En Tablero)';
    sel.appendChild(optActive);
  }

  const optBacklog = document.createElement('option');
  optBacklog.value = 'backlog';
  optBacklog.textContent = 'Idea / Por aprobar (Backlog)';
  sel.appendChild(optBacklog);

  if (selectedSprintId === null || selectedSprintId === undefined || selectedSprintId === 0) {
    sel.value = 'backlog';
  } else if (activeSprint && selectedSprintId === activeSprint.id) {
    sel.value = String(activeSprint.id);
  } else {
    sel.value = String(selectedSprintId || 'backlog');
  }
}

function populateModalColumnSelect() {
  const sel = document.getElementById('modal-task-column');
  if (!sel) return;
  sel.innerHTML = '';
  if (currentBoardData && currentBoardData.columns) {
    currentBoardData.columns.forEach(c => {
      const opt = document.createElement('option');
      opt.value = String(c.id);
      opt.textContent = c.title;
      sel.appendChild(opt);
    });
  }
}

function openTaskModalForCreate() {
  const { populateUserSelect } = window.HiggingsCommon;
  currentTaskId = null;
  currentTaskStoryPoints = 1;
  document.getElementById('modal-task-title').value = '';
  document.getElementById('modal-task-desc').value = '';
  document.getElementById('modal-task-tags').value = '';
  populatePhaseDatalist();
  document.getElementById('modal-task-phase').value = document.getElementById('board-filter-phase')?.value || 'Base';
  document.getElementById('modal-task-priority').value = document.getElementById('board-filter-priority')?.value || 'medium';
  document.getElementById('btn-modal-delete-task').style.display = 'none';

  populateUserSelect(document.getElementById('modal-task-assignee'), 'Sin asignar', 'Sin asignar');
  populateModalColumnSelect();

  const defaultSprintId = currentBoardData?.active_sprint?.id || null;
  populateModalSprintSelect(defaultSprintId);
  if (!defaultSprintId) {
    document.getElementById('modal-task-column').value = '0';
  } else {
    const firstBoardCol = currentBoardData?.columns?.find(c => !c.is_backlog && c.id > 0);
    if (firstBoardCol) document.getElementById('modal-task-column').value = String(firstBoardCol.id);
  }

  taskModalInstance.show();
}

function openTaskModalForEdit(task) {
  const { populateUserSelect } = window.HiggingsCommon;
  currentTaskId = task.id;
  currentTaskStoryPoints = task.story_points || 1;
  document.getElementById('modal-task-title').value = task.title;
  document.getElementById('modal-task-desc').value = task.description || '';
  document.getElementById('modal-task-tags').value = (task.tags || []).join(', ');
  populatePhaseDatalist();
  document.getElementById('modal-task-phase').value = getPhaseLabel(task.phase);
  document.getElementById('modal-task-priority').value = task.priority || 'medium';
  document.getElementById('btn-modal-delete-task').style.display = 'block';

  populateUserSelect(document.getElementById('modal-task-assignee'), task.assignee || 'Sin asignar', 'Sin asignar');
  populateModalColumnSelect();
  populateModalSprintSelect(task.sprint_id);

  // Si la tarea está en Backlog (sprint_id == null), reflejar columna 0 ("Backlog (Ideas)")
  const isBacklog = (task.sprint_id === null || task.sprint_id === undefined);
  document.getElementById('modal-task-column').value = isBacklog ? '0' : String(task.column_id);

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

function filterContent(q) {
  if (currentTab === 'board') {
    applyBoardFilters();
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
// 9. Bitácora del Proyecto
// ==========================================

const DEFAULT_BITACORA_TEMPLATE = `**Proyecto:**  
PJ-XX (Nombre del Proyecto)

**Actividades:**  
[Descripción de actividades realizadas]

**Herramientas:**  
[Herramientas, librerías o plataformas usadas]

**Aprendí:**  
[Lecciones técnicas o de gestión]

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
    if (cardNew.style.display !== 'none') {
      closeForm();
    } else {
      cardNew.style.display = 'block';
      if (inputDate && !inputDate.value) {
        inputDate.value = new Date().toISOString().split('T')[0];
      }
      if (textareaContent && !textareaContent.value.trim()) {
        const projName = currentProjectData ? `PJ-${currentProjectData.id} (${currentProjectData.name})` : 'PJ-XX';
        textareaContent.value = DEFAULT_BITACORA_TEMPLATE.replace('PJ-XX (Nombre del Proyecto)', projName);
      }
      inputTitle?.focus();
    }
  });

  btnClose?.addEventListener('click', closeForm);
  btnCancel?.addEventListener('click', closeForm);

  btnSave?.addEventListener('click', async () => {
    if (currentProjectId === null || currentProjectId === undefined) return;
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
  const { escapeHtml } = window.HiggingsCommon;
  if (currentProjectId === null || currentProjectId === undefined) return;
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
          <p class="mb-2 fw-medium">No hay entradas en la bitácora todavía.</p>
          <p class="small text-secondary mb-0">Haz clic en <strong>+ Nueva Entrada</strong> para registrar una entrada.</p>
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
            <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-edit-entry" id="btn-edit-${entry.id}">Editar</button>
            <button class="btn btn-sm btn-success py-0 px-2 btn-save-entry" id="btn-save-${entry.id}" style="display:none;">Guardar</button>
            <button class="btn btn-sm btn-secondary py-0 px-2 btn-cancel-entry" id="btn-cancel-${entry.id}" style="display:none;">Cancelar</button>
            <button class="btn btn-sm btn-outline-danger py-0 px-2 btn-delete-entry" id="btn-delete-${entry.id}">Eliminar</button>
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
