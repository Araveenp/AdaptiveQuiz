import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadText, uploadUrl } from "../api";

export default function ContentUpload() {
  const [tab, setTab] = useState("text");
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setMsg(""); setErr("");
    try {
      if (tab === "text") {
        await uploadText({ title: title || "Untitled", text });
      } else {
        await uploadUrl({ title: title || url, url });
      }
      setMsg("Content uploaded successfully!");
      setTimeout(() => nav("/content"), 1000);
    } catch (error) {
      setErr(error.response?.data?.msg || "Upload failed");
    }
  };

  return (
    <div className="card">
      <h2>Upload Content</h2>
      {msg && <div className="msg msg-success">{msg}</div>}
      {err && <div className="msg msg-error">{err}</div>}
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <button className={`btn ${tab === "text" ? "btn-primary" : ""}`} onClick={() => setTab("text")}>Paste Text</button>
        <button className={`btn ${tab === "url" ? "btn-primary" : ""}`} onClick={() => setTab("url")}>From URL</button>
      </div>
      <form onSubmit={submit}>
        <input placeholder="Title (optional)" value={title} onChange={e => setTitle(e.target.value)} />
        {tab === "text" ? (
          <textarea rows={8} placeholder="Paste your learning content here..." value={text} onChange={e => setText(e.target.value)} required />
        ) : (
          <input placeholder="https://en.wikipedia.org/wiki/..." value={url} onChange={e => setUrl(e.target.value)} required />
        )}
        <button className="btn btn-primary" type="submit">Upload & Process</button>
      </form>
    </div>
  );
}
