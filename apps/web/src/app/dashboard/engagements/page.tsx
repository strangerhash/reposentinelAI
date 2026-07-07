"use client";

import { useCallback, useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type Engagement = {
  id: string;
  name: string;
  target_org: string | null;
  status: string;
  repo_ids: string[];
  report_summary: Record<string, unknown> | null;
  created_at: string;
  completed_at: string | null;
};

type Report = {
  engagement_id: string;
  engagement_name: string;
  target_org: string | null;
  posture_score: number;
  summary: { total_flags: number; repos_assessed: number; recommendation: string };
  flags_by_severity: Record<string, number>;
  top_risks: { flag_id: string; title: string; severity: string }[];
  repositories: { full_name: string; platform: string; open_flags: number; critical: number }[];
};

export default function EngagementsPage() {
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", target_org: "" });

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/v1/engagements`);
      if (!res.ok) throw new Error(`API ${res.status}`);
      setEngagements(await res.json());
      setApiError(null);
    } catch {
      setApiError(`Cannot reach API at ${API_URL}. Run: make dev`);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function createEngagement(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/v1/engagements`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: form.name, target_org: form.target_org || null, repo_ids: [] }),
      });
      if (res.ok) {
        setForm({ name: "", target_org: "" });
        await load();
      }
    } finally {
      setLoading(false);
    }
  }

  async function runScan(id: string) {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/v1/engagements/${id}/scan`, { method: "POST" });
      if (res.ok) {
        await load();
        const reportRes = await fetch(`${API_URL}/v1/engagements/${id}/report`);
        if (reportRes.ok) setReport(await reportRes.json());
      }
    } finally {
      setLoading(false);
    }
  }

  async function viewReport(id: string) {
    const res = await fetch(`${API_URL}/v1/engagements/${id}/report`);
    if (res.ok) setReport(await res.json());
  }

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", textTransform: "uppercase" }}>Wedge</div>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>M&A Due Diligence Engagements</h1>
        <p style={{ color: "var(--text-secondary)", marginTop: 8 }}>
          Primary product wedge — scoped security assessment for consultancy pursuits.
        </p>
      </div>

      {apiError && (
        <div className="card" style={{ marginBottom: 24, borderColor: "#fecaca", background: "#fef2f2", color: "#991b1b" }}>
          {apiError}
        </div>
      )}

      <form onSubmit={createEngagement} className="card" style={{ marginBottom: 24, display: "grid", gap: 12 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>New engagement</h2>
        <input
          required
          placeholder="Engagement name (e.g. TargetCo Acquisition)"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          style={{ padding: 10, border: "1px solid var(--border)", borderRadius: 6 }}
        />
        <input
          placeholder="Target organization"
          value={form.target_org}
          onChange={(e) => setForm({ ...form, target_org: e.target.value })}
          style={{ padding: 10, border: "1px solid var(--border)", borderRadius: 6 }}
        />
        <button type="submit" className="btn-primary" disabled={loading} style={{ width: "fit-content" }}>
          Create engagement
        </button>
      </form>

      <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 24 }}>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Target</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {engagements.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: 32, textAlign: "center", color: "var(--text-secondary)" }}>
                  No engagements yet.
                </td>
              </tr>
            ) : (
              engagements.map((eng) => (
                <tr key={eng.id}>
                  <td style={{ fontWeight: 500 }}>{eng.name}</td>
                  <td>{eng.target_org || "—"}</td>
                  <td>
                    <span className={`badge badge-${eng.status === "completed" ? "completed" : eng.status === "scanning" ? "scanning" : "new"}`}>
                      {eng.status}
                    </span>
                  </td>
                  <td style={{ display: "flex", gap: 8 }}>
                    <button className="btn-primary" onClick={() => runScan(eng.id)} disabled={loading}>
                      Run scan
                    </button>
                    {eng.status === "completed" && (
                      <button className="btn-secondary" onClick={() => viewReport(eng.id)}>
                        View report
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {report && (
        <div className="card">
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>{report.engagement_name}</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 20 }}>Target: {report.target_org || "N/A"}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 20 }}>
            <div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>Posture score</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: "var(--accent)" }}>{report.posture_score}</div>
            </div>
            <div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>Total flags</div>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{report.summary.total_flags}</div>
            </div>
            <div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>Repos assessed</div>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{report.summary.repos_assessed}</div>
            </div>
          </div>
          <div
            style={{
              padding: 16,
              background: "var(--accent-subtle)",
              borderRadius: 8,
              marginBottom: 20,
              fontWeight: 500,
            }}
          >
            {report.summary.recommendation}
          </div>
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Top risks</h3>
          <ul style={{ listStyle: "none", display: "grid", gap: 8 }}>
            {report.top_risks.map((risk) => (
              <li key={risk.flag_id} style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span className={`badge badge-${risk.severity}`}>{risk.severity}</span>
                <span>{risk.title}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
