"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";

interface StatsData {
  totalUsers:    number;
  activeUsers:   number;
  inactiveUsers: number;
  adminCount:    number;
  userCount:     number;
}

// ── Stat card icon SVGs ───────────────────────────────────────────────────────

function TotalIcon()    { return <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><circle cx="10" cy="7" r="3"/><path d="M3 18c0-3.9 3.1-7 7-7s7 3.1 7 7"/></svg>; }
function ActiveIcon()   { return <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="10" cy="10" r="8"/><path d="M7 10l2 2 4-4"/></svg>; }
function InactiveIcon() { return <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><circle cx="10" cy="10" r="8"/><path d="M8 8l4 4M12 8l-4 4"/></svg>; }
function AdminIcon()    { return <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M10 2l2.5 5 5.5.8-4 3.9.9 5.5L10 14.5l-4.9 2.7.9-5.5-4-3.9 5.5-.8z"/></svg>; }
function UserIcon()     { return <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><circle cx="10" cy="7" r="3"/><path d="M4 18c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>; }

// ── Component ─────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats,   setStats]   = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(false);

  const loadStats = useCallback(() => {
    setLoading(true);
    setError(false);
    fetch("/api/users")
      .then((r) => {
        if (!r.ok) throw new Error("fetch failed");
        return r.json();
      })
      .then((users: Array<{ isActive: boolean; role: { name: string } }>) => {
        setStats({
          totalUsers:    users.length,
          activeUsers:   users.filter((u) => u.isActive).length,
          inactiveUsers: users.filter((u) => !u.isActive).length,
          adminCount:    users.filter((u) => u.role.name === "admin").length,
          userCount:     users.filter((u) => u.role.name === "user").length,
        });
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadStats(); }, [loadStats]);

  const firstName = user?.email?.split("@")[0] ?? "Admin";

  const cards = stats
    ? [
        { label: "Total Users",    value: stats.totalUsers,    color: "var(--accent)",   Icon: TotalIcon },
        { label: "Active",         value: stats.activeUsers,   color: "var(--success)",  Icon: ActiveIcon },
        { label: "Inactive",       value: stats.inactiveUsers, color: "var(--danger)",   Icon: InactiveIcon },
        { label: "Admins",         value: stats.adminCount,    color: "var(--highlight)",Icon: AdminIcon },
        { label: "Regular Users",  value: stats.userCount,     color: "var(--purple)",   Icon: UserIcon },
      ]
    : [];

  return (
    <div>
      {/* Page header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: "var(--primary)" }}>Dashboard</h1>
          <p style={{ color: "var(--muted)", marginTop: 4, fontSize: 14 }}>
            Welcome back, <strong>{firstName}</strong>
          </p>
        </div>
        {!loading && (
          <button className="btn btn-ghost" onClick={loadStats} style={{ fontSize: 13 }}>
            ↻ Refresh
          </button>
        )}
      </div>

      {/* Stats */}
      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(190px, 1fr))", gap: 16 }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="card">
              <div className="skeleton" style={{ height: 36, width: "55%", marginBottom: 10 }} />
              <div className="skeleton" style={{ height: 14, width: "75%" }} />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="card" style={{ textAlign: "center", padding: "40px 24px" }}>
          <p style={{ color: "var(--danger)", marginBottom: 12, fontWeight: 500 }}>
            Failed to load statistics
          </p>
          <button className="btn btn-ghost" onClick={loadStats}>Retry</button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(190px, 1fr))", gap: 16 }}>
          {cards.map(({ label, value, color, Icon }) => (
            <div key={label} className="card" style={{ borderTop: `4px solid ${color}` }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                <div style={{ fontSize: 34, fontWeight: 800, color }}>{value}</div>
                <div style={{ color, opacity: 0.7 }}><Icon /></div>
              </div>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* MCP Tools */}
      <div className="card" style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>MCP Tools</h2>
        <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 14 }}>
          Available tools exposed by the MCP server
        </p>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
          {["generate_pdf", "generate_image"].map((tool) => (
            <span key={tool} className="badge badge-blue" style={{ fontSize: 13, padding: "6px 14px" }}>
              {tool}
            </span>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "var(--muted)" }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--success)", display: "inline-block" }} />
          MCP Server at{" "}
          <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: 4, fontSize: 12 }}>
            http://localhost:8000
          </code>
        </div>
      </div>
    </div>
  );
}
