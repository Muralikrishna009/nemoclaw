"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";

interface StatsData {
  totalUsers: number;
  activeUsers: number;
  inactiveUsers: number;
  adminCount: number;
  userCount: number;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    fetch("/api/users")
      .then((r) => r.json())
      .then((users: Array<{ isActive: boolean; role: { name: string } }>) => {
        setStats({
          totalUsers: users.length,
          activeUsers: users.filter((u) => u.isActive).length,
          inactiveUsers: users.filter((u) => !u.isActive).length,
          adminCount: users.filter((u) => u.role.name === "admin").length,
          userCount: users.filter((u) => u.role.name === "user").length,
        });
      })
      .catch(console.error);
  }, []);

  const cards = stats
    ? [
        { label: "Total Users", value: stats.totalUsers, color: "var(--accent)" },
        { label: "Active Users", value: stats.activeUsers, color: "#16a34a" },
        { label: "Inactive Users", value: stats.inactiveUsers, color: "#dc2626" },
        { label: "Admins", value: stats.adminCount, color: "var(--highlight)" },
        { label: "Regular Users", value: stats.userCount, color: "#7c3aed" },
      ]
    : [];

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, color: "var(--primary)" }}>Dashboard</h1>
        <p style={{ color: "var(--muted)", marginTop: 4 }}>Welcome back, {user?.email}</p>
      </div>

      {stats ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16 }}>
          {cards.map(({ label, value, color }) => (
            <div key={label} className="card" style={{ borderTop: `4px solid ${color}` }}>
              <div style={{ fontSize: 32, fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: "var(--muted)" }}>Loading stats…</p>
      )}

      <div className="card" style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>MCP Tools Available</h2>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {["generate_pdf", "generate_image"].map((tool) => (
            <span key={tool} className="badge badge-blue" style={{ fontSize: 13, padding: "6px 14px" }}>
              {tool}
            </span>
          ))}
        </div>
        <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 12 }}>
          MCP Server running at <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: 4 }}>http://localhost:8000</code>
        </p>
      </div>
    </div>
  );
}
