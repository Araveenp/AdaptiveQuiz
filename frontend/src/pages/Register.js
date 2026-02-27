import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register, login } from "../api";

export default function Register({ setToken, setUser }) {
  const [form, setForm] = useState({ name: "", email: "", password: "", preferred_difficulty: "medium", subjects: "" });
  const [msg, setMsg] = useState("");
  const nav = useNavigate();

  const handle = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      const payload = { ...form, subjects: form.subjects.split(",").map(s => s.trim()).filter(Boolean) };
      await register(payload);
      const { data } = await login({ email: form.email, password: form.password });
      setToken(data.access_token);
      setUser(data.user);
      nav("/");
    } catch (err) {
      setMsg(err.response?.data?.msg || "Registration failed");
    }
  };

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="card">
      <h2>Create Your Account</h2>
      <p style={{ color: "#555", marginBottom: 16 }}>Set up your profile so we can personalize your quiz experience.</p>
      {msg && <div className="msg msg-error">{msg}</div>}
      <form onSubmit={handle}>
        <label style={{ fontWeight: 600, fontSize: 14 }}>Full Name</label>
        <input placeholder="e.g. John Doe" value={form.name} onChange={upd("name")} required />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Email</label>
        <input placeholder="e.g. john@example.com" type="email" value={form.email} onChange={upd("email")} required />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Password</label>
        <input placeholder="Min 6 characters" type="password" value={form.password} onChange={upd("password")} required />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Starting Difficulty Level</label>
        <p style={{ fontSize: 12, color: "#777", marginBottom: 6, marginTop: -8 }}>
          This sets your initial quiz difficulty. The system will <strong>auto-adjust</strong> based on your performance.
        </p>
        <select value={form.preferred_difficulty} onChange={upd("preferred_difficulty")}>
          <option value="easy">🟢 Easy — I'm just getting started</option>
          <option value="medium">🟡 Medium — I have some knowledge</option>
          <option value="hard">🔴 Hard — Challenge me!</option>
        </select>

        <label style={{ fontWeight: 600, fontSize: 14 }}>Subjects of Interest</label>
        <p style={{ fontSize: 12, color: "#777", marginBottom: 6, marginTop: -8 }}>
          Add topics you want to study. Separate with commas.
        </p>
        <input placeholder="e.g. Machine Learning, Biology, History" value={form.subjects} onChange={upd("subjects")} />

        <button className="btn btn-primary" type="submit" style={{ marginTop: 8 }}>Create Account</button>
      </form>
    </div>
  );
}
