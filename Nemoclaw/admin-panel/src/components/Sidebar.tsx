"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { signOut } from "@/lib/auth";
import toast from "react-hot-toast";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: "⬛" },
  { href: "/users", label: "Users", icon: "👤" },
  { href: "/permissions", label: "Permissions", icon: "🔑" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleSignOut() {
    await signOut();
    toast.success("Signed out");
    router.push("/login");
  }

  return (
    <aside style={{
      width: 240,
      minHeight: "100vh",
      background: "var(--primary)",
      display: "flex",
      flexDirection: "column",
      padding: "24px 0",
      flexShrink: 0,
    }}>
      {/* Brand */}
      <div style={{ padding: "0 20px 28px", borderBottom: "1px solid rgba(255,255,255,.1)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, background: "var(--highlight)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ color: "#fff", fontSize: 18, fontWeight: 800 }}>N</span>
          </div>
          <div>
            <div style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>NemoClaw</div>
            <div style={{ color: "rgba(255,255,255,.5)", fontSize: 11 }}>Admin Panel</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "20px 12px" }}>
        {nav.map(({ href, label, icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "10px 12px",
                borderRadius: 8,
                marginBottom: 4,
                color: active ? "#fff" : "rgba(255,255,255,.6)",
                background: active ? "rgba(255,255,255,.1)" : "transparent",
                textDecoration: "none",
                fontSize: 14,
                fontWeight: active ? 600 : 400,
                transition: "all .15s",
              }}
            >
              <span style={{ fontSize: 16 }}>{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Sign out */}
      <div style={{ padding: "0 12px" }}>
        <button
          onClick={handleSignOut}
          className="btn"
          style={{ width: "100%", justifyContent: "center", background: "rgba(255,255,255,.08)", color: "rgba(255,255,255,.7)", fontSize: 13 }}
        >
          Sign Out
        </button>
      </div>
    </aside>
  );
}
