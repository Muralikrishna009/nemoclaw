"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { signOut } from "@/lib/auth";
import toast from "react-hot-toast";

// ── Inline SVG icons ──────────────────────────────────────────────────────────

function DashboardIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <rect x="1" y="1" width="6" height="6" rx="1.5" />
      <rect x="9" y="1" width="6" height="6" rx="1.5" />
      <rect x="1" y="9" width="6" height="6" rx="1.5" />
      <rect x="9" y="9" width="6" height="6" rx="1.5" />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <circle cx="8" cy="5" r="3" />
      <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" />
    </svg>
  );
}

function PermissionsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="7" width="10" height="8" rx="2" />
      <path d="M5 7V5a3 3 0 016 0v2" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="8" cy="8" r="2.5" />
      <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.1 3.1l1.4 1.4M11.5 11.5l1.4 1.4M3.1 12.9l1.4-1.4M11.5 4.5l1.4-1.4" />
    </svg>
  );
}

function SignOutIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M10 5l3 3-3 3M13 8H6" />
      <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3" />
    </svg>
  );
}

// ── Nav items ─────────────────────────────────────────────────────────────────

const nav = [
  { href: "/dashboard",   label: "Dashboard",   Icon: DashboardIcon },
  { href: "/users",       label: "Users",       Icon: UsersIcon },
  { href: "/permissions", label: "Permissions", Icon: PermissionsIcon },
  { href: "/settings",    label: "Settings",    Icon: SettingsIcon },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function Sidebar() {
  const pathname = usePathname();
  const router   = useRouter();

  async function handleSignOut() {
    try {
      await signOut();
      toast.success("Signed out");
      router.push("/login");
    } catch {
      toast.error("Sign out failed");
    }
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
          <div style={{
            width: 36, height: 36,
            background: "var(--highlight)",
            borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0,
          }}>
            <span style={{ color: "#fff", fontSize: 18, fontWeight: 800 }}>N</span>
          </div>
          <div>
            <div style={{ color: "#fff", fontWeight: 700, fontSize: 15 }}>NemoClaw</div>
            <div style={{ color: "rgba(255,255,255,.45)", fontSize: 11 }}>Admin Panel</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "20px 12px" }}>
        {nav.map(({ href, label, Icon }) => {
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
                color: active ? "#fff" : "rgba(255,255,255,.55)",
                background: active ? "rgba(255,255,255,.12)" : "transparent",
                textDecoration: "none",
                fontSize: 14,
                fontWeight: active ? 600 : 400,
                transition: "all .15s",
                borderLeft: active ? "3px solid var(--highlight)" : "3px solid transparent",
              }}
            >
              <Icon />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Sign out */}
      <div style={{ padding: "12px 12px 0" }}>
        <button
          onClick={handleSignOut}
          className="btn"
          style={{
            width: "100%",
            justifyContent: "center",
            gap: 8,
            background: "rgba(255,255,255,.07)",
            color: "rgba(255,255,255,.6)",
            fontSize: 13,
            border: "1px solid rgba(255,255,255,.1)",
          }}
        >
          <SignOutIcon />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
