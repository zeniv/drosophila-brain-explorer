export interface SimulationParams {
  t_run: number;
  n_run: number;
  v_0: number;
  v_rst: number;
  v_th: number;
  t_mbr: number;
  tau: number;
  t_rfc: number;
  t_dly: number;
  w_syn: number;
  r_poi: number;
  r_poi2: number;
  f_poi: number;
  n_proc: number;
}

export const DEFAULT_PARAMS: SimulationParams = {
  t_run: 1000,
  n_run: 30,
  v_0:   -52,
  v_rst: -52,
  v_th:  -45,
  t_mbr:  20,
  tau:     5,
  t_rfc:   2.2,
  t_dly:   1.8,
  w_syn:   0.275,
  r_poi:   150,
  r_poi2:  0,
  f_poi:   250,
  n_proc: -1,
};

export type ExperimentStatus = 'pending' | 'running' | 'completed' | 'failed';
export type HypothesisStatus = 'untested' | 'confirmed' | 'refuted' | 'requires_validation';

export interface NeuronResult {
  neuron_id: number;
  mean_rate: number;
  spike_count: number;
  std_rate: number;
}

export interface ExperimentResult {
  total_neurons_active: number;
  top_neurons: NeuronResult[];
  mean_network_rate: number;
  duration_ms: number;
}

export interface Experiment {
  id: string;
  name: string;
  description?: string;
  status: ExperimentStatus;
  params: SimulationParams;
  neu_exc: number[];
  neu_slnc: number[];
  neu_exc2: number[];
  tags: string[];
  hypothesis_id?: string;
  result_summary?: ExperimentResult;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface Hypothesis {
  id: string;
  title: string;
  description?: string;
  prediction?: string;
  status: HypothesisStatus;
  notes?: string;
  experiment_ids?: string[];
  arxiv_section?: string;
  created_at: string;
  updated_at?: string;
}

export interface CompareResponse {
  experiment_a: string;
  experiment_b: string;
  network_rate_a: number;
  network_rate_b: number;
  network_rate_delta: number;
  top_increased: NeuronDiff[];
  top_decreased: NeuronDiff[];
  p_value?: number;
  significant?: boolean;
}

export interface NeuronDiff {
  neuron_id: number;
  rate_a: number;
  rate_b: number;
  delta: number;
  delta_pct: number;
}

export interface Preset {
  name: string;
  description: string;
  neu_exc: number[];
  hypothesis: string;
}
