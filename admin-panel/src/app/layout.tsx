import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";
import { Toaster } from "react-hot-toast";

// All pages need Firebase auth state — disable static prerendering at build time.
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "NemoClaw Admin",
  description: "Admin panel for NemoClaw platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
          <Toaster position="top-right" toastOptions={{ duration: 3500 }} />
        </AuthProvider>
      </body>
    </html>
  );
}
