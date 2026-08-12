import type { ResolveResponse } from "./types.ts";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function resolveDateTime(text: string): Promise<ResolveResponse> {
  const response = await fetch(`${API_BASE_URL}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return response.json();
}