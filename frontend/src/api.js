// Central API client. Every request automatically carries the login token.
import axios from "axios";

const baseURL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "") + "/api";

const api = axios.create({ baseURL, timeout: 60000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// If the token expired, log the user out
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && localStorage.getItem("token")) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (!window.location.pathname.startsWith("/login")) window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const errorMessage = (err) =>
  err?.response?.data?.error ||
  (err?.code === "ECONNABORTED" ? "The server is waking up. Please try again in a moment." : "Network error. Please try again.");

export const fieldErrors = (err) => err?.response?.data?.fields || {};

// Open a protected attachment (needs the token, so we fetch it as a blob)
export async function openAttachment(id) {
  const res = await api.get(`/grievances/attachments/${id}`, { responseType: "blob" });
  const url = URL.createObjectURL(res.data);
  window.open(url, "_blank", "noopener");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

export default api;
