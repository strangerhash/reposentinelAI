import Link from "next/link";

export default function LandingPage() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "16px 48px",
          borderBottom: "1px solid var(--border)",
          background: "rgba(255,255,255,0.9)",
          backdropFilter: "blur(8px)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, fontWeight: 700 }}>
          <div
            style={{
              width: 28,
              height: 28,
              background: "var(--accent)",
              borderRadius: 6,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: 14,
            }}
          >
            E
          </div>
          EstateGuard
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link href="/dashboard" className="btn-secondary" style={{ padding: "8px 16px", borderRadius: 6 }}>
            Dashboard
          </Link>
          <Link href="/dashboard/engagements" className="btn-primary" style={{ padding: "8px 16px", borderRadius: 6 }}>
            M&A Engagements
          </Link>
        </nav>
      </header>

      <section
        style={{
          background: "linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%)",
          color: "white",
          padding: "96px 48px 80px",
        }}
      >
        <div style={{ maxWidth: 720 }}>
          <span
            style={{
              display: "inline-block",
              padding: "4px 12px",
              background: "rgba(59,130,246,0.2)",
              border: "1px solid rgba(59,130,246,0.3)",
              borderRadius: 20,
              fontSize: 12,
              color: "#93c5fd",
              marginBottom: 20,
            }}
          >
            Tool Hub wedge · Multi-VCS · Consultancy-ready
          </span>
          <h1 style={{ fontSize: 44, fontWeight: 700, lineHeight: 1.1, marginBottom: 16, letterSpacing: "-0.02em" }}>
            The control plane for mixed git estates
          </h1>
          <p style={{ fontSize: 18, color: "#a1a1aa", lineHeight: 1.6, marginBottom: 32, maxWidth: 560 }}>
            Unify security posture, architecture truth, and institutional knowledge across GitHub, GitLab, and
            Bitbucket — with consultancy-grade M&A due diligence that scanners and IDE copilots cannot deliver.
          </p>
          <div style={{ display: "flex", gap: 12 }}>
            <Link href="/dashboard/engagements" className="btn-primary" style={{ padding: "12px 24px" }}>
              Start M&A engagement
            </Link>
            <Link href="/dashboard" className="btn-secondary" style={{ padding: "12px 24px" }}>
              View dashboard
            </Link>
          </div>
        </div>
      </section>

      <section style={{ padding: "64px 48px", maxWidth: 1100, margin: "0 auto" }}>
        <h2 style={{ fontSize: 28, fontWeight: 700, marginBottom: 32 }}>Why not Cursor or another scanner?</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
          {[
            {
              title: "vs Cursor / Claude",
              body: "IDE copilots help one developer on one task. EstateGuard governs the entire estate — continuous, auditable, board-ready.",
            },
            {
              title: "vs GitHub-only scanners",
              body: "Mixed VCS estates need one risk register. We unify GitHub + GitLab with event-driven scanning, not scheduled polls.",
            },
            {
              title: "vs generic AppSec",
              body: "M&A due diligence reports, white-label MSP delivery, and institutional knowledge — not just CVE alerts.",
            },
          ].map((item) => (
            <div key={item.title} className="card">
              <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{item.title}</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.6 }}>{item.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
