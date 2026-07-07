import { api } from "@/lib/api";

type Flag = {
  id: string;
  title: string;
  severity: string;
  status: string;
  repository_full_name: string | null;
  explanation: string | null;
  created_at: string;
};

export default async function FlagsPage() {
  let flags: Flag[] = [];
  try {
    flags = await api<Flag[]>("/v1/flags");
  } catch {
    /* empty */
  }

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", textTransform: "uppercase" }}>Security</div>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>Risk Register</h1>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Title</th>
              <th>Repository</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {flags.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: 40, textAlign: "center", color: "var(--text-secondary)" }}>
                  No flags yet. Create an engagement and run a scan, or connect a repo via webhook.
                </td>
              </tr>
            ) : (
              flags.map((flag) => (
                <tr key={flag.id}>
                  <td>
                    <span className={`badge badge-${flag.severity}`}>{flag.severity}</span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{flag.title}</div>
                    {flag.explanation && (
                      <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>{flag.explanation}</div>
                    )}
                  </td>
                  <td className="mono">{flag.repository_full_name}</td>
                  <td>
                    <span className={`badge badge-${flag.status === "new" ? "new" : "low"}`}>{flag.status}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
