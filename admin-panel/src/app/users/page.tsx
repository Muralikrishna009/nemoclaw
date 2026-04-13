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
  telegramId: string | null;
  phoneNumber: string | null;
  isActive: boolean;
  role: Role;
  createdAt: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  function loadUsers() {
    setLoading(true);
    fetch("/api/users")
      .then((r) => r.json())
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

  async function deleteUser(id: number) {
    if (!confirm("Delete this user?")) return;
    const res = await fetch(`/api/users/${id}`, { method: "DELETE" });
    if (res.ok) {
      toast.success("User deleted");
      loadUsers();
    } else {
      toast.error("Delete failed");
    }
  }

  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      (u.telegramId ?? "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Users</h1>
          <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>{users.length} total users</p>
        </div>
        <Link href="/users/new" className="btn btn-primary">+ Add User</Link>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {/* Search */}
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
          <input
            className="form-input"
            style={{ maxWidth: 320 }}
            placeholder="Search by name or Telegram ID…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--muted)" }}>Loading…</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--muted)" }}>No users found.</div>
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
                  <tr key={user.id}>
                    <td style={{ fontWeight: 600 }}>{user.name}</td>
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
                        {user.role.rolePermissions.map(({ permission }) => (
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
                      >
                        {user.isActive ? "Active" : "Inactive"}
                      </button>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 8 }}>
                        <Link href={`/users/${user.id}`} className="btn btn-ghost" style={{ padding: "4px 12px", fontSize: 13 }}>
                          Edit
                        </Link>
                        <button
                          onClick={() => deleteUser(user.id)}
                          className="btn btn-danger"
                          style={{ padding: "4px 12px", fontSize: 13 }}
                        >
                          Delete
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
