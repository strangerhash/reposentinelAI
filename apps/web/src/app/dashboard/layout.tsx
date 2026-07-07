import Link from "next/link";
import { ApiStatusBanner } from "@/components/ApiStatusBanner";

const NAV = [
  { href: "/dashboard", label: "Posture" },
  { href: "/dashboard/flags", label: "Flags" },
  { href: "/dashboard/engagements", label: "Engagements" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        style={{
          width: "var(--sidebar-w)",
          borderRight: "1px solid var(--border)",
          background: "var(--bg-sidebar)",
          padding: "20px 0",
          position: "fixed",
          top: 0,
          bottom: 0,
        }}
      >
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "0 20px 24px",
            fontWeight: 700,
          }}
        >
          <div
            style={{
              width: 28,
              height: 28,
              background: "var(--accent)",
              borderRadius: 6,
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
            }}
          >
            E
          </div>
          EstateGuard
        </Link>
        <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-tertiary)", padding: "0 20px 8px" }}>
          Platform
        </div>
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            style={{
              display: "block",
              padding: "8px 20px",
              fontSize: 14,
              color: "var(--text-secondary)",
            }}
          >
            {item.label}
          </Link>
        ))}
      </aside>
      <main style={{ marginLeft: "var(--sidebar-w)", flex: 1, padding: "32px 40px", maxWidth: 1100 }}>
        <ApiStatusBanner />
        {children}
      </main>
    </div>
  );
}
