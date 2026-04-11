"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Page() {
  const [msg, setMsg] = useState("");
  const [status, setStatus] = useState(null);

  async function send() {
    if (!msg.trim()) return;
    await fetch(`${API}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ intent: msg })
    });
    setMsg("");
    refresh();
  }

  async function refresh() {
    const r = await fetch(`${API}/status`);
    const j = await r.json();
    setStatus(j);
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={{ padding: 24, maxWidth: 1000, margin: "0 auto" }}>
      <h1>Zerenthis</h1>
      <p>Austin's personal Jarvis interface</p>

      <textarea
        value={msg}
        onChange={(e) => setMsg(e.target.value)}
        placeholder="Tell Zerenthis what to do..."
        style={{
          width: "100%",
          minHeight: 120,
          background: "#111",
          color: "white",
          border: "1px solid #333",
          borderRadius: 12,
          padding: 12
        }}
      />

      <button
        onClick={send}
        style={{
          marginTop: 12,
          padding: "10px 16px",
          borderRadius: 10,
          border: 0,
          background: "white",
          color: "black",
          fontWeight: 700,
          cursor: "pointer"
        }}
      >
        Send
      </button>

      <h2 style={{ marginTop: 24 }}>Live Status</h2>
      <pre
        style={{
          background: "#111",
          border: "1px solid #333",
          borderRadius: 12,
          padding: 12,
          whiteSpace: "pre-wrap"
        }}
      >
        {status ? JSON.stringify(status, null, 2) : "Loading..."}
      </pre>
    </div>
  );
}
