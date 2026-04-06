"use client";

import { use } from "react";
import UserForm from "@/components/UserForm";

export default function EditUserPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Edit User</h1>
        <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>Update role and status</p>
      </div>
      <div className="card">
        <UserForm userId={Number(id)} />
      </div>
    </div>
  );
}
