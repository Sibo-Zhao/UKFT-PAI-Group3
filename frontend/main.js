// Student Wellbeing System JavaScript

// Global variables
let currentUser = null;
let students = [];
let courses = [];
let currentPage = 'login';

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
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  const savedUser = localStorage.getItem('currentUser');
  if (savedUser) {
    currentUser = JSON.parse(savedUser);
  }

  const pageName = getCurrentPageName();
  const isLoginPage = pageName === 'index.html';

  if (!isLoginPage && !currentUser) {
    window.location.href = 'index.html';
    return;
  }

  if (isLoginPage && currentUser) {
    window.location.href = currentUser.role === 'wellbeing' ? 'wellbeing.html' : 'course.html';
    return;
  }

  setupEventListeners();
  applyTitleConfig();
  loadStudents();
  loadCourses();

  if (pageName === 'wellbeing.html') {
    loadWellbeingDashboard();
  } else if (pageName === 'students.html') {
    loadStudentsTable();
  } else if (pageName === 'course.html') {
    loadCourseDashboard();
  } else if (pageName === 'attendance.html') {
    loadCourseWeeklyReport();
  }
}

function getCurrentPageName() {
  const path = window.location.pathname;
  const name = path.substring(path.lastIndexOf('/') + 1) || 'index.html';
  return name;
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
}

// Authentication functions
function handleLogin(event) {
  event.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Simple fake login logic
  if (username === 'wellbeing') {
    currentUser = { username: 'wellbeing', role: 'wellbeing' };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    showPage('wellbeing-dashboard');
  } else if (username === 'course') {
    currentUser = { username: 'course', role: 'course' };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    showPage('course-dashboard');
  } else {
    alert('Invalid username. Use "wellbeing" or "course" as username.');
  }
}

function logout() {
  currentUser = null;
  localStorage.removeItem('currentUser');
  window.location.href = 'index.html';
}

// Page navigation
function showPage(pageId) {
  const map = {
    'login': 'index.html',
    'wellbeing-dashboard': 'wellbeing.html',
    'students': 'students.html',
    'course-dashboard': 'course.html',
    'attendance': 'attendance.html',
    'settings': 'settings.html'
  };
  const target = map[pageId] || 'index.html';
  window.location.href = target;
}

// Dashboard functions
function loadWellbeingDashboard() {
  loadEarlyWarningStudents();
  loadWeeklyReport();
  generateDefaultPlot();
}

function loadCourseDashboard() {
  loadCourseWeeklyReport();
  generateDefaultCoursePlot();
}

function loadStudentsTable() {
  renderStudentsTable();
}

// Early Warning Students
function loadEarlyWarningStudents() {
  const earlyWarningStudents = students.filter(student => student.stress_level >= 7 || student.sleep_hours <= 5);
  const tbody = document.getElementById('early-warning-tbody');
  if (tbody) {
    tbody.innerHTML = earlyWarningStudents.map(student => `
      <tr>
        <td>${student.name}</td>
        <td>${student.stress_level}</td>
        <td>${student.sleep_hours}h</td>
        <td><span class="status-${getStatusLevel(student.stress_level, student.sleep_hours)}">${getStatusText(student.stress_level, student.sleep_hours)}</span></td>
      </tr>
    `).join('');
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
  if (stress >= 8 || sleep <= 4) return 'High Risk';
  if (stress >= 6 || sleep <= 6) return 'Medium Risk';
  return 'Low Risk';
}

// Weekly Report
function loadWeeklyReport() {
  const summaryDiv = document.getElementById('weekly-summary');
  if (summaryDiv) {
    const avgStress = (students.reduce((sum, s) => sum + s.stress_level, 0) / students.length).toFixed(1);
    const avgSleep = (students.reduce((sum, s) => sum + s.sleep_hours, 0) / students.length).toFixed(1);
    const highRiskCount = students.filter(s => s.stress_level >= 7 || s.sleep_hours <= 5).length;
    
    summaryDiv.innerHTML = `
      <p class="mb-2"><strong>Average Stress Level:</strong> ${avgStress}/10</p>
      <p class="mb-2"><strong>Average Sleep Hours:</strong> ${avgSleep} h</p>
      <p class="mb-0"><strong>Students at Risk:</strong> ${highRiskCount} students</p>
    `;
  }

  // Create stress level chart
  createStressChart();
  createSleepChart();
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
function createStressChart() {
  const stressData = students.map(s => s.stress_level);
  const segments = [
    stressData.filter(s => s <= 3).length,
    stressData.filter(s => s > 3 && s <= 6).length,
    stressData.filter(s => s > 6).length
  ];
  renderGlassPie('stress-chart', segments, ['#27ae60', '#f39c12', '#e74c3c'], ['Low (1-3)', 'Medium (4-6)', 'High (7-10)']);
}

function createSleepChart() {
  const sleepData = students.map(s => s.sleep_hours);
  const segments = [
    sleepData.filter(s => s <= 4).length,
    sleepData.filter(s => s > 4 && s <= 7).length,
    sleepData.filter(s => s > 7).length
  ];
  renderGlassPie('sleep-chart', segments, ['#e74c3c', '#f39c12', '#27ae60'], ['Poor (0-4h)', 'Average (5-7h)', 'Good (8+h)']);
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

  const tip = (function ensureTip(){
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
    const label = labels[i] || `Segment ${i+1}`;
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

  Plotly.newPlot('attendance-chart', data, layout, {responsive: true});
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

  Plotly.newPlot('grade-chart', data, layout, {responsive: true});
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
function generatePlot() {
  const xAxis = document.getElementById('x-axis-select').value;
  const yAxis = document.getElementById('y-axis-select').value;

  // Generate mock data based on selections
  const xData = generateMockData(xAxis, students.length);
  const yData = generateMockData(yAxis, students.length);

  const trace = {
    x: xData,
    y: yData,
    mode: 'markers',
    type: 'scatter',
    marker: {
      size: 12,
      color: xData.map((_, i) => i),
      colorscale: 'Viridis',
      showscale: true
    },
    text: students.map(s => s.name),
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

  Plotly.newPlot('plot-container', [trace], layout, {responsive: true});
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

  Plotly.newPlot('course-plot-container', [trace], layout, {responsive: true});
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

// Student table functions
function loadStudents() {
  students = [...mockStudents];
}

function loadCourses() {
  courses = [...mockCourses];
}

function renderStudentsTable() {
  const tbody = document.getElementById('student-tbody');
  if (tbody) {
    tbody.innerHTML = students.map(student => `
      <tr>
        <td>${student.name}</td>
        <td><span class="badge ${getStressLevelClass(student.stress_level)}">${student.stress_level}</span></td>
        <td>${parseFloat(student.sleep_hours) <= 5 ? `<span class="badge bg-danger">${student.sleep_hours}h</span>` : `${student.sleep_hours}h`}</td>
        <td>${student.grades ? student.grades.join(', ') : 'N/A'}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editStudent(${student.id})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteStudent(${student.id})">
            <i class="bi bi-trash"></i>
          </button>
          <button class="btn btn-sm btn-outline-warning me-1" onclick="toggleStar(${student.id})">
            <i class="bi ${student.starred ? 'bi-star-fill' : 'bi-star'}"></i>
          </button>
          <button class="btn btn-sm btn-outline-info" onclick="trackStudent(${student.id})">
            <i class="bi bi-graph-up"></i>
          </button>
        </td>
      </tr>
    `).join('');
  }
}

function filterStudents() {
  const searchTerm = document.getElementById('student-search')?.value.toLowerCase() || '';
  const stressFilter = document.getElementById('stress-filter')?.value;
  const sleepFilter = document.getElementById('sleep-filter')?.value;

  let filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm);
    
    let matchesStress = true;
    if (stressFilter) {
      const [min, max] = stressFilter.split('-').map(Number);
      matchesStress = student.stress_level >= min && student.stress_level <= max;
    }
    
    let matchesSleep = true;
    if (sleepFilter) {
      const [min, max] = sleepFilter.split('-').map(Number);
      matchesSleep = student.sleep_hours >= min && student.sleep_hours <= max;
    }
    
    return matchesSearch && matchesStress && matchesSleep;
  });

  renderFilteredStudents(filteredStudents);
}

function renderFilteredStudents(filteredStudents) {
  const tbody = document.getElementById('student-tbody');
  if (tbody) {
    tbody.innerHTML = filteredStudents.map(student => `
      <tr>
        <td>${student.name}</td>
        <td><span class="badge ${getStressLevelClass(student.stress_level)}">${student.stress_level}</span></td>
        <td>${parseFloat(student.sleep_hours) <= 5 ? `<span class="badge bg-danger">${student.sleep_hours}h</span>` : `${student.sleep_hours}h`}</td>
        <td>${student.grades ? student.grades.join(', ') : 'N/A'}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editStudent(${student.id})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteStudent(${student.id})">
            <i class="bi bi-trash"></i>
          </button>
          <button class="btn btn-sm btn-outline-warning me-1" onclick="toggleStar(${student.id})">
            <i class="bi ${student.starred ? 'bi-star-fill' : 'bi-star'}"></i>
          </button>
          <button class="btn btn-sm btn-outline-info" onclick="trackStudent(${student.id})">
            <i class="bi bi-graph-up"></i>
          </button>
        </td>
      </tr>
    `).join('');
  }
}

function sortTable(sortBy) {
  students.sort((a, b) => {
    if (sortBy === 'stress_level') {
      return a.stress_level - b.stress_level;
    } else if (sortBy === 'sleep_hours') {
      return a.sleep_hours - b.sleep_hours;
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

function editStudent(id) {
  const student = students.find(s => s.id === id);
  if (student) {
    const newName = prompt('Enter new name:', student.name);
    if (newName) {
      student.name = newName;
      renderStudentsTable();
    }
  }
}

function deleteStudent(id) {
  if (confirm('Are you sure you want to delete this student?')) {
    students = students.filter(s => s.id !== id);
    renderStudentsTable();
  }
}

function toggleStar(id) {
  const student = students.find(s => s.id === id);
  if (student) {
    student.starred = !student.starred;
    renderStudentsTable();
  }
}

function trackStudent(id) {
  const student = students.find(s => s.id === id);
  if (student) {
    alert(`Tracking ${student.name} - Stress: ${student.stress_level}, Sleep: ${student.sleep_hours}h`);
  }
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
    reader.onload = function(e) {
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
    reader.onload = function(e) {
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
    reader.onload = function(e) {
      alert(`${uploadType} data uploaded successfully!`);
      fileInput.value = '';
      loadCourseDashboard(); // Refresh data
    };
    reader.readAsText(file);
  }
}

function handleCourseFileChange(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
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
  const earlyWarningStudents = students.filter(student => student.stress_level >= 7 || student.sleep_hours <= 5);
  let csvContent = "Name,Status\n";
  earlyWarningStudents.forEach(student => {
    csvContent += `${student.name},${getStatusText(student.stress_level, student.sleep_hours)}\n`;
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
window.addEventListener('load', function() {
  // Add fade-in animation to cards
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add('fade-in');
    }, index * 100);
  });
});
