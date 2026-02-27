import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { listContent, generateQuiz, getRecommendation } from "../api";

export default function QuizSetup() {
  const [contents, setContents] = useState([]);
  const [contentId, setContentId] = useState("");
  const [difficulty, setDifficulty] = useState("auto");
  const [numQ, setNumQ] = useState(10);
  const [types, setTypes] = useState(["mcq", "fill_blank", "true_false", "short_answer"]);
  const [rec, setRec] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const nav = useNavigate();

  useEffect(() => {
    listContent().then(({ data }) => setContents(data.contents)).catch(() => {});
    getRecommendation().then(({ data }) => setRec(data)).catch(() => {});
  }, []);

  const toggleType = (t) => {
    setTypes(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]);
  };

  const start = async (e) => {
    e.preventDefault();
    if (!contentId) { setErr("Select content first"); return; }
    setLoading(true); setErr("");
    try {
      const { data } = await generateQuiz({ content_id: parseInt(contentId), num_questions: numQ, difficulty, types });
      nav("/quiz/play", { state: { questions: data.questions, attemptId: data.attempt_id, difficulty: data.difficulty } });
    } catch (error) {
      setErr(error.response?.data?.msg || "Failed to generate quiz");
    } finally { setLoading(false); }
  };

  return (
    <div className="card">
      <h2>Start a Quiz</h2>
      {rec && (
        <div className="msg msg-success">
          📊 Recommended difficulty: <strong>{rec.recommended_difficulty}</strong> |
          Recent avg: {rec.recent_average_score}% |
          Total quizzes: {rec.total_quizzes_taken}
        </div>
      )}
      {err && <div className="msg msg-error">{err}</div>}
      <form onSubmit={start}>
        <label>Select Content</label>
        <select value={contentId} onChange={e => setContentId(e.target.value)} required>
          <option value="">-- Choose content --</option>
          {contents.map(c => <option key={c.id} value={c.id}>{c.title} ({c.chunk_count} chunks)</option>)}
        </select>

        <label>Difficulty</label>
        <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
          <option value="auto">Auto (adaptive)</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>

        <label>Number of Questions</label>
        <input type="number" min={1} max={50} value={numQ} onChange={e => setNumQ(parseInt(e.target.value) || 5)} />

        <label>Question Types</label>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 12 }}>
          {["mcq", "fill_blank", "true_false", "short_answer"].map(t => (
            <label key={t} style={{ cursor: "pointer" }}>
              <input type="checkbox" checked={types.includes(t)} onChange={() => toggleType(t)} /> {t.replace("_", " ")}
            </label>
          ))}
        </div>

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Quiz"}
        </button>
      </form>
    </div>
  );
}
