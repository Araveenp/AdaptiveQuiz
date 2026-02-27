import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { submitQuiz, flagQuestion, submitFeedback } from "../api";

export default function QuizPlay() {
  const { state } = useLocation();
  const nav = useNavigate();
  const questions = state?.questions || [];
  const attemptId = state?.attemptId;

  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startTimes] = useState(() => {
    const t = {}; questions.forEach((_, i) => { t[i] = Date.now(); }); return t;
  });
  const [results, setResults] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!questions.length) return <div className="card"><h2>No questions</h2><p>Go back and generate a quiz first.</p></div>;

  const q = questions[idx];
  const total = questions.length;
  const progress = ((idx + 1) / total) * 100;

  const selectAnswer = (ans) => {
    setAnswers({ ...answers, [q.id]: { answer: ans, time: (Date.now() - (startTimes[idx] || Date.now())) / 1000 } });
  };

  const next = () => { if (idx < total - 1) { startTimes[idx + 1] = Date.now(); setIdx(idx + 1); } };
  const prev = () => { if (idx > 0) setIdx(idx - 1); };

  const finish = async () => {
    setSubmitting(true);
    const payload = {
      attempt_id: attemptId,
      answers: questions.map(qq => ({
        question_id: qq.id,
        answer: answers[qq.id]?.answer || "",
        time_spent_seconds: answers[qq.id]?.time || 0,
      })),
    };
    try {
      const { data } = await submitQuiz(payload);
      setResults(data);
    } catch (e) {
      alert("Failed to submit: " + (e.response?.data?.msg || e.message));
    } finally { setSubmitting(false); }
  };

  // Results view
  if (results) {
    const attempt = results.attempt;
    return (
      <div className="card">
        <h2>Quiz Results</h2>
        <div className="progress-bar"><div className="fill" style={{ width: `${attempt.score_percent}%` }} /></div>
        <p><strong>Score:</strong> {attempt.correct_count}/{attempt.total_questions} ({attempt.score_percent.toFixed(1)}%)</p>
        <p><strong>Time:</strong> {attempt.time_taken_seconds.toFixed(1)}s</p>
        <p><strong>Recommended next difficulty:</strong> <span className={`badge badge-${results.recommended_difficulty}`}>{results.recommended_difficulty}</span></p>
        <hr style={{ margin: "16px 0" }} />
        <h3>Review</h3>
        {results.results.map((r, i) => (
          <div key={i} style={{ padding: 12, background: r.is_correct ? "#d4edda" : "#f8d7da", borderRadius: 6, marginBottom: 8 }}>
            <p><strong>Q{i + 1}:</strong> {questions.find(q => q.id === r.question_id)?.question_text}</p>
            <p>Your answer: <strong>{r.your_answer || "(blank)"}</strong></p>
            <p>Correct: <strong>{r.correct_answer}</strong></p>
            {r.explanation && <p><em>{r.explanation}</em></p>}
            <button className="btn btn-sm" onClick={() => flagQuestion(r.question_id).then(() => alert("Flagged!"))}>🚩 Flag</button>
          </div>
        ))}
        <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => nav("/quiz")}>Take Another Quiz</button>
      </div>
    );
  }

  // Quiz play view
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <span>Question {idx + 1} of {total}</span>
        <span className={`badge badge-${q.difficulty}`}>{q.difficulty}</span>
      </div>
      <div className="progress-bar"><div className="fill" style={{ width: `${progress}%` }} /></div>
      <h3 style={{ marginBottom: 16 }}>{q.question_text}</h3>

      {q.question_type === "mcq" || q.question_type === "true_false" ? (
        q.options.map((opt, i) => (
          <div key={i} className={`quiz-option ${answers[q.id]?.answer === opt ? "selected" : ""}`} onClick={() => selectAnswer(opt)}>
            {opt}
          </div>
        ))
      ) : (
        <input
          placeholder="Type your answer..."
          value={answers[q.id]?.answer || ""}
          onChange={e => selectAnswer(e.target.value)}
          style={{ fontSize: 16, padding: 14 }}
        />
      )}

      <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
        {idx > 0 && <button className="btn" onClick={prev}>← Previous</button>}
        {idx < total - 1 ? (
          <button className="btn btn-primary" onClick={next} disabled={!answers[q.id]}>Next →</button>
        ) : (
          <button className="btn btn-primary" onClick={finish} disabled={submitting || !answers[q.id]}>
            {submitting ? "Submitting..." : "Finish Quiz"}
          </button>
        )}
      </div>
    </div>
  );
}
