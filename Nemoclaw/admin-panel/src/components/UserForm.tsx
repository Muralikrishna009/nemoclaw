"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

interface Role {
  id: number;
  name: string;
}

interface UserFormData {
  name: string;
  telegramId: string;
  phoneNumber: string;
  roleId: string;
  isActive: boolean;
}

interface Props {
  userId?: number; // present when editing
}

export default function UserForm({ userId }: Props) {
  const router = useRouter();
  const [roles, setRoles] = useState<Role[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const isEdit = !!userId;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UserFormData>({ defaultValues: { isActive: true } });

  // Load roles
  useEffect(() => {
    fetch("/api/roles")
      .then((r) => r.json())
      .then(setRoles)
      .catch(() => toast.error("Failed to load roles"));
  }, []);

  // If editing, load existing user data
  useEffect(() => {
    if (!userId) return;
    fetch(`/api/users/${userId}`)
      .then((r) => r.json())
      .then((user) => {
        reset({
          name: user.name,
          telegramId: user.telegramId ?? "",
          phoneNumber: user.phoneNumber ?? "",
          roleId: String(user.roleId),
          isActive: user.isActive,
        });
      })
      .catch(() => toast.error("Failed to load user"));
  }, [userId, reset]);

  async function onSubmit(data: UserFormData) {
    setSubmitting(true);
    const payload = {
      name: data.name,
      telegramId: data.telegramId || null,
      phoneNumber: data.phoneNumber || null,
      roleId: Number(data.roleId),
      isActive: data.isActive,
    };

    const res = await fetch(isEdit ? `/api/users/${userId}` : "/api/users", {
      method: isEdit ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    setSubmitting(false);

    if (res.ok) {
      toast.success(isEdit ? "User updated" : "User created");
      router.push("/users");
    } else {
      const err = await res.json();
      toast.error(err.error ?? "Something went wrong");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} style={{ maxWidth: 520 }}>
      <div className="form-group">
        <label className="form-label">Full Name *</label>
        <input
          className="form-input"
          placeholder="John Doe"
          {...register("name", { required: "Name is required" })}
        />
        {errors.name && <span className="form-error">{errors.name.message}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Telegram ID</label>
        <input
          className="form-input"
          placeholder="e.g. user_123456"
          {...register("telegramId")}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Phone Number</label>
        <input
          className="form-input"
          placeholder="+1234567890"
          {...register("phoneNumber")}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Role *</label>
        <select
          className="form-input"
          {...register("roleId", { required: "Role is required" })}
        >
          <option value="">Select a role…</option>
          {roles.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>
        {errors.roleId && <span className="form-error">{errors.roleId.message}</span>}
      </div>

      <div className="form-group">
        <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}>
          <input type="checkbox" {...register("isActive")} style={{ width: 16, height: 16 }} />
          <span style={{ fontSize: 14, fontWeight: 500 }}>Active (can use MCP tools)</span>
        </label>
      </div>

      <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : isEdit ? "Update User" : "Create User"}
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => router.push("/users")}>
          Cancel
        </button>
      </div>
    </form>
  );
}
