import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

export default function Login({ setToken, setUser }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const nav = useNavigate();

  const handle = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      const { data } = await login({ email, password });
      setToken(data.access_token);
      setUser(data.user);
      nav("/");
    } catch (err) {
      setMsg(err.response?.data?.msg || "Login failed");
    }
  };

  return (
    <div className="card">
      <h2>Login</h2>
      {msg && <div className="msg msg-error">{msg}</div>}
      <form onSubmit={handle}>
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button className="btn btn-primary" type="submit">Login</button>
      </form>
    </div>
  );
}
