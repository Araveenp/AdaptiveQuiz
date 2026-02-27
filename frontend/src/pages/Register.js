import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register, login } from "../api";

export default function Register({ setToken, setUser }) {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [msg, setMsg] = useState("");
  const nav = useNavigate();

  const handle = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      await register(form);
      const { data } = await login({ email: form.email, password: form.password });
      setToken(data.access_token);
      setUser(data.user);
      nav("/profile");
    } catch (err) {
      setMsg(err.response?.data?.msg || "Registration failed");
    }
  };

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="card">
      <h2>Create Your Account</h2>
      <p style={{ color: "#555", marginBottom: 16 }}>Sign up to get started. You can set your difficulty and subjects after logging in.</p>
      {msg && <div className="msg msg-error">{msg}</div>}
      <form onSubmit={handle}>
        <label style={{ fontWeight: 600, fontSize: 14 }}>Full Name</label>
        <input placeholder="e.g. John Doe" value={form.name} onChange={upd("name")} required />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Email</label>
        <input placeholder="e.g. john@example.com" type="email" value={form.email} onChange={upd("email")} required />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Password</label>
        <input placeholder="Min 6 characters" type="password" value={form.password} onChange={upd("password")} required />

        <button className="btn btn-primary" type="submit" style={{ marginTop: 8 }}>Create Account</button>
      </form>
    </div>
  );
}
