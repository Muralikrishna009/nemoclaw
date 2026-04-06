import AuthGuard from "@/components/AuthGuard";
import Sidebar from "@/components/Sidebar";

export default function UsersLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main style={{ flex: 1, padding: 32, overflowY: "auto" }}>
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}
