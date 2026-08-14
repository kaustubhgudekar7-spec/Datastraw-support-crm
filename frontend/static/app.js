const API_BASE = "/api/tickets";

async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ? JSON.stringify(err.detail) : `Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiPut(url, body) {
  const res = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ? JSON.stringify(err.detail) : `Request failed: ${res.status}`);
  }
  return res.json();
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
