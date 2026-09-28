/**
 * ==========================================================================
 * SAFEGATE HSE PORTAL - JAVASCRIPT CONTROLLER
 * Quản lý Cổng An Toàn & Trang Bị Bảo Hộ Lao Động (PPE)
 * Chạy 100% Client-Side trên GitHub Pages + Hỗ trợ kết nối SafeGate Gateway
 * ==========================================================================
 */

// --------------------------------------------------------------------------
// 1. DỮ LIỆU KHỞI TẠO MẪU (DEFAULT SAMPLE DATA)
// --------------------------------------------------------------------------
const DEFAULT_WORKERS = [
  { code: 'NV-1001', name: 'Nguyễn Văn An', dept: 'Thi công kết cấu', role: 'Thợ sắt' },
  { code: 'NV-1002', name: 'Trần Đình Bình', dept: 'Cơ điện MEP', role: 'Thợ điện' },
  { code: 'NV-1003', name: 'Lê Hoàng Cường', dept: 'Hoàn thiện xây dựng', role: 'Thợ sơn' },
  { code: 'NV-1004', name: 'Phạm Minh Đức', dept: 'Ban an toàn HSE', role: 'Cán bộ an toàn' },
  { code: 'NV-1005', name: 'Vũ Quốc Hùng', dept: 'Thi công kết cấu', role: 'Vận hành cẩu tháp' },
  { code: 'NV-1006', name: 'Hoàng Thị Mai', dept: 'Ban chỉ huy công trường', role: 'Kỹ sư giám sát' },
  { code: 'NV-1007', name: 'Đỗ Anh Tuấn', dept: 'Cơ điện MEP', role: 'Kỹ sư cơ điện' },
  { code: 'NV-1008', name: 'Bùi Văn Hạnh', dept: 'Thi công kết cấu', role: 'Thợ giàn giáo' }
];

const DEFAULT_LOGS = [
  { id: 1, timestamp: '2026-09-28 07:05:12', worker_code: 'NV-1001', worker_name: 'Nguyễn Văn An', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ bảo hộ & Áo phản quang', vote_ratio: '10/10' },
  { id: 2, timestamp: '2026-09-28 07:11:45', worker_code: 'NV-1002', worker_name: 'Trần Đình Bình', dept: 'Cơ điện MEP', status: 'PASS', reason: 'Đủ trang bị: Mũ bảo hộ & Áo phản quang', vote_ratio: '10/10' },
  { id: 3, timestamp: '2026-09-28 07:16:30', worker_code: 'NV-1003', worker_name: 'Lê Hoàng Cường', dept: 'Hoàn thiện xây dựng', status: 'FAIL', reason: 'Cầm mũ bảo hộ trên tay (Holding Helmet)', vote_ratio: '3/10' },
  { id: 4, timestamp: '2026-09-28 07:22:18', worker_code: 'NV-1004', worker_name: 'Phạm Minh Đức', dept: 'Ban an toàn HSE', status: 'PASS', reason: 'Đủ trang bị chuẩn HSE', vote_ratio: '10/10' },
  { id: 5, timestamp: '2026-09-28 07:29:50', worker_code: 'NV-1005', worker_name: 'Vũ Quốc Hùng', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ bảo hộ & Áo phản quang', vote_ratio: '9/10' },
  { id: 6, timestamp: '2026-09-28 07:35:05', worker_code: 'NV-1006', worker_name: 'Hoàng Thị Mai', dept: 'Ban chỉ huy công trường', status: 'PASS', reason: 'Đủ trang bị: Mũ trắng giám sát & Áo phản quang', vote_ratio: '10/10' },
  { id: 7, timestamp: '2026-09-28 07:42:22', worker_code: 'NV-1007', worker_name: 'Đỗ Anh Tuấn', dept: 'Cơ điện MEP', status: 'PASS', reason: 'Đủ trang bị: Mũ bảo hộ & Áo phản quang', vote_ratio: '10/10' },
  { id: 8, timestamp: '2026-09-28 07:49:10', worker_code: 'NV-1008', worker_name: 'Bùi Văn Hạnh', dept: 'Thi công kết cấu', status: 'FAIL', reason: 'Không đội mũ bảo hộ (Missing Helmet)', vote_ratio: '2/10' },
  { id: 9, timestamp: '2026-09-28 07:55:34', worker_code: 'NV-1003', worker_name: 'Lê Hoàng Cường', dept: 'Hoàn thiện xây dựng', status: 'PASS', reason: 'Đã bổ sung đội mũ chuẩn quy định', vote_ratio: '9/10' },
  { id: 10, timestamp: '2026-09-28 08:05:40', worker_code: 'NV-1001', worker_name: 'Nguyễn Văn An', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị bảo hộ', vote_ratio: '10/10' },
  { id: 11, timestamp: '2026-09-28 08:20:15', worker_code: 'NV-1008', worker_name: 'Bùi Văn Hạnh', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đã đội mũ đầy đủ sau khi nhắc nhở', vote_ratio: '9/10' },
  { id: 12, timestamp: '2026-09-28 08:45:00', worker_code: 'NV-1002', worker_name: 'Trần Đình Bình', dept: 'Cơ điện MEP', status: 'FAIL', reason: 'Thiếu áo phản quang bảo hộ', vote_ratio: '4/10' },
  { id: 13, timestamp: '2026-09-28 09:02:18', worker_code: 'NV-1002', worker_name: 'Trần Đình Bình', dept: 'Cơ điện MEP', status: 'PASS', reason: 'Đã mặc áo phản quang bổ sung', vote_ratio: '10/10' },
  { id: 14, timestamp: '2026-09-28 09:30:25', worker_code: 'NV-1005', worker_name: 'Vũ Quốc Hùng', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ & Áo phản quang', vote_ratio: '10/10' },
  { id: 15, timestamp: '2026-09-28 10:15:10', worker_code: 'NV-1004', worker_name: 'Phạm Minh Đức', dept: 'Ban an toàn HSE', status: 'PASS', reason: 'Đủ trang bị: Mũ & Áo phản quang', vote_ratio: '10/10' },
  { id: 16, timestamp: '2026-09-28 11:05:44', worker_code: 'NV-1007', worker_name: 'Đỗ Anh Tuấn', dept: 'Cơ điện MEP', status: 'PASS', reason: 'Đủ trang bị bảo hộ lao động', vote_ratio: '9/10' },
  { id: 17, timestamp: '2026-09-28 12:55:08', worker_code: 'NV-1001', worker_name: 'Nguyễn Văn An', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ & Áo phản quang', vote_ratio: '10/10' },
  { id: 18, timestamp: '2026-09-28 13:02:19', worker_code: 'NV-1003', worker_name: 'Lê Hoàng Cường', dept: 'Hoàn thiện xây dựng', status: 'FAIL', reason: 'Chưa cài quai mũ an toàn', vote_ratio: '5/10' },
  { id: 19, timestamp: '2026-09-28 13:08:40', worker_code: 'NV-1003', worker_name: 'Lê Hoàng Cường', dept: 'Hoàn thiện xây dựng', status: 'PASS', reason: 'Đã cài quai mũ đạt chuẩn', vote_ratio: '9/10' },
  { id: 20, timestamp: '2026-09-28 13:40:12', worker_code: 'NV-1006', worker_name: 'Hoàng Thị Mai', dept: 'Ban chỉ huy công trường', status: 'PASS', reason: 'Đủ trang bị bảo hộ', vote_ratio: '10/10' },
  { id: 21, timestamp: '2026-09-28 14:15:33', worker_code: 'NV-1008', worker_name: 'Bùi Văn Hạnh', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ & Áo phản quang', vote_ratio: '10/10' },
  { id: 22, timestamp: '2026-09-28 15:20:11', worker_code: 'NV-1005', worker_name: 'Vũ Quốc Hùng', dept: 'Thi công kết cấu', status: 'PASS', reason: 'Đủ trang bị: Mũ & Áo phản quang', vote_ratio: '10/10' }
];

// --------------------------------------------------------------------------
// 2. STATE STORAGE QUẢN LÝ (LOCALSTORAGE)
// --------------------------------------------------------------------------
let state = {
  currentTab: 'dashboard',
  workers: [],
  logs: [],
  gatewayUrl: 'http://localhost:8000',
  isGatewayConnected: false
};

function loadState() {
  try {
    const savedWorkers = localStorage.getItem('safegate_workers');
    const savedLogs = localStorage.getItem('safegate_logs');
    const savedGateway = localStorage.getItem('safegate_gateway_url');

    state.workers = savedWorkers ? JSON.parse(savedWorkers) : [...DEFAULT_WORKERS];
    state.logs = savedLogs ? JSON.parse(savedLogs) : [...DEFAULT_LOGS];
    if (savedGateway) state.gatewayUrl = savedGateway;

    // Lưu lại nếu lần đầu mở
    if (!savedWorkers) saveWorkers();
    if (!savedLogs) saveLogs();
  } catch (e) {
    console.error('Lỗi khi đọc LocalStorage:', e);
    state.workers = [...DEFAULT_WORKERS];
    state.logs = [...DEFAULT_LOGS];
  }
}

function saveWorkers() {
  localStorage.setItem('safegate_workers', JSON.stringify(state.workers));
}

function saveLogs() {
  localStorage.setItem('safegate_logs', JSON.stringify(state.logs));
}

// --------------------------------------------------------------------------
// 3. ĐIỀU HƯỚNG TAB (ROUTING)
// --------------------------------------------------------------------------
const TAB_TITLES = {
  dashboard: {
    heading: 'BẢNG ĐIỀU KHIỂN TỔNG QUAN',
    subheading: 'Giám sát mức độ tuân thủ trang bị bảo hộ lao động theo thời gian thực'
  },
  logs: {
    heading: 'NHẬT KÝ RA VÀO CỔNG AN TOÀN',
    subheading: 'Danh sách chi tiết kết quả kiểm tra QR và nhận diện PPE của công nhân'
  },
  workers: {
    heading: 'QUẢN LÝ NHÂN VIÊN & IN THẺ QR',
    subheading: 'Cấp phát thẻ định danh chuẩn, in ấn mã QR cá nhân cho từng công nhân'
  },
  analytics: {
    heading: 'PHÂN TÍCH AN TOÀN & BÁO CÁO HSE',
    subheading: 'Đánh giá các vi phạm phổ biến và mức độ chấp hành theo nhà thầu'
  },
  sync: {
    heading: 'KẾT NỐI TRẠM AI TẠI CỔNG',
    subheading: 'Đồng bộ hóa dữ liệu trực tiếp với phần mềm SafeGate AI chạy tại máy trạm'
  }
};

function switchTab(tabId) {
  if (!TAB_TITLES[tabId]) return;
  state.currentTab = tabId;

  // Cập nhật Menu Sidebar
  document.querySelectorAll('.sidebar-menu .nav-item').forEach(btn => {
    btn.classList.remove('active');
  });
  const activeNav = document.getElementById(`nav-${tabId}`);
  if (activeNav) activeNav.classList.add('active');

  // Cập nhật Tab Pane
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.remove('active');
  });
  const activePane = document.getElementById(`tab-${tabId}`);
  if (activePane) activePane.classList.add('active');

  // Cập nhật Tiêu đề trang
  document.getElementById('page-heading').textContent = TAB_TITLES[tabId].heading;
  document.getElementById('page-subheading').textContent = TAB_TITLES[tabId].subheading;

  // Đóng sidebar trên mobile nếu đang mở
  document.querySelector('.sidebar').classList.remove('open');

  // Render nội dung của tab tương ứng
  renderCurrentTab();
}

function renderCurrentTab() {
  switch (state.currentTab) {
    case 'dashboard':
      renderDashboard();
      break;
    case 'logs':
      filterLogsTable();
      break;
    case 'workers':
      filterWorkersGrid();
      break;
    case 'analytics':
      renderAnalytics();
      break;
    case 'sync':
      // Không cần render động nhiều, chỉ cập nhật input
      const input = document.getElementById('gateway-url-input');
      if (input) input.value = state.gatewayUrl;
      break;
  }
}

function refreshCurrentTab() {
  renderCurrentTab();
  showToast('Đã làm mới dữ liệu thành công!', 'info');
}

function toggleSidebar() {
  document.querySelector('.sidebar').classList.toggle('open');
}

// --------------------------------------------------------------------------
// 4. ĐỒNG HỒ THỜI GIAN THỰC (LIVE CLOCK)
// --------------------------------------------------------------------------
function startLiveClock() {
  const clockEl = document.getElementById('live-time');
  function update() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('vi-VN', { hour12: false });
    const dateStr = now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
    if (clockEl) {
      clockEl.textContent = `${timeStr} • ${dateStr}`;
    }
  }
  update();
  setInterval(update, 1000);
}

// --------------------------------------------------------------------------
// 5. TAB 1: RENDER EXECUTIVE DASHBOARD
// --------------------------------------------------------------------------
function renderDashboard() {
  const total = state.logs.length;
  const pass = state.logs.filter(l => l.status === 'PASS').length;
  const fail = state.logs.filter(l => l.status === 'FAIL').length;
  const rate = total > 0 ? ((pass / total) * 100).toFixed(1) : '100.0';

  // Cập nhật Metric KPI
  const elTotal = document.getElementById('kpi-total-checks');
  const elPass = document.getElementById('kpi-pass-count');
  const elFail = document.getElementById('kpi-fail-count');
  const elRate = document.getElementById('kpi-pass-rate');
  const elProgress = document.getElementById('kpi-progress-bar');

  if (elTotal) elTotal.textContent = total;
  if (elPass) elPass.textContent = pass;
  if (elFail) elFail.textContent = fail;
  if (elRate) elRate.textContent = `${rate}%`;
  if (elProgress) elProgress.style.width = `${rate}%`;

  // Render Biểu đồ theo giờ
  renderHourlyChart();

  // Render Danh sách sự kiện gần nhất
  renderRecentAlerts();
}

function renderHourlyChart() {
  const chartEl = document.getElementById('hourly-chart');
  if (!chartEl) return;

  // Các khung giờ trong ngày làm việc
  const hours = ['06h', '07h', '08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h'];
  
  // Tính lượt theo giờ từ log timestamp
  const hourData = {};
  hours.forEach(h => { hourData[h] = { pass: 0, fail: 0 }; });

  state.logs.forEach(log => {
    try {
      const parts = log.timestamp.split(' ');
      if (parts.length > 1) {
        const hour = parseInt(parts[1].split(':')[0], 10);
        const key = `${hour < 10 ? '0' + hour : hour}h`;
        if (hourData[key]) {
          if (log.status === 'PASS') hourData[key].pass++;
          else hourData[key].fail++;
        }
      }
    } catch (e) {}
  });

  // Tìm max value để scale chiều cao
  let maxCount = 1;
  hours.forEach(h => {
    const total = hourData[h].pass + hourData[h].fail;
    if (total > maxCount) maxCount = total;
  });

  chartEl.innerHTML = '';
  hours.forEach(h => {
    const pCount = hourData[h].pass;
    const fCount = hourData[h].fail;
    
    // Scale chiều cao từ 4px đến 140px
    const pHeight = Math.max(4, Math.round((pCount / maxCount) * 130));
    const fHeight = Math.max(4, Math.round((fCount / maxCount) * 130));

    const group = document.createElement('div');
    group.className = 'chart-bar-group';
    group.innerHTML = `
      <div class="chart-bars">
        <div class="bar pass" style="height: ${pCount > 0 ? pHeight : 4}px;" title="${h}: ${pCount} lượt Đạt (PASS)"></div>
        <div class="bar fail" style="height: ${fCount > 0 ? fHeight : 4}px;" title="${h}: ${fCount} lượt Vi phạm (FAIL)"></div>
      </div>
      <span class="bar-label">${h}</span>
    `;
    chartEl.appendChild(group);
  });
}

function renderRecentAlerts() {
  const container = document.getElementById('recent-alerts-list');
  if (!container) return;

  // Lấy 5 log gần nhất (xếp giảm dần theo thời gian)
  const recent = [...state.logs].reverse().slice(0, 5);

  if (recent.length === 0) {
    container.innerHTML = '<p class="status-sub" style="text-align: center; padding: 20px;">Chưa có dữ liệu kiểm tra</p>';
    return;
  }

  container.innerHTML = recent.map(log => {
    const isPass = log.status === 'PASS';
    const icon = isPass ? 'fa-circle-check' : 'fa-triangle-exclamation';
    const timeOnly = log.timestamp.split(' ')[1] || log.timestamp;

    return `
      <div class="alert-item ${isPass ? 'pass' : 'fail'}">
        <div class="alert-icon">
          <i class="fa-solid ${icon}"></i>
        </div>
        <div class="alert-info">
          <div class="alert-title">${escapeHtml(log.worker_name)} (${escapeHtml(log.worker_code)})</div>
          <div class="alert-sub">${escapeHtml(log.reason)}</div>
        </div>
        <div class="alert-time">${timeOnly}</div>
      </div>
    `;
  }).join('');
}

// --------------------------------------------------------------------------
// 6. TAB 2: ACCESS LOGS & CSV EXPORT
// --------------------------------------------------------------------------
function filterLogsTable() {
  const searchInput = document.getElementById('log-search-input');
  const statusSelect = document.getElementById('log-status-select');
  const deptSelect = document.getElementById('log-dept-select');
  const tbody = document.getElementById('logs-table-body');
  const countSummary = document.getElementById('log-count-summary');

  if (!tbody) return;

  const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
  const statusFilter = statusSelect ? statusSelect.value : 'ALL';
  const deptFilter = deptSelect ? deptSelect.value : 'ALL';

  // Lọc danh sách logs
  const filtered = state.logs.filter(log => {
    // Lọc theo trạng thái
    if (statusFilter !== 'ALL' && log.status !== statusFilter) return false;
    
    // Lọc theo phòng ban
    if (deptFilter !== 'ALL' && log.dept !== deptFilter) return false;

    // Lọc theo tìm kiếm từ khóa
    if (query) {
      const matchName = log.worker_name.toLowerCase().includes(query);
      const matchCode = log.worker_code.toLowerCase().includes(query);
      const matchDept = log.dept.toLowerCase().includes(query);
      const matchReason = log.reason.toLowerCase().includes(query);
      if (!matchName && !matchCode && !matchDept && !matchReason) return false;
    }

    return true;
  });

  // Hiển thị số lượng
  if (countSummary) {
    countSummary.textContent = `Hiển thị ${filtered.length} trên tổng số ${state.logs.length} lượt kiểm tra`;
  }

  // Render bảng
  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 36px; color: var(--text-muted);">
          <i class="fa-solid fa-inbox" style="font-size: 28px; margin-bottom: 8px; display: block;"></i>
          Không tìm thấy lượt kiểm tra nào phù hợp với bộ lọc
        </td>
      </tr>
    `;
    return;
  }

  // Sắp xếp mới nhất lên đầu
  const sorted = [...filtered].reverse();

  tbody.innerHTML = sorted.map(log => {
    const isPass = log.status === 'PASS';
    const badgeClass = isPass ? 'pass' : 'fail';
    const badgeIcon = isPass ? 'fa-check' : 'fa-xmark';
    const statusText = isPass ? 'ĐẠT (PASS)' : 'CHẶN (FAIL)';

    return `
      <tr>
        <td><strong>${escapeHtml(log.timestamp)}</strong></td>
        <td><span class="badge-code-tag" style="margin: 0;">${escapeHtml(log.worker_code)}</span></td>
        <td><strong>${escapeHtml(log.worker_name)}</strong></td>
        <td>${escapeHtml(log.dept)}</td>
        <td>
          <span class="status-badge ${badgeClass}">
            <i class="fa-solid ${badgeIcon}"></i> ${statusText}
          </span>
        </td>
        <td>${escapeHtml(log.reason)}</td>
        <td>
          <span style="font-weight: 700; color: ${isPass ? 'var(--accent-green)' : 'var(--accent-red)'}">
            ${escapeHtml(log.vote_ratio || 'N/A')}
          </span>
        </td>
        <td>
          <button class="btn-secondary" style="padding: 6px 12px; font-size: 11px;" onclick="openBadgeModal('${log.worker_code}')" title="Xem & In thẻ">
            <i class="fa-solid fa-qrcode"></i> Thẻ QR
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function exportLogsToCSV() {
  if (state.logs.length === 0) {
    showToast('Chưa có dữ liệu nhật ký để xuất CSV!', 'warning');
    return;
  }

  // Tạo tiêu đề cột CSV (Bổ sung BOM \uFEFF để Excel mở tiếng Việt chuẩn)
  let csvContent = '\uFEFF';
  csvContent += 'Mã Lượt,Thời Gian,Mã Nhân Viên,Họ và Tên,Đội Thi Công / Bộ Phận,Trạng Thái,Lỗi / Ghi Chú,Voting AI\r\n';

  state.logs.forEach((log, index) => {
    const row = [
      index + 1,
      `"${log.timestamp}"`,
      `"${log.worker_code}"`,
      `"${log.worker_name.replace(/"/g, '""')}"`,
      `"${log.dept.replace(/"/g, '""')}"`,
      `"${log.status}"`,
      `"${log.reason.replace(/"/g, '""')}"`,
      `"${log.vote_ratio || ''}"`
    ];
    csvContent += row.join(',') + '\r\n';
  });

  // Tạo Blob và tải file
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
  const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '');
  link.setAttribute('href', url);
  link.setAttribute('download', `safegate_access_logs_${dateStr}_${timeStr}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  showToast('Đã xuất file CSV thành công!', 'success');
}

// --------------------------------------------------------------------------
// 7. TAB 3: WORKERS & QR BADGE MODAL
// --------------------------------------------------------------------------
function filterWorkersGrid() {
  const searchInput = document.getElementById('worker-search-input');
  const grid = document.getElementById('workers-card-grid');
  if (!grid) return;

  const query = (searchInput ? searchInput.value : '').trim().toLowerCase();

  const filtered = state.workers.filter(w => {
    if (!query) return true;
    return w.name.toLowerCase().includes(query) ||
           w.code.toLowerCase().includes(query) ||
           w.dept.toLowerCase().includes(query) ||
           (w.role && w.role.toLowerCase().includes(query));
  });

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px; color: var(--text-muted);">
        <i class="fa-solid fa-users-slash" style="font-size: 32px; margin-bottom: 12px; display: block;"></i>
        Không tìm thấy nhân viên nào phù hợp với từ khóa tìm kiếm
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map(worker => {
    // Lấy 2 ký tự đầu viết hoa làm avatar
    const nameParts = worker.name.trim().split(' ');
    const initials = nameParts.length >= 2 
      ? (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase()
      : worker.name.slice(0, 2).toUpperCase();

    // Đếm số lượt check của nhân viên này
    const workerLogs = state.logs.filter(l => l.worker_code === worker.code);
    const passCount = workerLogs.filter(l => l.status === 'PASS').length;
    const lastLog = workerLogs.length > 0 ? workerLogs[workerLogs.length - 1] : null;

    return `
      <div class="worker-card">
        <div class="worker-card-header">
          <div class="worker-avatar">${initials}</div>
          <div class="worker-header-info">
            <h3>${escapeHtml(worker.name)}</h3>
            <span class="worker-code">${escapeHtml(worker.code)}</span>
          </div>
        </div>

        <div class="worker-card-body">
          <div><i class="fa-solid fa-briefcase" style="width: 18px; color: var(--accent-cyan);"></i> ${escapeHtml(worker.dept)}</div>
          <div><i class="fa-solid fa-id-badge" style="width: 18px; color: var(--text-muted);"></i> ${escapeHtml(worker.role || 'Công nhân')}</div>
          <div><i class="fa-solid fa-clock-rotate-left" style="width: 18px; color: var(--text-muted);"></i> Lượt qua cổng: <strong>${passCount}/${workerLogs.length} Đạt</strong></div>
          ${lastLog ? `<div><i class="fa-solid fa-shield" style="width: 18px; color: ${lastLog.status === 'PASS' ? 'var(--accent-green)' : 'var(--accent-red)'};"></i> Gần nhất: <strong>${lastLog.status}</strong> (${lastLog.timestamp.split(' ')[1]})</div>` : ''}
        </div>

        <div class="worker-card-actions">
          <button class="btn-primary" style="flex: 1;" onclick="openBadgeModal('${worker.code}')">
            <i class="fa-solid fa-qrcode"></i> Xem & In Thẻ
          </button>
          <button class="btn-secondary" title="Giả lập quét cổng ngay" onclick="simulateGateCheck('${worker.code}')">
            <i class="fa-solid fa-play"></i> Quét cổng
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function openBadgeModal(workerCode) {
  const worker = state.workers.find(w => w.code === workerCode);
  if (!worker) {
    showToast(`Không tìm thấy thông tin của mã ${workerCode}`, 'error');
    return;
  }

  // Điền dữ liệu vào Modal
  document.getElementById('badge-modal-name').textContent = worker.name.toUpperCase();
  document.getElementById('badge-modal-code').textContent = worker.code;
  document.getElementById('badge-modal-dept').textContent = worker.dept;
  document.getElementById('badge-modal-role').textContent = worker.role || 'Công nhân công trường';

  // Xóa QR cũ và tạo QR mới
  const qrContainer = document.getElementById('badge-qr-canvas');
  qrContainer.innerHTML = '';

  try {
    new QRCode(qrContainer, {
      text: worker.code,
      width: 170,
      height: 170,
      colorDark: '#0F172A',
      colorLight: '#FFFFFF',
      correctLevel: QRCode.CorrectLevel.H
    });
  } catch (err) {
    console.error('Lỗi khi vẽ mã QR:', err);
    qrContainer.innerHTML = `<p style="color: red; padding: 20px;">Lỗi tạo mã QR</p>`;
  }

  // Mở Dialog
  const dialog = document.getElementById('badge-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    dialog.showModal();
  }
}

function openAddWorkerModal() {
  const form = document.getElementById('add-worker-form');
  if (form) form.reset();

  // Đề xuất mã nhân viên kế tiếp
  const nextNum = 1001 + state.workers.length;
  const codeInput = document.getElementById('new-worker-code');
  if (codeInput) codeInput.value = `NV-${nextNum}`;

  const dialog = document.getElementById('add-worker-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    dialog.showModal();
  }
}

function closeModal(dialogId) {
  const dialog = document.getElementById(dialogId);
  if (dialog && typeof dialog.close === 'function') {
    dialog.close();
  }
}

function handleCreateWorker(event) {
  event.preventDefault();

  const code = document.getElementById('new-worker-code').value.trim().toUpperCase();
  const name = document.getElementById('new-worker-name').value.trim();
  const dept = document.getElementById('new-worker-dept').value;
  const role = document.getElementById('new-worker-role').value.trim() || 'Công nhân';

  if (!code || !name) {
    showToast('Vui lòng nhập đầy đủ Mã và Họ tên nhân viên!', 'warning');
    return;
  }

  // Kiểm tra trùng mã
  if (state.workers.some(w => w.code === code)) {
    showToast(`Mã nhân viên "${code}" đã tồn tại! Vui lòng chọn mã khác.`, 'error');
    return;
  }

  const newWorker = { code, name, dept, role };
  state.workers.push(newWorker);
  saveWorkers();

  closeModal('add-worker-dialog');
  filterWorkersGrid();
  showToast(`Đã thêm thành công công nhân: ${name} (${code})`, 'success');

  // Mở ngay thẻ QR cho người dùng xem và in
  setTimeout(() => {
    openBadgeModal(code);
  }, 300);
}

// Giả lập quét cổng ngay tại chỗ cho 1 công nhân
function simulateGateCheck(workerCode) {
  const worker = state.workers.find(w => w.code === workerCode);
  if (!worker) return;

  const now = new Date();
  const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

  // 85% xác suất ĐẠT, 15% xác suất VI PHẠM để dữ liệu thực tế
  const isPass = Math.random() > 0.18;
  const failReasons = [
    'Thiếu mũ bảo hộ (Missing Helmet)',
    'Thiếu áo phản quang bảo hộ',
    'Cầm mũ bảo hộ trên tay (Holding Helmet)',
    'Chưa cài quai mũ an toàn'
  ];

  const status = isPass ? 'PASS' : 'FAIL';
  const reason = isPass ? 'Đủ trang bị: Mũ bảo hộ & Áo phản quang' : failReasons[Math.floor(Math.random() * failReasons.length)];
  const vote_ratio = isPass ? `${Math.floor(Math.random() * 2) + 9}/10` : `${Math.floor(Math.random() * 4) + 2}/10`;

  const newLog = {
    id: Date.now(),
    timestamp: timeStr,
    worker_code: worker.code,
    worker_name: worker.name,
    dept: worker.dept,
    status: status,
    reason: reason,
    vote_ratio: vote_ratio
  };

  state.logs.push(newLog);
  saveLogs();

  filterWorkersGrid();
  showToast(`[GIẢ LẬP] ${worker.name}: ${status === 'PASS' ? '✅ ĐẠT CHUẨN' : '❌ VI PHẠM BỊ CHẶN'}`, status === 'PASS' ? 'success' : 'warning');
}

// --------------------------------------------------------------------------
// 8. TAB 4: SAFETY ANALYTICS & CONTRACTOR RANKINGS
// --------------------------------------------------------------------------
function renderAnalytics() {
  renderViolationsBreakdown();
  renderContractorRanking();
}

function renderViolationsBreakdown() {
  const container = document.getElementById('violations-list');
  if (!container) return;

  // Thống kê các lỗi trong logs FAIL
  const failLogs = state.logs.filter(l => l.status === 'FAIL');
  const counts = {
    'Thiếu mũ bảo hộ (Missing Helmet)': 0,
    'Thiếu áo phản quang': 0,
    'Cầm mũ trên tay (Holding Helmet)': 0,
    'Chưa cài quai mũ an toàn': 0
  };

  failLogs.forEach(log => {
    const r = log.reason.toLowerCase();
    if (r.includes('cầm mũ') || r.includes('holding')) {
      counts['Cầm mũ trên tay (Holding Helmet)']++;
    } else if (r.includes('không đội mũ') || r.includes('missing helmet') || r.includes('thiếu mũ')) {
      counts['Thiếu mũ bảo hộ (Missing Helmet)']++;
    } else if (r.includes('áo')) {
      counts['Thiếu áo phản quang']++;
    } else {
      counts['Chưa cài quai mũ an toàn']++;
    }
  });

  const totalFails = Math.max(failLogs.length, 1);

  container.innerHTML = Object.entries(counts).map(([title, count]) => {
    const percent = ((count / totalFails) * 100).toFixed(0);
    return `
      <div style="margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 6px;">
          <span>${title}</span>
          <span style="color: var(--accent-red); font-weight: 700;">${count} vụ (${percent}%)</span>
        </div>
        <div class="progress-bar-bg" style="height: 8px;">
          <div class="progress-bar-fill" style="width: ${percent}%; background: var(--accent-red);"></div>
        </div>
      </div>
    `;
  }).join('');
}

function renderContractorRanking() {
  const tbody = document.getElementById('ranking-table-body');
  if (!tbody) return;

  // Gom nhóm theo Đội thi công
  const deptStats = {};

  state.logs.forEach(log => {
    const d = log.dept || 'Khác';
    if (!deptStats[d]) {
      deptStats[d] = { total: 0, pass: 0 };
    }
    deptStats[d].total++;
    if (log.status === 'PASS') deptStats[d].pass++;
  });

  const rankingList = Object.entries(deptStats).map(([dept, stats]) => {
    const rate = stats.total > 0 ? (stats.pass / stats.total) * 100 : 100;
    return { dept, total: stats.total, pass: stats.pass, rate };
  });

  // Sắp xếp theo tỷ lệ Đạt giảm dần
  rankingList.sort((a, b) => b.rate - a.rate);

  tbody.innerHTML = rankingList.map((item, index) => {
    let rankBadge = `${index + 1}`;
    if (index === 0) rankBadge = '🥇';
    else if (index === 1) rankBadge = '🥈';
    else if (index === 2) rankBadge = '🥉';

    let ratingText = '⭐ Xuất sắc';
    let ratingColor = 'var(--accent-green)';
    if (item.rate < 85) {
      ratingText = '⚠️ Cần chấn chỉnh';
      ratingColor = 'var(--accent-red)';
    } else if (item.rate < 95) {
      ratingText = '✔️ Đạt yêu cầu';
      ratingColor = 'var(--accent-cyan)';
    }

    return `
      <tr>
        <td style="font-weight: 800; font-size: 16px;">${rankBadge}</td>
        <td><strong>${escapeHtml(item.dept)}</strong></td>
        <td>${item.total} lượt</td>
        <td>
          <span style="font-weight: 800; color: ${ratingColor};">${item.rate.toFixed(1)}%</span>
        </td>
        <td><span style="font-weight: 700; color: ${ratingColor};">${ratingText}</span></td>
      </tr>
    `;
  }).join('');
}

// --------------------------------------------------------------------------
// 9. TAB 5: GATEWAY CONNECTION & SYNC
// --------------------------------------------------------------------------
async function testGatewayConnection() {
  const input = document.getElementById('gateway-url-input');
  const resultBox = document.getElementById('connection-result-box');
  const resultText = document.getElementById('connection-result-text');
  const statusText = document.getElementById('gateway-status-text');
  const urlDisplay = document.getElementById('gateway-url-display');

  if (!input) return;

  let url = input.value.trim();
  if (!url) url = 'http://localhost:8000';
  url = url.replace(/\/+$/, ''); // Bỏ dấu / cuối cùng nếu có

  state.gatewayUrl = url;
  localStorage.setItem('safegate_gateway_url', url);

  if (resultText) {
    resultText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang kết nối đến SafeGate API trạm máy tính...';
  }

  try {
    const startTime = performance.now();
    const res = await fetch(`${url}/api/stats`, {
      method: 'GET',
      mode: 'cors',
      headers: { 'Accept': 'application/json' }
    });

    const latency = Math.round(performance.now() - startTime);

    if (res.ok) {
      const stats = await res.json();
      state.isGatewayConnected = true;

      if (statusText) statusText.textContent = 'Trực tiếp: Trạm AI Online';
      if (urlDisplay) urlDisplay.textContent = `Kết nối: ${url} (${latency}ms)`;

      if (resultText) {
        resultText.innerHTML = `
          <strong style="color: var(--accent-green);"><i class="fa-solid fa-circle-check"></i> Kết nối thành công tới trạm SafeGate Gateway (${latency}ms)!</strong><br>
          Trạng thái trạm: <strong>${stats.status || 'OK'}</strong> • Tổng số lượt lưu trữ tại trạm: <strong>${stats.total_checks || 0}</strong>.
          Dữ liệu trực tiếp từ trạm AI sẽ liên tục được liên kết đồng bộ.
        `;
      }
      showToast('Kết nối thành công đến trạm SafeGate!', 'success');
      
      // Thử đồng bộ logs nếu server hỗ trợ
      syncLogsFromGateway(url);
    } else {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
  } catch (err) {
    state.isGatewayConnected = false;
    if (statusText) statusText.textContent = 'GitHub Cloud Mode';
    if (urlDisplay) urlDisplay.textContent = 'Trực tuyến trên GitHub Pages';

    if (resultText) {
      resultText.innerHTML = `
        <strong style="color: var(--accent-amber);"><i class="fa-solid fa-cloud"></i> Chế độ Độc lập (GitHub Cloud Local Storage)</strong><br>
        Không thể kết nối đến máy chủ tại <code>${escapeHtml(url)}</code> (${err.message}).<br>
        <em>Gợi ý: Nếu bạn mở trang web này từ domain GitHub Pages (HTTPS), trình duyệt có thể ngăn chặn kết nối Mixed-Content tới <code>http://localhost:8000</code>. Tuy nhiên, mọi tính năng quản lý, in ấn mã QR, lưu trữ công nhân và xuất CSV vẫn hoạt động 100% độc lập!</em>
      `;
    }
    showToast('Đang ở chế độ GitHub Cloud độc lập.', 'info');
  }
}

async function syncLogsFromGateway(url) {
  try {
    const res = await fetch(`${url}/api/logs?limit=50`, { method: 'GET', mode: 'cors' });
    if (res.ok) {
      const serverLogs = await res.json();
      if (Array.isArray(serverLogs) && serverLogs.length > 0) {
        // Gộp logs mới
        state.logs = serverLogs;
        saveLogs();
        renderDashboard();
        showToast(`Đã đồng bộ ${serverLogs.length} bản ghi nhật ký từ trạm AI!`, 'success');
      }
    }
  } catch (e) {
    console.log('Không thể lấy logs tự động từ gateway:', e);
  }
}

function resetToDefaultData() {
  if (confirm('Bạn có chắc chắn muốn khôi phục lại danh sách nhân viên và nhật ký mẫu ban đầu không?')) {
    state.workers = [...DEFAULT_WORKERS];
    state.logs = [...DEFAULT_LOGS];
    saveWorkers();
    saveLogs();
    renderCurrentTab();
    showToast('Đã khôi phục dữ liệu mẫu thành công!', 'success');
  }
}

// --------------------------------------------------------------------------
// 10. TOAST NOTIFICATION & TIỆN ÍCH
// --------------------------------------------------------------------------
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const colors = {
    success: 'var(--accent-green)',
    warning: 'var(--accent-amber)',
    error: 'var(--accent-red)',
    info: 'var(--accent-cyan)'
  };
  const icons = {
    success: 'fa-circle-check',
    warning: 'fa-triangle-exclamation',
    error: 'fa-circle-xmark',
    info: 'fa-circle-info'
  };

  toast.style.cssText = `
    background: var(--bg-surface-elevated);
    color: var(--text-primary);
    border: 1px solid ${colors[type] || colors.info};
    border-left: 4px solid ${colors[type] || colors.info};
    padding: 12px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    gap: 10px;
    pointer-events: auto;
    animation: toastIn 0.3s ease;
    max-width: 380px;
  `;

  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 16px;"></i>
    <span>${escapeHtml(message)}</span>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// --------------------------------------------------------------------------
// 11. KHỞI TẠO ỨNG DỤNG (INITIALIZATION)
// --------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  loadState();
  startLiveClock();
  switchTab('dashboard');

  // Lắng nghe phím ESC để đóng modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal('badge-dialog');
      closeModal('add-worker-dialog');
    }
  });

  // Tự động kiểm tra kết nối nếu đang mở ở localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    testGatewayConnection();
  }
});
