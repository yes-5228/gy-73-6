const API_BASE = import.meta.env.VITE_API_BASE || "/api";

function buildQueryString(params) {
  if (!params) return "";
  const entries = Object.entries(params).filter(
    ([, value]) => value !== undefined && value !== null && value !== ""
  );
  if (entries.length === 0) return "";
  return "?" + entries.map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join("&");
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || "请求失败");
  }
  return body;
}

export const api = {
  health: () => request("/health/"),
  listOrders: (filters) => request(`/orders/${buildQueryString(filters)}`),
  exportOrders: (filters) => `${API_BASE}/orders/export/${buildQueryString(filters)}`,
  createOrder: (payload) => request("/orders/", { method: "POST", body: JSON.stringify(payload) }),
  claimOrder: (orderId, workerId) =>
    request(`/orders/${orderId}/claim/`, { method: "POST", body: JSON.stringify({ worker_id: workerId }) }),
  assignOrder: (orderId, workerId) =>
    request(`/orders/${orderId}/assign/`, { method: "POST", body: JSON.stringify({ worker_id: workerId }) }),
  addProgress: (orderId, payload) =>
    request(`/tracking/orders/${orderId}/events/`, { method: "POST", body: JSON.stringify(payload) }),
  createReview: (orderId, payload) =>
    request(`/reviews/orders/${orderId}/`, { method: "POST", body: JSON.stringify(payload) }),
  listWorkers: () => request("/workers/"),
  createWorker: (payload) => request("/workers/", { method: "POST", body: JSON.stringify(payload) }),
};
