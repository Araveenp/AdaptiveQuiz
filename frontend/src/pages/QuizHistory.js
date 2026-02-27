import React, { useEffect, useState } from "react";
import { quizHistory } from "../api";

export default function QuizHistory() {
  const [attempts, setAttempts] = useState([]);

  useEffect(() => {
    quizHistory().then(({ data }) => setAttempts(data.attempts)).catch(() => {});
  }, []);

  return (
    <div className="card">
      <h2>Quiz History</h2>
      {attempts.length === 0 && <p>No quizzes taken yet.</p>}
      <table>
        <thead>
          <tr><th>#</th><th>Difficulty</th><th>Score</th><th>Questions</th><th>Time</th><th>Date</th></tr>
        </thead>
        <tbody>
          {attempts.map((a, i) => (
            <tr key={a.id}>
              <td>{i + 1}</td>
              <td><span className={`badge badge-${a.difficulty}`}>{a.difficulty}</span></td>
              <td>{a.score_percent.toFixed(1)}%</td>
              <td>{a.correct_count}/{a.total_questions}</td>
              <td>{a.time_taken_seconds.toFixed(1)}s</td>
              <td>{new Date(a.started_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
