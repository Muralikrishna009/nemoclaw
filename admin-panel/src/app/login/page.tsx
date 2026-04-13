"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { signIn } from "@/lib/auth";
import { useAuth } from "@/hooks/useAuth";

interface LoginForm {
  email:    string;
  password: string;
}

function EyeIcon({ open }: { open: boolean }) {
  return open ? (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M1 9C2.7 5.5 5.6 3 9 3s6.3 2.5 8 6c-1.7 3.5-4.6 6-8 6S2.7 12.5 1 9z"/>
      <circle cx="9" cy="9" r="2.5"/>
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M1 9C2.7 5.5 5.6 3 9 3s6.3 2.5 8 6"/>
      <path d="M13.5 13.5A8.7 8.7 0 019 15c-3.4 0-6.3-2.5-8-6"/>
      <line x1="2" y1="2" x2="16" y2="16"/>
    </svg>
  );
}

export default function LoginPage() {
  const { user, loading } = useAuth();
  const router            = useRouter();
  const [submitting,    setSubmitting]    = useState(false);
  const [showPassword,  setShowPassword]  = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [user, loading, router]);

  async function onSubmit(data: LoginForm) {
    setSubmitting(true);
    try {
      await signIn(data.email, data.password);
      toast.success("Welcome back!");
      router.push("/dashboard");
    } catch (err: unknown) {
      const code = (err as { code?: string }).code;
      if (code === "auth/user-not-found" || code === "auth/wrong-password" || code === "auth/invalid-credential") {
        toast.error("Invalid email or password");
      } else if (code === "auth/too-many-requests") {
        toast.error("Too many attempts — try again later");
      } else {
        toast.error("Sign in failed. Check your connection.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "var(--bg)",
    }}>
      <div className="card" style={{ width: "100%", maxWidth: 420 }}>
        {/* Logo / header */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            width: 56, height: 56,
            background: "var(--primary)",
            borderRadius: 16,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 14,
          }}>
            <span style={{ color: "#fff", fontSize: 26, fontWeight: 800 }}>N</span>
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--primary)" }}>NemoClaw Admin</h1>
          <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 4 }}>Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="form-input"
              type="email"
              autoComplete="email"
              placeholder="admin@example.com"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && <span className="form-error">{errors.email.message}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: "relative" }}>
              <input
                className="form-input"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="••••••••"
                style={{ paddingRight: 44 }}
                {...register("password", {
                  required: "Password is required",
                  minLength: { value: 6, message: "Min 6 characters" },
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                style={{
                  position: "absolute", right: 12, top: "50%",
                  transform: "translateY(-50%)",
                  background: "none", border: "none",
                  cursor: "pointer", color: "var(--muted)",
                  display: "flex", alignItems: "center",
                  padding: 0,
                }}
              >
                <EyeIcon open={showPassword} />
              </button>
            </div>
            {errors.password && <span className="form-error">{errors.password.message}</span>}
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={submitting}
            style={{ width: "100%", justifyContent: "center", padding: "12px", fontSize: 15, marginTop: 8 }}
          >
            {submitting ? (
              <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="spinner spinner-sm" style={{ borderColor: "rgba(255,255,255,.3)", borderTopColor: "#fff" }} />
                Signing in…
              </span>
            ) : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
