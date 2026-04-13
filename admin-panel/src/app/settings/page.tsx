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

interface PasswordConfig {
  enabled: boolean;
  password: string;
  showPwd: boolean;
  dirty: boolean;
}

function PasswordSection({
  title,
  subtitle,
  config,
  onChange,
  onSave,
  saving,
}: {
  title: string;
  subtitle: string;
  config: PasswordConfig;
  onChange: (patch: Partial<PasswordConfig>) => void;
  onSave: () => void;
  saving: boolean;
}) {
  return (
    <div className="card" style={{ padding: 28, maxWidth: 560, marginBottom: 20 }}>
      {/* Section title */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
        <div style={{
          width: 3, height: 20, background: "var(--accent)",
          borderRadius: 2, flexShrink: 0,
        }} />
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: "var(--primary)", margin: 0 }}>
            {title}
          </h2>
          <p style={{ fontSize: 12, color: "var(--muted)", margin: 0, marginTop: 2 }}>
            {subtitle}
          </p>
        </div>
      </div>

      {/* Toggle row */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "14px 16px",
        background: config.enabled ? "var(--success-bg, #f0fdf4)" : "var(--bg)",
        border: `1px solid ${config.enabled ? "var(--success, #22c55e)" : "var(--border)"}`,
        borderRadius: 8,
        marginBottom: 16,
        transition: "all .2s",
      }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, color: "var(--primary)" }}>
            Enable password protection
          </div>
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>
            {config.enabled
              ? "Files will require the password below to open."
              : "Files are generated without a password."}
          </div>
        </div>
        <button
          onClick={() => onChange({ enabled: !config.enabled, dirty: true })}
          role="switch"
          aria-checked={config.enabled}
          style={{
            width: 44, height: 24,
            borderRadius: 999,
            border: "none",
            cursor: "pointer",
            background: config.enabled ? "var(--highlight)" : "var(--border)",
            position: "relative",
            flexShrink: 0,
            transition: "background .2s",
            padding: 0,
          }}
        >
          <span style={{
            position: "absolute",
            top: 3, left: config.enabled ? 23 : 3,
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
        opacity: config.enabled ? 1 : 0.45,
        pointerEvents: config.enabled ? "auto" : "none",
        transition: "opacity .2s",
      }}>
        <label className="form-label">Password</label>
        <div style={{ position: "relative" }}>
          <input
            className="form-input"
            type={config.showPwd ? "text" : "password"}
            placeholder="Enter password…"
            value={config.password}
            onChange={(e) => onChange({ password: e.target.value, dirty: true })}
            style={{ paddingRight: 40 }}
          />
          <button
            type="button"
            onClick={() => onChange({ showPwd: !config.showPwd })}
            style={{
              position: "absolute", right: 12, top: "50%",
              transform: "translateY(-50%)",
              background: "none", border: "none",
              cursor: "pointer", color: "var(--muted)", padding: 0,
            }}
            tabIndex={-1}
          >
            <EyeIcon open={config.showPwd} />
          </button>
        </div>
        <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 6 }}>
          Users must enter this password to open the generated file.
        </p>
      </div>

      {/* Save button */}
      <div style={{ marginTop: 24, display: "flex", alignItems: "center", gap: 12 }}>
        <button
          className="btn btn-primary"
          onClick={onSave}
          disabled={saving || !config.dirty}
          style={{ minWidth: 100 }}
        >
          {saving ? (
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="spinner-sm" /> Saving…
            </span>
          ) : "Save Changes"}
        </button>
        {config.dirty && !saving && (
          <span style={{ fontSize: 12, color: "var(--highlight)" }}>● Unsaved changes</span>
        )}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [savingPdf, setSavingPdf] = useState(false);
  const [savingExcel, setSavingExcel] = useState(false);

  const [pdf, setPdf] = useState<PasswordConfig>({
    enabled: false, password: "", showPwd: false, dirty: false,
  });
  const [excel, setExcel] = useState<PasswordConfig>({
    enabled: false, password: "", showPwd: false, dirty: false,
  });

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((data) => {
        setPdf({
          enabled: data.pdf_password_enabled === "true",
          password: data.pdf_password ?? "",
          showPwd: false,
          dirty: false,
        });
        setExcel({
          enabled: data.excel_password_enabled === "true",
          password: data.excel_password ?? "",
          showPwd: false,
          dirty: false,
        });
      })
      .catch(() => toast.error("Failed to load settings"))
      .finally(() => setLoading(false));
  }, []);

  async function savePdf() {
    if (pdf.enabled && !pdf.password.trim()) {
      toast.error("Enter a password or disable PDF password protection.");
      return;
    }
    setSavingPdf(true);
    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pdf_password_enabled: String(pdf.enabled),
          pdf_password: pdf.password,
        }),
      });
      if (!res.ok) throw new Error();
      toast.success("PDF settings saved");
      setPdf((p) => ({ ...p, dirty: false }));
    } catch {
      toast.error("Failed to save PDF settings");
    } finally {
      setSavingPdf(false);
    }
  }

  async function saveExcel() {
    if (excel.enabled && !excel.password.trim()) {
      toast.error("Enter a password or disable Excel password protection.");
      return;
    }
    setSavingExcel(true);
    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          excel_password_enabled: String(excel.enabled),
          excel_password: excel.password,
        }),
      });
      if (!res.ok) throw new Error();
      toast.success("Excel settings saved");
      setExcel((e) => ({ ...e, dirty: false }));
    } catch {
      toast.error("Failed to save Excel settings");
    } finally {
      setSavingExcel(false);
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
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[1, 2].map((i) => (
            <div key={i} className="card" style={{ padding: 28, maxWidth: 560 }}>
              <div className="skeleton" style={{ height: 20, width: "40%", marginBottom: 16 }} />
              <div className="skeleton" style={{ height: 52, width: "100%", marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 44, width: "100%" }} />
            </div>
          ))}
        </div>
      ) : (
        <>
          <PasswordSection
            title="PDF Password Protection"
            subtitle="Applied to all generated .pdf files"
            config={pdf}
            onChange={(patch) => setPdf((p) => ({ ...p, ...patch }))}
            onSave={savePdf}
            saving={savingPdf}
          />
          <PasswordSection
            title="Excel Password Protection"
            subtitle="Applied to all generated .xlsx files"
            config={excel}
            onChange={(patch) => setExcel((e) => ({ ...e, ...patch }))}
            onSave={saveExcel}
            saving={savingExcel}
          />
        </>
      )}
    </div>
  );
}
