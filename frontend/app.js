const tokenKey = "school_api_token";
const tokenBox = document.querySelector("#tokenBox");
const output = document.querySelector("#output");
const apiStatus = document.querySelector("#apiStatus");
const apiStatusText = document.querySelector("#apiStatusText");

const today = new Date().toISOString().slice(0, 10);
document.querySelector('input[name="date"]').value = today;
tokenBox.value = localStorage.getItem(tokenKey) || "";

function show(data, label = "Response") {
  output.textContent = `${label}\n\n${JSON.stringify(data, null, 2)}`;
}

function showError(error, label = "Error") {
  output.textContent = `${label}\n\n${error.message || error}`;
}

function saveToken(token) {
  localStorage.setItem(tokenKey, token);
  tokenBox.value = token;
}

function getToken() {
  const token = tokenBox.value.trim();
  if (token) {
    localStorage.setItem(tokenKey, token);
  }
  return token;
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
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

function formDataToObject(form) {
  const data = Object.fromEntries(new FormData(form).entries());

  for (const [key, value] of Object.entries(data)) {
    const field = form.elements[key];
    if (field?.type === "number") {
      data[key] = Number(value);
    }
    if (value === "") {
      data[key] = null;
    }
  }

  return data;
}

async function handleJsonForm(formId, path, label) {
  const form = document.querySelector(formId);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await request(path, {
        method: "POST",
        body: JSON.stringify(formDataToObject(form)),
      });
      show(data, label);
    } catch (error) {
      showError(error, label);
    }
  });
}

async function checkApi() {
  try {
    const data = await request("/api/status");
    apiStatus.className = "dot ok";
    apiStatusText.textContent = data.message || "API online";
  } catch {
    apiStatus.className = "dot bad";
    apiStatusText.textContent = "API offline";
  }
}

document.querySelector("#registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  try {
    const data = await request("/auth/register", {
      method: "POST",
      body: JSON.stringify(formDataToObject(form)),
    });
    show(data, "Registered User");
  } catch (error) {
    showError(error, "Register Failed");
  }
});

document.querySelector("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const body = new URLSearchParams(new FormData(form));

  try {
    const data = await request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    saveToken(data.access_token);
    show(data, "Logged In");
  } catch (error) {
    showError(error, "Login Failed");
  }
});

document.querySelector("#meBtn").addEventListener("click", async () => {
  try {
    show(await request("/auth/me"), "Current User");
  } catch (error) {
    showError(error, "Get Me Failed");
  }
});

document.querySelector("#clearTokenBtn").addEventListener("click", () => {
  localStorage.removeItem(tokenKey);
  tokenBox.value = "";
  show({ message: "Token cleared" }, "Token");
});

document.querySelector("#clearOutputBtn").addEventListener("click", () => {
  output.textContent = "Ready.";
});

document.querySelectorAll("[data-get]").forEach((button) => {
  button.addEventListener("click", async () => {
    const path = button.dataset.get;
    try {
      show(await request(path), `GET ${path}`);
    } catch (error) {
      showError(error, `GET ${path} Failed`);
    }
  });
});

document.querySelector("#refreshAllBtn").addEventListener("click", async () => {
  const paths = ["/classrooms/", "/students/", "/teachers/", "/attendance/", "/fees/", "/results/"];
  const results = {};

  for (const path of paths) {
    try {
      results[path] = await request(path);
    } catch (error) {
      results[path] = error.message;
    }
  }

  show(results, "All Lists");
});

handleJsonForm("#classroomForm", "/classrooms/", "Classroom Created");
handleJsonForm("#studentForm", "/students/", "Student Created");
handleJsonForm("#teacherForm", "/teachers/", "Teacher Created");
handleJsonForm("#attendanceForm", "/attendance/", "Attendance Marked");
handleJsonForm("#feeForm", "/fees/", "Fee Added");
handleJsonForm("#resultForm", "/results/", "Result Added");

checkApi();
