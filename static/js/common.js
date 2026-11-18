/**
 * Higgings Agile & MCP Platform — Shared Frontend Utilities & Modals
 */

window.HiggingsCommon = (() => {
  let usersCatalog = [];
  let usersModalInstance = null;
  let editingUserId = null;

  function initTheme() {
    const savedTheme = localStorage.getItem('pj67-theme') || 'dark';
    applyTheme(savedTheme);

    document.getElementById('btn-theme-toggle')?.addEventListener('click', () => {
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

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatProjectDisplay(p) {
    if (!p) return '';
    const prefix = `PJ-${String(p.id).padStart(2, '0')}`;
    return p.name && p.name.startsWith('PJ-') ? p.name : `${prefix} — ${p.name || ''}`;
  }

  function getStatusBadgeClass(status) {
    if (status === 'Completado') return 'bg-success text-white border border-success';
    if (status === 'En tiempo') return 'bg-success-subtle text-success border border-success-subtle';
    if (status === 'En riesgo') return 'bg-warning-subtle text-warning border border-warning-subtle';
    if (status === 'Retrasado') return 'bg-danger-subtle text-danger border border-danger-subtle';
    if (status === 'En mantenimiento') return 'bg-info-subtle text-info border border-info-subtle';
    return 'bg-secondary-subtle text-secondary border';
  }

  function getPriorityBadgeClass(priority) {
    if (priority === 'Crítica') return 'bg-danger-subtle text-danger border border-danger-subtle';
    if (priority === 'Alta') return 'bg-warning-subtle text-warning border border-warning-subtle';
    if (priority === 'Media') return 'bg-primary-subtle text-primary border border-primary-subtle';
    return 'bg-secondary-subtle text-secondary border';
  }

  function renderBlockerAlertBadge(project) {
    const text = (project && project.risks_blockers ? project.risks_blockers : '').trim();
    if (!text) return '';
    return `<span class="badge bg-warning text-dark rounded-circle fw-bold d-inline-flex align-items-center justify-content-center ms-1" style="width:18px;height:18px;font-size:11px;cursor:help;" title="Bloqueo / Riesgo: ${escapeHtml(text)}">!</span>`;
  }

  function isProjectOverdue(p) {
    if (!p || !p.due_date) return false;
    if (p.status === 'Completado' || p.status === 'En mantenimiento') return false;
    const today = new Date().toISOString().slice(0, 10);
    return p.due_date < today;
  }

  // ==========================================
  // Catálogo y Gestión de Usuarios (Equipo)
  // ==========================================

  async function fetchUsersCatalog(includeInactive = true) {
    try {
      const res = await fetch(`/api/users?include_inactive=${includeInactive ? 'true' : 'false'}`);
      if (!res.ok) throw new Error('Error al cargar usuarios');
      usersCatalog = await res.json();
    } catch (err) {
      console.error('Users fetch error:', err);
      usersCatalog = [];
    }
    return usersCatalog;
  }

  function getUsers() {
    return usersCatalog;
  }

  function getActiveUsers() {
    return usersCatalog.filter(u => u.is_active !== false);
  }

  function getUserColor(name) {
    if (!name || name === 'Sin asignar') return null;
    const u = usersCatalog.find(item => item.name === name);
    return u && u.color ? u.color : '#0c66e4';
  }

  function getUserBadgeAttributes(name) {
    const clean = name && name.trim() ? name.trim() : 'Sin asignar';
    if (clean === 'Sin asignar') {
      return { className: 'agent-default', style: '' };
    }
    const color = getUserColor(clean) || '#0c66e4';
    return {
      className: 'user-custom-badge',
      style: `background-color: ${color}22; color: ${color}; border: 1px solid ${color}44;`
    };
  }

  function populateUserSelect(selectEl, selectedValue = '', emptyLabel = 'Sin asignar') {
    if (!selectEl) return;
    const targetVal = (selectedValue || '').trim();
    selectEl.innerHTML = '';

    const defaultOpt = document.createElement('option');
    defaultOpt.value = emptyLabel === 'Sin asignar' ? 'Sin asignar' : '';
    defaultOpt.textContent = emptyLabel;
    selectEl.appendChild(defaultOpt);

    const activeUsers = getActiveUsers();
    const seen = new Set([defaultOpt.value]);

    activeUsers.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.name;
      opt.textContent = u.area ? `${u.name} (${u.area})` : u.name;
      selectEl.appendChild(opt);
      seen.add(u.name);
    });

    // Preservar un valor histórico o inactivo si existe en el registro actual
    if (targetVal && !seen.has(targetVal)) {
      const fallbackOpt = document.createElement('option');
      fallbackOpt.value = targetVal;
      fallbackOpt.textContent = `${targetVal} (No listado)`;
      selectEl.appendChild(fallbackOpt);
    }

    selectEl.value = targetVal || defaultOpt.value;
  }

  function setupUsersModal(onUsersChanged) {
    const modalEl = document.getElementById('users-modal');
    if (modalEl && typeof bootstrap !== 'undefined') {
      usersModalInstance = new bootstrap.Modal(modalEl);
    }

    const btnOpen = document.getElementById('btn-manage-users');
    btnOpen?.addEventListener('click', async () => {
      await fetchUsersCatalog(true);
      resetUserForm();
      renderUsersTable(onUsersChanged);
      if (usersModalInstance) usersModalInstance.show();
    });

    document.getElementById('btn-user-form-cancel')?.addEventListener('click', resetUserForm);

    document.getElementById('btn-user-form-save')?.addEventListener('click', async () => {
      const name = document.getElementById('user-form-name')?.value.trim();
      const email = document.getElementById('user-form-email')?.value.trim() || '';
      const role = document.getElementById('user-form-role')?.value.trim() || 'Miembro';
      const area = document.getElementById('user-form-area')?.value.trim() || '';
      const color = document.getElementById('user-form-color')?.value || '#0c66e4';

      if (!name) {
        alert('El nombre del usuario es obligatorio.');
        return;
      }

      const url = editingUserId ? `/api/users/${editingUserId}` : '/api/users';
      const method = editingUserId ? 'PUT' : 'POST';

      try {
        const res = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, role, area, color, is_active: true })
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || 'Error al guardar usuario');
          return;
        }
        await fetchUsersCatalog(true);
        resetUserForm();
        renderUsersTable(onUsersChanged);
        if (typeof onUsersChanged === 'function') await onUsersChanged();
      } catch (err) {
        console.error('Save user error:', err);
        alert('Error de conexión al guardar usuario.');
      }
    });
  }

  function resetUserForm() {
    editingUserId = null;
    const setVal = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.value = v;
    };
    setVal('user-form-name', '');
    setVal('user-form-email', '');
    setVal('user-form-role', 'Responsable');
    setVal('user-form-area', '');
    setVal('user-form-color', '#0c66e4');
    const titleEl = document.getElementById('user-form-heading');
    if (titleEl) titleEl.textContent = 'Agregar Integrante';
    const cancelBtn = document.getElementById('btn-user-form-cancel');
    if (cancelBtn) cancelBtn.style.display = 'none';
  }

  function renderUsersTable(onUsersChanged) {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;

    if (usersCatalog.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center text-muted py-4 small">
            No hay integrantes registrados. Agrega el primero en el formulario superior.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = '';
    usersCatalog.forEach(u => {
      const tr = document.createElement('tr');
      const activeBadge = u.is_active !== false
        ? '<span class="badge bg-success-subtle text-success border border-success-subtle">Activo</span>'
        : '<span class="badge bg-secondary-subtle text-muted border">Inactivo</span>';

      tr.innerHTML = `
        <td>
          <div class="d-flex align-items-center gap-2">
            <span class="rounded-circle d-inline-block flex-shrink-0" style="width:10px;height:10px;background:${escapeHtml(u.color || '#0c66e4')};"></span>
            <div>
              <div class="fw-semibold text-body small">${escapeHtml(u.name)}</div>
              ${u.email ? `<div class="text-muted" style="font-size:11px;">${escapeHtml(u.email)}</div>` : ''}
            </div>
          </div>
        </td>
        <td class="small">${escapeHtml(u.role || 'Miembro')}</td>
        <td class="small text-muted">${escapeHtml(u.area || '—')}</td>
        <td class="text-center">${activeBadge}</td>
        <td class="text-end">
          <div class="d-flex justify-content-end gap-1">
            <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-edit-user">Editar</button>
            <button class="btn btn-sm btn-outline-danger py-0 px-2 btn-delete-user">Eliminar</button>
          </div>
        </td>
      `;

      tr.querySelector('.btn-edit-user')?.addEventListener('click', () => {
        editingUserId = u.id;
        document.getElementById('user-form-name').value = u.name || '';
        document.getElementById('user-form-email').value = u.email || '';
        document.getElementById('user-form-role').value = u.role || 'Miembro';
        document.getElementById('user-form-area').value = u.area || '';
        document.getElementById('user-form-color').value = u.color || '#0c66e4';
        const titleEl = document.getElementById('user-form-heading');
        if (titleEl) titleEl.textContent = `Editando a ${u.name}`;
        const cancelBtn = document.getElementById('btn-user-form-cancel');
        if (cancelBtn) cancelBtn.style.display = 'inline-block';
      });

      tr.querySelector('.btn-delete-user')?.addEventListener('click', async () => {
        if (!confirm(`¿Eliminar a "${u.name}"? Sus tareas asignadas pasarán a "Sin asignar".`)) return;
        const res = await fetch(`/api/users/${u.id}`, { method: 'DELETE' });
        if (res.ok) {
          await fetchUsersCatalog(true);
          renderUsersTable(onUsersChanged);
          if (typeof onUsersChanged === 'function') await onUsersChanged();
        }
      });

      tbody.appendChild(tr);
    });
  }

  // ==========================================
  // Helpers Compartidos de Modal de Proyecto
  // ==========================================

  function populateProjectSettingsModal(project, modalInstance) {
    const isCreate = !project;
    const p = project || {};

    const titleEl = document.getElementById('modal-proj-title');
    if (titleEl) titleEl.textContent = isCreate ? 'Nuevo Proyecto' : 'Configuración del Proyecto';

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val;
    };

    setVal('modal-proj-id', isCreate ? '' : p.id);
    setVal('modal-proj-name', p.name || '');
    setVal('modal-proj-area', p.area || p.theme || '');
    setVal('modal-proj-stakeholder', p.stakeholder || '');
    setVal('modal-proj-area-key-user', p.area_key_user || '');
    setVal('modal-proj-start-date', p.start_date || '');
    setVal('modal-proj-due-date', p.due_date || '');
    setVal('modal-proj-priority', p.priority || 'Media');
    setVal('modal-proj-status', p.status || 'En tiempo');
    setVal('modal-proj-folder', p.folder_url || '');
    setVal('modal-proj-github', p.github_url || '');
    setVal('modal-proj-next-step', p.next_step || '');
    setVal('modal-proj-risks-blockers', p.risks_blockers || '');
    setVal('modal-proj-desc', p.description || '');

    const ownerSel = document.getElementById('modal-proj-owner');
    populateUserSelect(ownerSel, p.owner || '', 'Sin asignar');

    const visInput = document.getElementById('modal-proj-visible');
    if (visInput) visInput.checked = isCreate ? true : (p.is_visible !== false);

    if (modalInstance) modalInstance.show();
  }

  async function submitProjectSettingsModal(modalInstance, onSaved) {
    const idRaw = document.getElementById('modal-proj-id')?.value;
    const hasId = idRaw !== undefined && idRaw !== null && idRaw !== '';
    const targetId = hasId ? parseInt(idRaw, 10) : null;

    const name = document.getElementById('modal-proj-name')?.value.trim();
    if (!name) {
      alert('El nombre del proyecto es obligatorio.');
      return;
    }

    const ownerVal = document.getElementById('modal-proj-owner')?.value || '';
    const areaVal = document.getElementById('modal-proj-area')?.value.trim() || '';
    const payload = {
      name,
      area: areaVal,
      theme: areaVal,
      stakeholder: document.getElementById('modal-proj-stakeholder')?.value.trim() || '',
      area_key_user: document.getElementById('modal-proj-area-key-user')?.value.trim() || '',
      owner: ownerVal === 'Sin asignar' ? '' : ownerVal,
      start_date: document.getElementById('modal-proj-start-date')?.value || '',
      due_date: document.getElementById('modal-proj-due-date')?.value || '',
      priority: document.getElementById('modal-proj-priority')?.value || 'Media',
      status: document.getElementById('modal-proj-status')?.value || 'En tiempo',
      folder_url: document.getElementById('modal-proj-folder')?.value.trim() || '',
      github_url: document.getElementById('modal-proj-github')?.value.trim() || '',
      next_step: document.getElementById('modal-proj-next-step')?.value.trim() || '',
      risks_blockers: document.getElementById('modal-proj-risks-blockers')?.value.trim() || '',
      description: document.getElementById('modal-proj-desc')?.value.trim() || '',
      is_visible: document.getElementById('modal-proj-visible') ? document.getElementById('modal-proj-visible').checked : true
    };

    const url = targetId !== null ? `/api/projects/${targetId}` : '/api/projects';
    const method = targetId !== null ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        alert('Error al guardar proyecto: ' + (err.detail || 'Error desconocido'));
        return;
      }
      const saved = await res.json();
      if (modalInstance) modalInstance.hide();
      if (typeof onSaved === 'function') await onSaved(saved, targetId === null);
    } catch (err) {
      console.error('Error saving project:', err);
      alert('Error de conexión al guardar proyecto.');
    }
  }

  // ==========================================
  // Registro Histórico de Actividad Compartido
  // ==========================================

  let activityModalInstance = null;
  let activityState = {
    range: 'week',
    projectsGetter: () => [],
    defaultProjectId: null
  };

  function toUtcIsoNoMs(dateObj) {
    return dateObj.toISOString().replace(/\.\d{3}Z$/, 'Z');
  }

  function toLocalDateInputValue(dateObj) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  function parseLocalDateInput(val, isEnd) {
    if (!val || !/^\d{4}-\d{2}-\d{2}$/.test(val)) return null;
    const [y, m, d] = val.split('-').map(Number);
    return isEnd
      ? new Date(y, m - 1, d, 23, 59, 59)
      : new Date(y, m - 1, d, 0, 0, 0);
  }

  function ensureDefaultCustomDates() {
    const fromEl = document.getElementById('activity-date-from');
    const toEl = document.getElementById('activity-date-to');
    if (!fromEl || !toEl) return;
    const now = new Date();
    if (!toEl.value) {
      toEl.value = toLocalDateInputValue(now);
    }
    if (!fromEl.value) {
      const weekAgo = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
      fromEl.value = toLocalDateInputValue(weekAgo);
    }
  }

  function computeActivityRange(rangeKey) {
    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
    const endOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

    if (rangeKey === 'today') {
      return {
        label: 'Hoy',
        startIso: toUtcIsoNoMs(startOfToday),
        endIso: toUtcIsoNoMs(endOfToday)
      };
    }
    if (rangeKey === 'yesterday') {
      const yStart = new Date(startOfToday);
      yStart.setDate(yStart.getDate() - 1);
      const yEnd = new Date(yStart.getFullYear(), yStart.getMonth(), yStart.getDate(), 23, 59, 59);
      return {
        label: 'Ayer',
        startIso: toUtcIsoNoMs(yStart),
        endIso: toUtcIsoNoMs(yEnd)
      };
    }
    if (rangeKey === 'week') {
      const dayOfWeek = (startOfToday.getDay() + 6) % 7; // 0 = Lunes
      const weekStart = new Date(startOfToday);
      weekStart.setDate(weekStart.getDate() - dayOfWeek);
      return {
        label: 'Esta semana',
        startIso: toUtcIsoNoMs(weekStart),
        endIso: toUtcIsoNoMs(endOfToday)
      };
    }
    if (rangeKey === 'month') {
      const mStart = new Date(startOfToday);
      mStart.setDate(mStart.getDate() - 30);
      return {
        label: 'Últimos 30 días',
        startIso: toUtcIsoNoMs(mStart),
        endIso: toUtcIsoNoMs(endOfToday)
      };
    }
    if (rangeKey === 'custom') {
      ensureDefaultCustomDates();
      let fromVal = document.getElementById('activity-date-from')?.value || '';
      let toVal = document.getElementById('activity-date-to')?.value || '';
      if (fromVal && toVal && fromVal > toVal) {
        [fromVal, toVal] = [toVal, fromVal];
      }
      const startDt = parseLocalDateInput(fromVal, false);
      const endDt = parseLocalDateInput(toVal, true);
      const label = (fromVal && toVal)
        ? `${fromVal} a ${toVal}`
        : (fromVal ? `Desde ${fromVal}` : (toVal ? `Hasta ${toVal}` : 'Personalizado'));
      return {
        label,
        startIso: startDt ? toUtcIsoNoMs(startDt) : null,
        endIso: endDt ? toUtcIsoNoMs(endDt) : null
      };
    }
    return { label: 'Todo el historial', startIso: null, endIso: null };
  }

  function formatActivityDate(isoStr) {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    if (Number.isNaN(d.getTime())) return isoStr;
    return d.toLocaleString('es-MX', {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function formatEntityBadge(entityType) {
    const map = {
      task: { label: 'Tarea', cls: 'bg-primary-subtle text-primary border-primary-subtle' },
      project: { label: 'Proyecto', cls: 'bg-info-subtle text-info border-info-subtle' },
      sprint: { label: 'Sprint', cls: 'bg-success-subtle text-success border-success-subtle' },
      release: { label: 'Release', cls: 'bg-warning-subtle text-warning border-warning-subtle' },
      bitacora: { label: 'Bitácora', cls: 'bg-secondary-subtle text-secondary border-secondary-subtle' }
    };
    const item = map[entityType] || { label: entityType || 'Evento', cls: 'bg-secondary-subtle text-secondary border-secondary-subtle' };
    return `<span class="badge border ${item.cls}">${escapeHtml(item.label)}</span>`;
  }

  function exportTextFile(filename, content) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function buildActivityDigest(rangeLabel, summary, events) {
    const lines = [
      `Resumen de Actividad (${rangeLabel}) — Generado ${new Date().toLocaleString('es-MX')}`,
      `Total eventos: ${summary.total_events} | Backlog -> Tablero: ${summary.moved_from_backlog} | Terminadas: ${summary.tasks_completed} | Creadas: ${summary.tasks_created} | Bloqueos: ${summary.blockers_logged}`,
      '------------------------------------------------------------------------'
    ];
    if (!events.length) {
      lines.push('- Sin movimientos registrados en este periodo.');
      return lines.join('\n');
    }
    events.forEach(ev => {
      const pName = ev.project_name || (ev.project_id ? `PJ-${ev.project_id}` : 'General');
      lines.push(`- [${formatActivityDate(ev.created_at)}] [${pName}] (${ev.actor}) ${ev.summary}`);
    });
    return lines.join('\n');
  }

  function populateActivityProjectFilter() {
    const sel = document.getElementById('activity-filter-project');
    if (!sel) return;
    const prev = sel.value;
    const projects = typeof activityState.projectsGetter === 'function' ? activityState.projectsGetter() : [];
    sel.innerHTML = '<option value="">Todos los proyectos</option>';
    (projects || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = String(p.id);
      opt.textContent = formatProjectDisplay(p);
      sel.appendChild(opt);
    });
    if (prev) sel.value = prev;
  }

  async function loadAndRenderActivity() {
    const tbody = document.getElementById('activity-events-tbody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4 small">Cargando historial...</td></tr>';

    const rangeInfo = computeActivityRange(activityState.range);
    const projectVal = document.getElementById('activity-filter-project')?.value || '';
    const entityVal = document.getElementById('activity-filter-entity')?.value || '';

    const params = new URLSearchParams();
    params.set('limit', '200');
    if (projectVal) params.set('project_id', projectVal);
    if (entityVal) params.set('entity_type', entityVal);
    if (rangeInfo.startIso) params.set('start_iso', rangeInfo.startIso);
    if (rangeInfo.endIso) params.set('end_iso', rangeInfo.endIso);

    try {
      const res = await fetch(`/api/activity?${params.toString()}`);
      if (!res.ok) throw new Error('Error cargando actividad');
      const data = await res.json();
      const s = data.summary || {};
      const events = data.events || [];

      const setNum = (id, v) => {
        const el = document.getElementById(id);
        if (el) el.textContent = String(v ?? 0);
      };
      setNum('act-sum-total', s.total_events);
      setNum('act-sum-from-backlog', s.moved_from_backlog);
      setNum('act-sum-completed', s.tasks_completed);
      setNum('act-sum-created', s.tasks_created);
      setNum('act-sum-projects', s.projects_updated);
      setNum('act-sum-blockers', s.blockers_logged);

      const exportBtn = document.getElementById('btn-export-activity-txt');
      if (exportBtn) {
        exportBtn.dataset.digest = buildActivityDigest(rangeInfo.label, s, events);
        exportBtn.dataset.rangeLabel = rangeInfo.label;
      }

      if (events.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4 small">Sin actividad registrada para los filtros seleccionados.</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      events.forEach(ev => {
        const tr = document.createElement('tr');
        const actorBadge = ev.actor === 'MCP'
          ? '<span class="badge bg-info-subtle text-info border border-info-subtle">MCP</span>'
          : '<span class="badge bg-secondary-subtle text-body border">Web</span>';
        const projLabel = ev.project_name || (ev.project_id ? `PJ-${ev.project_id}` : 'Portafolio');
        const projHtml = ev.project_id
          ? `<a href="/project/${ev.project_id}" class="text-decoration-none fw-semibold small">${escapeHtml(projLabel)}</a>`
          : `<span class="text-muted small">${escapeHtml(projLabel)}</span>`;
        const transitionBadge = (ev.field_name === 'estado' && ev.old_value && ev.new_value)
          ? `<div class="mt-1"><span class="badge bg-body-secondary text-muted border fw-normal">${escapeHtml(ev.old_value)}</span> <span class="text-muted small">-&gt;</span> <span class="badge bg-primary-subtle text-primary border border-primary-subtle fw-semibold">${escapeHtml(ev.new_value)}</span></div>`
          : '';

        tr.innerHTML = `
          <td class="small text-muted text-nowrap">${escapeHtml(formatActivityDate(ev.created_at))}</td>
          <td>${projHtml}</td>
          <td>${formatEntityBadge(ev.entity_type)}</td>
          <td class="small">
            <div>${escapeHtml(ev.summary)}</div>
            ${transitionBadge}
          </td>
          <td class="text-end">${actorBadge}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Activity load error:', err);
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger py-4 small">No se pudo cargar el historial de actividad.</td></tr>';
    }
  }

  function updatePresetButtonsUI(activeRange) {
    document.querySelectorAll('.activity-preset-btn').forEach(btn => {
      const isMatch = btn.dataset.range === activeRange;
      btn.classList.toggle('btn-primary', isMatch);
      btn.classList.toggle('btn-outline-secondary', !isMatch);
    });
    const customWrap = document.getElementById('activity-custom-range');
    if (customWrap) {
      customWrap.classList.toggle('d-none', activeRange !== 'custom');
    }
    if (activeRange === 'custom') {
      ensureDefaultCustomDates();
    }
  }

  function openActivityModal(projectIdOverride = undefined) {
    populateActivityProjectFilter();
    const sel = document.getElementById('activity-filter-project');
    if (sel) {
      const resolvedDefault = projectIdOverride !== undefined
        ? projectIdOverride
        : (typeof activityState.defaultProjectId === 'function' ? activityState.defaultProjectId() : activityState.defaultProjectId);
      sel.value = resolvedDefault ? String(resolvedDefault) : '';
    }
    updatePresetButtonsUI(activityState.range);
    if (activityModalInstance) activityModalInstance.show();
    loadAndRenderActivity();
  }

  function setupActivityModal(options = {}) {
    activityState.projectsGetter = options.projectsGetter || (() => []);
    activityState.defaultProjectId = options.defaultProjectId ?? null;

    const modalEl = document.getElementById('activity-modal');
    if (modalEl && typeof bootstrap !== 'undefined') {
      activityModalInstance = new bootstrap.Modal(modalEl);
    }

    document.getElementById('btn-open-activity')?.addEventListener('click', () => {
      openActivityModal();
    });

    document.querySelectorAll('.activity-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        activityState.range = btn.dataset.range || 'week';
        updatePresetButtonsUI(activityState.range);
        loadAndRenderActivity();
      });
    });

    const handleCustomDateChange = () => {
      activityState.range = 'custom';
      updatePresetButtonsUI('custom');
      loadAndRenderActivity();
    };
    document.getElementById('activity-date-from')?.addEventListener('change', handleCustomDateChange);
    document.getElementById('activity-date-to')?.addEventListener('change', handleCustomDateChange);

    document.getElementById('activity-filter-project')?.addEventListener('change', loadAndRenderActivity);
    document.getElementById('activity-filter-entity')?.addEventListener('change', loadAndRenderActivity);

    document.getElementById('btn-export-activity-txt')?.addEventListener('click', (e) => {
      const btn = e.currentTarget;
      const digest = btn.dataset.digest || '';
      if (!digest) return;
      const stamp = toLocalDateInputValue(new Date());
      exportTextFile(`actividad_higgings_${stamp}.txt`, digest);
    });
  }

  return {
    initTheme,
    applyTheme,
    escapeHtml,
    formatProjectDisplay,
    getStatusBadgeClass,
    getPriorityBadgeClass,
    renderBlockerAlertBadge,
    isProjectOverdue,
    fetchUsersCatalog,
    getUsers,
    getActiveUsers,
    getUserBadgeAttributes,
    populateUserSelect,
    setupUsersModal,
    populateProjectSettingsModal,
    submitProjectSettingsModal,
    setupActivityModal,
    openActivityModal
  };
})();
