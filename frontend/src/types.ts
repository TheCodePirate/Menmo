export interface UserProfilePayload {
  name: string;
  email: string;
  organization?: string;
  focus_areas?: string;
  goals?: string;
}

export interface GrantPayload {
  title: string;
  description: string;
  sponsor?: string;
  deadline?: string;
  url?: string;
}

export interface MatchResult {
  grant: GrantPayload & { id: number };
  score: number;
}
