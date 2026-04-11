"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type StatusShape = {
  status: string;
  identity?: string;
  mode?: string;
  current_focus?: string;
  last_user_intent?: string;
  last_reply?: string;
  recent_actions?: Array<{ ts: number; intent: string; actions: string[] }>;
};

export default function Page() {
  const [intent, setIntent] = useState("");
  const [reply, setReply] = useState("");
  const [status, setStatus] = useState<StatusShape | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function loadStatus() {
    try {
      const res = await fetch(`${API}/status`, { cache: "no-store" });
      const data = await res.json();
      setStatus(data);
    } catch {
      setError("Could not reach Jarvis backend.");
    }
  }

  useEffect(() => {
    loadStatus();
  }, []);

  async function sendIntent() {
    if (!intent.trim()) return;
    setBusy(true);
    setError("");
    try {
      const res = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intent })
      });
      const data = await res.json();
      setReply(data.reply || "");
      setIntent("");
      await loadStatus();
    } catch {
      setError("Execution failed. Backend connection may be offline.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 36, marginBottom: 8 }}>Zerenthis Jarvis</h1>
      <p style={{ opacity: 0.8, marginTop: 0 }}>
        Persistent operator companion shell
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 20 }}>
        <section style={{ background: "#121933", borderRadius: 16, padding: 20 }}>
          <h2>Talk to Jarvis</h2>
          <textarea
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Tell Zerenthis what to do..."
            style={{
              width: "100%",
              minHeight: 140,
              padding: 14,
              borderRadius: 12,
              border: "1px solid #2d3a6b",
              background: "#0d1430",
              color: "#e8ecf3"
            }}
          />
          <button
            onClick={sendIntent}
            disabled={busy}
            style={{
              marginTop: 12,
              padding: "12px 18px",
              borderRadius: 12,
              border: "none",
              cursor: "pointer"
            }}
          >
            {busy ? "Sending..." : "Execute"}
          </button>

          <div style={{ marginTop: 20 }}>
            <h3>Reply</h3>
            <div style={{ background: "#0d1430", borderRadius: 12, padding: 14, minHeight: 80 }}>
              {reply || "Jarvis is waiting."}
            </div>
          </div>

          {error ? <p style={{ color: "#ff8080" }}>{error}</p> : null}
        </section>

        <aside style={{ background: "#121933", borderRadius: 16, padding: 20 }}>
          <h2>Status</h2>
          <p><strong>Backend:</strong> {status?.status || "unknown"}</p>
          <p><strong>Identity:</strong> {status?.identity || "Zerenthis"}</p>
          <p><strong>Mode:</strong> {status?.mode || "jarvis_companion"}</p>
          <p><strong>Focus:</strong> {status?.current_focus || "none"}</p>
          <p><strong>Last Intent:</strong> {status?.last_user_intent || "none"}</p>
          <p><strong>Last Reply:</strong> {status?.last_reply || "none"}</p>

          <h3>Recent Actions</h3>
          <div style={{ background: "#0d1430", borderRadius: 12, padding: 12 }}>
            {(status?.recent_actions || []).length === 0 ? (
              <p>No actions yet.</p>
            ) : (
              (status?.recent_actions || []).map((item, idx) => (
                <div key={idx} style={{ marginBottom: 12 }}>
                  <div><strong>Intent:</strong> {item.intent || "(empty)"}</div>
                  <div><strong>Actions:</strong> {(item.actions || []).join(", ")}</div>
                </div>
              ))
            )}
          </div>
        </aside>
      </div>
    </main>
  );
}
