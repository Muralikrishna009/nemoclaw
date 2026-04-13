"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";

interface Permission {
  id: number;
  name: string;
  description: string | null;
}

interface Role {
  id: number;
  name: string;
  rolePermissions: { permission: Permission }[];
  _count: { users: number };
}

export default function PermissionsPage() {
  const [roles,      setRoles]      = useState<Role[]>([]);
  const [permissions,setPermissions]= useState<Permission[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [saving,     setSaving]     = useState<number | null>(null);
  const [localPerms, setLocalPerms] = useState<Record<number, Set<number>>>({});
  const [dirty,      setDirty]      = useState<Set<number>>(new Set());

  function loadData() {
    setLoading(true);
    Promise.all([
      fetch("/api/roles").then((r) => r.json()),
      fetch("/api/permissions").then((r) => r.json()),
    ])
      .then(([rolesData, permsData]: [Role[], Permission[]]) => {
        setRoles(rolesData);
        setPermissions(permsData);
        const map: Record<number, Set<number>> = {};
        for (const role of rolesData) {
          map[role.id] = new Set(role.rolePermissions.map((rp) => rp.permission.id));
        }
        setLocalPerms(map);
        setDirty(new Set());
      })
      .catch(() => toast.error("Failed to load data"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadData(); }, []);

  function toggle(roleId: number, permId: number) {
    setLocalPerms((prev) => {
      const set = new Set(prev[roleId] ?? []);
      if (set.has(permId)) set.delete(permId);
      else set.add(permId);
      return { ...prev, [roleId]: set };
    });
    setDirty((prev) => new Set(prev).add(roleId));
  }

  async function saveRole(roleId: number) {
    setSaving(roleId);
    const permissionIds = Array.from(localPerms[roleId] ?? []);
    const res = await fetch(`/api/roles/${roleId}/permissions`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permissionIds }),
    });
    setSaving(null);
    if (res.ok) {
      toast.success("Permissions updated");
      setDirty((prev) => { const s = new Set(prev); s.delete(roleId); return s; });
      loadData();
    } else {
      toast.error("Failed to update permissions");
    }
  }

  const permDescriptions: Record<string, string> = {
    generate_pdf:   "Can generate PDF financial reports via MCP",
    generate_image: "Can generate diagrams and charts via MCP",
  };

  if (loading) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Permissions</h1>
          <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>
            Assign tool permissions to roles.
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[1, 2].map((i) => (
            <div key={i} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                <div className="skeleton" style={{ height: 28, width: 80, borderRadius: 999 }} />
                <div className="skeleton" style={{ height: 32, width: 110, borderRadius: 8 }} />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div className="skeleton" style={{ height: 20, width: "60%" }} />
                <div className="skeleton" style={{ height: 20, width: "50%" }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Permissions</h1>
        <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>
          Assign tool permissions to roles. Users inherit permissions from their role.
        </p>
      </div>

      {/* Legend */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>Available Permissions</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {permissions.map((p) => (
            <div key={p.id} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span className="badge badge-green">{p.name}</span>
              <span style={{ fontSize: 13, color: "var(--muted)" }}>
                {p.description ?? permDescriptions[p.name] ?? ""}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Role cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {roles.map((role) => {
          const isDirty = dirty.has(role.id);
          return (
            <div key={role.id} className="card"
              style={{ borderLeft: isDirty ? "3px solid var(--highlight)" : "3px solid transparent" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span className={`badge ${role.name === "admin" ? "badge-blue" : "badge-yellow"}`}
                    style={{ fontSize: 14, padding: "4px 14px" }}>
                    {role.name}
                  </span>
                  <span style={{ fontSize: 13, color: "var(--muted)" }}>
                    {role._count.users} user{role._count.users !== 1 ? "s" : ""}
                  </span>
                  {isDirty && (
                    <span style={{ fontSize: 12, color: "var(--highlight)", fontWeight: 600 }}>
                      ● Unsaved changes
                    </span>
                  )}
                </div>
                <button
                  className="btn btn-primary"
                  onClick={() => saveRole(role.id)}
                  disabled={saving === role.id || !isDirty}
                  style={{
                    fontSize: 13, padding: "6px 16px",
                    background: isDirty ? "var(--highlight)" : "var(--border)",
                    color: isDirty ? "#fff" : "var(--muted)",
                    cursor: isDirty ? "pointer" : "default",
                  }}
                >
                  {saving === role.id ? (
                    <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span className="spinner spinner-sm" />Saving…
                    </span>
                  ) : isDirty ? "Save Changes" : "Saved"}
                </button>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {permissions.map((perm) => {
                  const checked = localPerms[role.id]?.has(perm.id) ?? false;
                  return (
                    <label key={perm.id}
                      style={{
                        display: "flex", alignItems: "flex-start", gap: 12,
                        cursor: "pointer",
                        padding: "10px 14px",
                        borderRadius: 8,
                        background: checked ? "#f0fdf4" : "transparent",
                        border: `1px solid ${checked ? "#bbf7d0" : "var(--border)"}`,
                        transition: "all .15s",
                      }}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggle(role.id, perm.id)}
                        style={{ width: 16, height: 16, accentColor: "var(--accent)", marginTop: 1 }}
                      />
                      <div>
                        <span style={{ fontSize: 14, fontWeight: 600 }}>{perm.name}</span>
                        <span style={{ fontSize: 12, color: "var(--muted)", display: "block", marginTop: 2 }}>
                          {perm.description ?? permDescriptions[perm.name]}
                        </span>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
