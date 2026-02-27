import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listContent, deleteContent } from "../api";

export default function ContentList() {
  const [items, setItems] = useState([]);

  const load = () => listContent().then(({ data }) => setItems(data.contents)).catch(() => {});
  useEffect(() => { load(); }, []);

  const remove = async (id) => {
    if (!window.confirm("Delete this content?")) return;
    await deleteContent(id);
    load();
  };

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>My Content</h2>
        <Link to="/upload" className="btn btn-primary" style={{ textDecoration: "none" }}>+ Upload</Link>
      </div>
      {items.length === 0 && <p style={{ marginTop: 12 }}>No content yet. Upload some learning material to get started!</p>}
      <table style={{ marginTop: 12 }}>
        <thead><tr><th>Title</th><th>Source</th><th>Chunks</th><th>Date</th><th></th></tr></thead>
        <tbody>
          {items.map(c => (
            <tr key={c.id}>
              <td>{c.title}</td>
              <td><span className="badge badge-medium">{c.source_type}</span></td>
              <td>{c.chunk_count}</td>
              <td>{new Date(c.created_at).toLocaleDateString()}</td>
              <td><button className="btn btn-danger btn-sm" onClick={() => remove(c.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
