/**
 * 一人公司AI团队 - 看板前端 (v2)
 * T13+T14: 全部API驱动，动态渲染
 */

// ============ 全局状态 ============
const AGENTS = {
    copywriter:      { name: '文案助理',   color: 'blue',   desc: '公文 · 周报 · 邮件 · 润色',     letter: 'CW' },
    social_media:    { name: '新媒体运营', color: 'pink',   desc: '小红书 · 抖音 · 公众号 · 热点', letter: 'SM' },
    analyst:         { name: '数据分析师', color: 'cyan',   desc: '报表 · 图表 · 趋势分析 · 清洗', letter: 'DA' },
    project_manager: { name: '项目管家',   color: 'indigo', desc: '任务拆解 · 进度追踪 · 日报',     letter: 'PM' },
    consultant:      { name: '商业顾问',   color: 'amber',  desc: '商业计划 · 竞品分析 · BP',       letter: 'BC' }
};

const STATUS_LABELS = {
    pending: '待处理', working: '进行中', review: '待审批',
    done: '已完成', rejected: '已打回', attention: '需关注'
};

const STATUS_STYLES = {
    pending:   'bg-gray-100 text-gray-600',
    working:   'bg-amber-50 text-amber-600',
    review:    'bg-purple-50 text-purple-600',
    done:      'bg-emerald-50 text-emerald-600',
    rejected:  'bg-red-50 text-red-500',
    attention: 'bg-orange-50 text-orange-600',
    idle:      'bg-gray-100 text-gray-500'
};

// 员工色块配色（用于替代emoji）
const AGENT_COLORS = {
    blue:   { bg: 'bg-blue-50',   text: 'text-blue-600',   border: 'border-blue-200', ring: 'ring-blue-100' },
    pink:   { bg: 'bg-pink-50',   text: 'text-pink-600',   border: 'border-pink-200', ring: 'ring-pink-100' },
    cyan:   { bg: 'bg-cyan-50',   text: 'text-cyan-600',   border: 'border-cyan-200', ring: 'ring-cyan-100' },
    indigo: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200', ring: 'ring-indigo-100' },
    amber:  { bg: 'bg-amber-50',  text: 'text-amber-600',  border: 'border-amber-200', ring: 'ring-amber-100' }
};

let selectedModalAgent = null;
let selectedTopic = null;
let startTime = Date.now();
let allTasksCache = [];
let currentFilter = 'all';
let currentAgentFilter = 'all';

// Chart.js 实例
let statusPieChart = null;
let agentBarChart = null;
let completionChart = null;

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', () => {
    updateWorkstationTime();
    updateUptime();
    loadAllData();
    setInterval(updateUptime, 60000);
    setInterval(loadAllData, 30000);
});

// ============ 统一数据加载入口 ============
async function loadAllData() {
    updateLastRefresh();
    await Promise.all([
        loadStats(),
        loadAgentStatus(),
        loadTasks(),
        loadReviews(),
        loadTimeline()
    ]);
}

// ============ API: 统计数据 ============
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) return;
        const s = await res.json();

        // 统计卡片
        animateNumber('statTotal', s.total_reviews);
        animateNumber('statDone', s.approved);
        animateNumber('statWorking', s.pending_review);
        animateNumber('statReview', s.pending_review);

        // 今日增量
        const todayDelta = document.querySelector('#statDone + div');
        if (todayDelta && s.today_done > 0) {
            todayDelta.textContent = `今日 +${s.today_done}`;
        }

        // 渲染图表
        renderStatusPieChart(s);
        if (s.agent_stats) {
            renderAgentBarChart(s.agent_stats);
            renderCompletionChart(s.agent_stats);
        }
    } catch (e) { /* 静默 */ }
}

// 数字跳动动画
function animateNumber(elId, target) {
    const el = document.getElementById(elId);
    if (!el) return;
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    const diff = target - current;
    const steps = 12;
    let step = 0;
    const timer = setInterval(() => {
        step++;
        el.textContent = Math.round(current + diff * (step / steps));
        if (step >= steps) { el.textContent = target; clearInterval(timer); }
    }, 30);
}

// ============ API: 员工状态 ============
async function loadAgentStatus() {
    try {
        const res = await fetch('/api/agents/status');
        if (!res.ok) return;
        const agents = await res.json();
        renderAgentPanel(agents);
    } catch (e) { /* 静默 */ }
}

function renderAgentPanel(agents) {
    const panel = document.getElementById('agentsPanel');
    if (!panel) return;

    let html = '';
    for (const [key, a] of Object.entries(agents)) {
        const colors = AGENT_COLORS[a.color] || AGENT_COLORS.blue;
        const statusLabel = a.status === 'working' ? '工作中' :
                           a.status === 'attention' ? '需关注' : '在线';
        const statusClass = a.status === 'working' ? 'bg-amber-50 text-amber-600' :
                           a.status === 'attention' ? 'bg-orange-50 text-orange-600' :
                           'bg-emerald-50 text-emerald-600';
        const dotClass = a.status === 'working' ? 'bg-amber-500 pulse-working' :
                        a.status === 'attention' ? 'bg-orange-500' : 'bg-emerald-500 pulse-online';
        const progressAnimated = a.status === 'working' ? 'progress-animated' : '';

        html += `
        <div class="agent-row flex items-center gap-4 px-5 py-3.5 cursor-pointer" onclick="showAgentDetail('${key}')">
            <div class="w-10 h-10 rounded-xl ${colors.bg} flex items-center justify-center shrink-0">
                <span class="text-xs font-bold ${colors.text}">${a.letter}</span>
            </div>
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                    <span class="text-sm font-semibold text-slate-800">${a.name}</span>
                    <span class="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${statusClass}">
                        <span class="w-1.5 h-1.5 rounded-full ${dotClass}"></span>${statusLabel}
                    </span>
                </div>
                <div class="text-xs text-gray-400 mt-0.5">${a.desc}</div>
            </div>
            <div class="text-right shrink-0">
                <div class="text-sm font-semibold text-slate-700">累计 <span class="text-brand-600">${a.total}</span> 项</div>
                <div class="text-xs text-gray-400 mt-0.5">完成 ${a.done}/${a.total}</div>
            </div>
            <div class="w-24 shrink-0 hidden sm:block">
                <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div class="h-full ${a.progress === 100 ? 'bg-emerald-500' : a.status === 'working' ? 'bg-amber-500 ' + progressAnimated : 'bg-gray-300'} rounded-full" style="width:${a.progress}%"></div>
                </div>
            </div>
            <svg class="w-4 h-4 text-gray-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </div>`;
    }
    panel.innerHTML = html;
}

// ============ API: 任务列表 ============
async function loadTasks() {
    try {
        const res = await fetch('/api/tasks');
        if (!res.ok) return;
        allTasksCache = await res.json();
        renderFilteredTasks();
    } catch (e) { /* 静默 */ }
}

function renderFilteredTasks() {
    let tasks = allTasksCache;

    // 状态筛选
    if (currentFilter !== 'all') {
        tasks = tasks.filter(t => t.status === currentFilter);
    }
    // 员工筛选
    if (currentAgentFilter !== 'all') {
        tasks = tasks.filter(t => t.agent === currentAgentFilter);
    }

    renderTaskTable(tasks);
}

function renderTaskTable(tasks) {
    const tbody = document.getElementById('taskTableBody');
    if (!tbody) return;

    if (!tasks || !tasks.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-5 py-12 text-center text-gray-400 text-sm">暂无任务记录</td></tr>';
        return;
    }

    tbody.innerHTML = tasks.map(t => {
        const agent = AGENTS[t.agent] || { name: t.agent || '未知', color: 'blue', letter: '?' };
        const colors = AGENT_COLORS[agent.color] || AGENT_COLORS.blue;
        const statusClass = STATUS_STYLES[t.status] || STATUS_STYLES.pending;
        const statusLabel = STATUS_LABELS[t.status] || t.status;
        const time = t.created_at ? t.created_at.slice(11, 16) : '';
        const id = typeof t.id === 'string' ? `"${t.id}"` : t.id;

        return `
        <tr class="task-row">
            <td class="px-5 py-3">
                <div class="text-sm font-medium text-slate-700">${t.input || t.title || '未命名'}</div>
            </td>
            <td class="px-4 py-3 hidden md:table-cell">
                <span class="inline-flex items-center gap-1.5">
                    <span class="w-5 h-5 rounded ${colors.bg} flex items-center justify-center">
                        <span class="text-[9px] font-bold ${colors.text}">${agent.letter}</span>
                    </span>
                    <span class="text-sm text-gray-600">${agent.name}</span>
                </span>
            </td>
            <td class="px-4 py-3 hidden lg:table-cell">
                <span class="text-sm text-gray-500">${t.type || '-'}</span>
            </td>
            <td class="px-4 py-3">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${statusClass}">${statusLabel}</span>
            </td>
            <td class="px-4 py-3 hidden sm:table-cell">
                <span class="text-xs text-gray-400">${time}</span>
            </td>
            <td class="px-5 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                    ${t.status === 'review' ? `
                        <button onclick="reviewTask(${id}, 'approve')" class="px-2.5 py-1 rounded-md text-xs font-medium text-emerald-600 hover:bg-emerald-50 transition">通过</button>
                        <button onclick="reviewTask(${id}, 'reject')" class="px-2.5 py-1 rounded-md text-xs font-medium text-red-500 hover:bg-red-50 transition">打回</button>
                    ` : `
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium text-gray-500 hover:bg-gray-100 transition">查看</button>
                    `}
                </div>
            </td>
        </tr>`;
    }).join('');

    const countEl = document.getElementById('taskCount');
    if (countEl) countEl.textContent = `共 ${tasks.length} 条记录`;
}

// ============ API: 待审批 ============
async function loadReviews() {
    try {
        const res = await fetch('/api/reviews');
        if (!res.ok) return;
        const reviews = await res.json();
        renderPendingPanel(reviews);
    } catch (e) { /* 静默 */ }
}

function renderPendingPanel(reviews) {
    const panel = document.getElementById('pendingTasksPanel');
    const countEl = document.getElementById('pendingCount');
    if (!panel) return;

    if (countEl) countEl.textContent = `${reviews.length} 项待办`;

    if (!reviews.length) {
        panel.innerHTML = '<div class="p-4 text-center text-sm text-gray-400">暂无待审批任务</div>';
        return;
    }

    panel.innerHTML = reviews.slice(0, 5).map(r => {
        const agent = AGENTS[r.employee] || { name: '未知', color: 'blue', letter: '?' };
        const colors = AGENT_COLORS[agent.color] || AGENT_COLORS.blue;
        return `
        <div class="p-4 flex items-start gap-3 hover:bg-gray-50 transition cursor-pointer">
            <div class="w-2 h-2 rounded-full bg-purple-400 mt-1.5 shrink-0"></div>
            <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-slate-700 truncate">${r.title || '未命名'}</div>
                <div class="text-xs text-gray-400 mt-0.5">${agent.name} · ${r.task_type || ''}</div>
            </div>
            <div class="flex items-center gap-1 shrink-0">
                <button onclick="reviewTask('${r.review_id || r.id}', 'approve')" class="px-2 py-1 rounded text-[11px] font-medium text-emerald-600 hover:bg-emerald-50">通过</button>
                <button onclick="reviewTask('${r.review_id || r.id}', 'reject')" class="px-2 py-1 rounded text-[11px] font-medium text-red-500 hover:bg-red-50">打回</button>
            </div>
        </div>`;
    }).join('');
}

// ============ API: 时间线 ============
async function loadTimeline() {
    try {
        const res = await fetch('/api/timeline');
        if (!res.ok) return;
        const timeline = await res.json();
        renderTimeline(timeline);
    } catch (e) { /* 静默 */ }
}

function renderTimeline(items) {
    const panel = document.getElementById('collabTimeline');
    if (!panel) return;

    if (!items || !items.length) {
        panel.innerHTML = '<div class="p-4 text-center text-sm text-gray-400">暂无动态</div>';
        return;
    }

    const typeColors = {
        task_created: 'bg-blue-400',
        task_completed: 'bg-emerald-400',
        review_approve: 'bg-emerald-400',
        review_reject: 'bg-red-400',
        topics_generated: 'bg-pink-400'
    };

    panel.innerHTML = items.slice(0, 8).map(item => {
        const agent = AGENTS[item.agent] || { name: '系统' };
        const dotColor = typeColors[item.type] || 'bg-gray-400';
        const time = item.time ? item.time.slice(11, 16) : '';
        return `
        <div class="p-4">
            <div class="flex items-center gap-2 text-xs text-gray-500 mb-1">
                <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
                <span class="font-medium text-gray-700">${agent.name}</span>
                <span>${item.message || ''}</span>
            </div>
            <div class="text-[11px] text-gray-400 mt-1 pl-3.5 ml-[3px]">${time}</div>
        </div>`;
    }).join('');
}

// ============ 审批操作（调API） ============
async function reviewTask(id, action) {
    const label = action === 'approve' ? '通过' : '打回';
    try {
        const res = await fetch(`/api/reviews/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        if (res.ok) {
            showToast(`已${label}`, action === 'approve' ? 'success' : 'warning');
            loadAllData();
        } else {
            showToast(`${label}失败`, 'error');
        }
    } catch (e) {
        showToast('网络错误', 'error');
    }
}

// ============ 导航切换 ============
function switchTab(btn, tab) {
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
        el.classList.add('text-gray-500');
    });
    btn.classList.add('active');
    btn.classList.remove('text-gray-500');
}

// ============ 员工筛选 ============
function filterByAgent(agent) {
    currentAgentFilter = agent;
    renderFilteredTasks();
}

// ============ 任务筛选 ============
function filterTasks(btn, status) {
    currentFilter = status;
    document.querySelectorAll('.task-filter').forEach(el => {
        el.classList.remove('active', 'bg-white', 'text-slate-700', 'shadow-sm');
        el.classList.add('text-gray-500');
    });
    btn.classList.add('active', 'bg-white', 'text-slate-700', 'shadow-sm');
    btn.classList.remove('text-gray-500');
    renderFilteredTasks();
}

// ============ 选题相关 ============
function selectTopic(el, index) {
    document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    selectedTopic = index;
}

async function confirmTopicSelection() {
    if (selectedTopic === null) {
        showToast('请先选择一个选题', 'warning');
        return;
    }
    showToast('正在生成文案...', 'info');
    // TODO: 调用后端生成
    await loadAllData();
}

// ============ 快速派单弹窗 ============
function showQuickDispatch() {
    document.getElementById('dispatchModal').classList.remove('hidden');
}

function closeDispatchModal() {
    document.getElementById('dispatchModal').classList.add('hidden');
    document.getElementById('dispatchInput').value = '';
    selectedModalAgent = null;
    document.querySelectorAll('.modal-agent-btn').forEach(b => {
        b.classList.remove('border-brand-500', 'bg-brand-50');
        b.classList.add('border-gray-200');
    });
}

function selectModalAgent(btn, agentKey) {
    selectedModalAgent = agentKey;
    document.querySelectorAll('.modal-agent-btn').forEach(b => {
        b.classList.remove('border-brand-500', 'bg-brand-50');
        b.classList.add('border-gray-200');
    });
    btn.classList.add('border-brand-500', 'bg-brand-50');
    btn.classList.remove('border-gray-200');
}

async function submitDispatch() {
    const input = document.getElementById('dispatchInput').value.trim();
    if (!selectedModalAgent) { showToast('请先选择一个员工', 'warning'); return; }
    if (!input) { showToast('请输入任务描述', 'warning'); return; }

    try {
        const res = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent: selectedModalAgent, type: '快速派单', input })
        });
        if (res.ok) {
            showToast(`任务已派发给 ${AGENTS[selectedModalAgent].name}`, 'success');
            closeDispatchModal();
            loadAllData();
        } else {
            showToast('派发失败', 'error');
        }
    } catch (e) {
        showToast('网络错误', 'error');
    }
}

// ============ AI助手快捷操作 ============
function quickAction(agent) {
    const inputEl = document.getElementById('quickTaskInput');
    inputEl.placeholder = agent === 'all' ? '输入任务（自动分配最优员工）...' : `给${AGENTS[agent].name}派任务...`;
    inputEl.dataset.agent = agent;
    inputEl.focus();
}

async function quickDispatch() {
    const inputEl = document.getElementById('quickTaskInput');
    const input = inputEl.value.trim();
    const agent = inputEl.dataset.agent || 'copywriter';
    if (!input) return;

    try {
        const res = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent, type: '快捷任务', input })
        });
        if (res.ok) {
            showToast('任务已派发', 'success');
            inputEl.value = '';
            loadAllData();
        }
    } catch (e) {
        showToast('派发失败', 'error');
    }
}

// ============ 员工详情 ============
function showAgentDetail(agentKey) {
    const agent = AGENTS[agentKey];
    if (!agent) return;
    // TODO: 弹出详情面板
    showToast(`${agent.name} — ${agent.desc}`, 'info');
}

// ============ 时间相关 ============
function updateWorkstationTime() {
    const now = new Date();
    const days = ['周日','周一','周二','周三','周四','周五','周六'];
    const dateStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${days[now.getDay()]}`;
    document.getElementById('workstationTime').textContent = dateStr;
}

function updateUptime() {
    const elapsed = Date.now() - startTime;
    const h = Math.floor(elapsed / 3600000);
    const m = Math.floor((elapsed % 3600000) / 60000);
    document.getElementById('uptime').textContent = `${h}h ${m}m`;
}

function updateLastRefresh() {
    const now = new Date();
    document.getElementById('lastRefresh').textContent =
        `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
}

function refreshAll() {
    showToast('正在刷新...', 'info');
    loadAllData();
}

// ============ Chart.js 图表 ============

// 通用Chart.js配色
const CHART_COLORS = {
    blue:   '#3B82F6', pink:   '#EC4899', cyan:   '#06B6D4',
    indigo: '#6366F1', amber:  '#F59E0B', emerald: '#10B981',
    red:    '#EF4444', gray:   '#9CA3AF', brand:  '#6366F1'
};

// 任务状态分布饼图
function renderStatusPieChart(stats) {
    const ctx = document.getElementById('statusPieChart');
    if (!ctx) return;

    const data = {
        labels: ['已通过', '待审批', '已打回'],
        datasets: [{
            data: [stats.approved || 0, stats.pending_review || 0, stats.rejected || 0],
            backgroundColor: [
                CHART_COLORS.emerald,
                CHART_COLORS.brand,
                CHART_COLORS.red
            ],
            borderWidth: 0,
            hoverOffset: 6
        }]
    };

    if (statusPieChart) {
        statusPieChart.data = data;
        statusPieChart.update('none');
        return;
    }

    statusPieChart = new Chart(ctx, {
        type: 'doughnut',
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 12, usePointStyle: true, pointStyleWidth: 8, font: { size: 11 } }
                }
            },
            animation: { animateRotate: true, duration: 800 }
        }
    });
}

// 各员工产出柱状图
function renderAgentBarChart(agentStats) {
    const ctx = document.getElementById('agentBarChart');
    if (!ctx) return;

    const keys = Object.keys(AGENTS);
    const labels = keys.map(k => AGENTS[k].name);
    const done = keys.map(k => (agentStats[k] || {}).done || 0);
    const pending = keys.map(k => (agentStats[k] || {}).pending || 0);

    const data = {
        labels,
        datasets: [
            {
                label: '已完成',
                data: done,
                backgroundColor: CHART_COLORS.emerald,
                borderRadius: 4,
                barPercentage: 0.6
            },
            {
                label: '待审批',
                data: pending,
                backgroundColor: CHART_COLORS.brand,
                borderRadius: 4,
                barPercentage: 0.6
            }
        ]
    };

    if (agentBarChart) {
        agentBarChart.data = data;
        agentBarChart.update('none');
        return;
    }

    agentBarChart = new Chart(ctx, {
        type: 'bar',
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true, grid: { display: false }, ticks: { font: { size: 10 } } },
                y: { stacked: true, beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } }, grid: { color: '#F1F5F9' } }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 12, usePointStyle: true, pointStyleWidth: 8, font: { size: 11 } }
                }
            },
            animation: { duration: 600 }
        }
    });
}

// 各员工完成率（水平柱状图）
function renderCompletionChart(agentStats) {
    const ctx = document.getElementById('completionChart');
    if (!ctx) return;

    const keys = Object.keys(AGENTS);
    const labels = keys.map(k => AGENTS[k].name);
    const rates = keys.map(k => {
        const s = agentStats[k] || {};
        return s.total > 0 ? Math.round(s.done / s.total * 100) : 0;
    });

    const bgColors = keys.map(k => {
        const rate = agentStats[k] ? (agentStats[k].total > 0 ? agentStats[k].done / agentStats[k].total * 100 : 0) : 0;
        return rate >= 80 ? CHART_COLORS.emerald : rate >= 50 ? CHART_COLORS.amber : CHART_COLORS.red;
    });

    const data = {
        labels,
        datasets: [{
            label: '完成率 %',
            data: rates,
            backgroundColor: bgColors,
            borderRadius: 4,
            barPercentage: 0.55
        }]
    };

    if (completionChart) {
        completionChart.data = data;
        completionChart.update('none');
        return;
    }

    completionChart = new Chart(ctx, {
        type: 'bar',
        data,
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%', font: { size: 10 } }, grid: { color: '#F1F5F9' } },
                y: { grid: { display: false }, ticks: { font: { size: 10 } } }
            },
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => ctx.raw + '%' } }
            },
            animation: { duration: 600 }
        }
    });
}

// ============ Toast通知系统 ============
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const colors = {
        success: 'bg-emerald-500', warning: 'bg-amber-500',
        error:   'bg-red-500',    info:    'bg-brand-500'
    };
    const icons = {
        success: '&#10003;', warning: '&#9888;', error: '&#10007;', info: '&#8505;'
    };
    const toast = document.createElement('div');
    toast.className = `toast-enter flex items-center gap-2 px-4 py-3 rounded-xl ${colors[type]} text-white text-sm font-medium shadow-lg`;
    toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.transition = 'all 0.3s';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}
