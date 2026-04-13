import UserForm from "@/components/UserForm";

export default function NewUserPage() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--primary)" }}>Add User</h1>
        <p style={{ color: "var(--muted)", marginTop: 2, fontSize: 14 }}>Create a new NemoClaw user</p>
      </div>
      <div className="card">
        <UserForm />
      </div>
    </div>
  );
}
