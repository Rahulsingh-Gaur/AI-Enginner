// ============================================================
// QA TASK MANAGER - API INTEGRATION
// Backend: Node.js + Express + SQLite
// ============================================================

const API_BASE_URL = 'http://localhost:3000/api';
const STATUSES = ['Unassigned', 'Assigned', 'In Progress', 'UAT Completed', 'Overdue', 'Deprecated', 'Blocked', 'Deployed', 'Rollbacked'];
const STATUS_COLORS = {
    'Unassigned': '#7c3aed',
    'Assigned': '#14b8a6',
    'In Progress': '#b45309',
    'UAT Completed': '#059669',
    'Overdue': '#dc2626',
    'Deprecated': '#6b7280',
    'Blocked': '#dc2626',
    'Deployed': '#0ea5e9',
    'Rollbacked': '#f43f5e'
};
const PRIORITY_ORDER = { 'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3 };
const ASSIGNEE_COLORS = {
    'Rahul': '#6366f1',
    'Suraj': '#ec4899',
    'Neet': '#f59e0b',
    'Anita': '#10b981'
};
const TAG_CLASSES = {
    'Bug': 'tag-bug',
    'Feature': 'tag-feature',
    'Regression': 'tag-regression',
    'Automation': 'tag-automation',
    'Manual': 'tag-manual',
    'API': 'tag-api',
    'UI': 'tag-ui',
    'Performance': 'tag-performance'
};

let tasks = [];
let taskIdCounter = 1;
let currentView = 'kanban';
let isLoading = false;
let apiAvailable = true;

// ============================================================
// API LAYER
// ============================================================

async function apiRequest(endpoint, options = {}) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
            },
            signal: controller.signal,
            ...options
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        apiAvailable = true;
        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        apiAvailable = false;
        console.warn('API unavailable, using localStorage fallback:', error.message);
        throw error;
    }
}

// Check API health
async function checkApiHealth() {
    try {
        const result = await apiRequest('/health');
        console.log('✅ API Connected:', result);
        return true;
    } catch (error) {
        console.warn('❌ API not available:', error.message);
        showToast('⚠️ Running in offline mode - data saved locally', 'info');
        return false;
    }
}

// ============================================================
// OFFLINE SYNC FUNCTIONALITY
// ============================================================

const OFFLINE_TASKS_KEY = 'qa_offline_tasks';

// Get offline tasks from localStorage
function getOfflineTasks() {
    const stored = localStorage.getItem(OFFLINE_TASKS_KEY);
    return stored ? JSON.parse(stored) : [];
}

// Save offline tasks to localStorage
function saveOfflineTasks(offlineTasks) {
    localStorage.setItem(OFFLINE_TASKS_KEY, JSON.stringify(offlineTasks));
    updateSyncUI();
}

// Add task to offline queue
function addOfflineTask(taskData) {
    const offlineTasks = getOfflineTasks();
    const offlineTask = {
        ...taskData,
        offlineId: 'OFFLINE-' + Date.now(),
        createdAt: new Date().toISOString()
    };
    offlineTasks.push(offlineTask);
    saveOfflineTasks(offlineTasks);
    showToast('📴 Task saved offline. Will sync when server is available.', 'info');
    return offlineTask;
}

// Update sync UI (button visibility, count, etc.)
function updateSyncUI() {
    const offlineTasks = getOfflineTasks();
    const syncSection = document.getElementById('sync-section');
    const syncCount = document.getElementById('sync-count');
    const syncText = document.getElementById('sync-text');
    const syncBtn = document.getElementById('sync-btn');
    const syncStatus = document.getElementById('sync-status');
    
    if (!syncSection) return;
    
    const count = offlineTasks.length;
    
    if (count > 0) {
        syncSection.style.display = 'block';
        syncCount.textContent = count;
        syncCount.classList.remove('hidden');
        syncText.textContent = `${count} task${count > 1 ? 's' : ''} pending sync`;
        syncBtn.disabled = false;
        syncSection.classList.add('has-pending');
        syncStatus.textContent = '';
        syncStatus.className = 'sync-status';
    } else {
        syncSection.style.display = 'block';
        syncCount.classList.add('hidden');
        syncText.textContent = 'No pending changes';
        syncBtn.disabled = true;
        syncSection.classList.remove('has-pending');
        syncStatus.textContent = '';
        syncStatus.className = 'sync-status';
    }
}

// Sync offline tasks with server
async function syncOfflineData() {
    const offlineTasks = getOfflineTasks();
    if (offlineTasks.length === 0) {
        showToast('No offline tasks to sync', 'info');
        return;
    }
    
    const syncBtn = document.getElementById('sync-btn');
    const syncBtnText = document.getElementById('sync-btn-text');
    const syncStatus = document.getElementById('sync-status');
    
    syncBtn.disabled = true;
    syncBtn.classList.add('syncing');
    syncBtnText.textContent = '🔄 Syncing...';
    syncStatus.textContent = 'Syncing offline tasks...';
    syncStatus.className = 'sync-status';
    
    let successCount = 0;
    let failCount = 0;
    const failedTasks = [];
    
    for (const task of offlineTasks) {
        try {
            // Remove offline-specific fields before sending to API
            const { offlineId, createdAt, ...taskData } = task;
            
            const response = await fetch(`${API_BASE_URL}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
            
            if (response.ok) {
                successCount++;
            } else {
                failCount++;
                failedTasks.push(task);
            }
        } catch (error) {
            failCount++;
            failedTasks.push(task);
        }
    }
    
    // Save failed tasks for retry
    saveOfflineTasks(failedTasks);
    
    // Update UI
    syncBtn.classList.remove('syncing');
    syncBtn.disabled = failedTasks.length === 0;
    syncBtnText.textContent = '🔄 Sync Now';
    
    if (failCount === 0) {
        syncStatus.textContent = `✅ All ${successCount} task(s) synced successfully!`;
        syncStatus.className = 'sync-status success';
        showToast(`✅ Sync complete: ${successCount} task(s) uploaded`, 'success');
        
        // Reload tasks from server
        await loadTasks();
        renderAll();
    } else {
        syncStatus.textContent = `⚠️ ${successCount} synced, ${failCount} failed. Will retry.`;
        syncStatus.className = 'sync-status error';
        showToast(`⚠️ Sync partial: ${successCount} success, ${failCount} failed`, 'warning');
    }
}

// Auto-sync when coming back online
async function autoSyncWhenOnline() {
    const offlineTasks = getOfflineTasks();
    if (offlineTasks.length > 0 && apiAvailable) {
        showToast('🌐 Connection restored. Auto-syncing offline tasks...', 'info');
        await syncOfflineData();
    }
}

// ============================================================
// SYSTEM STATUS PANEL
// ============================================================

// Update status indicator
function updateStatusIndicator(type, status, message) {
    const indicator = document.getElementById(`indicator-${type}`);
    const text = document.getElementById(`text-${type}`);
    
    if (!indicator || !text) return;
    
    // Remove all status classes
    indicator.classList.remove('online', 'offline', 'checking');
    
    // Add appropriate class
    if (status === 'online') {
        indicator.classList.add('online');
        text.textContent = message || 'Connected';
        text.style.color = '#10b981';
    } else if (status === 'offline') {
        indicator.classList.add('offline');
        text.textContent = message || 'Disconnected';
        text.style.color = '#ef4444';
    } else {
        indicator.classList.add('checking');
        text.textContent = message || 'Checking...';
        text.style.color = 'rgba(255,255,255,0.5)';
    }
}

// Check all system statuses
let previousApiStatus = 'unknown';

async function checkSystemStatus() {
    let serverOnline = false;
    let apiOnline = false;
    
    // Check Server (can we reach the port?)
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        await fetch('http://localhost:3000', { 
            method: 'HEAD',
            signal: controller.signal 
        });
        clearTimeout(timeoutId);
        updateStatusIndicator('server', 'online', 'Running');
        serverOnline = true;
    } catch (error) {
        updateStatusIndicator('server', 'offline', 'Stopped');
    }
    
    // Check API
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (response.ok) {
            updateStatusIndicator('api', 'online', 'Running');
            apiOnline = true;
            
            // Check if API just came back online
            if (previousApiStatus === 'offline') {
                console.log('🌐 API back online, checking for offline tasks...');
                await autoSyncWhenOnline();
            }
            previousApiStatus = 'online';
        } else {
            updateStatusIndicator('api', 'offline', 'Error');
            previousApiStatus = 'offline';
        }
    } catch (error) {
        updateStatusIndicator('api', 'offline', 'Stopped');
        previousApiStatus = 'offline';
    }
    
    // Check Database
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            if (data.database && data.database.includes('SQLite')) {
                updateStatusIndicator('db', 'online', 'Connected');
            } else {
                updateStatusIndicator('db', 'offline', 'Error');
            }
        } else {
            updateStatusIndicator('db', 'offline', 'Error');
        }
    } catch (error) {
        updateStatusIndicator('db', 'offline', 'Disconnected');
    }
    
    // Update sync UI whenever status changes
    updateSyncUI();
}

// Start periodic status checks
function startStatusChecks() {
    // Check immediately
    checkSystemStatus();
    
    // Check every 10 seconds
    setInterval(checkSystemStatus, 10000);
}

// ============================================================
// DATA OPERATIONS
// ============================================================

// Load tasks from API or fallback to localStorage
async function loadTasks() {
    showLoading(true);
    try {
        const filters = getFilterParams();
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = queryString ? `/tasks?${queryString}` : '/tasks';
        
        const result = await apiRequest(endpoint);
        tasks = result.data || [];
        taskIdCounter = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;
        apiAvailable = true;
        
        // Backup to localStorage
        localStorage.setItem('qa_tasks_cache', JSON.stringify(tasks));
    } catch (error) {
        // Fallback to cache
        const cached = localStorage.getItem('qa_tasks_cache');
        if (cached) {
            tasks = JSON.parse(cached);
            showToast('📂 Loaded from cache', 'info');
        } else {
            tasks = [];
        }
    } finally {
        showLoading(false);
    }
}

// Create new task
async function createTask(taskData) {
    try {
        const result = await apiRequest('/tasks', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
        showToast('✅ Task created successfully!', 'success');
        return result;
    } catch (error) {
        // Fallback: add to offline queue for later sync
        const offlineTask = addOfflineTask(taskData);
        
        // Also add to local array for immediate display
        const newTask = {
            id: offlineTask.offlineId,
            task_id: offlineTask.offlineId,
            ...taskData,
            tags: Array.isArray(taskData.tags) ? taskData.tags : (taskData.tags || '').split(','),
            updated_at: new Date().toISOString(),
            isOffline: true
        };
        tasks.push(newTask);
        localStorage.setItem('qa_tasks_cache', JSON.stringify(tasks));
        
        return { success: true, data: newTask };
    }
}

// Update task
async function updateTask(id, taskData) {
    try {
        const result = await apiRequest(`/tasks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(taskData)
        });
        showToast('✅ Task updated successfully!', 'success');
        return result;
    } catch (error) {
        // Fallback: update local array
        const index = tasks.findIndex(t => t.id == id);
        if (index !== -1) {
            tasks[index] = { ...tasks[index], ...taskData, updated_at: new Date().toISOString() };
            localStorage.setItem('qa_tasks_cache', JSON.stringify(tasks));
        }
        showToast('✅ Task updated locally (API unavailable)', 'info');
        return { success: true };
    }
}

// Delete task
async function deleteTaskApi(id) {
    try {
        const result = await apiRequest(`/tasks/${id}`, {
            method: 'DELETE'
        });
        showToast('🗑️ Task deleted', 'info');
        return result;
    } catch (error) {
        // Fallback: remove from local array
        tasks = tasks.filter(t => t.id != id);
        localStorage.setItem('qa_tasks_cache', JSON.stringify(tasks));
        showToast('🗑️ Task deleted locally (API unavailable)', 'info');
        return { success: true };
    }
}

// Update task status
async function updateTaskStatus(id, status) {
    try {
        const result = await apiRequest(`/tasks/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status })
        });
        return result;
    } catch (error) {
        // Fallback
        const index = tasks.findIndex(t => t.id == id);
        if (index !== -1) {
            tasks[index].status = status;
            tasks[index].updated_at = new Date().toISOString();
            localStorage.setItem('qa_tasks_cache', JSON.stringify(tasks));
        }
        return { success: true };
    }
}

// Get filter params from UI
function getFilterParams() {
    const params = {};
    const search = document.getElementById('searchInput')?.value;
    const priority = document.getElementById('filterPriority')?.value;
    const status = document.getElementById('filterStatus')?.value;
    
    // Get selected assignees from checkboxes
    const allAssigneesCheckbox = document.getElementById('filterAllAssignees');
    let assignee = '';
    
    if (!allAssigneesCheckbox?.checked) {
        const selectedAssignees = [];
        document.querySelectorAll('.filter-assignee-option:checked').forEach(cb => {
            selectedAssignees.push(cb.value);
        });
        if (selectedAssignees.length > 0) {
            assignee = selectedAssignees[0]; // Use first for API
        }
    }
    
    if (search) params.search = search;
    if (priority) params.priority = priority;
    if (assignee) params.assignee = assignee;
    if (status) params.status = status;
    
    return params;
}

// ============================================================
// UI HELPERS
// ============================================================

function showLoading(show) {
    isLoading = show;
    let loader = document.getElementById('page-loader');
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'page-loader';
            loader.innerHTML = `
                <div style="display:flex;flex-direction:column;align-items:center;gap:12px;">
                    <div style="width:40px;height:40px;border:3px solid #e5e7eb;border-top-color:#6366f1;border-radius:50%;animation:spin 1s linear infinite;"></div>
                    <span style="font-size:14px;color:#6b7280;font-weight:500;">Loading...</span>
                </div>
                <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
            `;
            loader.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:9999;background:rgba(255,255,255,0.95);padding:30px 40px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.2);';
            document.body.appendChild(loader);
        }
    } else if (loader) {
        loader.remove();
    }
}

// Helpers
function getTodayStr() {
    return new Date().toISOString().split('T')[0];
}
function getTomorrowStr() {
    const d = new Date(); d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
}
function getYesterdayStr() {
    const d = new Date(); d.setDate(d.getDate() - 1);
    return d.toISOString().split('T')[0];
}
function addDays(n) {
    const d = new Date(); d.setDate(d.getDate() + n);
    return d.toISOString().split('T')[0];
}
function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}
function isOverdue(dateStr) {
    if (!dateStr) return false;
    return new Date(dateStr) < new Date(getTodayStr());
}
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// FILTERING
// ============================================================

function getFilteredTasks() {
    let filtered = [...tasks];
    const search = document.getElementById('searchInput').value.toLowerCase();
    const priority = document.getElementById('filterPriority').value;
    const status = document.getElementById('filterStatus').value;
    
    // Get selected assignees from checkboxes
    const allAssigneesCheckbox = document.getElementById('filterAllAssignees');
    let selectedAssignees = [];
    
    if (!allAssigneesCheckbox?.checked) {
        document.querySelectorAll('.filter-assignee-option:checked').forEach(cb => {
            selectedAssignees.push(cb.value);
        });
    }

    if (search) filtered = filtered.filter(t =>
        t.title?.toLowerCase().includes(search) ||
        t.description?.toLowerCase().includes(search) ||
        t.module?.toLowerCase().includes(search) ||
        (t.tags && t.tags.some(tag => tag.toLowerCase().includes(search)))
    );
    if (priority) filtered = filtered.filter(t => t.priority === priority);
    if (selectedAssignees.length > 0) {
        // Filter tasks that contain ANY of the selected assignees
        filtered = filtered.filter(t => {
            if (!t.assignee) return false;
            const taskAssignees = t.assignee.split(',').map(a => a.trim());
            return selectedAssignees.some(sa => taskAssignees.includes(sa));
        });
    }
    if (status) filtered = filtered.filter(t => t.status === status);

    filtered.sort((a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]);
    return filtered;
}

async function filterTasks() { 
    await loadTasks();
    renderAll(); 
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filterPriority').value = '';
    document.getElementById('filterStatus').value = '';
    
    // Reset filter assignee checkbox dropdown
    resetFilterAssigneeDropdown();
    
    filterTasks();
}

async function filterBySidebarStatus(status) {
    document.getElementById('filterStatus').value = status;
    await filterTasks();
}

async function filterByTag(tag) {
    document.getElementById('searchInput').value = tag;
    await filterTasks();
}

// ============================================================
// RENDERING
// ============================================================

function renderAll() {
    renderStats();
    renderKanban();
    renderTable();
    renderListView();
    updateNavCounts();
    populateAssigneeFilter();
}

function renderStats() {
    const total = tasks.length;
    const byStatus = {};
    STATUSES.forEach(s => byStatus[s] = tasks.filter(t => t.status === s).length);
    const uatPercent = total > 0 ? Math.round((byStatus['UAT Completed'] / total) * 100) : 0;
    const overdueTasks = tasks.filter(t => t.status !== 'UAT Completed' && t.status !== 'Deployed' && isOverdue(t.due_date)).length;

    document.getElementById('stats-grid').innerHTML = `
        <div class="stat-card total" onclick="document.getElementById('filterStatus').value=''; filterTasks();">
            <div class="stat-info">
                <h4>Total Tasks</h4>
                <div class="stat-number">${total}</div>
                <div class="stat-change up">📊 All tasks tracked</div>
            </div>
            <div class="stat-icon">📋</div>
        </div>
        <div class="stat-card review" onclick="filterBySidebarStatus('Unassigned')">
            <div class="stat-info">
                <h4>Unassigned</h4>
                <div class="stat-number">${byStatus['Unassigned']}</div>
                <div class="stat-change">👁️ Awaiting to assigned</div>
            </div>
            <div class="stat-icon">🔍</div>
        </div>
        <div class="stat-card assigned" onclick="filterBySidebarStatus('Assigned')">
            <div class="stat-info">
                <h4>Assigned</h4>
                <div class="stat-number">${byStatus['Assigned']}</div>
                <div class="stat-change up">✅ Task assigned</div>
            </div>
            <div class="stat-icon">👤</div>
        </div>
        <div class="stat-card progress" onclick="filterBySidebarStatus('In Progress')">
            <div class="stat-info">
                <h4>In Progress</h4>
                <div class="stat-number">${byStatus['In Progress']}</div>
                <div class="stat-change">🔄 Active work</div>
            </div>
            <div class="stat-icon">⚡</div>
        </div>
        <div class="stat-card done" onclick="filterBySidebarStatus('UAT Completed')">
            <div class="stat-info">
                <h4>UAT Completed</h4>
                <div class="stat-number">${byStatus['UAT Completed']}</div>
                <div class="stat-change up">✅ ${uatPercent}% done</div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width:${uatPercent}%; background: linear-gradient(90deg, #10b981, #059669);"></div>
                </div>
            </div>
            <div class="stat-icon">🏆</div>
        </div>
        <div class="stat-card bugs">
            <div class="stat-info">
                <h4>Overdue</h4>
                <div class="stat-number">${overdueTasks}</div>
                <div class="stat-change down">⏰ Past due date</div>
            </div>
            <div class="stat-icon">🔥</div>
        </div>
        <div class="stat-card deprecated" onclick="filterBySidebarStatus('Deprecated')">
            <div class="stat-info">
                <h4>Deprecated</h4>
                <div class="stat-number">${byStatus['Deprecated']}</div>
                <div class="stat-change">🗄️ Archived tasks</div>
            </div>
            <div class="stat-icon">📦</div>
        </div>
        <div class="stat-card blocked" onclick="filterBySidebarStatus('Blocked')">
            <div class="stat-info">
                <h4>Blocked</h4>
                <div class="stat-number">${byStatus['Blocked']}</div>
                <div class="stat-change down">🚫 Needs attention</div>
            </div>
            <div class="stat-icon">⛔</div>
        </div>
        <div class="stat-card deployed" onclick="filterBySidebarStatus('Deployed')">
            <div class="stat-info">
                <h4>Deployed</h4>
                <div class="stat-number">${byStatus['Deployed']}</div>
                <div class="stat-change up">🚀 In Production</div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width:${total > 0 ? Math.round((byStatus['Deployed'] / total) * 100) : 0}%; background: linear-gradient(90deg, #0ea5e9, #0284c7);"></div>
                </div>
            </div>
            <div class="stat-icon">🚀</div>
        </div>
        <div class="stat-card rollbacked" onclick="filterBySidebarStatus('Rollbacked')">
            <div class="stat-info">
                <h4>Rollbacked</h4>
                <div class="stat-number">${byStatus['Rollbacked']}</div>
                <div class="stat-change down">⚠️ Reverted</div>
            </div>
            <div class="stat-icon">↩️</div>
        </div>
    `;
}

function renderKanban() {
    const filtered = getFilteredTasks();
    const board = document.getElementById('kanban-board');
    board.innerHTML = '';

    const displayStatuses = ['Unassigned', 'Assigned', 'In Progress', 'UAT Completed', 'Overdue', 'Deprecated', 'Blocked', 'Deployed', 'Rollbacked'];

    displayStatuses.forEach(status => {
        const statusTasks = filtered.filter(t => t.status === status);
        const col = document.createElement('div');
        col.className = 'kanban-column';
        col.dataset.status = status;
        
        // Add drag and drop event listeners to column
        col.addEventListener('dragover', handleDragOver);
        col.addEventListener('dragenter', handleDragEnter);
        col.addEventListener('dragleave', handleDragLeave);
        col.addEventListener('drop', handleDrop);
        
        col.innerHTML = `
            <div class="column-header">
                <div class="column-header-left">
                    <div class="column-dot" style="background:${STATUS_COLORS[status]}"></div>
                    <h3>${status}</h3>
                </div>
                <span class="column-count">${statusTasks.length}</span>
            </div>
            <div class="column-content">
                ${statusTasks.map(t => renderTaskCard(t)).join('')}
            </div>
            <button class="add-card-btn" onclick="openAddModalWithStatus('${status}')">➕ Add Task</button>
        `;
        board.appendChild(col);
    });
}

let draggedTaskId = null;

// Helper function to render multiple assignees
function renderAssignees(assigneeData, size = 'normal') {
    // Handle different data types (string, array, or undefined)
    let assignees = [];
    
    if (!assigneeData) {
        return '<span class="task-assignee"><span style="color:#9ca3af;">Unassigned</span></span>';
    } else if (typeof assigneeData === 'string') {
        // Check for corrupted data
        if (assigneeData.includes('[object')) {
            return '<span class="task-assignee"><span style="color:#9ca3af;">Unassigned</span></span>';
        }
        assignees = assigneeData.split(',').map(a => a.trim()).filter(a => a && !a.includes('[object'));
    } else if (Array.isArray(assigneeData)) {
        assignees = assigneeData.filter(a => a && typeof a === 'string' && !a.includes('[object'));
    } else {
        return '<span class="task-assignee"><span style="color:#9ca3af;">Unassigned</span></span>';
    }
    
    if (assignees.length === 0) return '<span class="task-assignee"><span style="color:#9ca3af;">Unassigned</span></span>';
    
    const avatarSize = size === 'small' ? '22px' : '26px';
    const fontSize = size === 'small' ? '9px' : '10px';
    
    let html = '<div class="task-assignee-multi" style="display:flex;align-items:center;gap:2px;">';
    
    // Show overlapping avatars (max 3)
    const displayAssignees = assignees.slice(0, 3);
    displayAssignees.forEach((assignee, index) => {
        const avatarColor = ASSIGNEE_COLORS[assignee] || '#6b7280';
        // Get first 2 characters of name as initial
        const initial = assignee.substring(0, 2).toUpperCase();
        
        html += `
            <div class="assignee-avatar" style="background:${avatarColor};width:${avatarSize};height:${avatarSize};font-size:${fontSize};border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.2);margin-left:${index > 0 ? '-6px' : '0'};z-index:${10-index};display:flex;align-items:center;justify-content:center;font-weight:700;color:white;border-radius:50%;">${initial}</div>
        `;
    });
    
    // Show count if more than 3 assignees
    if (assignees.length > 3) {
        html += `<span style="margin-left:4px;font-size:10px;font-weight:600;color:#6b7280;background:#f3f4f6;padding:2px 6px;border-radius:10px;">+${assignees.length - 3}</span>`;
    }
    
    // Show names text - for multiple assignees, show shortened format
    let nameDisplay = '';
    if (assignees.length === 1) {
        nameDisplay = assignees[0];
    } else {
        // For multiple assignees, just show count
        nameDisplay = `${assignees.length} assignees`;
    }
    
    html += `<span style="margin-left:6px;font-size:11px;color:var(--gray-600);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100px;">${nameDisplay}</span>`;
    
    html += '</div>';
    return html;
}

function renderTaskCard(t) {
    const priorityClass = `priority-${t.priority?.toLowerCase()}`;
    const overdue = t.status !== 'UAT Completed' && t.status !== 'Deployed' && isOverdue(t.due_date);
    const taskTags = Array.isArray(t.tags) ? t.tags : (t.tags ? t.tags.split(',') : []);

    return `
        <div class="task-card" draggable="true" data-task-id="${t.id}" ondragstart="handleDragStart(event, ${t.id})" ondragend="handleDragEnd(event)" ondblclick="openEditModal(${t.id})">
            <div class="task-actions">
                <button class="task-action-btn edit" onclick="event.stopPropagation(); openEditModal(${t.id})" title="Edit">✏️</button>
                <button class="task-action-btn delete" onclick="event.stopPropagation(); deleteTaskHandler(${t.id})" title="Delete">🗑️</button>
            </div>
            <div class="task-card-top">
                <span class="task-id">${t.task_id || 'QA-' + String(t.id).padStart(3,'0')}</span>
                <span class="task-priority ${priorityClass}">${t.priority}</span>
            </div>
            <h4>${escapeHtml(t.title)}</h4>
            <p>${escapeHtml(t.description || '').substring(0, 80)}${(t.description || '').length > 80 ? '...' : ''}</p>
            ${taskTags.length > 0 ? `
                <div class="task-tags">
                    ${taskTags.map(tag => `<span class="task-tag ${TAG_CLASSES[tag] || ''}">${tag}</span>`).join('')}
                </div>
            ` : ''}
            <div class="task-card-bottom">
                ${renderAssignees(t.assignee)}
                <div class="task-meta">
                    <span class="task-meta-item">🚀 ${formatDate(t.start_date)}</span>
                    <span class="task-meta-item ${overdue ? 'overdue' : ''}" style="${overdue ? 'color:#dc2626;font-weight:700;' : ''}">
                        📅 ${formatDate(t.due_date)}${overdue ? ' ⚠️' : ''}
                    </span>
                </div>
            </div>
        </div>
    `;
}

function renderTable() {
    const filtered = getFilteredTasks();
    const tbody = document.getElementById('table-body');

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">📭</div><h3>No tasks found</h3><p>Try adjusting your filters or add a new task.</p></div></td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(t => {
        const statusClass = `status-${t.status?.toLowerCase().replace(/\s+/g, '-')}`;
        const priorityClass = `priority-${t.priority?.toLowerCase()}`;
        const overdue = t.status !== 'UAT Completed' && t.status !== 'Deployed' && isOverdue(t.due_date);
        const isDone = t.status === 'Deployed';
        const taskTags = Array.isArray(t.tags) ? t.tags : (t.tags ? t.tags.split(',') : []);

        return `
            <tr ondblclick="openEditModal(${t.id})">
                <td>
                    <div class="table-task-name">
                        <div class="checkbox ${isDone ? 'checked' : ''}" onclick="event.stopPropagation(); toggleDone(${t.id})"></div>
                        <div>
                            <div style="font-weight:600; color: var(--gray-800); ${isDone ? 'text-decoration:line-through; opacity:0.6;' : ''}">
                                <span style="color:var(--gray-400); font-size:11px; margin-right:6px;">${t.task_id || 'QA-' + String(t.id).padStart(3,'0')}</span>
                                ${escapeHtml(t.title)}
                            </div>
                            <div style="font-size:11px; color:var(--gray-400); margin-top:2px;">📁 ${t.module || 'General'} • 🌐 ${t.environment || 'QA'}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge ${statusClass}" style="cursor:pointer;" onclick="event.stopPropagation(); cycleStatus(${t.id})">${t.status}</span>
                </td>
                <td><span class="task-priority ${priorityClass}">${t.priority}</span></td>
                <td>
                    ${renderAssignees(t.assignee, 'small')}
                </td>
                <td>
                    <span class="start-date">🚀 ${formatDate(t.start_date)}</span>
                </td>
                <td>
                    <span class="due-date ${overdue ? 'overdue' : ''}">
                        📅 ${formatDate(t.due_date)} ${overdue ? '⚠️' : ''}
                    </span>
                </td>
                <td>
                    <div class="task-tags">
                        ${taskTags.map(tag => `<span class="task-tag ${TAG_CLASSES[tag] || ''}">${tag}</span>`).join('')}
                    </div>
                </td>
                <td>
                    <div class="table-actions">
                        <button class="task-action-btn edit" onclick="event.stopPropagation(); openEditModal(${t.id})" title="Edit">✏️</button>
                        <button class="task-action-btn delete" onclick="event.stopPropagation(); deleteTaskHandler(${t.id})" title="Delete">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderListView() {
    const filtered = getFilteredTasks();
    const container = document.getElementById('list-view');

    if (filtered.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">📭</div><h3>No tasks found</h3><p>Try adjusting your filters or add a new task.</p></div>`;
        return;
    }

    container.innerHTML = filtered.map(t => {
        const overdue = t.status !== 'UAT Completed' && t.status !== 'Deployed' && isOverdue(t.due_date);
        const isDone = t.status === 'Deployed';
        const statusClass = `status-${t.status?.toLowerCase().replace(/\s+/g, '-')}`;
        const priorityColor = t.priority === 'Critical' ? '#dc2626' : t.priority === 'High' ? '#ea580c' : t.priority === 'Medium' ? '#ca8a04' : '#16a34a';
        const taskTags = Array.isArray(t.tags) ? t.tags : (t.tags ? t.tags.split(',') : []);

        return `
            <div class="list-card" ondblclick="openEditModal(${t.id})">
                <div class="list-priority-bar" style="background:${priorityColor}"></div>
                <div class="list-checkbox ${isDone ? 'done' : ''}" onclick="event.stopPropagation(); toggleDone(${t.id})"></div>
                <div class="list-card-content">
                    <h4 style="${isDone ? 'text-decoration:line-through; opacity:0.5;' : ''}">${escapeHtml(t.title)}</h4>
                    <div class="list-desc">${escapeHtml(t.description || '').substring(0, 100)}${(t.description || '').length > 100 ? '...' : ''}</div>
                    <div class="list-card-meta">
                        <span class="status-badge ${statusClass}" style="cursor:pointer;font-size:10px;" onclick="event.stopPropagation(); cycleStatus(${t.id})">${t.status}</span>
                        ${taskTags.map(tag => `<span class="task-tag ${TAG_CLASSES[tag] || ''}" style="font-size:9px;">${tag}</span>`).join('')}
                        <span style="font-size:11px; color:var(--gray-400);">📁 ${t.module || 'General'}</span>
                        <span style="font-size:11px; color:var(--gray-400);">🌐 ${t.environment || 'QA'}</span>
                    </div>
                </div>
                <div class="list-card-right">
                    <span class="start-date" style="font-size:11px; color:var(--gray-500);">🚀 ${formatDate(t.start_date)}</span>
                    <span class="due-date ${overdue ? 'overdue' : ''}">
                        📅 ${formatDate(t.due_date)} ${overdue ? '⚠️' : ''}
                    </span>
                    ${renderAssignees(t.assignee, 'small')}
                    <button class="task-action-btn edit" onclick="event.stopPropagation(); openEditModal(${t.id})" title="Edit">✏️</button>
                    <button class="task-action-btn delete" onclick="event.stopPropagation(); deleteTaskHandler(${t.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `;
    }).join('');
}

function updateNavCounts() {
    document.getElementById('nav-total-count').textContent = tasks.length;
    document.getElementById('nav-blocked-count').textContent = tasks.filter(t => t.status === 'Blocked').length;
}

function populateAssigneeFilter() {
    const select = document.getElementById('filterAssignee');
    const currentValue = select.value;
    
    // Get unique assignees from all tasks (handling comma-separated multiple assignees)
    const allAssignees = new Set();
    tasks.forEach(t => {
        if (t.assignee) {
            t.assignee.split(',').forEach(a => allAssignees.add(a.trim()));
        }
    });
    
    const assignees = [...allAssignees].sort();
    select.innerHTML = '<option value="">All Assignees</option>' +
        assignees.map(a => `<option value="${a}" ${a === currentValue ? 'selected' : ''}>${a}</option>`).join('');
}

// ============================================================
// CRUD OPERATIONS
// ============================================================

function openAddModal() {
    document.getElementById('modalTitle').textContent = '➕ Add New Task';
    document.getElementById('editTaskId').value = '';
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDesc').value = '';
    document.getElementById('taskStatus').value = 'Unassigned';
    document.getElementById('taskPriority').value = 'Medium';
    
    // Reset assignee checkbox dropdown
    resetAssigneeDropdown('taskAssignee');
    
    document.getElementById('taskStartDate').value = getTodayStr();
    document.getElementById('taskDueDate').value = getTodayStr();
    document.getElementById('taskModule').value = '';
    document.getElementById('taskEnv').value = 'QA';
    const tagsSelect = document.getElementById('taskTags');
    for (let i = 0; i < tagsSelect.options.length; i++) tagsSelect.options[i].selected = false;

    document.getElementById('taskModal').classList.add('active');
    document.getElementById('taskTitle').focus();
}

function openAddModalWithStatus(status) {
    openAddModal();
    document.getElementById('taskStatus').value = status;
}

function openEditModal(id) {
    const task = tasks.find(t => t.id == id);
    if (!task) return;

    document.getElementById('modalTitle').textContent = '✏️ Edit Task — ' + (task.task_id || 'QA-' + String(id).padStart(3, '0'));
    document.getElementById('editTaskId').value = id;
    document.getElementById('taskTitle').value = task.title;
    document.getElementById('taskDesc').value = task.description || '';
    document.getElementById('taskStatus').value = task.status;
    document.getElementById('taskPriority').value = task.priority;
    
    // Handle multiple assignees using checkbox dropdown
    setSelectedAssignees('taskAssignee', task.assignee);
    
    document.getElementById('taskStartDate').value = task.start_date || getTodayStr();
    document.getElementById('taskDueDate').value = task.due_date;
    document.getElementById('taskModule').value = task.module || '';
    document.getElementById('taskEnv').value = task.environment || 'QA';

    const tagsSelect = document.getElementById('taskTags');
    const taskTags = Array.isArray(task.tags) ? task.tags : (task.tags ? task.tags.split(',') : []);
    for (let i = 0; i < tagsSelect.options.length; i++) {
        tagsSelect.options[i].selected = taskTags.includes(tagsSelect.options[i].value);
    }

    document.getElementById('taskModal').classList.add('active');
}

function closeModal() {
    document.getElementById('taskModal').classList.remove('active');
}

async function saveTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const desc = document.getElementById('taskDesc').value.trim();
    const status = document.getElementById('taskStatus').value;
    const priority = document.getElementById('taskPriority').value;
    
    // Get multiple assignees
    const assigneeSelect = document.getElementById('taskAssignee');
    const assignees = [];
    for (let i = 0; i < assigneeSelect.options.length; i++) {
        if (assigneeSelect.options[i].selected) assignees.push(assigneeSelect.options[i].value);
    }
    
    const startDate = document.getElementById('taskStartDate').value;
    const dueDate = document.getElementById('taskDueDate').value;
    const module = document.getElementById('taskModule').value.trim();
    const env = document.getElementById('taskEnv').value;
    const editId = document.getElementById('editTaskId').value;

    const tagsSelect = document.getElementById('taskTags');
    const tags = [];
    for (let i = 0; i < tagsSelect.options.length; i++) {
        if (tagsSelect.options[i].selected) tags.push(tagsSelect.options[i].value);
    }

    if (!title) { showToast('❌ Task title is required!', 'error'); return; }
    if (assignees.length === 0) { showToast('❌ At least one assignee is required!', 'error'); return; }
    if (!startDate) { showToast('❌ Start date is required!', 'error'); return; }
    if (!dueDate) { showToast('❌ Due date is required!', 'error'); return; }

    // Ensure assignees is properly formatted as array of strings
    const assigneeArray = assignees.filter(a => a && typeof a === 'string');
    
    const taskData = {
        title,
        description: desc,
        status,
        priority,
        assignee: assigneeArray, // Array of assignees
        start_date: startDate,
        due_date: dueDate,
        module: module || 'General',
        environment: env,
        tags
    };

    showLoading(true);
    
    if (editId) {
        await updateTask(editId, taskData);
    } else {
        await createTask(taskData);
    }

    closeModal();
    await loadTasks();
    renderAll();
    showLoading(false);
}

async function deleteTaskHandler(id) {
    const task = tasks.find(t => t.id == id);
    const taskLabel = task ? (task.task_id || 'QA-' + String(id).padStart(3, '0')) : `Task ${id}`;
    
    if (!confirm(`Are you sure you want to delete ${taskLabel}?`)) return;
    
    showLoading(true);
    await deleteTaskApi(id);
    await loadTasks();
    renderAll();
    showLoading(false);
}

async function toggleDone(id) {
    const task = tasks.find(t => t.id == id);
    if (task) {
        let newStatus;
        let previousStatus = task.previous_status;
        
        if (task.status === 'Deployed') {
            // Unchecking: restore previous status (or default to Unassigned if none stored)
            newStatus = previousStatus || 'Unassigned';
        } else {
            // Checking: store current status as previous, then mark as Deployed
            newStatus = 'Deployed';
            previousStatus = task.status;
        }
        
        showLoading(true);
        
        // Update task with new status and previous_status
        const updateData = {
            status: newStatus,
            previous_status: previousStatus
        };
        
        await updateTask(id, updateData);
        await loadTasks();
        renderAll();
        showLoading(false);
        
        if (newStatus === 'Deployed') {
            showToast('🚀 Task marked as Deployed!', 'success');
        } else {
            showToast(`↩️ Task restored to "${newStatus}"`, 'success');
        }
    }
}

async function cycleStatus(id) {
    const task = tasks.find(t => t.id == id);
    if (task) {
        const currentIdx = STATUSES.indexOf(task.status);
        const newStatus = STATUSES[(currentIdx + 1) % STATUSES.length];
        showLoading(true);
        await updateTaskStatus(id, newStatus);
        await loadTasks();
        renderAll();
        showLoading(false);
        showToast(`🔄 Status changed to "${newStatus}"`, 'info');
    }
}

// ============================================================
// VIEW SWITCHING
// ============================================================
function switchView(view, tabEl) {
    currentView = view;
    document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
    document.getElementById('view-' + view).classList.add('active');
    document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
    if (tabEl) tabEl.classList.add('active');
}

function switchPage(page) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

// ============================================================
// TOAST
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================================
// DRAG AND DROP - KANBAN BOARD
// ============================================================

function handleDragStart(event, taskId) {
    draggedTaskId = taskId;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', taskId);
    
    // Add dragging class for visual feedback
    event.target.classList.add('dragging');
    
    // Create a custom drag image
    const dragImage = event.target.cloneNode(true);
    dragImage.style.opacity = '0.8';
    dragImage.style.transform = 'rotate(2deg) scale(1.02)';
    dragImage.style.width = event.target.offsetWidth + 'px';
    document.body.appendChild(dragImage);
    event.dataTransfer.setDragImage(dragImage, 20, 20);
    
    // Remove the custom element after a brief delay
    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
    
    // Highlight all drop zones
    document.querySelectorAll('.kanban-column').forEach(col => {
        if (col.dataset.status !== tasks.find(t => t.id == taskId)?.status) {
            col.classList.add('drop-target');
        }
    });
}

function handleDragEnd(event) {
    event.target.classList.remove('dragging');
    draggedTaskId = null;
    
    // Remove all highlights
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.classList.remove('drop-target', 'drop-active');
    });
}

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(event) {
    event.preventDefault();
    const column = event.currentTarget;
    if (draggedTaskId) {
        column.classList.add('drop-active');
    }
}

function handleDragLeave(event) {
    const column = event.currentTarget;
    // Only remove if we're actually leaving the column (not entering a child)
    if (!column.contains(event.relatedTarget)) {
        column.classList.remove('drop-active');
    }
}

async function handleDrop(event) {
    event.preventDefault();
    const column = event.currentTarget;
    const newStatus = column.dataset.status;
    
    column.classList.remove('drop-active');
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.classList.remove('drop-target');
    });
    
    if (!draggedTaskId || !newStatus) return;
    
    const task = tasks.find(t => t.id == draggedTaskId);
    if (!task || task.status === newStatus) return;
    
    const oldStatus = task.status;
    
    // Show loading
    showLoading(true);
    
    // Update task status via API
    const result = await updateTaskStatus(draggedTaskId, newStatus);
    
    if (result.success) {
        showToast(`✅ Moved to "${newStatus}"`, 'success');
        await loadTasks();
        renderAll();
    } else {
        showToast('❌ Failed to move task', 'error');
    }
    
    showLoading(false);
    draggedTaskId = null;
}

// ============================================================
// CHECKBOX DROPDOWN FUNCTIONS
// ============================================================

// Toggle dropdown open/close
function toggleAssigneeDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    const content = dropdown.querySelector('.checkbox-dropdown-content');
    const header = dropdown.querySelector('.checkbox-dropdown-header');
    
    content.classList.toggle('show');
    header.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdowns = document.querySelectorAll('.checkbox-dropdown');
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(e.target)) {
            const content = dropdown.querySelector('.checkbox-dropdown-content');
            const header = dropdown.querySelector('.checkbox-dropdown-header');
            if (content) content.classList.remove('show');
            if (header) header.classList.remove('active');
        }
    });
});

// Update display text and hidden select when checkboxes change
function updateAssigneeDisplay(selectId) {
    const dropdown = document.getElementById(selectId + 'Dropdown');
    const display = document.getElementById(selectId + 'Display');
    const hiddenSelect = document.getElementById(selectId);
    
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
    const selected = [];
    
    checkboxes.forEach((cb, index) => {
        if (cb.checked) {
            selected.push(cb.value);
        }
        // Update hidden select option
        hiddenSelect.options[index].selected = cb.checked;
    });
    
    // Update display text
    if (selected.length === 0) {
        display.textContent = 'Select Assignees...';
    } else if (selected.length === 1) {
        display.textContent = selected[0];
    } else {
        display.textContent = `${selected[0]} +${selected.length - 1} more`;
    }
}

// Set selected assignees (for edit mode)
function setSelectedAssignees(selectId, assignees) {
    const dropdown = document.getElementById(selectId + 'Dropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
    const assigneeList = assignees ? assignees.split(',').map(a => a.trim()) : [];
    
    checkboxes.forEach(cb => {
        cb.checked = assigneeList.includes(cb.value);
    });
    
    updateAssigneeDisplay(selectId);
}

// Reset assignee dropdown
function resetAssigneeDropdown(selectId) {
    const dropdown = document.getElementById(selectId + 'Dropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
    
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    
    // Select first by default
    if (checkboxes.length > 0) {
        checkboxes[0].checked = true;
    }
    
    updateAssigneeDisplay(selectId);
}

// ============================================================
// FILTER ASSIGNEE DROPDOWN FUNCTIONS
// ============================================================

// Update filter assignee display and trigger filter
function updateFilterAssigneeDisplay() {
    const allAssigneesCheckbox = document.getElementById('filterAllAssignees');
    const assigneeCheckboxes = document.querySelectorAll('.filter-assignee-option');
    const display = document.getElementById('filterAssigneeDisplay');
    const hiddenSelect = document.getElementById('filterAssignee');
    
    // If "All Assignees" is checked, uncheck all others
    if (allAssigneesCheckbox.checked) {
        assigneeCheckboxes.forEach(cb => {
            cb.checked = false;
        });
        display.textContent = 'All Assignees';
        hiddenSelect.value = '';
    } else {
        // Get selected assignees
        const selected = [];
        assigneeCheckboxes.forEach(cb => {
            if (cb.checked) selected.push(cb.value);
        });
        
        // If no individual assignees selected, check "All Assignees"
        if (selected.length === 0) {
            allAssigneesCheckbox.checked = true;
            display.textContent = 'All Assignees';
            hiddenSelect.value = '';
        } else {
            // Update display
            if (selected.length === 1) {
                display.textContent = selected[0];
            } else {
                display.textContent = `${selected[0]} +${selected.length - 1}`;
            }
            
            // Update hidden select (use first selected for API compatibility)
            hiddenSelect.value = selected[0];
        }
    }
    
    // Trigger filter
    filterTasks();
}

// Handle individual assignee checkbox change
function handleFilterAssigneeChange() {
    const allAssigneesCheckbox = document.getElementById('filterAllAssignees');
    const assigneeCheckboxes = document.querySelectorAll('.filter-assignee-option');
    
    // If any individual assignee is checked, uncheck "All Assignees"
    const anySelected = Array.from(assigneeCheckboxes).some(cb => cb.checked);
    if (anySelected) {
        allAssigneesCheckbox.checked = false;
    }
    
    updateFilterAssigneeDisplay();
}

// Reset filter assignee dropdown
function resetFilterAssigneeDropdown() {
    const allAssigneesCheckbox = document.getElementById('filterAllAssignees');
    const assigneeCheckboxes = document.querySelectorAll('.filter-assignee-option');
    
    allAssigneesCheckbox.checked = true;
    assigneeCheckboxes.forEach(cb => {
        cb.checked = false;
    });
    
    updateFilterAssigneeDisplay();
}

// ============================================================
// INIT
// ============================================================
async function init() {
    // Set current date
    const now = new Date();
    document.getElementById('current-date').textContent =
        now.toLocaleDateString('en-IN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });

    // Set default dates
    document.getElementById('taskDueDate').value = getTodayStr();

    // Check API health
    await checkApiHealth();
    
    // Start system status checks
    startStatusChecks();
    
    // Initialize sync UI
    updateSyncUI();
    
    // Check for offline tasks and try auto-sync if online
    const offlineTasks = getOfflineTasks();
    if (offlineTasks.length > 0) {
        console.log(`📴 Found ${offlineTasks.length} offline task(s) pending sync`);
        if (apiAvailable) {
            await autoSyncWhenOnline();
        }
    }

    // Load and render
    await loadTasks();
    renderAll();

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
        if (e.key === 'n' && e.altKey) { e.preventDefault(); openAddModal(); }
    });

    // Close modal on overlay click
    document.getElementById('taskModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('taskModal')) closeModal();
    });
    
    // Auto-refresh every 30 seconds when API is available
    setInterval(async () => {
        if (apiAvailable && document.visibilityState === 'visible') {
            await loadTasks();
            renderAll();
        }
    }, 30000);
}

// Start the app
init();
