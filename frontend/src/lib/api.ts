export interface UserPayload {
  name: string;
  email: string;
  organization?: string;
  interests: string;
  goals?: string;
}

export interface GrantPayload {
  title: string;
  description: string;
  focus_area?: string;
  sponsor?: string;
}

export interface Grant {
  id: number;
  title: string;
  description: string;
  focus_area?: string | null;
  sponsor?: string | null;
}

export interface GrantMatch {
  grant: Grant;
  score: number;
}

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function createUser(payload: UserPayload) {
  return request<Grant>("/users/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listGrants() {
  return request<Grant[]>("/grants/");
}

export function getMatches(userId: number, topK = 5) {
  const params = new URLSearchParams({ top_k: topK.toString() });
  return request<GrantMatch[]>(`/matches/${userId}?${params.toString()}`, {
    method: "POST",
  });
}
