const tokenKey = "school_api_token";
const state = {
  view: "dashboard",
  selected: null,
  editing: false,
  currentUser: null,
  loading: false,
  data: {
    students: [],
    teachers: [],
    classrooms: [],
    attendance: [],
    results: [],
    fees: [],
  },
};

const configs = {
  dashboard: { title: "Dashboard", list: "students" },
  students: {
    title: "Students",
    endpoint: "/students/",
    fields: [
      ["roll_no", "Roll No", "text"],
      ["name", "Name", "text"],
      ["email", "Email", "email"],
      ["phone", "Phone", "text"],
      ["address", "Address", "text"],
      ["father_name", "Father Name", "text"],
      ["mother_name", "Mother Name", "text"],
      ["classroom_id", "Classroom", "classroom"],
    ],
  },
  teachers: {
    title: "Teachers",
    endpoint: "/teachers/",
    fields: [
      ["employee_id", "Employee ID", "text"],
      ["name", "Name", "text"],
      ["email", "Email", "email"],
      ["phone", "Phone", "text"],
      ["subject", "Subject", "text"],
      ["salary", "Salary", "number"],
    ],
  },
  classrooms: {
    title: "Classrooms",
    endpoint: "/classrooms/",
    fields: [
      ["class_name", "Class Name", "text"],
      ["section", "Section", "text"],
    ],
  },
  attendance: {
    title: "Attendance",
    endpoint: "/attendance/",
    fields: [
      ["student_id", "Student", "student"],
      ["status", "Status", "select", ["present", "absent"]],
      ["date", "Date", "date"],
    ],
  },
  results: {
    title: "Results",
    endpoint: "/results/",
    fields: [
      ["student_roll_no", "Student", "studentRoll"],
      ["student_name", "Student Name", "text"],
      ["subject", "Subject", "text"],
      ["marks", "Marks", "number"],
      ["total_marks", "Total Marks", "number"],
      ["grade", "Grade", "text"],
    ],
  },
  fees: {
    title: "Fees",
    endpoint: "/fees/",
    fields: [
      ["student_id", "Student", "student"],
      ["amount", "Amount", "number"],
      ["status", "Status", "select", ["pending", "paid"]],
    ],
  },
  settings: { title: "Settings", list: "settings" },
};

const labels = {
  id: "ID",
  roll_no: "Roll No",
  employee_id: "Employee ID",
  name: "Name",
  email: "Email",
  phone: "Phone",
  address: "Address",
  father_name: "Father",
  mother_name: "Mother",
  classroom_id: "Classroom ID",
  class_name: "Class",
  section: "Section",
  total_students: "Total Students",
  subject: "Subject",
  salary: "Salary",
  student_id: "Student ID",
  status: "Status",
  date: "Date",
  amount: "Amount",
  student_name: "Student Name",
  student_class: "Class",
  student_roll_no: "Roll No",
  marks: "Marks",
  total_marks: "Total Marks",
  grade: "Grade",
};

const permissions = {
  admin: {
    create: ["students", "teachers", "classrooms", "attendance", "results", "fees"],
    edit: ["students", "teachers", "classrooms", "results", "fees"],
    delete: ["students", "teachers", "classrooms", "attendance", "results", "fees"],
  },
  teacher: {
    create: ["attendance"],
    edit: ["results"],
    delete: [],
  },
  student: {
    create: [],
    edit: [],
    delete: [],
  },
};

const today = new Date().toISOString().slice(0, 10);
const $ = (selector) => document.querySelector(selector);
const output = $("#output");

function token() {
  return localStorage.getItem(tokenKey) || "";
}

function currentRole() {
  return state.currentUser?.role || "";
}

function can(action, key) {
  return Boolean(permissions[currentRole()]?.[action]?.includes(key));
}

function canView(key) {
  if (["dashboard", "settings"].includes(key)) return true;
  if (!state.currentUser) return false;
  if (currentRole() === "admin") return ["students", "teachers", "classrooms", "attendance", "results", "fees"].includes(key);
  if (currentRole() === "teacher") return ["students", "teachers", "classrooms", "attendance", "results", "fees"].includes(key);
  if (currentRole() === "student") return ["students", "results"].includes(key);
  return false;
}

function setToken(value) {
  if (value) {
    localStorage.setItem(tokenKey, value);
  } else {
    localStorage.removeItem(tokenKey);
    state.currentUser = null;
  }
  updateAuthBanner();
}

function updateAuthBanner() {
  $("#authBanner").classList.toggle("hidden", Boolean(token()));
  $("#userBadge").textContent = state.currentUser
    ? `${state.currentUser.username} (${state.currentUser.role})`
    : "Guest";
}

function show(data, label = "Response") {
  output.textContent = `${label}\n\n${JSON.stringify(data, null, 2)}`;
}

function errorMessage(error) {
  try {
    const parsed = JSON.parse(error.message || error);
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail)) {
      return parsed.detail.map((item) => item.msg || item.message || JSON.stringify(item)).join("\n");
    }
    return parsed.message || JSON.stringify(parsed, null, 2);
  } catch {
    return error.message || String(error);
  }
}

function showError(error, label = "Error") {
  output.textContent = `${label}\n\n${errorMessage(error)}`;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (token()) {
    headers.set("Authorization", `Bearer ${token()}`);
  }
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    throw new Error(JSON.stringify(data, null, 2));
  }
  return data;
}

function formToObject(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const [key, value] of Object.entries(data)) {
    const field = form.elements[key];
    if (value === "") data[key] = null;
    if (field?.type === "number" && value !== "") data[key] = Number(value);
  }
  return data;
}

function selectedStudentById(id) {
  return state.data.students.find((student) => String(student.id) === String(id));
}

function selectedStudentByRoll(rollNo) {
  return state.data.students.find((student) => String(student.roll_no) === String(rollNo));
}

function preparePayload(key, payload) {
  if (key === "fees") {
    const student = selectedStudentById(payload.student_id);
    if (student) {
      payload.student_name = student.name;
      payload.student_class = student.class_name || String(student.classroom_id || "");
      payload.section = student.section || "";
    }
  }

  if (key === "results") {
    const student = selectedStudentByRoll(payload.student_roll_no);
    if (student) {
      payload.student_name = student.name;
    }
  }

  return payload;
}

function validatePayload(key, payload) {
  if (key === "results" && payload.marks != null && payload.total_marks != null && payload.marks > payload.total_marks) {
    return "Marks cannot be greater than total marks.";
  }

  if (key === "fees" && payload.amount <= 0) {
    return "Fee amount must be greater than 0.";
  }

  return "";
}

function currentListKey() {
  if (state.view === "dashboard") return "students";
  return state.view;
}

function titleFor(view = state.view) {
  return configs[view]?.title || "Dashboard";
}

function searchableValue(item) {
  return Object.values(item || {}).join(" ").toLowerCase();
}

function primaryName(item, key) {
  if (!item) return "No record selected";
  if (key === "classrooms") return `Class ${item.class_name || ""} ${item.section || ""}`.trim();
  if (key === "attendance") return `Student #${item.student_id || ""}`;
  if (key === "results") return item.student_name || `Result #${item.id}`;
  if (key === "fees") return item.student_name || `Fee #${item.id}`;
  return item.name || item.username || `Record #${item.id}`;
}

function secondaryText(item, key) {
  if (!item) return "";
  if (key === "students") return `${item.class_name || "Class"} ${item.section || ""} | Roll ${item.roll_no || "-"}`;
  if (key === "teachers") return `${item.subject || "Subject"} | ${item.employee_id || "-"}`;
  if (key === "classrooms") return `${item.total_students || 0} students`;
  if (key === "attendance") return `${item.status || "-"} | ${item.date || "-"}`;
  if (key === "results") return `${item.subject || "-"} | ${item.marks || 0}/${item.total_marks || 0}`;
  if (key === "fees") return `${item.status || "-"} | Rs. ${item.amount || 0}`;
  return `ID ${item.id || "-"}`;
}

function initials(text) {
  return String(text || "S").split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

function setView(view) {
  if (!canView(view)) {
    showError("You do not have access to this section.", "Access Denied");
    activateTab("raw");
    return;
  }
  state.view = view;
  state.editing = false;
  state.selected = null;
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
    if (btn.dataset.view) {
      btn.style.display = canView(btn.dataset.view) ? "" : "none";
    }
  });
  render();
}

function renderStats() {
  $("#studentCount").textContent = state.data.students.length;
  $("#teacherCount").textContent = state.data.teachers.length;
  $("#classroomCount").textContent = state.data.classrooms.length;
  $("#attendanceCount").textContent = state.data.attendance.length;
  $("#feeCount").textContent = state.data.fees.length;
}

function renderDashboard() {
  const classroomMap = new Map();

  state.data.students.forEach((student) => {
    const label = `Class ${student.class_name || student.classroom_id || "-"} ${student.section || ""}`.trim();
    if (!classroomMap.has(label)) {
      classroomMap.set(label, 0);
    }
    classroomMap.set(label, classroomMap.get(label) + 1);
  });

  state.data.classrooms.forEach((room) => {
    const label = `Class ${room.class_name || "-"} ${room.section || ""}`.trim();
    if (!classroomMap.has(label)) {
      classroomMap.set(label, Number(room.total_students) || 0);
    }
  });

  const activeClassCount = Array.from(classroomMap.values()).filter((count) => count > 0).length;
  const totals = [
    ["Students", state.data.students.length],
    ["Teachers", state.data.teachers.length],
    ["Classrooms", activeClassCount || state.data.classrooms.length],
    ["Attendance", state.data.attendance.length],
    ["Results", state.data.results.length],
    ["Fees", state.data.fees.length],
  ];
  const maxTotal = Math.max(...totals.map(([, value]) => value), 1);

  $("#activityChart").innerHTML = totals.map(([label, value]) => `
    <div class="bar-item">
      <span class="bar-value">${value}</span>
      <div class="bar-fill" style="height: ${Math.max((value / maxTotal) * 100, 8)}%"></div>
      <span class="bar-label">${label}</span>
    </div>
  `).join("");

  const present = state.data.attendance.filter((item) => String(item.status).toLowerCase() === "present").length;
  const absent = state.data.attendance.filter((item) => String(item.status).toLowerCase() === "absent").length;
  const attendanceTotal = present + absent;
  const presentPercent = attendanceTotal ? Math.round((present / attendanceTotal) * 100) : 0;
  $("#attendanceDonut").innerHTML = `
    <div>
      <div class="donut" style="--angle: ${presentPercent * 3.6}deg">
        <strong>${presentPercent}%</strong>
        <span>Present</span>
      </div>
      <p class="metric-note"><strong>${present}</strong> present / <strong>${absent}</strong> absent</p>
    </div>
  `;

  const scoredResults = state.data.results.filter((item) => Number(item.total_marks) > 0);
  const avgPercent = scoredResults.length
    ? Math.round(scoredResults.reduce((sum, item) => sum + (Number(item.marks) / Number(item.total_marks)) * 100, 0) / scoredResults.length)
    : 0;
  const subjectMap = new Map();
  scoredResults.forEach((item) => {
    const subject = item.subject || "Subject";
    const percent = Math.round((Number(item.marks) / Number(item.total_marks)) * 100);
    if (!subjectMap.has(subject)) subjectMap.set(subject, []);
    subjectMap.get(subject).push(percent);
  });
  const subjectRows = Array.from(subjectMap.entries()).map(([subject, values]) => {
    const avg = Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
    return [subject, avg];
  }).sort((a, b) => b[1] - a[1]).slice(0, 4);
  $("#marksGauge").innerHTML = `
    <div>
      <div class="gauge" style="--angle: ${avgPercent * 3.6}deg">
        <strong>${avgPercent}%</strong>
        <span>Average</span>
      </div>
      <div class="subject-chart">
        ${subjectRows.length ? subjectRows.map(([subject, avg]) => `
          <div class="class-row">
            <strong>${subject}</strong>
            <div class="class-bar"><span style="width: ${avg}%"></span></div>
            <span class="list-meta">${avg}%</span>
          </div>
        `).join("") : `<p class="metric-note">Add results to see subject performance.</p>`}
      </div>
    </div>
  `;

  const fallbackClassCounts = Array.from(classroomMap.entries())
    .sort((a, b) => b[1] - a[1]);
  const maxClass = Math.max(...fallbackClassCounts.map(([, count]) => count), 1);
  $("#classChart").innerHTML = fallbackClassCounts.length ? fallbackClassCounts.map(([label, count]) => `
    <div class="class-row">
      <strong>${label}</strong>
      <div class="class-bar"><span style="width: ${Math.max((count / maxClass) * 100, count ? 8 : 0)}%"></span></div>
      <span class="list-meta">${count}</span>
    </div>
  `).join("") : `<div class="empty-chart">Create students or classrooms to build this chart.</div>`;
}

function renderList() {
  const key = currentListKey();
  const list = Array.isArray(state.data[key]) ? state.data[key] : [];
  const query = ($("#listSearch").value || $("#globalSearch").value || "").toLowerCase();
  const filtered = list.filter((item) => searchableValue(item).includes(query));
  const body = $("#listBody");

  $("#listEyebrow").textContent = key === "settings" ? "Account" : key === "classrooms" ? "Classrooms" : "Directory";
  $("#listTitle").textContent = titleFor(key);

  if (key === "settings") {
    body.innerHTML = state.currentUser
      ? `<article class="list-item active"><span class="mini-avatar">${initials(state.currentUser.username)}</span><div class="list-main"><strong>${state.currentUser.username}</strong><span>${state.currentUser.email || "-"} | ${state.currentUser.role}</span></div></article>`
      : `<p class="list-meta">Login to view account details.</p>`;
    return;
  }

  body.innerHTML = filtered.map((item) => {
    const active = state.selected?.id === item.id ? "active" : "";
    const name = primaryName(item, key);
    return `
      <article class="list-item ${active}" data-id="${item.id}">
        <span class="mini-avatar">${initials(name)}</span>
        <div class="list-main">
          <strong>${name}</strong>
          <span>${secondaryText(item, key)}</span>
        </div>
        <span class="list-meta">#${item.id || "-"}</span>
      </article>
    `;
  }).join("") || `<p class="list-meta">No records found.</p>`;

  body.querySelectorAll(".list-item").forEach((item) => {
    item.addEventListener("click", () => {
      state.selected = list.find((record) => String(record.id) === item.dataset.id);
      state.editing = false;
      render();
    });
  });

  if (!state.selected && filtered[0]) {
    state.selected = filtered[0];
  }
}

function renderDetails() {
  const key = currentListKey();
  const item = key === "settings" ? state.currentUser : state.selected;
  const name = primaryName(item, key);

  $("#heroAvatar").textContent = initials(name);
  $("#heroName").textContent = name;
  $("#heroMeta").textContent = item ? secondaryText(item, key) : "Select a record from the list.";
  $("#detailTitle").textContent = `${titleFor(key)} Details`;

  const editable = item && can("edit", key);
  const deletable = item && can("delete", key);
  $("#editBtn").style.display = item && editable ? "" : "none";
  $("#deleteBtn").style.display = item && deletable ? "" : "none";

  if (!item) {
    $("#detailBody").innerHTML = `<div class="detail-field"><span>Status</span><strong>No data loaded</strong></div>`;
    return;
  }

  const entries = Object.entries(item).filter(([field]) => field !== "students");
  $("#detailBody").innerHTML = entries.map(([field, value]) => `
    <div class="detail-field">
      <span>${labels[field] || field}</span>
      <strong>${value ?? "-"}</strong>
    </div>
  `).join("");
}

function renderOverview() {
  const student = state.data.students[0];
  const latestAttendance = state.data.attendance[0];
  const latestResult = state.data.results[0];
  const cards = [
    ["Selected", state.selected ? primaryName(state.selected, currentListKey()) : "None"],
    ["Latest Student", student ? primaryName(student, "students") : "No students"],
    ["Latest Attendance", latestAttendance ? secondaryText(latestAttendance, "attendance") : "No attendance"],
    ["Latest Result", latestResult ? secondaryText(latestResult, "results") : "No results"],
    ["Auth", state.currentUser ? `${state.currentUser.username} (${state.currentUser.role})` : "Login required"],
  ];
  $("#overviewBody").innerHTML = cards.map(([label, value]) => `
    <article class="overview-card">
      <span>${label}</span>
      <strong>${value}</strong>
    </article>
  `).join("");
}

function renderForm() {
  const key = currentListKey();
  const config = configs[key];
  const canEdit = state.editing && state.selected && can("edit", key);
  const canCreate = can("create", key);
  const source = canEdit ? state.selected : {};

  if (!canEdit && !canCreate) {
    $("#recordForm").innerHTML = `<p class="list-meta">You have read-only access here.</p>`;
    return;
  }

  if (!config?.fields) {
    $("#recordForm").innerHTML = `<p class="list-meta">No form available for this view.</p>`;
    return;
  }

  $("#recordForm").innerHTML = config.fields.map(([name, label, type, options]) => {
    const value = source[name] ?? (name === "date" ? today : "");
    if (type === "classroom") {
      return `
        <label>
          <span class="list-meta">${label}</span>
          <select name="${name}" required>
            <option value="">Select classroom</option>
            ${state.data.classrooms.map((room) => `<option value="${room.id}" ${String(value) === String(room.id) ? "selected" : ""}>Class ${room.class_name} ${room.section}</option>`).join("")}
          </select>
        </label>
      `;
    }
    if (type === "student") {
      return `
        <label>
          <span class="list-meta">${label}</span>
          <select name="${name}" required>
            <option value="">Select student</option>
            ${state.data.students.map((student) => `<option value="${student.id}" ${String(value) === String(student.id) ? "selected" : ""}>${student.name} | Roll ${student.roll_no}</option>`).join("")}
          </select>
        </label>
      `;
    }
    if (type === "studentRoll") {
      return `
        <label>
          <span class="list-meta">${label}</span>
          <select name="${name}" required>
            <option value="">Select student</option>
            ${state.data.students.map((student) => `<option value="${student.roll_no}" ${String(value) === String(student.roll_no) ? "selected" : ""}>${student.name} | Roll ${student.roll_no}</option>`).join("")}
          </select>
        </label>
      `;
    }
    if (type === "select") {
      return `
        <label>
          <span class="list-meta">${label}</span>
          <select name="${name}">
            ${options.map((option) => `<option value="${option}" ${value === option ? "selected" : ""}>${option}</option>`).join("")}
          </select>
        </label>
      `;
    }
    return `
      <label>
        <span class="list-meta">${label}</span>
        <input name="${name}" type="${type}" value="${value ?? ""}" placeholder="${label}" ${name === "student_name" && key === "results" ? "readonly" : ""}>
      </label>
    `;
  }).join("") + `
    <div class="form-actions">
      <button type="submit">${canEdit ? "Update" : "Create"} ${titleFor(key)}</button>
      <button id="cancelEditBtn" type="button">Cancel</button>
    </div>
  `;

  $("#cancelEditBtn").addEventListener("click", () => {
    state.editing = false;
    activateTab("overview");
    renderForm();
  });
}

function render() {
  $("#pageTitle").textContent = titleFor();
  document.querySelectorAll(".nav-btn[data-view]").forEach((btn) => {
    btn.style.display = canView(btn.dataset.view) ? "" : "none";
    btn.classList.toggle("active", btn.dataset.view === state.view);
  });
  renderStats();
  renderDashboard();
  const isDashboard = state.view === "dashboard";
  $("#dashboardPanel").classList.toggle("hidden", !isDashboard);
  $("#recordPanel").classList.toggle("hidden", isDashboard);
  $("#newRecordBtn").style.display = !isDashboard && can("create", currentListKey()) ? "" : "none";
  $("#refreshBtn").disabled = state.loading;
  $("#refreshBtn").textContent = state.loading ? "Loading..." : "Refresh";
  if (!isDashboard) {
    renderList();
    renderDetails();
    renderOverview();
    renderForm();
  }
  updateAuthBanner();
}

function activateTab(tab) {
  document.querySelectorAll(".tab").forEach((btn) => btn.classList.toggle("active", btn.dataset.tab === tab));
  document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
  $(`#${tab}Tab`).classList.add("active");
}

async function loadAll() {
  const status = $("#apiStatus");
  state.loading = true;
  render();
  try {
    await api("/api/status");
    status.textContent = "API Online";
    status.className = "status-pill ok";
  } catch {
    status.textContent = "API Offline";
    status.className = "status-pill bad";
  }

  if (!token()) {
    state.loading = false;
    render();
    return;
  }

  try {
    state.currentUser = await api("/auth/me");
  } catch (error) {
    setToken("");
    state.loading = false;
    showError(error, "Session Expired");
    render();
    return;
  }

  for (const key of Object.keys(state.data)) {
    const endpoint = configs[key]?.endpoint;
    if (!canView(key)) {
      state.data[key] = [];
      continue;
    }
    if (!endpoint) continue;
    try {
      const data = await api(endpoint);
      state.data[key] = Array.isArray(data) ? data : [];
    } catch (error) {
      state.data[key] = [];
      if (![401, 403].some((code) => error.message?.includes(String(code)))) {
        showError(error, `Load ${titleFor(key)} Failed`);
      }
    }
  }
  state.loading = false;
  render();
}

async function saveRecord(event) {
  event.preventDefault();
  const key = currentListKey();
  const config = configs[key];
  const payload = preparePayload(key, formToObject(event.currentTarget));
  const validationError = validatePayload(key, payload);
  if (validationError) {
    showError(validationError, `Save ${titleFor(key)} Failed`);
    activateTab("raw");
    return;
  }

  const isUpdate = state.editing && state.selected && can("edit", key);
  if (!isUpdate && !can("create", key)) {
    showError("You do not have permission for this action.", "Access Denied");
    activateTab("raw");
    return;
  }

  const url = isUpdate ? `${config.endpoint}${state.selected.id}` : config.endpoint;

  try {
    state.loading = true;
    render();
    const data = await api(url, {
      method: isUpdate ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    show(data, `${isUpdate ? "Updated" : "Created"} ${titleFor(key)}`);
    state.editing = false;
    await loadAll();
    state.selected = data?.id ? state.data[key].find((item) => item.id === data.id) || data : state.selected;
    activateTab("overview");
    render();
  } catch (error) {
    state.loading = false;
    showError(error, `Save ${titleFor(key)} Failed`);
    activateTab("raw");
    render();
  }
}

async function deleteSelected() {
  const key = currentListKey();
  if (!state.selected) return;
  if (!can("delete", key)) {
    showError("You do not have permission for this action.", "Access Denied");
    activateTab("raw");
    return;
  }

  if (!confirm(`Delete ${primaryName(state.selected, key)}?`)) return;

  try {
    state.loading = true;
    render();
    const data = await api(`${configs[key].endpoint}${state.selected.id}`, { method: "DELETE" });
    show(data, `Deleted ${titleFor(key)}`);
    state.selected = null;
    await loadAll();
  } catch (error) {
    state.loading = false;
    showError(error, `Delete ${titleFor(key)} Failed`);
    activateTab("raw");
    render();
  }
}

$("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = formToObject(event.currentTarget);
  try {
    state.loading = true;
    render();
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    });
    setToken(data.access_token);
    show(data, "Logged In");
    await loadAll();
  } catch (error) {
    state.loading = false;
    showError(error, "Login Failed");
    render();
  }
});

$("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    state.loading = true;
    render();
    const data = await api("/auth/register", {
      method: "POST",
      body: JSON.stringify(formToObject(event.currentTarget)),
    });
    show(data, "Registered User");
  } catch (error) {
    showError(error, "Register Failed");
  } finally {
    state.loading = false;
    render();
  }
});

$("#logoutBtn").addEventListener("click", () => {
  setToken("");
  state.view = "dashboard";
  state.selected = null;
  for (const key of Object.keys(state.data)) state.data[key] = [];
  show({ message: "Logged out locally" }, "Logout");
  render();
});

$("#refreshBtn").addEventListener("click", loadAll);
$("#newRecordBtn").addEventListener("click", () => {
  state.editing = false;
  activateTab("form");
  renderForm();
});
$("#editBtn").addEventListener("click", () => {
  state.editing = true;
  activateTab("form");
  renderForm();
});
$("#deleteBtn").addEventListener("click", deleteSelected);
$("#recordForm").addEventListener("submit", saveRecord);
$("#globalSearch").addEventListener("input", renderList);
$("#listSearch").addEventListener("input", renderList);

document.querySelectorAll(".nav-btn[data-view]").forEach((btn) => {
  btn.addEventListener("click", () => setView(btn.dataset.view));
});

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => activateTab(btn.dataset.tab));
});

loadAll();
