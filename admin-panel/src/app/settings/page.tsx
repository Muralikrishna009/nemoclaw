"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";

function EyeIcon({ open }: { open: boolean }) {
  return open ? (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" />
      <circle cx="8" cy="8" r="2" />
    </svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <path d="M2 2l12 12M6.5 6.6A2 2 0 0010.4 10M4.2 4.3C2.6 5.4 1 8 1 8s2.5 5 7 5c1.4 0 2.7-.4 3.8-1M6.9 3.1C7.3 3 7.6 3 8 3c4.5 0 7 5 7 5s-.6 1.2-1.7 2.4" />
    </svg>
  );
}

export default function SettingsPage() {
  const [enabled,     setEnabled]     = useState(false);
  const [password,    setPassword]    = useState("");
  const [showPwd,     setShowPwd]     = useState(false);
  const [loading,     setLoading]     = useState(true);
  const [saving,      setSaving]      = useState(false);
  const [dirty,       setDirty]       = useState(false);

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((data) => {
        setEnabled(data.pdf_password_enabled === "true");
        setPassword(data.pdf_password ?? "");
      })
      .catch(() => toast.error("Failed to load settings"))
      .finally(() => setLoading(false));
  }, []);

  function markDirty() { setDirty(true); }

  function handleToggle(val: boolean) {
    setEnabled(val);
    markDirty();
  }

  function handlePasswordChange(val: string) {
    setPassword(val);
    markDirty();
  }

  async function save() {
    if (enabled && !password.trim()) {
      toast.error("Please enter a password or disable password protection.");
      return;
    }
    setSaving(true);
    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pdf_password_enabled: String(enabled),
          pdf_password: password,
        }),
      });
      if (!res.ok) throw new Error();
      toast.success("Settings saved");
      setDirty(false);
    } catch {
      toast.error("Failed to save settings");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Settings</h1>
        <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>
          Configure system-wide options
        </p>
      </div>

      {loading ? (
        <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="skeleton" style={{ height: 20, width: "30%" }} />
          <div className="skeleton" style={{ height: 44, width: "100%" }} />
          <div className="skeleton" style={{ height: 44, width: "60%" }} />
        </div>
      ) : (
        <div className="card" style={{ padding: 28, maxWidth: 560 }}>
          {/* Section title */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <div style={{
              width: 3, height: 20, background: "var(--accent)",
              borderRadius: 2, flexShrink: 0,
            }} />
            <h2 style={{ fontSize: 15, fontWeight: 700, color: "var(--primary)" }}>
              PDF Password Protection
            </h2>
          </div>

          {/* Toggle row */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "14px 16px",
            background: enabled ? "var(--success-bg, #f0fdf4)" : "var(--bg)",
            border: `1px solid ${enabled ? "var(--success, #22c55e)" : "var(--border)"}`,
            borderRadius: 8,
            marginBottom: 16,
            transition: "all .2s",
          }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "var(--primary)" }}>
                Enable password on all generated PDFs
              </div>
              <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
                {enabled
                  ? "All PDFs will require the password below to open."
                  : "PDFs are generated without a password."}
              </div>
            </div>
            {/* Toggle switch */}
            <button
              onClick={() => handleToggle(!enabled)}
              role="switch"
              aria-checked={enabled}
              style={{
                width: 44, height: 24,
                borderRadius: 999,
                border: "none",
                cursor: "pointer",
                background: enabled ? "var(--highlight)" : "var(--border)",
                position: "relative",
                flexShrink: 0,
                transition: "background .2s",
                padding: 0,
              }}
            >
              <span style={{
                position: "absolute",
                top: 3, left: enabled ? 23 : 3,
                width: 18, height: 18,
                borderRadius: "50%",
                background: "#fff",
                transition: "left .2s",
                boxShadow: "0 1px 3px rgba(0,0,0,.2)",
              }} />
            </button>
          </div>

          {/* Password field */}
          <div style={{
            opacity: enabled ? 1 : 0.45,
            pointerEvents: enabled ? "auto" : "none",
            transition: "opacity .2s",
          }}>
            <label className="form-label">PDF Password</label>
            <div style={{ position: "relative" }}>
              <input
                className="form-input"
                type={showPwd ? "text" : "password"}
                placeholder="Enter password for PDFs…"
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                style={{ paddingRight: 40 }}
              />
              <button
                type="button"
                onClick={() => setShowPwd((v) => !v)}
                style={{
                  position: "absolute", right: 12, top: "50%",
                  transform: "translateY(-50%)",
                  background: "none", border: "none",
                  cursor: "pointer", color: "var(--muted)", padding: 0,
                }}
                tabIndex={-1}
              >
                <EyeIcon open={showPwd} />
              </button>
            </div>
            <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 6 }}>
              Users must enter this password to open any generated PDF.
            </p>
          </div>

          {/* Save button */}
          <div style={{ marginTop: 24, display: "flex", alignItems: "center", gap: 12 }}>
            <button
              className="btn btn-primary"
              onClick={save}
              disabled={saving || !dirty}
              style={{ minWidth: 100 }}
            >
              {saving ? (
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span className="spinner-sm" /> Saving…
                </span>
              ) : "Save Changes"}
            </button>
            {dirty && !saving && (
              <span style={{ fontSize: 12, color: "var(--highlight)" }}>
                ● Unsaved changes
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
