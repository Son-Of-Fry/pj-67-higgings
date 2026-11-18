/**
 * Higgings Platform — Landing Hub & Portfolio Executive View (/home)
 */

let allProjects = [];
let projectSettingsModalInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  const {
    initTheme,
    fetchUsersCatalog,
    setupUsersModal,
    setupActivityModal,
    populateProjectSettingsModal,
    submitProjectSettingsModal
  } = window.HiggingsCommon;

  initTheme();

  const projModalEl = document.getElementById('project-settings-modal');
  if (projModalEl && typeof bootstrap !== 'undefined') {
    projectSettingsModalInstance = new bootstrap.Modal(projModalEl);
  }

  await fetchUsersCatalog(true);

  setupUsersModal(async () => {
    await loadHubData();
  });

  setupActivityModal({
    defaultProjectId: null,
    projectsGetter: () => allProjects
  });

  setupBackupsModal();
  setupHubEvents(populateProjectSettingsModal, submitProjectSettingsModal);
  await loadHubData();
});

function setupHubEvents(populateProjectSettingsModal, submitProjectSettingsModal) {
  document.getElementById('home-project-jump')?.addEventListener('change', (e) => {
    const pid = e.target.value;
    if (pid !== '') {
      window.location.href = `/project/${pid}`;
    }
  });

  const openCreateModal = () => populateProjectSettingsModal(null, projectSettingsModalInstance);
  document.getElementById('btn-add-project')?.addEventListener('click', openCreateModal);
  document.getElementById('btn-hub-new-project')?.addEventListener('click', openCreateModal);

  document.getElementById('btn-modal-save-proj')?.addEventListener('click', async () => {
    await submitProjectSettingsModal(projectSettingsModalInstance, async () => {
      await loadHubData();
    });
  });

  document.getElementById('hub-filter-search')?.addEventListener('input', applyHubFilters);
  document.getElementById('hub-filter-owner')?.addEventListener('change', applyHubFilters);
  document.getElementById('hub-filter-area')?.addEventListener('change', applyHubFilters);
  document.getElementById('hub-filter-priority')?.addEventListener('change', applyHubFilters);
  document.getElementById('hub-filter-status')?.addEventListener('change', applyHubFilters);
  document.getElementById('hub-filter-blocked')?.addEventListener('change', applyHubFilters);

  document.getElementById('btn-hub-reset-filters')?.addEventListener('click', () => {
    ['hub-filter-search', 'hub-filter-owner', 'hub-filter-area', 'hub-filter-priority', 'hub-filter-status'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    const blockedEl = document.getElementById('hub-filter-blocked');
    if (blockedEl) blockedEl.checked = false;
    renderPortfolioTable(allProjects);
  });
}

async function loadHubData() {
  try {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error('Error cargando proyectos');
    allProjects = await res.json();

    populateQuickJumpSelect(allProjects);
    renderHubMetrics(allProjects);
    renderQuickAccessCards(allProjects);
    populateFilterDropdowns(allProjects);
    applyHubFilters();
  } catch (err) {
    console.error('Error loading hub:', err);
  }
}

function populateQuickJumpSelect(projects) {
  const { formatProjectDisplay } = window.HiggingsCommon;
  const sel = document.getElementById('home-project-jump');
  if (!sel) return;

  sel.innerHTML = '<option value="">Ir a proyecto...</option>';
  projects.filter(p => p.is_visible !== false).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = formatProjectDisplay(p);
    sel.appendChild(opt);
  });
}

function renderHubMetrics(projects) {
  const { isProjectOverdue } = window.HiggingsCommon;
  const total = projects.length;
  const atRiskOrDelayed = projects.filter(p => p.status === 'En riesgo' || p.status === 'Retrasado' || isProjectOverdue(p)).length;
  const blockedCount = projects.filter(p => (p.risks_blockers || '').trim().length > 0).length;
  const delivered = projects.filter(p => p.status === 'Completado' || p.status === 'En mantenimiento').length;

  let totalTasks = 0;
  let completedTasks = 0;
  projects.forEach(p => {
    totalTasks += (p.total_tasks || 0);
    completedTasks += (p.completed_tasks || 0);
  });

  const overallPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const setText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setText('hub-metric-total-projects', total);
  setText('hub-metric-active-projects', atRiskOrDelayed);
  setText('hub-metric-blocked-count', `${blockedCount} con bloqueos detectados`);
  setText('hub-metric-completed-projects', delivered);
  setText('hub-metric-overall-progress', `${overallPct}%`);
  setText('hub-metric-tasks-ratio', `${completedTasks}/${totalTasks} tareas completadas`);
  setText('hub-portfolio-count', `${total} proyectos`);
}

function renderQuickAccessCards(projects) {
  const { escapeHtml, getStatusBadgeClass, getPriorityBadgeClass, renderBlockerAlertBadge, isProjectOverdue } = window.HiggingsCommon;
  const container = document.getElementById('hub-quick-access-container');
  if (!container) return;

  let featured = projects.filter(p => p.is_visible !== false && p.id !== 0);
  if (featured.length < 4) {
    for (const p of projects) {
      if (featured.length >= 4) break;
      if (!featured.some(f => f.id === p.id)) featured.push(p);
    }
  }
  featured = featured.slice(0, 4);

  container.innerHTML = '';
  featured.forEach(p => {
    const col = document.createElement('div');
    col.className = 'col-md-3 col-sm-6';

    const pct = p.progress_percent || 0;
    const statusBadge = getStatusBadgeClass(p.status);
    const prioBadge = getPriorityBadgeClass(p.priority || 'Media');
    const blockerHtml = renderBlockerAlertBadge(p);
    const overdue = isProjectOverdue(p);
    const ownerText = p.owner || 'Sin asignar';
    const areaText = p.area || p.theme || 'General';

    col.innerHTML = `
      <a href="/project/${p.id}" class="text-decoration-none">
        <div class="card p-3 border shadow-sm bg-body h-100 hub-quick-card" style="cursor: pointer;">
          <div class="d-flex justify-content-between align-items-start mb-2 gap-1">
            <div class="d-flex align-items-center gap-1">
              <span class="badge bg-body-secondary text-body border font-monospace">PJ-${String(p.id).padStart(2, '0')}</span>
              <span class="badge ${prioBadge}" style="font-size:10px;">${escapeHtml(p.priority || 'Media')}</span>
              ${blockerHtml}
            </div>
            <span class="badge ${statusBadge}">${escapeHtml(p.status || 'En tiempo')}</span>
          </div>
          <h6 class="fw-bold text-body text-truncate mb-1" title="${escapeHtml(p.name)}">${escapeHtml(p.name)}</h6>
          <p class="small text-muted text-truncate mb-1" style="font-size: 12px;">
            ${escapeHtml(areaText)} &middot; ${escapeHtml(ownerText)}
          </p>
          ${p.next_step ? `<p class="small text-primary text-truncate mb-2" style="font-size: 11px;" title="Siguiente paso: ${escapeHtml(p.next_step)}">Sig: ${escapeHtml(p.next_step)}</p>` : '<div class="mb-2"></div>'}
          <div class="mt-auto pt-2 border-top">
            <div class="d-flex justify-content-between small mb-1" style="font-size: 11px;">
              <span class="${overdue ? 'text-danger fw-semibold' : 'text-muted'}">
                ${p.due_date ? `Límite: ${escapeHtml(p.due_date)}` : 'Progreso'}
              </span>
              <span class="font-monospace fw-semibold text-body">${pct}%</span>
            </div>
            <div class="progress" style="height: 5px; background: var(--border-subtle);">
              <div class="progress-bar ${pct === 100 ? 'bg-success' : 'bg-primary'}" style="width: ${pct}%"></div>
            </div>
          </div>
        </div>
      </a>
    `;

    container.appendChild(col);
  });
}

function populateFilterDropdowns(projects) {
  const populate = (selectId, values, defaultLabel) => {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    const cur = sel.value;
    sel.innerHTML = `<option value="">${defaultLabel}</option>`;
    values.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = v;
      sel.appendChild(opt);
    });
    sel.value = cur;
  };

  const areas = Array.from(new Set(projects.map(p => p.area || p.theme).filter(Boolean))).sort();
  const owners = Array.from(new Set(projects.map(p => p.owner).filter(Boolean))).sort();

  populate('hub-filter-area', areas, 'Todas las Áreas');
  populate('hub-filter-owner', owners, 'Todos los Responsables');
}

function applyHubFilters() {
  const search = (document.getElementById('hub-filter-search')?.value || '').toLowerCase().trim();
  const owner = document.getElementById('hub-filter-owner')?.value || '';
  const area = document.getElementById('hub-filter-area')?.value || '';
  const priority = document.getElementById('hub-filter-priority')?.value || '';
  const status = document.getElementById('hub-filter-status')?.value || '';
  const onlyBlocked = document.getElementById('hub-filter-blocked')?.checked || false;

  const filtered = allProjects.filter(p => {
    const projArea = p.area || p.theme || '';
    if (search) {
      const haystack = [
        `pj-${String(p.id).padStart(2, '0')}`,
        `pj-${p.id}`,
        p.name,
        p.description,
        projArea,
        p.owner,
        p.stakeholder,
        p.area_key_user,
        p.next_step,
        p.risks_blockers
      ].join(' ').toLowerCase();
      if (!haystack.includes(search)) return false;
    }
    if (owner && p.owner !== owner) return false;
    if (area && projArea !== area) return false;
    if (priority && (p.priority || 'Media') !== priority) return false;
    if (status && p.status !== status) return false;
    if (onlyBlocked && !(p.risks_blockers || '').trim()) return false;
    return true;
  });

  renderPortfolioTable(filtered);
}

function renderPortfolioTable(projects) {
  const {
    escapeHtml,
    getStatusBadgeClass,
    getPriorityBadgeClass,
    renderBlockerAlertBadge,
    isProjectOverdue,
    populateProjectSettingsModal
  } = window.HiggingsCommon;

  const tbody = document.getElementById('hub-portfolio-table-body');
  if (!tbody) return;

  const countEl = document.getElementById('hub-portfolio-count');
  if (countEl) countEl.textContent = `${projects.length} proyectos`;

  if (projects.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="11" class="text-center py-5 text-muted">
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

    const pct = p.progress_percent || 0;
    const completed = p.completed_tasks || 0;
    const total = p.total_tasks || 0;
    const statusClass = getStatusBadgeClass(p.status);
    const prioClass = getPriorityBadgeClass(p.priority || 'Media');
    const blockerHtml = renderBlockerAlertBadge(p);
    const overdue = isProjectOverdue(p);

    const projArea = p.area || p.theme || '';
    const startText = p.start_date ? escapeHtml(p.start_date) : '—';
    const dueText = p.due_date ? escapeHtml(p.due_date) : '—';
    const subtitle = p.next_step
      ? `<div class="small text-primary text-truncate" style="max-width: 260px;" title="Siguiente paso: ${escapeHtml(p.next_step)}">Siguiente: ${escapeHtml(p.next_step)}</div>`
      : (p.description ? `<div class="small text-muted text-truncate" style="max-width: 260px;" title="${escapeHtml(p.description)}">${escapeHtml(p.description)}</div>` : '');

    const folderBtn = p.folder_url
      ? `<a href="${escapeHtml(p.folder_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-secondary py-0 px-2" title="Abrir carpeta compartida">Carpeta</a>`
      : '';

    tr.innerHTML = `
      <td>
        <span class="badge bg-body-secondary text-body border font-monospace">PJ-${String(p.id).padStart(2, '0')}</span>
      </td>
      <td>
        <div class="d-flex align-items-center gap-1">
          <a href="/project/${p.id}" class="fw-bold text-body text-decoration-none" title="Abrir proyecto">
            ${escapeHtml(p.name)}
          </a>
          ${blockerHtml}
        </div>
        ${subtitle}
      </td>
      <td>
        ${projArea ? `<span class="badge bg-info-subtle text-info border border-info-subtle">${escapeHtml(projArea)}</span>` : '<span class="text-muted small">—</span>'}
      </td>
      <td>
        <div class="small ${p.stakeholder ? 'text-body' : 'text-muted'}">${escapeHtml(p.stakeholder || '—')}</div>
        ${p.area_key_user ? `<div class="text-muted text-truncate" style="font-size:11px; max-width:160px;" title="Key User: ${escapeHtml(p.area_key_user)}">KU: ${escapeHtml(p.area_key_user)}</div>` : ''}
      </td>
      <td>
        <span class="small ${p.owner ? 'fw-semibold text-body' : 'text-muted'}">${escapeHtml(p.owner || 'Sin asignar')}</span>
      </td>
      <td>
        <span class="badge ${prioClass}">${escapeHtml(p.priority || 'Media')}</span>
      </td>
      <td>
        <span class="badge ${statusClass}">${escapeHtml(p.status || 'En tiempo')}</span>
      </td>
      <td>
        <div class="small font-monospace text-muted" style="font-size: 11px;">Ini: ${startText}</div>
        <div class="small font-monospace ${overdue ? 'text-danger fw-bold' : 'text-body'}" style="font-size: 11px;">Lim: ${dueText}</div>
      </td>
      <td class="text-center">
        <button class="btn btn-sm py-0 px-2 btn-toggle-vis ${p.is_visible !== false ? 'btn-outline-success' : 'btn-outline-secondary'}" style="font-size: 0.75rem;" title="${p.is_visible !== false ? 'Visible en selector superior (clic para ocultar)' : 'Oculto de selector superior (clic para mostrar)'}">
          ${p.is_visible !== false ? 'Visible' : 'Oculto'}
        </button>
      </td>
      <td>
        <div class="d-flex align-items-center gap-2">
          <div class="progress flex-grow-1 portfolio-progress-bar" style="background: var(--border-subtle); height: 6px;">
            <div class="progress-bar ${pct === 100 ? 'bg-success' : 'bg-primary'}" role="progressbar" style="width: ${pct}%"></div>
          </div>
          <span class="small text-muted font-monospace" style="min-width: 38px;">${completed}/${total}</span>
        </div>
      </td>
      <td class="text-end">
        <div class="d-flex justify-content-end gap-1 flex-nowrap">
          ${folderBtn}
          <a href="/project/${p.id}?tab=bitacora" class="btn btn-sm btn-outline-secondary py-0 px-2" title="${p.last_bitacora_date ? `Última bitácora: ${escapeHtml(p.last_bitacora_date)}` : 'Ir a bitácora'}">Bitácora</a>
          <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-portfolio-edit" title="Editar proyecto">Editar</button>
          <a href="/project/${p.id}" class="btn btn-sm btn-outline-primary py-0 px-2" title="Abrir tablero">Abrir</a>
        </div>
      </td>
    `;

    tr.querySelector('.btn-toggle-vis')?.addEventListener('click', async (e) => {
      e.stopPropagation();
      const newVis = !(p.is_visible !== false);
      try {
        const res = await fetch(`/api/projects/${p.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_visible: newVis })
        });
        if (res.ok) {
          p.is_visible = newVis;
          populateQuickJumpSelect(allProjects);
          applyHubFilters();
        }
      } catch (err) {
        console.error('Error toggling visibility:', err);
      }
    });

    tr.querySelector('.btn-portfolio-edit')?.addEventListener('click', (e) => {
      e.stopPropagation();
      populateProjectSettingsModal(p, projectSettingsModalInstance);
    });

    tbody.appendChild(tr);
  });
}

let backupsModalInstance = null;

function setupBackupsModal() {
  const modalEl = document.getElementById('backups-modal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    backupsModalInstance = new bootstrap.Modal(modalEl);
  }

  document.getElementById('btn-open-backups')?.addEventListener('click', async () => {
    setBackupStatus('', '');
    if (backupsModalInstance) backupsModalInstance.show();
    await loadBackupsList();
  });

  document.getElementById('btn-create-manual-backup')?.addEventListener('click', async (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    const origText = btn.textContent;
    btn.textContent = 'Generando...';
    setBackupStatus('', '');
    try {
      const res = await fetch('/api/backups', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) {
        setBackupStatus(data.detail || 'Error generando respaldo.', 'danger');
      } else {
        setBackupStatus(`Respaldo creado: ${data.filename} (${data.size_human})`, 'success');
        await loadBackupsList();
      }
    } catch (err) {
      console.error('Create backup error:', err);
      setBackupStatus('Error de conexión al generar el respaldo.', 'danger');
    } finally {
      btn.disabled = false;
      btn.textContent = origText;
    }
  });
}

function setBackupStatus(message, type) {
  const el = document.getElementById('backup-status-msg');
  if (!el) return;
  if (!message) {
    el.className = 'alert py-2 small d-none';
    el.textContent = '';
    return;
  }
  el.className = `alert alert-${type || 'info'} py-2 small`;
  el.textContent = message;
}

async function loadBackupsList() {
  const { escapeHtml } = window.HiggingsCommon;
  const tbody = document.getElementById('backups-table-body');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4 small">Cargando respaldos...</td></tr>';
  try {
    const res = await fetch('/api/backups');
    if (!res.ok) throw new Error('Error listando respaldos');
    const backups = await res.json();
    if (!backups.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4 small">No hay respaldos registrados todavía.</td></tr>';
      return;
    }
    tbody.innerHTML = '';
    backups.forEach(b => {
      const tr = document.createElement('tr');
      const isAuto = b.backup_type === 'auto';
      const typeBadge = isAuto
        ? '<span class="badge bg-info-subtle text-info border border-info-subtle">Automático</span>'
        : '<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Manual</span>';
      const dt = b.created_at ? new Date(b.created_at) : null;
      const dateStr = dt && !Number.isNaN(dt.getTime())
        ? dt.toLocaleString('es-MX', { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })
        : (b.created_at || '—');

      tr.innerHTML = `
        <td class="small fw-semibold font-monospace">${escapeHtml(b.filename)}</td>
        <td>${typeBadge}</td>
        <td class="small text-muted text-nowrap">${escapeHtml(dateStr)}</td>
        <td class="small">${escapeHtml(b.size_human)}</td>
        <td class="text-end">
          <a href="/api/backups/${encodeURIComponent(b.filename)}/download" download class="btn btn-sm btn-outline-primary py-0 px-2">Descargar</a>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Backups list error:', err);
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger py-4 small">No se pudieron cargar los respaldos.</td></tr>';
  }
}
