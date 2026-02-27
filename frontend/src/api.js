import axios from "axios";

const API = axios.create({ baseURL: "/", headers: { "Content-Type": "application/json" } });

API.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// Auth
export const register = (d) => API.post("/auth/register", d);
export const login = (d) => API.post("/auth/login", d);
export const getProfile = () => API.get("/auth/profile");
export const updateProfile = (d) => API.put("/auth/profile", d);

// Content
export const uploadText = (d) => API.post("/content/upload/text", d);
export const uploadUrl = (d) => API.post("/content/upload/url", d);
export const listContent = () => API.get("/content/list");
export const getContent = (id) => API.get(`/content/${id}`);
export const deleteContent = (id) => API.delete(`/content/${id}`);

// Quiz
export const generateQuiz = (d) => API.post("/quiz/generate", d);
export const submitQuiz = (d) => API.post("/quiz/submit", d);
export const quizHistory = () => API.get("/quiz/history");
export const getAttempt = (id) => API.get(`/quiz/attempt/${id}`);
export const getRecommendation = () => API.get("/quiz/recommend");

// Admin
export const adminStats = () => API.get("/admin/stats");
export const adminUsers = () => API.get("/admin/users");
export const adminQuestions = (flagged) => API.get(`/admin/questions?flagged=${flagged}`);
export const flagQuestion = (id) => API.post(`/admin/questions/${id}/flag`);
export const deleteQuestion = (id) => API.delete(`/admin/questions/${id}`);
export const submitFeedback = (d) => API.post("/admin/feedback", d);
