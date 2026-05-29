export const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8765';
export const WS_URL = API_URL.replace(/^http/, 'ws') + '/ws';

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
