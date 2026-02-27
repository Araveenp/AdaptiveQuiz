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
      <p style={{ color: "#555", marginBottom: 16 }}>Personalize your quiz experience below.</p>
      {msg && <div className="msg msg-success">{msg}</div>}
      <form onSubmit={save}>
        <label style={{ fontWeight: 600, fontSize: 14 }}>Full Name</label>
        <input placeholder="e.g. John Doe" value={form.name} onChange={upd("name")} />

        <label style={{ fontWeight: 600, fontSize: 14 }}>Preferred Difficulty Level</label>
        <p style={{ fontSize: 12, color: "#777", marginBottom: 6, marginTop: -8 }}>
          This sets your quiz difficulty. The system will <strong>auto-adjust</strong> based on your performance.
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

        <button className="btn btn-primary" type="submit" style={{ marginTop: 8 }}>Save Changes</button>
      </form>
    </div>
  );
}
