const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) }
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json();
}

export type Health = { ok: boolean; model_version: string; artifact_version: string; schema_version: string; rows: Record<string, number>; qc_ok: boolean; target_columns: string[]; best_epoch?: number; test_raw_mse?: number; database_path: string };
export type Metrics = { model_version: string; best_score?: number; best_epoch?: number; test_loss?: number; test_raw_mse?: number; test_rmse_per_target: Record<string, number>; history_preview: any[] };
export type PredictionRow = { system_id:number; geom_id:number; k_index:number; y_true: Record<string, number>; y_pred: Record<string, number>; uncertainty?: number; p_physics?: number; stability_support?: number; rank_score?: number };
export type PredictionList = { rows: PredictionRow[]; count: number };
export type ScoreResponse = { reactant_scores: any[]; candidate_scores: any[]; rank_scores: any[]; note: string };
export type ExplainResponse = { ai_mode: string; summary: string; interpretation: string[]; recommended_next_steps: string[]; caveats: string[]; markdown: string };

export const getHealth = () => request<Health>('/api/v1/dess/health');
export const getMetrics = () => request<Metrics>('/api/v1/dess/metrics');
export const getPredictions = (limit=40, systemId?: string) => request<PredictionList>(`/api/v1/dess/predictions?limit=${limit}${systemId ? `&system_id=${encodeURIComponent(systemId)}` : ''}`);
export const scoreLab = (reactants: string[], candidates: string[]) => request<ScoreResponse>('/api/v1/dess/score', { method: 'POST', body: JSON.stringify({ reactants, candidates }) });
export const explainScore = (score: ScoreResponse, userContext = '') => request<ExplainResponse>('/api/v1/dess/explain', { method: 'POST', body: JSON.stringify({ ...score, user_context: userContext }) });
