/**
 * Browser: use public URL (host machine).
 * Server (SSR in Docker): use internal Docker network URL when set.
 */
function getApiUrl(): string {
  if (typeof window === "undefined") {
    return (
      process.env.API_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:19001"
    );
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:19001";
}

export const API_URL = getApiUrl();

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${getApiUrl()}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:19001"}/v1/health`, {
      cache: "no-store",
    });
    return res.ok;
  } catch {
    return false;
  }
}
