import { create } from 'zustand';
import type { SimulationParams, Experiment, Hypothesis } from '../types';
import { DEFAULT_PARAMS } from '../types';

interface AppStore {
  // Параметры текущего эксперимента
  params: SimulationParams;
  setParam: <K extends keyof SimulationParams>(key: K, value: SimulationParams[K]) => void;
  resetParams: () => void;

  // Нейроны
  neuExc: number[];
  neuSlnc: number[];
  neuExc2: number[];
  setNeuExc:  (ids: number[]) => void;
  setNeuSlnc: (ids: number[]) => void;
  setNeuExc2: (ids: number[]) => void;

  // Форма запуска
  expName: string;
  expDesc: string;
  selectedHypId: string | null;
  setExpName: (v: string) => void;
  setExpDesc: (v: string) => void;
  setSelectedHypId: (v: string | null) => void;

  // Кэш результатов
  experiments: Experiment[];
  setExperiments: (exps: Experiment[]) => void;
  upsertExperiment: (exp: Experiment) => void;

  // Выбранный эксперимент для просмотра
  activeExpId: string | null;
  setActiveExpId: (id: string | null) => void;

  // Сравнение
  compareA: string | null;
  compareB: string | null;
  setCompareA: (id: string | null) => void;
  setCompareB: (id: string | null) => void;

  // Гипотезы
  hypotheses: Hypothesis[];
  setHypotheses: (h: Hypothesis[]) => void;
  upsertHypothesis: (h: Hypothesis) => void;
}

export const useStore = create<AppStore>((set) => ({
  params: { ...DEFAULT_PARAMS },
  setParam: (key, value) =>
    set((s) => ({ params: { ...s.params, [key]: value } })),
  resetParams: () => set({ params: { ...DEFAULT_PARAMS } }),

  neuExc:  [],
  neuSlnc: [],
  neuExc2: [],
  setNeuExc:  (ids) => set({ neuExc: ids }),
  setNeuSlnc: (ids) => set({ neuSlnc: ids }),
  setNeuExc2: (ids) => set({ neuExc2: ids }),

  expName: '',
  expDesc: '',
  selectedHypId: null,
  setExpName: (v) => set({ expName: v }),
  setExpDesc: (v) => set({ expDesc: v }),
  setSelectedHypId: (v) => set({ selectedHypId: v }),

  experiments: [],
  setExperiments: (exps) => set({ experiments: exps }),
  upsertExperiment: (exp) =>
    set((s) => ({
      experiments: s.experiments.find((e) => e.id === exp.id)
        ? s.experiments.map((e) => (e.id === exp.id ? exp : e))
        : [exp, ...s.experiments],
    })),

  activeExpId: null,
  setActiveExpId: (id) => set({ activeExpId: id }),

  compareA: null,
  compareB: null,
  setCompareA: (id) => set({ compareA: id }),
  setCompareB: (id) => set({ compareB: id }),

  hypotheses: [],
  setHypotheses: (h) => set({ hypotheses: h }),
  upsertHypothesis: (h) =>
    set((s) => ({
      hypotheses: s.hypotheses.find((x) => x.id === h.id)
        ? s.hypotheses.map((x) => (x.id === h.id ? h : x))
        : [h, ...s.hypotheses],
    })),
}));
