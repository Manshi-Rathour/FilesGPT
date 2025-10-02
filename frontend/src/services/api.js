import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000",
  withCredentials: true, // ✅ important for CORS + auth
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
  const res = await API.get("/auth/me", { withCredentials: true });
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

// ---------- PDF Upload ----------
export const uploadPDF = async (file, url, userId) => {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (url) formData.append("url", url);
  if (userId) formData.append("user_id", userId);

  const res = await API.post("/pdf/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// ---------- Query PDF ----------
export const queryPDF = async (question, topK = 5) => {
  const res = await API.post("/query/", { question, top_k: topK });
  return res.data;
};

// ---------- Fetch User History ----------
export const fetchHistory = async (userId) => {
  const res = await API.get(`/history/${userId}`, { withCredentials: true });
  return res.data;
};

