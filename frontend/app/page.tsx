"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "";

export default function Home() {
  const [intent, setIntent] = useState("");
  const [status, setStatus] = useState<any>(null);
  const [reply, setReply] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function refreshStatus() {
    try {
      const r = await fetch(`${API}/status`);
      const j = await r.json();
      setStatus(j);
    } catch (e) {
      setStatus({ error: "Could not reach Zerenthis backend." });
    }
  }

  async function sendIntent() {
    if (!intent.trim()) return;
    setLoading(true);
    setReply(null);
    try {
      const r = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intent })
      });
      const j = await r.json();
      setReply(j);
      setIntent("");
      await refreshStatus();
    } catch (e) {
      setReply({ error: "Failed to send message to Zerenthis." });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshStatus();
    const t = setInterval(refreshStatus, 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 36, marginBottom: 8 }}>Zerenthis</h1>
      <p style={{ opacity: 0.8, marginTop: 0 }}>Austin&apos;s personal Jarvis interface</p>

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}>
        <section style={{ background: "#111", border: "1px solid #222", borderRadius: 16, padding: 20 }}>
          <h2>Talk to Zerenthis</h2>
          <textarea
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Tell Zerenthis what you want..."
            style={{
              width: "100%",
              minHeight: 140,
              background: "#0d0d0d",
              color: "#fff",
              border: "1px solid #333",
              borderRadius: 12,
              padding: 14,
              resize: "vertical"
            }}
          />
          <button
            onClick={sendIntent}
            disabled={loading}
            style={{
              marginTop: 12,
              background: "#fff",
              color: "#000",
              border: 0,
              borderRadius: 10,
              padding: "12px 18px",
              cursor: "pointer",
              fontWeight: 700
            }}
          >
            {loading ? "Sending..." : "Send to Zerenthis"}
          </button>

          <div style={{ marginTop: 20 }}>
            <h3>Latest reply</h3>
            <pre style={{ whiteSpace: "pre-wrap", background: "#0d0d0d", padding: 14, borderRadius: 12, border: "1px solid #222" }}>
              {reply ? JSON.stringify(reply, null, 2) : "No message sent yet."}
            </pre>
          </div>
        </section>

        <section style={{ background: "#111", border: "1px solid #222", borderRadius: 16, padding: 20 }}>
          <h2>Live Status</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#0d0d0d", padding: 14, borderRadius: 12, border: "1px solid #222" }}>
            {status ? JSON.stringify(status, null, 2) : "Loading..."}
          </pre>
        </section>
      </div>
    </main>
  );
}
