"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import toast from "react-hot-toast";

interface Permission {
  id: number;
  name: string;
}

interface Role {
  id: number;
  name: string;
  rolePermissions: { permission: Permission }[];
}

interface User {
  id: number;
  name: string;
  telegramId:  string | null;
  phoneNumber: string | null;
  isActive:    boolean;
  role:        Role;
  createdAt:   string;
}

function EmptyUsersIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <circle cx="24" cy="16" r="8"/>
      <path d="M8 42c0-8.8 7.2-16 16-16s16 7.2 16 16"/>
    </svg>
  );
}

export default function UsersPage() {
  const [users,   setUsers]   = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search,  setSearch]  = useState("");
  const [deleting, setDeleting] = useState<number | null>(null);

  function loadUsers() {
    setLoading(true);
    fetch("/api/users")
      .then((r) => {
        if (!r.ok) throw new Error("fetch failed");
        return r.json();
      })
      .then(setUsers)
      .catch(() => toast.error("Failed to load users"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadUsers(); }, []);

  async function toggleActive(user: User) {
    const res = await fetch(`/api/users/${user.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ isActive: !user.isActive }),
    });
    if (res.ok) {
      toast.success(`User ${!user.isActive ? "activated" : "deactivated"}`);
      loadUsers();
    } else {
      toast.error("Update failed");
    }
  }

  async function deleteUser(id: number, name: string) {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
    setDeleting(id);
    const res = await fetch(`/api/users/${id}`, { method: "DELETE" });
    setDeleting(null);
    if (res.ok) {
      toast.success("User deleted");
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } else {
      toast.error("Delete failed");
    }
  }

  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      (u.telegramId ?? "").toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Users</h1>
          <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>
            {loading ? "Loading…" : `${users.length} total user${users.length !== 1 ? "s" : ""}`}
          </p>
        </div>
        <Link href="/users/new" className="btn btn-primary">+ Add User</Link>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {/* Search bar */}
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12 }}>
          <input
            className="form-input"
            style={{ maxWidth: 300 }}
            placeholder="Search by name or Telegram ID…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              className="btn btn-ghost"
              style={{ fontSize: 12, padding: "6px 12px" }}
              onClick={() => setSearch("")}
            >
              Clear
            </button>
          )}
        </div>

        {/* Body */}
        {loading ? (
          <div style={{ padding: "32px 20px", display: "flex", flexDirection: "column", gap: 14 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ display: "flex", gap: 16, alignItems: "center" }}>
                <div className="skeleton" style={{ width: 32, height: 32, borderRadius: "50%" }} />
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
                  <div className="skeleton" style={{ height: 14, width: "25%" }} />
                  <div className="skeleton" style={{ height: 12, width: "40%" }} />
                </div>
                <div className="skeleton" style={{ width: 60, height: 24, borderRadius: 999 }} />
                <div className="skeleton" style={{ width: 80, height: 28, borderRadius: 6 }} />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <EmptyUsersIcon />
            <p style={{ fontWeight: 600, fontSize: 15 }}>
              {search ? "No users match your search" : "No users yet"}
            </p>
            {!search && (
              <Link href="/users/new" className="btn btn-primary" style={{ marginTop: 4 }}>
                Add First User
              </Link>
            )}
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Telegram ID</th>
                  <th>Phone</th>
                  <th>Role</th>
                  <th>Permissions</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((user) => (
                  <tr key={user.id} style={{ opacity: deleting === user.id ? 0.4 : 1, transition: "opacity .2s" }}>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        {/* Avatar initial */}
                        <div style={{
                          width: 30, height: 30, borderRadius: "50%",
                          background: "var(--accent)", color: "#fff",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 12, fontWeight: 700, flexShrink: 0,
                        }}>
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <span style={{ fontWeight: 600 }}>{user.name}</span>
                      </div>
                    </td>
                    <td style={{ color: "var(--muted)", fontFamily: "monospace", fontSize: 13 }}>
                      {user.telegramId ?? "—"}
                    </td>
                    <td style={{ color: "var(--muted)" }}>{user.phoneNumber ?? "—"}</td>
                    <td>
                      <span className={`badge ${user.role.name === "admin" ? "badge-blue" : "badge-yellow"}`}>
                        {user.role.name}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                        {user.role.rolePermissions.length === 0 ? (
                          <span style={{ fontSize: 12, color: "var(--muted)" }}>None</span>
                        ) : user.role.rolePermissions.map(({ permission }) => (
                          <span key={permission.id} className="badge badge-green" style={{ fontSize: 11 }}>
                            {permission.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <button
                        onClick={() => toggleActive(user)}
                        className={`badge ${user.isActive ? "badge-green" : "badge-red"}`}
                        style={{ cursor: "pointer", border: "none" }}
                        title={`Click to ${user.isActive ? "deactivate" : "activate"}`}
                      >
                        {user.isActive ? "Active" : "Inactive"}
                      </button>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <Link
                          href={`/users/${user.id}`}
                          className="btn btn-ghost"
                          style={{ padding: "4px 12px", fontSize: 13 }}
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => deleteUser(user.id, user.name)}
                          className="btn btn-danger"
                          style={{ padding: "4px 12px", fontSize: 13 }}
                          disabled={deleting === user.id}
                        >
                          {deleting === user.id ? "…" : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
