import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000", // FastAPI backend
});

// Attach token if available
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---- AUTH ENDPOINTS ----
export const signup = async (formData) => {
  const res = await API.post("/auth/signup", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const login = async (email, password) => {
  const form = new URLSearchParams();
  form.append("username", email); // FastAPI OAuth2 expects "username"
  form.append("password", password);

  const res = await API.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  // Save token
  localStorage.setItem("token", res.data.access_token);
  return res.data;
};

export const getMe = async () => {
  const res = await API.get("/auth/me");
  return res.data;
};

export const updateProfile = async (formData) => {
  const res = await API.put("/auth/me", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const deleteAccount = async () => {
  await API.delete("/auth/me");
  localStorage.removeItem("token");
};
