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
      <h2>Register</h2>
      {msg && <div className="msg msg-error">{msg}</div>}
      <form onSubmit={handle}>
        <input placeholder="Name" value={form.name} onChange={upd("name")} required />
        <input placeholder="Email" value={form.email} onChange={upd("email")} required />
        <input placeholder="Password" type="password" value={form.password} onChange={upd("password")} required />
        <select value={form.preferred_difficulty} onChange={upd("preferred_difficulty")}>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <input placeholder="Subjects (comma separated)" value={form.subjects} onChange={upd("subjects")} />
        <button className="btn btn-primary" type="submit">Register</button>
      </form>
    </div>
  );
}
