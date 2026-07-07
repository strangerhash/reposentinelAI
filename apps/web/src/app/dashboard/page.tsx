import { api } from "@/lib/api";

type Posture = {
  score: number;
  trend_90d: number;
  critical_open: number;
  high_open: number;
  total_open: number;
  repos_scanned: number;
};

export default async function PosturePage() {
  let posture: Posture = {
    score: 0,
    trend_90d: 0,
    critical_open: 0,
    high_open: 0,
    total_open: 0,
    repos_scanned: 0,
  };
  try {
    posture = await api<Posture>("/v1/posture");
  } catch {
    /* API may be offline during first boot */
  }

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Executive
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>Posture Dashboard</h1>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: 24, marginBottom: 24 }}>
        <div className="card" style={{ textAlign: "center", padding: 32 }}>
          <div style={{ fontSize: 48, fontWeight: 700, color: "var(--accent)" }}>{posture.score}</div>
          <div style={{ fontSize: 14, color: "var(--text-secondary)" }}>/ 100</div>
        </div>
        <div className="card">
          <div style={{ fontSize: 14, color: "var(--text-secondary)", marginBottom: 8 }}>90-day trend</div>
          <div style={{ fontSize: 24, fontWeight: 600 }}>{posture.trend_90d >= 0 ? "+" : ""}{posture.trend_90d} pts</div>
          <p style={{ marginTop: 12, color: "var(--text-secondary)", fontSize: 14 }}>
            Composite score from open flags weighted by severity. Run an M&A engagement scan to populate data.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
        {[
          { label: "Critical open", value: posture.critical_open, color: "var(--critical)" },
          { label: "High open", value: posture.high_open, color: "var(--high)" },
          { label: "Repos scanned", value: posture.repos_scanned, color: "var(--accent)" },
        ].map((stat) => (
          <div key={stat.label} className="card">
            <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>{stat.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: stat.color, marginTop: 4 }}>{stat.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
