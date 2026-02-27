import React, { useEffect, useState } from "react";
import { adminStats, adminUsers, adminQuestions, deleteQuestion } from "../api";

export default function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [showFlagged, setShowFlagged] = useState(false);
  const [tab, setTab] = useState("stats");

  useEffect(() => {
    adminStats().then(({ data }) => setStats(data)).catch(() => setStats({ error: true }));
    adminUsers().then(({ data }) => setUsers(data.users)).catch(() => {});
  }, []);

  useEffect(() => {
    adminQuestions(showFlagged).then(({ data }) => setQuestions(data.questions)).catch(() => {});
  }, [showFlagged]);

  const removeQ = async (id) => {
    if (!window.confirm("Delete this question?")) return;
    await deleteQuestion(id);
    setQuestions(prev => prev.filter(q => q.id !== id));
  };

  if (stats?.error) return <div className="card"><h2>Access Denied</h2><p>Admin privileges required.</p></div>;

  return (
    <div className="card">
      <h2>Admin Dashboard</h2>
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <button className={`btn ${tab === "stats" ? "btn-primary" : ""}`} onClick={() => setTab("stats")}>Stats</button>
        <button className={`btn ${tab === "users" ? "btn-primary" : ""}`} onClick={() => setTab("users")}>Users</button>
        <button className={`btn ${tab === "questions" ? "btn-primary" : ""}`} onClick={() => setTab("questions")}>Questions</button>
      </div>

      {tab === "stats" && stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
          {Object.entries(stats).map(([k, v]) => (
            <div key={k} style={{ background: "#f8f9fa", padding: 16, borderRadius: 8, textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: "#4361ee" }}>{v}</div>
              <div style={{ fontSize: 13, color: "#555" }}>{k.replace(/_/g, " ")}</div>
            </div>
          ))}
        </div>
      )}

      {tab === "users" && (
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Difficulty</th><th>Admin</th><th>Joined</th></tr></thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td><span className={`badge badge-${u.preferred_difficulty}`}>{u.preferred_difficulty}</span></td>
                <td>{u.is_admin ? "✅" : ""}</td>
                <td>{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === "questions" && (
        <>
          <label style={{ marginBottom: 12, display: "block" }}>
            <input type="checkbox" checked={showFlagged} onChange={() => setShowFlagged(!showFlagged)} /> Show flagged only
          </label>
          <table>
            <thead><tr><th>ID</th><th>Type</th><th>Difficulty</th><th>Question</th><th>Answer</th><th></th></tr></thead>
            <tbody>
              {questions.map(q => (
                <tr key={q.id} style={q.is_flagged ? { background: "#fff3cd" } : {}}>
                  <td>{q.id}</td>
                  <td>{q.question_type}</td>
                  <td><span className={`badge badge-${q.difficulty}`}>{q.difficulty}</span></td>
                  <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis" }}>{q.question_text}</td>
                  <td>{q.correct_answer}</td>
                  <td><button className="btn btn-danger btn-sm" onClick={() => removeQ(q.id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
