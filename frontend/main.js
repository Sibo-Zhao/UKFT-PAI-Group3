// Student Wellbeing System JavaScript

// Global variables
let currentUser = null;
let students = [];
let studentView = 'all';
let courses = [];
let currentPage = 'login';
let attendanceRecords = [];

// Cached survey records for visual explorer
let surveyRecords = [];

// Config for the visual explorer parameters (similar idea to app.py)
const VIZ_PARAM_CONFIG = {
  week: {
    label: 'Week',
    // backend field: week_number from surveys / analytics
    value: r => r.week_number
  },
  stress_level: {
    label: 'Stress level (1–5)',
    value: r => r.stress_level
  },
  sleep_hours: {
    label: 'Sleep hours',
    value: r => r.sleep_hours
  },
  social_connection_score: {
    label: 'Social connection (1–5)',
    value: r => r.social_connection_score
  },
  grade_achieved: {
    label: 'Grade %',
    value: r => r.grade_achieved
  },
  attendance_percent: {
    label: 'Attendance %',
    value: r => r.attendance_percent
  },
  submissions_on_time: {
    label: 'Submissions on time',
    value: r => r.submissions_on_time
  },
  submissions_late: {
    label: 'Submissions late',
    value: r => r.submissions_late
  }
};

const PLOT_RULES = {
  "week|stress_level": "line",
  "week|attendance_percent": "line",
  "week|grade_achieved": "line",
  "sleep_hours|stress_level": "scatter",
  "attendance_percent|grade_achieved": "bubble",
  "stress_level|grade_achieved": "box",
  "week|submissions_on_time": "bar",
  "week|submissions_late": "area",
  "attendance_percent|sleep_hours": "density",
  "stress_level|sleep_hours": "violin"
};

function inferPlotType(xKey, yKey) {
  const key = `${xKey}|${yKey}`;
  const reverseKey = `${yKey}|${xKey}`;
  return PLOT_RULES[key] || PLOT_RULES[reverseKey] || "scatter";
}

// Backend API base URL
const API_BASE_URL = 'http://localhost:5001'; // change if your Flask port is different

const USER_STORAGE_KEY = 'currentUser';
const ROLE_DEFAULT_PAGE = {
  wellbeing: 'wellbeing-dashboard',
  course: 'course-dashboard'
};
const ROLE_ALLOWED_PAGES = {
  wellbeing: new Set(['wellbeing.html', 'students.html', 'student_profile.html', 'index.html']),
  course: new Set(['course.html', 'attendance.html', 'students_simple.html', 'index.html'])
};

function loadStoredUser() {
  try {
    const raw = sessionStorage.getItem(USER_STORAGE_KEY) || localStorage.getItem(USER_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    // migrate away from localStorage so closing the tab logs the user out
    sessionStorage.setItem(USER_STORAGE_KEY, raw);
    localStorage.removeItem(USER_STORAGE_KEY);
    return parsed;
  } catch (e) {
    return null;
  }
}

function saveCurrentUser(user) {
  sessionStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  localStorage.removeItem(USER_STORAGE_KEY);
}

function clearStoredUser() {
  sessionStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
}

// Guard against navigating back to protected pages after logout (including bfcache restores)
window.addEventListener('pageshow', () => {
  const pageName = getCurrentPageName();
  const isLoginPage = pageName === 'index.html';
  const storedUser = loadStoredUser();
  if (!isLoginPage && !storedUser) {
    window.location.replace('index.html');
    return;
  }

  enforceRoleAccess(storedUser, pageName);
});

async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    console.error('API GET failed:', path, res.status);
    throw new Error(`API error ${res.status}`);
  }
  return res.json();
}

// Title configuration (can be overridden via localStorage)
// Reason: centralize sidebar title management and prevent Settings page from showing "settings"
const TITLE_CONFIG_KEY = 'titleConfig';
const defaultTitleConfig = {
  sidebarTitle: 'Wellbeing System',
  pageSidebarTitles: {
    'settings.html': 'Wellbeing System'
  }
};

// Mock data for demonstration
const mockStudents = [
  { id: 1, name: 'Alice Johnson', stress_level: 8, sleep_hours: 4.5, grades: [85, 92, 78], starred: true },
  { id: 2, name: 'Bob Smith', stress_level: 3, sleep_hours: 8.2, grades: [76, 88, 91], starred: false },
  { id: 3, name: 'Carol Davis', stress_level: 6, sleep_hours: 6.8, grades: [92, 87, 85], starred: true },
  { id: 4, name: 'David Wilson', stress_level: 9, sleep_hours: 3.2, grades: [68, 71, 74], starred: false },
  { id: 5, name: 'Emma Brown', stress_level: 2, sleep_hours: 9.1, grades: [94, 96, 89], starred: true }
];

const mockCourses = [
  { id: 1, name: 'Mathematics 101', code: 'MATH101', instructor: 'Dr. Johnson', enrollment: 45, average_grade: 82.5, attendance_rate: 88 },
  { id: 2, name: 'Physics 101', code: 'PHYS101', instructor: 'Dr. Smith', enrollment: 38, average_grade: 79.2, attendance_rate: 92 },
  { id: 3, name: 'Chemistry 101', code: 'CHEM101', instructor: 'Dr. Davis', enrollment: 42, average_grade: 85.1, attendance_rate: 89 }
];

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
  initializeApp();
});

function initializeApp() {
  currentUser = loadStoredUser();

  const pageName = getCurrentPageName();
  const isLoginPage = pageName === 'index.html';

  if (!isLoginPage && !currentUser) {
    window.location.href = 'index.html';
    return;
  }

  if (isLoginPage && currentUser) {
    // If you want to keep auto-redirect, re-enable this block.
    // For now, stay on login even if a session exists.
  }

  enforceRoleAccess(currentUser, pageName);

  setupEventListeners();
  applyTitleConfig();
  loadStudents();
  loadCoursesIntoDropdown();
  loadCourses();

  if (pageName === 'wellbeing.html') {
    loadWellbeingDashboard();
    setupVisualExplorer();
  } else if (pageName === 'student_profile.html') {
    loadStudentProfilePage();
  } else if (pageName === 'course.html') {
    loadCourseDashboard();
  } else if (pageName === 'attendance.html') {
    initAttendancePage();
  }
}

function getCurrentPageName() {
  const path = window.location.pathname;
  const name = path.substring(path.lastIndexOf('/') + 1) || 'index.html';
  return name;
}

function enforceRoleAccess(user, pageName) {
  if (!user) return;
  if (pageName === 'index.html') return;

  const allowedSet = ROLE_ALLOWED_PAGES[user.role];
  if (allowedSet && !allowedSet.has(pageName)) {
    const fallback = ROLE_DEFAULT_PAGE[user.role] || 'login';
    showPage(fallback, true);
  }
}

function getTitleConfig() {
  try {
    const raw = localStorage.getItem(TITLE_CONFIG_KEY);
    return raw ? JSON.parse(raw) : defaultTitleConfig;
  } catch (e) {
    return defaultTitleConfig;
  }
}

function applyTitleConfig() {
  const cfg = getTitleConfig();
  const pageName = getCurrentPageName();
  const override = (cfg.pageSidebarTitles && cfg.pageSidebarTitles[pageName]) || null;
  const el = document.querySelector('.sidebar-title');
  if (el) {
    if (override) {
      el.textContent = override;
    }
  }
}

function setupEventListeners() {
  // Login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }

  // Survey upload form
  const surveyUploadForm = document.getElementById('survey-upload-form');
  if (surveyUploadForm) {
    surveyUploadForm.addEventListener('submit', handleSurveyUpload);
  }

  // Course upload form
  const courseUploadForm = document.getElementById('course-upload-form');
  if (courseUploadForm) {
    courseUploadForm.addEventListener('submit', handleCourseUpload);
  }

  // Search and filter functionality
  const studentSearch = document.getElementById('student-search');
  if (studentSearch) {
    studentSearch.addEventListener('input', filterStudents);
  }

  const stressFilter = document.getElementById('stress-filter');
  if (stressFilter) {
    stressFilter.addEventListener('change', filterStudents);
  }

  const sleepFilter = document.getElementById('sleep-filter');
  if (sleepFilter) {
    sleepFilter.addEventListener('change', filterStudents);
  }

  const addStudentForm = document.getElementById("addStudentForm");
  if (addStudentForm) {
    addStudentForm.addEventListener("submit", handleAddStudent);
  }

  const updateForm = document.getElementById('updateStudentForm');
  if (updateForm) {
    updateForm.addEventListener('submit', handleUpdateStudentSubmit);
  }

  const allTab = document.getElementById('tab-all-students');
  const favTab = document.getElementById('tab-favourite-students');
  if (allTab && favTab) {
    allTab.addEventListener('click', () => setStudentView('all'));
    favTab.addEventListener('click', () => setStudentView('favourites'));
  }


}

// Authentication functions
async function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    console.log(data);

    if (!res.ok) {
      alert(data.error || 'Login failed');
      return;
    }

    // Backend roles: "CD" (course director) and "SWO" (student wellbeing officer)
    let role = 'course';
    if (data.role === 'SWO') role = 'wellbeing';

    currentUser = { username: data.username, role };
    saveCurrentUser(currentUser);

    if (role === 'wellbeing') {
      showPage('wellbeing-dashboard', true);
    } else {
      showPage('course-dashboard', true);
    }
  } catch (err) {
    console.error(err);
    alert('Unable to reach the server for login.');
  }
}

function logout() {
  currentUser = null;
  clearStoredUser();
  // Replace history entry so the previous protected page isn't reachable via back navigation
  showPage('login', true);
}

// Page navigation
function showPage(pageId, replace = false) {
  const map = {
    'login': 'index.html',
    'wellbeing-dashboard': 'wellbeing.html',
    'students': 'students.html',
    'course-dashboard': 'course.html',
    'attendance': 'attendance.html',
    'settings': 'settings.html'
  };
  const target = map[pageId] || 'index.html';
  if (replace) {
    window.location.replace(target);
  } else {
    window.location.href = target;
  }
}

// Dashboard functions
function loadWellbeingDashboard() {
  loadEarlyWarningStudents();
  loadWeeklyReport();
  generateDefaultPlot();
}

async function setupVisualExplorer() {
  const updateBtn = document.getElementById('viz-update-btn');
  const container = document.getElementById('plot-container');

  // Not on this page
  if (!updateBtn || !container) return;

  try {
    // Ensure we have survey data cached for plotting
    if (!surveyRecords.length) {
      surveyRecords = await apiGet('/api/surveys');
    }

    // Wire up the button
    updateBtn.addEventListener('click', generatePlot);

    // Draw an initial plot
    generatePlot();
  } catch (err) {
    console.error('FAILED TO SETUP VISUAL EXPLORER', err);
    container.innerHTML = '<p class="text-muted">UNABLE TO LOAD DATA FOR VISUALISATION.</p>';
  }
}

function loadCourseDashboard() {
  loadCourseWeeklyReport();
  generateDefaultCoursePlot();
}

function loadStudentsTable() {
  renderStudentsTable();
}

// Early Warning Students
// HIGH-RISK STUDENTS – use real backend data
async function loadEarlyWarningStudents() {
  const tbody = document.getElementById('early-warning-tbody');
  if (!tbody) return;

  try {
    // 1) Get current high-risk students from backend
    //    This should return stress_level (1–5) and sleep_hours for each student
    const data = await apiGet('/wellbeing/early-warning');

    // 2) Merge high-stress + low-sleep groups and de-duplicate
    const combined = [
      ...(data.high_stress_students?.students || []),
      ...(data.low_sleep_students?.students || [])
    ];

    const dedup = new Map(); // key: student_id
    for (const s of combined) {
      dedup.set(s.student_id, s);
    }
    const highRiskStudents = Array.from(dedup.values());

    // 3) Build table rows using REAL stress_level and sleep_hours
    tbody.innerHTML = highRiskStudents.map(student => {
      const stress = student.stress_level;   // 1–5 from backend
      const sleep = student.sleep_hours;    // hours from backend

      // Map 1–5 stress scale to 1–10 for your existing risk helpers
      const mappedStress = stress != null ? stress * 2 : 0;
      const safeSleep = sleep != null ? sleep : 8;

      return `
        <tr>
          <td>${student.name || `${student.first_name || ''} ${student.last_name || ''}`.trim()}</td>
          <td>${stress != null ? stress.toFixed(1) : '–'}</td>
          <td>${sleep != null ? sleep.toFixed(1) + 'h' : '–'}</td>
          <td>
            <span class="status-${getStatusLevel(mappedStress, safeSleep)}">
              ${getStatusText(mappedStress, safeSleep)}
            </span>
          </td>
        </tr>
      `;
    }).join('');

    // 4) If no high-risk students, show a friendly message
    if (!highRiskStudents.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="text-muted text-center">
            No high-risk students detected from latest surveys.
          </td>
        </tr>
      `;
    }

  } catch (err) {
    console.error('Failed to load high-risk students', err);
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="text-muted text-center">
          Unable to load high-risk students.
        </td>
      </tr>
    `;
  }
}

function getStressLevelClass(level) {
  if (level <= 3) return 'bg-success';
  if (level <= 6) return 'bg-warning';
  return 'bg-danger';
}

function getStatusLevel(stress, sleep) {
  if (stress >= 8 || sleep <= 4) return 'high';
  if (stress >= 6 || sleep <= 6) return 'medium';
  return 'low';
}

function getStatusText(stress, sleep) {
  if (stress >= 8 || sleep <= 4) return 'At High Risk';
  if (stress >= 6 || sleep <= 6) return 'At Medium Risk';
  return 'At Low Risk';
}

// Weekly Report
async function loadWeeklyReport() {
  const totalStudentsEl = document.getElementById('summary-total-students');
  const avgStressEl = document.getElementById('summary-avg-stress');
  const avgSleepEl = document.getElementById('summary-avg-sleep');
  const totalSubjectsEl = document.getElementById('summary-total-subjects');

  // If we're not on the wellbeing page, bail out
  if (!totalStudentsEl || !avgStressEl || !avgSleepEl || !totalSubjectsEl) return;

  try {
    // Load everything we need in parallel:
    const [studentsData, weeklyData, coursesData] = await Promise.all([
      apiGet('/students'),          // for total students
      apiGet('/wellbeing/weekly'),  // for avg stress & sleep
      apiGet('/courses')            // use courses as "subjects"
    ]);

    const totalStudents = Array.isArray(studentsData) ? studentsData.length : 0;
    const totalSubjects = Array.isArray(coursesData) ? coursesData.length : 0;

    const stress = weeklyData?.stress_level || {};
    const sleep = weeklyData?.sleep_hours || {};

    const avgStress = stress.current_week_average ?? null;
    const avgSleep = sleep.current_week_average ?? null;

    totalStudentsEl.textContent = totalStudents;
    totalSubjectsEl.textContent = totalSubjects;

    avgStressEl.textContent = avgStress != null ? avgStress.toFixed(2) : 'N/A';
    avgSleepEl.textContent = avgSleep != null ? avgSleep.toFixed(2) : 'N/A';
  } catch (err) {
    console.error('Failed to load summary tiles', err);
    totalStudentsEl.textContent = '–';
    totalSubjectsEl.textContent = '–';
    avgStressEl.textContent = 'N/A';
    avgSleepEl.textContent = 'N/A';
  }
}

async function handleUpdateStudentSubmit(e) {
  e.preventDefault();

  const student_id = document.getElementById('update_student_id').value;

  const body = {
    first_name: document.getElementById('update_first_name').value.trim(),
    last_name: document.getElementById('update_last_name').value.trim(),
    email: document.getElementById('update_email').value.trim(),
    enrolled_year: Number(document.getElementById('update_enrolled_year').value),
    current_course_id: document.getElementById('update_course_id').value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/students/${student_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    if (!res.ok) {
      showNotification(data.error || 'Failed to update student', 'danger');
      return;
    }

    // Update local array so UI reflects changes
    const idx = students.findIndex(s => String(s.student_id) === String(student_id));
    if (idx !== -1) {
      students[idx] = {
        ...students[idx],
        ...body,
        name: `${body.first_name} ${body.last_name}`
      };
    }

    renderStudentsTable();

    // Close modal
    const modalEl = document.getElementById('updateStudentModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();

    showNotification('Student updated successfully', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Error updating student', 'danger');
  }
}

function loadCourseWeeklyReport() {
  const summaryDiv = document.getElementById('course-weekly-summary');
  if (summaryDiv) {
    summaryDiv.innerHTML = `
      <p class="mb-2"><strong>Total Courses:</strong> ${courses.length}</p>
      <p class="mb-2"><strong>Average Attendance:</strong> 89.7%</p>
      <p class="mb-0"><strong>Overall Performance:</strong> Good</p>
    `;
  }

  if (document.getElementById('course-attendance-mini')) {
    createCourseAttendanceMini();
  } else {
    createAttendanceChart();
  }

  if (document.getElementById('course-stress-mini')) {
    createCourseStressMini();
  } else {
    createGradeChart();
  }
}

// Chart creation functions
async function createStressChart() {
  const containerId = 'stress-chart';
  const el = document.getElementById(containerId);
  if (!el) return;

  try {
    const surveys = await apiGet('/api/surveys');
    if (!surveys.length) {
      el.innerHTML = '<p class="text-muted small mb-0">No survey data yet.</p>';
      return;
    }

    const stressData = surveys.map(s => s.stress_level); // 1–5

    const segments = [
      stressData.filter(s => s <= 2).length,        // Low
      stressData.filter(s => s === 3).length,       // Medium
      stressData.filter(s => s >= 4).length         // High
    ];

    renderGlassPie(
      containerId,
      segments,
      ['#27ae60', '#f39c12', '#e74c3c'],
      ['Low (1–2)', 'Medium (3)', 'High (4–5)']
    );
  } catch (e) {
    console.error(e);
    el.innerHTML = '<p class="text-muted small mb-0">Unable to load stress chart.</p>';
  }
}


async function createSleepChart() {
  const containerId = 'sleep-chart';
  const el = document.getElementById(containerId);
  if (!el) return;

  try {
    const surveys = await apiGet('/api/surveys');
    if (!surveys.length) {
      el.innerHTML = '<p class="text-muted small mb-0">No survey data yet.</p>';
      return;
    }

    const sleepData = surveys.map(s => s.sleep_hours);

    const segments = [
      sleepData.filter(s => s <= 4).length,              // Poor
      sleepData.filter(s => s > 4 && s <= 7).length,     // Average
      sleepData.filter(s => s > 7).length                // Good
    ];

    renderGlassPie(
      containerId,
      segments,
      ['#e74c3c', '#f39c12', '#27ae60'],
      ['Poor (0–4h)', 'Average (5–7h)', 'Good (8+h)']
    );
  } catch (e) {
    console.error(e);
    el.innerHTML = '<p class="text-muted small mb-0">Unable to load sleep chart.</p>';
  }
}


function renderConicPie(id, segments, colors) {
  const total = segments.reduce((a, b) => a + b, 0) || 1;
  let acc = 0;
  const stops = segments.map((v, i) => {
    const start = (acc / total) * 360;
    acc += v;
    const end = (acc / total) * 360;
    return `${colors[i]} ${start}deg ${end}deg`;
  }).join(', ');
  const el = document.getElementById(id);
  if (el) {
    el.style.background = `conic-gradient(${stops})`;
  }
}

function renderGlassPie(id, segments, colors, labels) {
  const el = document.getElementById(id);
  if (!el) return;
  const size = Math.min(el.clientWidth || 120, el.clientHeight || 120) || 120;
  const cx = size / 2;
  const cy = size / 2;
  const r = (size / 2) - 4;
  const total = segments.reduce((a, b) => a + b, 0) || 1;
  let start = 0;

  el.innerHTML = '';
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
  svg.style.borderRadius = '50%';
  el.appendChild(svg);

  const tip = (function ensureTip() {
    let t = el.__tip;
    if (!t) {
      t = document.createElement('div');
      t.className = 'mini-pie-tooltip';
      document.body.appendChild(t);
      el.__tip = t;
    }
    return t;
  })();

  for (let i = 0; i < segments.length; i++) {
    const value = segments[i];
    const angle = (value / total) * Math.PI * 2;
    const end = start + angle;
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', describeArc(cx, cy, r, start, end));
    path.setAttribute('fill', colors[i]);
    path.setAttribute('fill-opacity', '0.7');
    path.setAttribute('stroke', 'rgba(255,255,255,0.6)');
    path.setAttribute('stroke-width', '1');
    path.setAttribute('filter', 'url(#glassRefraction)');
    svg.appendChild(path);

    const percent = Math.round((value / total) * 1000) / 10; // one decimal
    const label = labels[i] || `Segment ${i + 1}`;
    const show = (evt) => {
      tip.innerHTML = `${label}: ${percent}% (${value})`;
      tip.style.display = 'block';
      tip.style.left = `${evt.pageX + 10}px`;
      tip.style.top = `${evt.pageY - 10}px`;
    };
    const hide = () => { tip.style.display = 'none'; };
    path.addEventListener('mouseenter', show);
    path.addEventListener('mousemove', show);
    path.addEventListener('mouseleave', hide);

    start = end;
  }
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const sx = cx + r * Math.cos(startAngle);
  const sy = cy + r * Math.sin(startAngle);
  const ex = cx + r * Math.cos(endAngle);
  const ey = cy + r * Math.sin(endAngle);
  const largeArcFlag = endAngle - startAngle > Math.PI ? 1 : 0;
  return `M ${cx} ${cy} L ${sx} ${sy} A ${r} ${r} 0 ${largeArcFlag} 1 ${ex} ${ey} Z`;
}

function createAttendanceChart() {
  const data = [{
    values: [89.7, 10.3],
    labels: ['Present', 'Absent'],
    type: 'pie',
    marker: {
      colors: ['#27ae60', '#e74c3c']
    }
  }];

  const layout = {
    title: 'Attendance Rate',
    height: 200,
    margin: { l: 20, r: 20, t: 40, b: 20 }
  };

  Plotly.newPlot('attendance-chart', data, layout, { responsive: true });
}

function createGradeChart() {
  const gradeRanges = ['A (90-100)', 'B (80-89)', 'C (70-79)', 'D (60-69)', 'F (0-59)'];
  const gradeCounts = [15, 18, 8, 3, 1];

  const data = [{
    values: gradeCounts,
    labels: gradeRanges,
    type: 'pie',
    marker: {
      colors: ['#27ae60', '#3498db', '#f39c12', '#e67e22', '#e74c3c']
    }
  }];

  const layout = {
    title: 'Grade Distribution',
    height: 200,
    margin: { l: 20, r: 20, t: 40, b: 20 }
  };

  Plotly.newPlot('grade-chart', data, layout, { responsive: true });
}

function createCourseAttendanceMini() {
  const present = Math.round(45 * 0.897); // mock based on 89.7%
  const absent = Math.max(0, 45 - present);
  const segments = [present, absent];
  renderGlassPie('course-attendance-mini', segments, ['#27ae60', '#e74c3c'], ['Present', 'Absent']);
}

function createCourseGradeMini() {
  const gradeRanges = ['A (90-100)', 'B (80-89)', 'C (70-79)', 'D (60-69)', 'F (0-59)'];
  const gradeCounts = [15, 18, 8, 3, 1];
  renderGlassPie('course-grade-mini', gradeCounts, ['#27ae60', '#3498db', '#f39c12', '#e67e22', '#e74c3c'], gradeRanges);
}

function createCourseStressMini() {
  const stressData = students.map(s => s.stress_level);
  const segments = [
    stressData.filter(s => s <= 3).length,
    stressData.filter(s => s > 3 && s <= 6).length,
    stressData.filter(s => s > 6).length
  ];
  renderGlassPie('course-stress-mini', segments, ['#27ae60', '#f39c12', '#e74c3c'], ['Low (1-3)', 'Medium (4-6)', 'High (7-10)']);
}

// Plot generation functions
async function generatePlot() {
  const xKey = document.getElementById('x-axis-select')?.value;
  const yKey = document.getElementById('y-axis-select')?.value;

  const xCfg = VIZ_PARAM_CONFIG[xKey];
  const yCfg = VIZ_PARAM_CONFIG[yKey];
  if (!xCfg || !yCfg) return;

  const rawType = inferPlotType(xKey, yKey);
  // For cohort-level data, "line" plots look messy – treat them as scatter
  const plotType = rawType === 'line' ? 'scatter' : rawType;

  const container = document.getElementById('plot-container');
  if (!container) return;

  try {
    // Cache surveys in surveyRecords
    if (!surveyRecords.length) {
      surveyRecords = await apiGet('/api/surveys');
    }

    const records = surveyRecords;

    if (!records.length) {
      container.innerHTML = '<p class="text-muted small mb-0">No data for this selection.</p>';
      return;
    }

    const x = records.map(xCfg.value);
    const y = records.map(yCfg.value);

    const layout = {
      margin: { t: 30, r: 20, b: 40, l: 50 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: xCfg.label },
      yaxis: { title: yCfg.label },
      height: 320
    };

    let data;

    switch (plotType) {
      case 'scatter':
        data = [{
          x,
          y,
          type: 'scatter',
          mode: 'markers',
          hovertemplate: 'x=%{x}<br>y=%{y}<extra></extra>'
        }];
        break;

      case 'bubble':
        data = [{
          x,
          y,
          mode: 'markers',
          type: 'scatter',
          marker: {
            size: y.map(v => Math.max(10, Math.abs(v || 0) * 0.6)),
            sizemode: 'area',
            opacity: 0.8
          },
          hovertemplate: 'x=%{x}<br>y=%{y}<extra></extra>'
        }];
        break;

      case 'box':
        data = [{
          x,
          y,
          type: 'box',
          boxpoints: 'all',
          jitter: 0.3,
          pointpos: -1.5
        }];
        break;

      case 'bar':
        data = [{
          x,
          y,
          type: 'bar',
          hovertemplate: 'x=%{x}<br>y=%{y}<extra></extra>'
        }];
        break;

      case 'area':
        data = [{
          x,
          y,
          type: 'scatter',
          mode: 'lines',
          fill: 'tozeroy',
          hovertemplate: 'x=%{x}<br>y=%{y}<extra></extra>'
        }];
        break;

      case 'density':
        data = [{
          x,
          y,
          type: 'histogram2dcontour',
          contours: { coloring: 'heatmap' }
        }];
        layout.coloraxis = { showscale: true };
        break;

      case 'violin':
        data = [{
          x,
          y,
          type: 'violin',
          points: 'all',
          jitter: 0.3,
          scalemode: 'width'
        }];
        break;

      default:
        // Fallback: simple scatter
        data = [{
          x,
          y,
          type: 'scatter',
          mode: 'markers'
        }];
    }

    Plotly.newPlot(container, data, layout, { responsive: true });

  } catch (err) {
    console.error(err);
    container.innerHTML = '<p class="text-muted small mb-0">Unable to load data for the plot.</p>';
  }
}


function generateCoursePlot() {
  const xAxis = document.getElementById('course-x-axis-select').value;
  const yAxis = document.getElementById('course-y-axis-select').value;

  // Generate mock data for courses
  const xData = generateMockData(xAxis, courses.length);
  const yData = generateMockData(yAxis, courses.length);

  const trace = {
    x: xData,
    y: yData,
    mode: 'markers+lines',
    type: 'scatter',
    marker: {
      size: 15,
      color: xData.map((_, i) => i * 50),
      colorscale: 'Plasma',
      showscale: true
    },
    text: courses.map(c => c.name),
    hovertemplate: '<b>%{text}</b><br>' + xAxis + ': %{x}<br>' + yAxis + ': %{y}<extra></extra>'
  };

  const layout = {
    xaxis: { title: xAxis.charAt(0).toUpperCase() + xAxis.slice(1) },
    yaxis: { title: yAxis.charAt(0).toUpperCase() + yAxis.slice(1) },
    hovermode: 'closest',
    margin: { t: 8, r: 20, b: 30, l: 40 },
    height: 300,
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)'
  };

  Plotly.newPlot('course-plot-container', [trace], layout, { responsive: true });
}

function generateDefaultPlot() {
  generatePlot();
}

function generateDefaultCoursePlot() {
  generateCoursePlot();
}

function generateMockData(type, count) {
  const data = [];
  for (let i = 0; i < count; i++) {
    switch (type) {
      case 'stress-level':
        data.push(Math.floor(Math.random() * 10) + 1);
        break;
      case 'sleep-hours':
        data.push((Math.random() * 8 + 2).toFixed(1));
        break;
      case 'grades':
        data.push(Math.floor(Math.random() * 40) + 60);
        break;
      case 'attendance':
        data.push(Math.floor(Math.random() * 20) + 80);
        break;
      case 'modules':
        data.push(Math.floor(Math.random() * 10) + 1);
        break;
      case 'weeks':
        data.push(Math.floor(Math.random() * 16) + 1);
        break;
      default:
        data.push(Math.floor(Math.random() * 100));
    }
  }
  return data;
}

function findStudentById(id) {
  return students.find(s => String(s.id) === String(id));
}

function getStudentsForCurrentView(list = students) {
  if (studentView === 'favourites') {
    return list.filter(s => s.starred);
  }
  return list;
}

// Student table functions
async function loadStudents() {
  const tbody = document.getElementById('student-tbody');
  if (tbody) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-4">
          LOADING STUDENTS FROM THE SERVER...
        </td>
      </tr>`;
  }
  try {
    const data = await apiGet('/students');
    const list = Array.isArray(data) ? data : data.students;
    students = list.map(s => ({
      id: s.student_id,
      student_id: s.student_id,
      first_name: s.first_name,
      last_name: s.last_name,
      name: `${s.first_name} ${s.last_name}`,
      email: s.email,
      enrolled_year: s.enrolled_year,
      current_course_id: s.current_course_id,
      stress_level: null,
      sleep_hours: null,
      grades: null,
      starred: false
    }));

    renderStudentsTable();
    populateVizStudentDropdown();

    students.forEach(s => fetchStudentWellbeingSummary(s));
    students.forEach(s => fetchStudentGrades?.(s));

  } catch (err) {
    console.error(err);
    showNotification('UNABLE TO LOAD STUDENTS FROM SERVER.', 'danger');
  }
}

// LOAD COURSES INTO ADD-STUDENT DROPDOWN
async function loadCoursesIntoDropdown() {
  try {
    const res = await fetch(`${API_BASE_URL}/courses`);
    const data = await res.json();

    // API may return either:
    //   [ {course_id, course_name...}, ... ]
    // OR { courses: [ ... ] }
    const list = Array.isArray(data) ? data : data.courses;

    const sel = document.getElementById("add_course_id");
    if (!sel) return;

    sel.innerHTML = ""; // clear existing

    list.forEach(c => {
      const op = document.createElement("option");
      op.value = c.course_id;
      op.textContent = `${c.course_id} — ${c.course_name}`;
      sel.appendChild(op);
    });

    // ALSO populate UPDATE form dropdown
    const upd = document.getElementById("update_course_id");
    if (upd) {
      upd.innerHTML = "";
      list.forEach(c => {
        const op = document.createElement("option");
        op.value = c.course_id;
        op.textContent = `${c.course_id} — ${c.course_name}`;
        upd.appendChild(op);
      });
    }

  } catch (err) {
    console.error("Failed to load courses into dropdown", err);
  }
}

async function handleAddStudent(event) {
  event.preventDefault();

  const body = {
    student_id: document.getElementById("add_student_id").value.trim(),
    first_name: document.getElementById("add_first_name").value.trim(),
    last_name: document.getElementById("add_last_name").value.trim(),
    email: document.getElementById("add_email").value.trim(),
    enrolled_year: parseInt(document.getElementById("add_enrolled_year").value),
    current_course_id: document.getElementById("add_course_id").value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/students`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok) {
      showNotification(data.error || "FAILED TO ADD STUDENT", "danger");
      return;
    }

    // Use nested "student" object if present
    const saved = data.student || data;

    students.push({
      id: saved.student_id,
      student_id: saved.student_id,
      first_name: saved.first_name,
      last_name: saved.last_name,
      name: `${saved.first_name} ${saved.last_name}`,
      email: saved.email,
      enrolled_year: saved.enrolled_year,
      current_course_id: saved.current_course_id,
      stress_level: null,
      sleep_hours: null,
      grades: null,
      starred: false
    });

    renderStudentsTable();

    showNotification("STUDENT ADDED SUCCESSFULLY!", "success");

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById("addStudentModal"));
    if (modal) modal.hide();

    event.target.reset();

  } catch (err) {
    console.error(err);
    showNotification("ERROR ADDING STUDENT", "danger");
  }
}

// Main entry for attendance.html
async function initAttendancePage() {
  try {
    await populateAttendanceModules(); // fill the Module dropdown from /courses
    await loadAttendanceRecords();     // load records from /academic/attendance
  } catch (err) {
    console.error('Failed to initialise attendance page', err);
    showNotification?.('Unable to load attendance page.', 'danger');
  }
}

// Fetch courses from backend and use them as "modules" in the dropdown
async function populateAttendanceModules() {
  const sel = document.getElementById('moduleSelect');
  if (!sel) return;

  try {
    const data = await apiGet('/courses');
    const list = Array.isArray(data) ? data : data.courses || [];

    // Start with an "all" option
    sel.innerHTML = '<option value="all">All Modules / Courses</option>';

    list.forEach(c => {
      const op = document.createElement('option');
      // best guess: course_id & course_name from your /courses endpoint
      op.value = c.course_id || c.id || '';
      op.textContent = `${c.course_id || c.id} — ${c.course_name || c.name || 'Untitled course'}`;
      sel.appendChild(op);
    });

    // Whenever module changes, reload records from server
    sel.addEventListener('change', () => {
      loadAttendanceRecords();
    });
  } catch (err) {
    console.error('Failed to load modules/courses for attendance page', err);
    // leave the original hard-coded options as a fallback
  }
}

// Load attendance from /academic/attendance with optional filters
async function loadAttendanceRecords() {
  const tbody = document.getElementById('attendanceTableBody');
  if (!tbody) return;

  const moduleSel = document.getElementById('moduleSelect');
  const weekSel   = document.getElementById('weekSelect');

  // Build query string for backend filters
  const params = new URLSearchParams();

  if (moduleSel && moduleSel.value && moduleSel.value !== 'all') {
    params.set('module_id', moduleSel.value);
  }
  if (weekSel && weekSel.value && weekSel.value !== 'all') {
    params.set('week_number', weekSel.value);
  }

  const url = params.toString()
    ? `/academic/attendance?${params.toString()}`
    : '/academic/attendance';

  try {
    const data = await apiGet(url);            // returns a list from attendances_schema :contentReference[oaicite:2]{index=2}
    attendanceRecords = Array.isArray(data) ? data : (data.attendance_records || []);
    applyAttendanceFiltersAndRender();         // also applies client-side date filter + stats
  } catch (err) {
    console.error('Failed to load attendance records', err);
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-danger">
          Unable to load attendance records from the server.
        </td>
      </tr>
    `;
  }
}

// Called from the Week / Date controls and after loading data
function applyAttendanceFiltersAndRender() {
  const tbody       = document.getElementById('attendanceTableBody');
  const weekSel     = document.getElementById('weekSelect');
  const dateInput   = document.getElementById('dateFilter');
  const recordCount = document.getElementById('recordCount');

  if (!tbody) return;

  let filtered = [...attendanceRecords];

  // Week filter (client-side, in addition to any server filter)
  if (weekSel && weekSel.value && weekSel.value !== 'all') {
    filtered = filtered.filter(r => String(r.week_number) === String(weekSel.value));
  }

  // Date filter – match YYYY-MM-DD prefix of class_date
  if (dateInput && dateInput.value) {
    const date = dateInput.value;
    filtered = filtered.filter(r => (r.class_date || '').startsWith(date));
  }

  // Update stats tiles
  const total   = filtered.length;
  const present = filtered.filter(r => r.is_present === true || r.is_present === 1 || r.is_present === 'Y').length;
  const absent  = total - present;
  const rate    = total ? Math.round((present / total) * 100) : 0;

  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };

  setText('statTotal', total);
  setText('statPresent', present);
  setText('statAbsent', absent);
  setText('statRate', rate + '%');

  if (recordCount) {
    recordCount.textContent = `Showing ${total} record${total === 1 ? '' : 's'}`;
  }

  if (!filtered.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted">
          No attendance records found
        </td>
      </tr>
    `;
    return;
  }

  // Helper to safely pick student id / name from schema
  const getStudentId = r =>
    r.student_id ||
    (r.student && r.student.student_id) ||
    (r.registration && r.registration.student_id) ||
    '';

  const getStudentName = r =>
    r.student_name ||
    (r.student && (r.student.name ||
      `${r.student.first_name || ''} ${r.student.last_name || ''}`.trim())) ||
    (r.registration && r.registration.student_name) ||
    '-';

  tbody.innerHTML = filtered.map(r => {
    const statusBadge = (r.is_present === true || r.is_present === 1 || r.is_present === 'Y')
      ? '<span class="badge bg-success">Present</span>'
      : '<span class="badge bg-danger">Absent</span>';

    const classDate = r.class_date ? String(r.class_date).substring(0, 10) : '-';
    const reason    = (!r.is_present && r.reason_absent) ? r.reason_absent : '';

    return `
      <tr>
        <td>${r.attendance_id || r.id || ''}</td>
        <td>${getStudentId(r)}</td>
        <td>${getStudentName(r)}</td>
        <td>${r.week_number ?? ''}</td>
        <td>${classDate}</td>
        <td>${statusBadge}</td>
        <td>${reason || '-'}</td>
        <td>
          <!-- Placeholder for future edit/delete actions -->
          <button class="btn btn-sm btn-outline-primary" disabled title="Edit coming soon">
            <i class="bi bi-pencil"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

// Hooked from inline onchange="filterRecords()" in attendance.html
function filterRecords() {
  applyAttendanceFiltersAndRender();
}

// Hooked from the "Clear Filters" button
function clearFilters() {
  const weekSel   = document.getElementById('weekSelect');
  const dateInput = document.getElementById('dateFilter');

  if (weekSel) weekSel.value = 'all';
  if (dateInput) dateInput.value = '';

  // Reload from server to clear any backend week/module filters too
  loadAttendanceRecords();
}

function populateVizStudentDropdown() {
  const sel = document.getElementById('viz-student-select');
  if (!sel) return;

  // Reset options
  sel.innerHTML = '<option value="all">All Students</option>';

  students.forEach(s => {
    const option = document.createElement('option');
    option.value = s.student_id;           // use backend id
    option.textContent = s.name;           // "First Last"
    sel.appendChild(option);
  });
}


async function fetchStudentWellbeingSummary(student) {
  try {
    const data = await apiGet(`/students/${student.student_id}/wellbeing_trends`);
    if (data && data.averages) {
      student.stress_level = data.averages.stress_level ?? null;
      student.sleep_hours = data.averages.sleep_hours ?? null;
      // Re-render to show updated badges
      renderStudentsTable();
    }
  } catch (err) {
    console.error(`Failed to load wellbeing for ${student.student_id}`, err);
  }
}

async function fetchStudentGrades(student) {
  try {
    // Call backend: /academic/submissions?student_id=S001
    const params = new URLSearchParams({ student_id: student.student_id });
    const submissions = await apiGet(`/academic/submissions?${params.toString()}`);

    if (!Array.isArray(submissions) || !submissions.length) {
      student.grades = null;
      return;
    }

    // Keep only graded submissions and map to a simple display value
    student.grades = submissions
      .filter(sub => sub.grade_achieved != null)
      .map(sub => sub.grade_achieved);         // or `${sub.assignment_id}: ${sub.grade_achieved}`

    // Re-render table to show updated grades
    renderStudentsTable();
  } catch (err) {
    console.error(`Failed to load grades for ${student.student_id}`, err);
  }
}


async function fetchStudentAcademicSummary(student) {
  try {
    const data = await apiGet(`/reports/student/${student.student_id}/academic`);

    // Example structure — adjust to match your backend's exact response
    student.grades = data.grades || null;

    renderStudentsTable();
  } catch (err) {
    console.error(`Failed to load academic info for ${student.student_id}`, err);
  }
}

function loadCourses() {
  courses = [...mockCourses];
}

function renderStudentsTable() {
  const tbody = document.getElementById('student-tbody');
  if (!tbody) return;

  const visibleStudents = getStudentsForCurrentView(students);

  if (!visibleStudents.length) {
    const message = studentView === 'favourites'
      ? 'No favourite students yet. Star students from the actions menu to pin them here.'
      : 'No students available.';
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-4">${message}</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = visibleStudents.map(student => {
    const stress = student.stress_level;
    const sleep = student.sleep_hours;

    const stressBadge = stress != null
      ? `<span class="badge ${getStressLevelClass(stress)}">${stress.toFixed(1)}</span>`
      : '<span class="badge bg-secondary">N/A</span>';

    const sleepCell = sleep != null
      ? (sleep <= 5
        ? `<span class="badge bg-danger">${sleep.toFixed(1)}h</span>`
        : `${sleep.toFixed(1)}h`)
      : 'N/A';

    return `
      <tr>
        <td>${student.name}</td>
        <td>${stressBadge}</td>
        <td>${sleepCell}</td>
        <td>${student.grades ? student.grades.join(', ') : 'N/A'}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="openUpdateModal('${student.id}')">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteStudent('${student.id}')">
            <i class="bi bi-trash"></i>
          </button>
          <button class="btn btn-sm btn-outline-warning me-1" onclick="toggleStar('${student.id}')">
            <i class="bi ${student.starred ? 'bi-star-fill' : 'bi-star'}"></i>
          </button>
          <button class="btn btn-sm btn-outline-info" onclick="viewStudentProfile('${student.id}')">
          <i class="bi bi-graph-up"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}


function filterStudents() {
  const searchTerm = document.getElementById('student-search')?.value.toLowerCase() || '';
  const stressFilter = document.getElementById('stress-filter')?.value;
  const sleepFilter = document.getElementById('sleep-filter')?.value;

  const baseList = getStudentsForCurrentView(students);

  const filteredStudents = baseList.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm);

    let matchesStress = true;
    if (stressFilter) {
      const [min, max] = stressFilter.split('-').map(Number);
      if (student.stress_level != null) {
        matchesStress = student.stress_level >= min && student.stress_level <= max;
      } else {
        matchesStress = false; // or true if you want to keep unknowns
      }
    }

    let matchesSleep = true;
    if (sleepFilter) {
      const [min, max] = sleepFilter.split('-').map(Number);
      if (student.sleep_hours != null) {
        matchesSleep = student.sleep_hours >= min && student.sleep_hours <= max;
      } else {
        matchesSleep = false;
      }
    }

    return matchesSearch && matchesStress && matchesSleep;
  });

  renderFilteredStudents(filteredStudents);
}


function renderFilteredStudents(filteredStudents) {
  const tbody = document.getElementById('student-tbody');
  if (!tbody) return;

  if (!filteredStudents.length) {
    const emptyMessage = studentView === 'favourites'
      ? 'No favourite students match your filters yet.'
      : 'No students match your filters yet.';
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-3">${emptyMessage}</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filteredStudents.map(student => {
    const stress = student.stress_level;
    const sleep = student.sleep_hours;

    const stressBadge = stress != null
      ? `<span class="badge ${getStressLevelClass(stress)}">${stress.toFixed(1)}</span>`
      : '<span class="badge bg-secondary">N/A</span>';

    const sleepCell = sleep != null
      ? (sleep <= 5
        ? `<span class="badge bg-danger">${sleep.toFixed(1)}h</span>`
        : `${sleep.toFixed(1)}h`)
      : 'N/A';

    return `
      <tr>
        <td>${student.name}</td>
        <td>${stressBadge}</td>
        <td>${sleepCell}</td>
        <td>${student.grades ? student.grades.join(', ') : 'N/A'}</td>
        <td>
<button class="btn btn-sm btn-outline-primary me-1" onclick="openUpdateModal('${student.id}')">
  <i class="bi bi-pencil"></i>
</button>
          <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteStudent('${student.id}')">
            <i class="bi bi-trash"></i>
          </button>
          <button class="btn btn-sm btn-outline-warning me-1" onclick="toggleStar('${student.id}')">
            <i class="bi ${student.starred ? 'bi-star-fill' : 'bi-star'}"></i>
          </button>
          <button class="btn btn-sm btn-outline-info" onclick="viewStudentProfile('${student.id}')">
          <i class="bi bi-graph-up"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function setStudentView(view) {
  studentView = view;

  const allBtn = document.getElementById('tab-all-students');
  const favBtn = document.getElementById('tab-favourite-students');

  if (allBtn) allBtn.classList.toggle('active', view === 'all');
  if (favBtn) favBtn.classList.toggle('active', view === 'favourites');

  // Re-apply any filters or search terms to the newly selected view
  filterStudents();
}

function sortTable(sortBy) {
  students.sort((a, b) => {
    if (sortBy === 'stress_level') {
      return (a.stress_level ?? Infinity) - (b.stress_level ?? Infinity);
    } else if (sortBy === 'sleep_hours') {
      return (a.sleep_hours ?? Infinity) - (b.sleep_hours ?? Infinity);
    }
    return 0;
  });

  renderStudentsTable();
}

function addStudent() {
  const name = prompt('Enter student name:');
  if (name) {
    const newStudent = {
      id: students.length + 1,
      name: name,
      stress_level: Math.floor(Math.random() * 10) + 1,
      sleep_hours: (Math.random() * 8 + 2).toFixed(1),
      grades: [Math.floor(Math.random() * 40) + 60, Math.floor(Math.random() * 40) + 60, Math.floor(Math.random() * 40) + 60],
      starred: false
    };
    students.push(newStudent);
    renderStudentsTable();
  }
}

function openUpdateModal(id) {
  const student = findStudentById(id);
  if (!student) return;

  // Fill hidden id + fields
  document.getElementById('update_student_id').value = student.student_id;
  document.getElementById('update_first_name').value = student.first_name || '';
  document.getElementById('update_last_name').value = student.last_name || '';
  document.getElementById('update_email').value = student.email || '';
  document.getElementById('update_enrolled_year').value = student.enrolled_year || '';

  const courseSelect = document.getElementById('update_course_id');
  if (courseSelect && student.current_course_id) {
    courseSelect.value = student.current_course_id;
  }

  // Show the Bootstrap modal
  const modalEl = document.getElementById('updateStudentModal');
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
}

async function editStudent(id) {
  const student = findStudentById(id);
  if (!student) return;

  const newName = prompt('Enter new name:', student.name);
  if (!newName) return;

  const parts = newName.trim().split(/\s+/);
  const first_name = parts[0];
  const last_name = parts.slice(1).join(' ') || student.last_name || '';

  try {
    const body = {
      first_name,
      last_name,
      email: student.email,
      enrolled_year: student.enrolled_year,
      current_course_id: student.current_course_id
    };

    const res = await fetch(`${API_BASE_URL}/students/${student.student_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok) {
      showNotification(data.error || 'Failed to update student', 'danger');
      return;
    }

    student.first_name = data.first_name;
    student.last_name = data.last_name;
    student.name = `${data.first_name} ${data.last_name}`;
    student.email = data.email;
    student.enrolled_year = data.enrolled_year;

    renderStudentsTable();
    showNotification('Student updated successfully', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Error updating student', 'danger');
  }
}


async function deleteStudent(id) {
  const student = findStudentById(id);
  if (!student) return;

  if (!confirm(`Are you sure you want to delete ${student.name}?`)) return;

  try {
    const res = await fetch(`${API_BASE_URL}/students/${student.student_id}`, {
      method: 'DELETE'
    });
    const data = await res.json();

    if (!res.ok) {
      showNotification(data.error || 'Failed to delete student', 'danger');
      return;
    }

    // Remove by matching ID as string to be safe
    students = students.filter(s => String(s.id) !== String(id));
    renderStudentsTable();
    showNotification('Student deleted successfully', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Error deleting student', 'danger');
  }
}

function toggleStar(id) {
  const student = findStudentById(id);
  if (!student) return;
  student.starred = !student.starred;
  filterStudents();
}

async function trackStudent(id) {
  const student = findStudentById(id);
  if (!student) return;

  try {
    const data = await apiGet(`/students/${student.student_id}/wellbeing_trends`);
    const avg = data.averages || {};
    const latest = (data.weekly_trends || []).slice(-1)[0];

    const msg = [
      `Tracking ${data.name || student.name}`,
      '',
      `Average stress: ${avg.stress_level != null ? avg.stress_level.toFixed(2) : 'N/A'}`,
      `Average sleep: ${avg.sleep_hours != null ? avg.sleep_hours.toFixed(2) + ' h' : 'N/A'}`,
      `Average social connection: ${avg.social_connection_score != null ? avg.social_connection_score.toFixed(2) : 'N/A'}`,
      latest
        ? `Latest week (${latest.week}): stress=${latest.stress_level}, sleep=${latest.sleep_hours} h`
        : ''
    ].join('\n');

    alert(msg);
  } catch (err) {
    console.error(err);
    alert(`Unable to load wellbeing trends for ${student.name}`);
  }
}

function viewStudentProfile(id) {
  const student = findStudentById(id);
  if (!student) return;
  window.location.href = `student_profile.html?student_id=${encodeURIComponent(student.student_id)}`;
}

// Course functions
function loadCourseInfo() {
  const courseSelect = document.getElementById('course-select');
  const courseInfoContent = document.getElementById('course-info-content');

  if (courseSelect && courseInfoContent) {
    const selectedCourse = courseSelect.value;
    const course = courses.find(c => c.code.toLowerCase() === selectedCourse);

    if (course) {
      courseInfoContent.innerHTML = `
        <p class="mb-1">
          <strong>Course Code:</strong> ${course.code}
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <strong>Instructor:</strong> ${course.instructor}
        </p>
        <p class="mb-0">
          <strong>Enrollment:</strong> ${course.enrollment} students
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <strong>Average Grade:</strong> ${course.average_grade}%
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <strong>Attendance Rate:</strong> ${course.attendance_rate}%
        </p>
      `;
    } else {
      courseInfoContent.innerHTML = '<p class="text-muted">Please select a course to view information</p>';
    }
  }
}

// File upload functions
function handleSurveyUpload(event) {
  event.preventDefault();
  const fileInput = document.getElementById('survey-file');
  const file = fileInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      alert('Survey data uploaded successfully!');
      fileInput.value = '';
      loadWellbeingDashboard();
    };
    reader.readAsText(file);
  }
}

function handleSurveyFileChange(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      alert('Survey data uploaded successfully!');
      event.target.value = '';
      loadWellbeingDashboard();
    };
    reader.readAsText(file);
  }
}

function handleCourseUpload(event) {
  event.preventDefault();
  const fileInput = document.getElementById('course-file');
  const uploadType = document.querySelector('input[name="upload-type"]:checked').value;
  const file = fileInput.files[0];

  if (file) {
    // Simulate file upload
    const reader = new FileReader();
    reader.onload = function (e) {
      alert(`${uploadType} data uploaded successfully!`);
      fileInput.value = '';
      loadCourseDashboard(); // Refresh data
    };
    reader.readAsText(file);
  }
}

async function loadStudentProfilePage() {
  // 1. Read student_id from query string
  const params = new URLSearchParams(window.location.search);
  const studentId = params.get('student_id');

  if (!studentId) {
    showNotification('No student_id provided in URL', 'danger');
    return;
  }

  try {
    // 2. Get full profile and wellbeing trends + academic summary
    const [profileRes, trendsRes, academicRes] = await Promise.all([
      apiGet(`/students/${studentId}/full_profile`),
      apiGet(`/students/${studentId}/wellbeing_trends`),
      apiGet(`/students/${studentId}/academic-performance`)
    ]);

    // 3. Header / meta
    const info = profileRes.student_info || {};
    const name = info.name || trendsRes.name || `Student ${studentId}`;

    document.getElementById('profile-name').textContent = name;

    const idEl = document.getElementById('profile-student-id');
    if (idEl) {
      idEl.textContent = info.student_id || studentId;
    }

    const emailEl = document.getElementById('profile-email');
    if (emailEl) {
      emailEl.textContent = info.email || trendsRes.email || 'Email not available';
    }

    // 4. Summary tiles
    document.getElementById('tile-avg-stress').textContent =
      trendsRes.averages?.stress_level != null
        ? trendsRes.averages.stress_level.toFixed(2)
        : '–';

    document.getElementById('tile-avg-sleep').textContent =
      trendsRes.averages?.sleep_hours != null
        ? trendsRes.averages.sleep_hours.toFixed(2)
        : '–';

    const avgGrade = academicRes.average_grade ??
      academicRes.analytics?.academic_performance?.average_grade ??
      null;

    const attendanceRate = academicRes.attendance_rate ??
      academicRes.analytics?.attendance?.overall_rate ??
      null;

    document.getElementById('tile-avg-grade').textContent =
      avgGrade != null
        ? Number(avgGrade).toFixed(2)
        : '-';

    document.getElementById('tile-attendance').textContent =
      attendanceRate != null
        ? Number(attendanceRate).toFixed(1) + '%'
        : '-';

    // 5. Weekly data arrays
    const weekly = trendsRes.weekly_trends || [];
    const weeks  = weekly.map(w => w.week);
    const stress = weekly.map(w => w.stress_level);
    const sleep  = weekly.map(w => w.sleep_hours);

    // ---- COMBINED BAR+LINE: Weekly Stress & Sleep ----
    const comboEl = document.getElementById('chart-weekly-combo');
    if (weeks.length && comboEl) {
      const comboData = [
        {
          x: weeks,
          y: stress,
          name: 'Stress (1–5)',
          type: 'bar',
          yaxis: 'y1'
        },
        {
          x: weeks,
          y: sleep,
          name: 'Sleep (h)',
          type: 'scatter',
          mode: 'lines+markers',
          yaxis: 'y2'
        }
      ];

      const comboLayout = {
        margin: { t: 10, r: 50, b: 40, l: 40 },
        xaxis: { title: 'Week' },
        yaxis: { title: 'Stress', rangemode: 'tozero' },
        yaxis2: {
          title: 'Sleep (h)',
          overlaying: 'y',
          side: 'right',
          rangemode: 'tozero'
        },
        legend: { orientation: 'h', y: -0.2 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
      };

      Plotly.newPlot('chart-weekly-combo', comboData, comboLayout, { responsive: true });
    } else if (comboEl) {
      comboEl.innerHTML =
        '<p class="text-muted small mb-0">No weekly data.</p>';
    }

    // 6. Pie charts: distribution of stress & sleep
    if (stress.length && document.getElementById('chart-stress-pie')) {
      const stressBuckets = [0, 0, 0]; // low, medium, high
      stress.forEach(v => {
        if (v == null) return;
        if (v <= 2)       stressBuckets[0]++;
        else if (v <= 4)  stressBuckets[1]++;
        else              stressBuckets[2]++;
      });

      Plotly.newPlot('chart-stress-pie', [{
        values: stressBuckets,
        labels: ['Low (1–2)', 'Medium (3–4)', 'High (5)'],
        type: 'pie',
        hole: 0.4
      }], {
        showlegend: true,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
      }, { responsive: true });
    } else {
      const el = document.getElementById('chart-stress-pie');
      if (el) {
        el.innerHTML =
          '<p class="text-muted small mb-0">No stress data.</p>';
      }
    }

    if (sleep.length && document.getElementById('chart-sleep-pie')) {
      const sleepBuckets = [0, 0, 0]; // poor, average, good
      sleep.forEach(v => {
        if (v == null) return;
        if (v <= 5)          sleepBuckets[0]++;
        else if (v <= 7)     sleepBuckets[1]++;
        else                 sleepBuckets[2]++;
      });

      Plotly.newPlot('chart-sleep-pie', [{
        values: sleepBuckets,
        labels: ['Poor (≤5h)', 'Average (5–7h)', 'Good (>7h)'],
        type: 'pie',
        hole: 0.4
      }], {
        showlegend: true,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
      }, { responsive: true });
    } else {
      const el = document.getElementById('chart-sleep-pie');
      if (el) {
        el.innerHTML =
          '<p class="text-muted small mb-0">No sleep data.</p>';
      }
    }

    // 7. Gauge / index: Stress & Sleep combined
    const avgStress = trendsRes.averages?.stress_level ?? null;
    const avgSleep  = trendsRes.averages?.sleep_hours ?? null;

    const balanceEl = document.getElementById('chart-balance');
    if (avgStress != null && avgSleep != null && balanceEl) {
      // simple risk score 0–100: higher = worse
      const stressComponent = (avgStress / 5) * 60;
      const sleepComponent  = Math.max(0, (8 - avgSleep)) / 8 * 40;
      const riskScore = Math.min(100, Math.max(0, stressComponent + sleepComponent));

      Plotly.newPlot('chart-balance', [{
        type: 'indicator',
        mode: 'gauge+number',
        value: riskScore,
        title: { text: 'Risk Score', font: { size: 14 } },
        gauge: {
          axis: { range: [0, 100] },
          bar: { color: '#8e44ad' },
          steps: [
            { range: [0, 33], color: 'rgba(39, 174, 96,0.4)' },
            { range: [33, 66], color: 'rgba(243,156,18,0.4)' },
            { range: [66, 100], color: 'rgba(231,76,60,0.5)' }
          ]
        }
      }], {
        margin: { t: 10, b: 10, l: 10, r: 10 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
      }, { responsive: true });
    } else if (balanceEl) {
      balanceEl.innerHTML =
        '<p class="text-muted small mb-0">Not enough data to calculate risk.</p>';
    }

  } catch (err) {
    console.error('Failed to load student profile page', err);
    showNotification('Unable to load student profile.', 'danger');
  }
}

function handleCourseFileChange(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const selected = document.querySelector('input[name="course-upload-type"]:checked');
      const typ = selected ? selected.value : 'data';
      alert(`${typ.charAt(0).toUpperCase() + typ.slice(1)} data uploaded successfully!`);
      event.target.value = '';
      loadCourseDashboard();
    };
    reader.readAsText(file);
  }
}

function exportEarlyWarning() {
  // Use 1–5 stress scale and guard nulls
  const earlyWarningStudents = students.filter(student => {
    const stress = student.stress_level;
    const sleep = student.sleep_hours;

    const isHighStress = stress != null && stress >= 4;  // 4–5 on 1–5 scale
    const isLowSleep = sleep != null && sleep < 5;      // < 5 hours

    return isHighStress || isLowSleep;
  });

  let csvContent = "Name,Status\n";
  earlyWarningStudents.forEach(student => {
    const stress = student.stress_level;
    const sleep = student.sleep_hours;
    // scale stress to 1–10 for getStatusText/getStatusLevel
    const mappedStress = stress != null ? stress * 2 : 0;
    csvContent += `${student.name},${getStatusText(mappedStress, sleep ?? 8)}\n`;
  });

  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'early_warning_students.csv';
  a.click();
  window.URL.revokeObjectURL(url);
}


// Utility functions
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} position-fixed`;
  notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
  notification.innerHTML = `
    <div class="d-flex justify-content-between align-items-center">
      <span>${message}</span>
      <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
    </div>
  `;

  document.body.appendChild(notification);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Initialize charts and data when page loads
window.addEventListener('load', function () {
  // Add fade-in animation to cards
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add('fade-in');
    }, index * 100);
  });
});

