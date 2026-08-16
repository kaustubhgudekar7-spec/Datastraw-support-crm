const API_BASE = "/api/tickets";
const TOKEN_KEY = "datastraw_crm_token";
const AGENT_KEY = "datastraw_crm_agent";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(token, agent) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(AGENT_KEY, JSON.stringify(agent));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(AGENT_KEY);
}

function getCurrentAgent() {
  const raw = localStorage.getItem(AGENT_KEY);
  return raw ? JSON.parse(raw) : null;
}

function logout() {
  clearSession();
  window.location.href = "/login";
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/login";
  }
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleAuthResponse(res) {
  if (res.status === 401) {
    clearSession();
    window.location.href = "/login";
    throw new Error("Not authenticated");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ? JSON.stringify(err.detail) : `Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiGet(url) {
  const res = await fetch(url, { headers: { ...authHeaders() } });
  return handleAuthResponse(res);
}

async function apiPost(url, body, skipAuth = false) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(skipAuth ? {} : authHeaders()) },
    body: JSON.stringify(body),
  });
  return handleAuthResponse(res);
}

async function apiPut(url, body) {
  const res = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handleAuthResponse(res);
}
function statusBadgeClass(status) {
  switch (status) {
    case "Open":
      return "bg-blue-100 text-blue-700 border border-blue-200";
    case "In Progress":
      return "bg-amber-100 text-amber-700 border border-amber-200";
    case "Closed":
      return "bg-emerald-100 text-emerald-700 border border-emerald-200";
    default:
      return "bg-gray-100 text-gray-700 border border-gray-200";
  }
}

function priorityBadgeClass(priority) {
  switch (priority) {
    case "Urgent":
      return "bg-red-100 text-red-700 border border-red-200";
    case "High":
      return "bg-orange-100 text-orange-700 border border-orange-200";
    case "Medium":
      return "bg-sky-100 text-sky-700 border border-sky-200";
    case "Low":
      return "bg-gray-100 text-gray-600 border border-gray-200";
    default:
      return "bg-gray-100 text-gray-600 border border-gray-200";
  }
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}
