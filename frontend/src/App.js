import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import ContentUpload from "./pages/ContentUpload";
import ContentList from "./pages/ContentList";
import QuizSetup from "./pages/QuizSetup";
import QuizPlay from "./pages/QuizPlay";
import QuizHistory from "./pages/QuizHistory";
import AdminPanel from "./pages/AdminPanel";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  }, [token]);

  const logout = () => { setToken(null); setUser(null); };

  return (
    <Router>
      <div className="app">
        <nav>
          <Link to="/">🧠 AdaptiveQuiz</Link>
          {token ? (
            <>
              <Link to="/content">Content</Link>
              <Link to="/quiz">Quiz</Link>
              <Link to="/history">History</Link>
              <Link to="/profile">Profile</Link>
              {user?.is_admin && <Link to="/admin">Admin</Link>}
              <span className="spacer" />
              <button onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <span className="spacer" />
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>

        <Routes>
          <Route path="/login" element={<Login setToken={setToken} setUser={setUser} />} />
          <Route path="/register" element={<Register setToken={setToken} setUser={setUser} />} />
          <Route path="/profile" element={token ? <Profile user={user} setUser={setUser} /> : <Navigate to="/login" />} />
          <Route path="/content" element={token ? <ContentList /> : <Navigate to="/login" />} />
          <Route path="/upload" element={token ? <ContentUpload /> : <Navigate to="/login" />} />
          <Route path="/quiz" element={token ? <QuizSetup /> : <Navigate to="/login" />} />
          <Route path="/quiz/play" element={token ? <QuizPlay /> : <Navigate to="/login" />} />
          <Route path="/history" element={token ? <QuizHistory /> : <Navigate to="/login" />} />
          <Route path="/admin" element={token ? <AdminPanel /> : <Navigate to="/login" />} />
          <Route path="/" element={
            <div className="card">
              <h1>Welcome to Adaptive Quiz</h1>
              <p>Upload learning content, generate personalized quizzes, and track your progress with adaptive difficulty!</p>
              <br />
              <p><strong>Features:</strong></p>
              <ul style={{marginLeft: 20, marginTop: 8}}>
                <li>📚 Upload text, URLs, or PDFs</li>
                <li>❓ Auto-generate MCQ, Fill-in-the-blank, True/False, Short Answer</li>
                <li>📈 Adaptive difficulty based on your performance</li>
                <li>📊 Track quiz history and scores</li>
                <li>🛡️ Admin dashboard for content moderation</li>
              </ul>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
