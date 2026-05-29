const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API ${path} failed`);
  return response.json();
}

export function websocketUrl(): string {
  return API_URL.replace(/^http/, "ws") + "/ws";
}
