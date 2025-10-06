export interface UserProfilePayload {
  name: string;
  email: string;
  organization?: string;
  focus_areas?: string;
  goals?: string;
  industry?: string;
  entity_type?: string;
  location?: string;
  company_size?: string;
  project_type?: string;
  budget_min?: number;
  budget_max?: number;
}

export interface UserProfile extends UserProfilePayload {
  id: number;
}

export interface GrantPayload {
  title: string;
  description: string;
  sponsor?: string;
  deadline?: string;
  url?: string;
  jurisdiction?: string;
  entity_types?: string[];
  industries?: string[];
  project_types?: string[];
  budget_min?: number;
  budget_max?: number;
  min_co2_reduction?: number;
  max_support?: number;
  support_unit?: string;
}

export interface Grant {
  id: number;
  title: string;
  description: string;
  sponsor?: string | null;
  deadline?: string | null;
  url?: string | null;
  jurisdiction?: string | null;
  entity_types?: string[] | null;
  industries?: string[] | null;
  project_types?: string[] | null;
  budget_min?: number | null;
  budget_max?: number | null;
  min_co2_reduction?: number | null;
  max_support?: number | null;
  support_unit?: string | null;
}

export interface QuickScanPayload {
  industry?: string;
  entity_type?: string;
  location?: string;
  company_size?: string;
  project_type?: string;
  budget_min?: number;
  budget_max?: number;
}

export interface QuickScanResult {
  grant_id: number;
  grant_title: string;
  status: string;
  reasons: Record<string, unknown>[];
  blockers: Record<string, unknown>[];
  citations: Record<string, unknown>[];
}

export interface FundingMatchPayload {
  project_description: string;
  capex?: number;
  opex?: number;
  timeline?: string;
  co2_reduction?: number;
  partners?: string;
  top_k?: number;
}

export interface MatchResult {
  id: number;
  grant: Grant;
  score: number;
  status: string;
  reasons: Record<string, unknown>[];
  blockers: Record<string, unknown>[];
  citations: Record<string, unknown>[];
  insights: Record<string, unknown>;
}
