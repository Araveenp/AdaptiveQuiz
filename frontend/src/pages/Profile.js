import React, { useState, useEffect } from "react";
import { getProfile, updateProfile } from "../api";

export default function Profile({ user, setUser }) {
  const [form, setForm] = useState({ name: "", preferred_difficulty: "medium", subjects: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    getProfile().then(({ data }) => {
      const u = data.user;
      setForm({ name: u.name || "", preferred_difficulty: u.preferred_difficulty, subjects: (u.subjects || []).join(", ") });
      setUser(u);
    }).catch(() => {});
  }, [setUser]);

  const save = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...form, subjects: form.subjects.split(",").map(s => s.trim()).filter(Boolean) };
      const { data } = await updateProfile(payload);
      setUser(data.user);
      setMsg("Profile updated!");
    } catch (err) {
      setMsg(err.response?.data?.msg || "Update failed");
    }
  };

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="card">
      <h2>My Profile</h2>
      {msg && <div className="msg msg-success">{msg}</div>}
      <form onSubmit={save}>
        <label>Name</label>
        <input value={form.name} onChange={upd("name")} />
        <label>Preferred Difficulty</label>
        <select value={form.preferred_difficulty} onChange={upd("preferred_difficulty")}>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <label>Subjects (comma separated)</label>
        <input value={form.subjects} onChange={upd("subjects")} />
        <button className="btn btn-primary" type="submit">Save</button>
      </form>
    </div>
  );
}
