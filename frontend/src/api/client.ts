import axios from 'axios';
import type {
  Experiment, Hypothesis, CompareResponse,
  SimulationParams, Preset,
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// ── Experiments ──────────────────────────────────────────────────────────────

export const experimentsApi = {
  create: (data: {
    name: string;
    description?: string;
    params: SimulationParams;
    neu_exc: number[];
    neu_slnc?: number[];
    neu_exc2?: number[];
    hypothesis_id?: string;
    tags?: string[];
  }) => api.post<Experiment>('/experiments/', data).then(r => r.data),

  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get<Experiment[]>('/experiments/', { params }).then(r => r.data),

  get: (id: string) =>
    api.get<Experiment>(`/experiments/${id}`).then(r => r.data),

  compare: (id_a: string, id_b: string) =>
    api.post<CompareResponse>('/experiments/compare', {
      experiment_id_a: id_a,
      experiment_id_b: id_b,
    }).then(r => r.data),
};

// ── Hypotheses ───────────────────────────────────────────────────────────────

export const hypothesesApi = {
  create: (data: {
    title: string;
    description?: string;
    prediction?: string;
    arxiv_section?: string;
  }) => api.post<Hypothesis>('/hypotheses/', data).then(r => r.data),

  list: () =>
    api.get<Hypothesis[]>('/hypotheses/').then(r => r.data),

  get: (id: string) =>
    api.get<Hypothesis>(`/hypotheses/${id}`).then(r => r.data),

  update: (id: string, data: {
    status?: string;
    notes?: string;
    prediction?: string;
  }) => api.patch<Hypothesis>(`/hypotheses/${id}`, data).then(r => r.data),

  attach: (hypId: string, expId: string) =>
    api.post<Hypothesis>(`/hypotheses/${hypId}/attach/${expId}`).then(r => r.data),
};

// ── Neurons ──────────────────────────────────────────────────────────────────

export const neuronsApi = {
  search: (q?: string, ids?: string) =>
    api.get('/neurons/search', { params: { q, ids } }).then(r => r.data),

  presets: () =>
    api.get<{ presets: Preset[] }>('/neurons/presets').then(r => r.data),
};
