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
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [saving, setSaving] = useState<number | null>(null);
  const [localPerms, setLocalPerms] = useState<Record<number, Set<number>>>({});

  function loadData() {
    Promise.all([fetch("/api/roles").then((r) => r.json()), fetch("/api/permissions").then((r) => r.json())])
      .then(([rolesData, permsData]: [Role[], Permission[]]) => {
        setRoles(rolesData);
        setPermissions(permsData);
        // Build local state: roleId → Set of permissionIds
        const map: Record<number, Set<number>> = {};
        for (const role of rolesData) {
          map[role.id] = new Set(role.rolePermissions.map((rp) => rp.permission.id));
        }
        setLocalPerms(map);
      })
      .catch(() => toast.error("Failed to load data"));
  }

  useEffect(() => { loadData(); }, []);

  function toggle(roleId: number, permId: number) {
    setLocalPerms((prev) => {
      const set = new Set(prev[roleId] ?? []);
      if (set.has(permId)) set.delete(permId);
      else set.add(permId);
      return { ...prev, [roleId]: set };
    });
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
      loadData();
    } else {
      toast.error("Failed to update permissions");
    }
  }

  const permDescriptions: Record<string, string> = {
    generate_pdf: "Can generate PDF financial reports via MCP",
    generate_image: "Can generate diagrams and charts via MCP",
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Permissions</h1>
        <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>
          Assign tool permissions to roles. Users inherit permissions from their role.
        </p>
      </div>

      {/* Permission legend */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Available Permissions</h2>
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

      {/* Role permission matrix */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {roles.map((role) => (
          <div key={role.id} className="card">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span className={`badge ${role.name === "admin" ? "badge-blue" : "badge-yellow"}`} style={{ fontSize: 14, padding: "4px 14px" }}>
                  {role.name}
                </span>
                <span style={{ fontSize: 13, color: "var(--muted)" }}>{role._count.users} user{role._count.users !== 1 ? "s" : ""}</span>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => saveRole(role.id)}
                disabled={saving === role.id}
                style={{ fontSize: 13, padding: "6px 16px" }}
              >
                {saving === role.id ? "Saving…" : "Save Changes"}
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {permissions.map((perm) => {
                const checked = localPerms[role.id]?.has(perm.id) ?? false;
                return (
                  <label key={perm.id} style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggle(role.id, perm.id)}
                      style={{ width: 16, height: 16, accentColor: "var(--accent)" }}
                    />
                    <div>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>{perm.name}</span>
                      <span style={{ fontSize: 12, color: "var(--muted)", marginLeft: 8 }}>
                        {perm.description ?? permDescriptions[perm.name]}
                      </span>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
