"use client";

import { useEffect, useState } from "react";

export function ApiStatusBanner() {
  const [status, setStatus] = useState<"checking" | "ok" | "down">("checking");
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:19001";

  useEffect(() => {
    fetch(`${apiUrl}/v1/health`, { cache: "no-store" })
      .then((r) => setStatus(r.ok ? "ok" : "down"))
      .catch(() => setStatus("down"));
  }, [apiUrl]);

  if (status === "ok" || status === "checking") return null;

  return (
    <div
      style={{
        marginBottom: 20,
        padding: "12px 16px",
        background: "#fef2f2",
        border: "1px solid #fecaca",
        borderRadius: 8,
        color: "#991b1b",
        fontSize: 14,
      }}
    >
      <strong>API not reachable</strong> at {apiUrl}. Run{" "}
      <code style={{ background: "#fff", padding: "2px 6px", borderRadius: 4 }}>make dev</code> or{" "}
      <code style={{ background: "#fff", padding: "2px 6px", borderRadius: 4 }}>make api</code> in another terminal.
    </div>
  );
}
