import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { experimentsApi, hypothesesApi } from '../api/client';
import ParameterPanel from '../components/ParameterPanel';
import NeuronSelector from '../components/NeuronSelector';
import ResultsViewer from '../components/ResultsViewer';

export default function ExperimentBuilder() {
  const {
    params, neuExc, neuSlnc, neuExc2,
    expName, expDesc, setExpName, setExpDesc,
    selectedHypId, setSelectedHypId,
    experiments, setExperiments, upsertExperiment,
    activeExpId, setActiveExpId,
    hypotheses, setHypotheses,
  } = useStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [polling, setPolling] = useState<ReturnType<typeof setInterval> | null>(null);

  // Загрузить историю
  useEffect(() => {
    experimentsApi.list({ limit: 50 }).then(setExperiments);
    hypothesesApi.list().then(setHypotheses);
  }, []);

  // Polling активного эксперимента
  useEffect(() => {
    if (!activeExpId) return;
    const activeExp = experiments.find((e) => e.id === activeExpId);
    if (activeExp?.status === 'completed' || activeExp?.status === 'failed') return;

    const id = setInterval(async () => {
      const updated = await experimentsApi.get(activeExpId);
      upsertExperiment(updated);
      if (updated.status === 'completed' || updated.status === 'failed') {
        clearInterval(id);
      }
    }, 2000);
    setPolling(id);
    return () => clearInterval(id);
  }, [activeExpId]);

  async function runExperiment() {
    if (!expName.trim()) { setError('Enter experiment name'); return; }
    if (neuExc.length === 0) { setError('Select at least one neuron to excite'); return; }

    setError('');
    setLoading(true);
    try {
      const exp = await experimentsApi.create({
        name: expName,
        description: expDesc || undefined,
        params,
        neu_exc: neuExc,
        neu_slnc: neuSlnc,
        neu_exc2: neuExc2,
        hypothesis_id: selectedHypId || undefined,
        tags: [],
      });
      upsertExperiment(exp);
      setActiveExpId(exp.id);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to start simulation');
    } finally {
      setLoading(false);
    }
  }

  const activeExp = activeExpId ? experiments.find((e) => e.id === activeExpId) : null;

  return (
    <div className="flex h-full gap-4 min-h-0">
      {/* Левая панель — параметры */}
      <div className="w-72 flex-shrink-0 overflow-y-auto space-y-3 pr-1 custom-scroll">
        <NeuronSelector />
        <ParameterPanel />
      </div>

      {/* Центр — запуск + результаты */}
      <div className="flex-1 overflow-y-auto space-y-3 custom-scroll">
        {/* Форма запуска */}
        <div className="bg-gray-900 rounded-xl p-4 space-y-3">
          <h2 className="text-white font-semibold text-sm uppercase tracking-wider">
            New Experiment
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-gray-400 text-xs block mb-1">Name *</label>
              <input
                className="w-full text-sm bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500"
                placeholder="e.g. Sugar taste activation"
                value={expName}
                onChange={(e) => setExpName(e.target.value)}
              />
            </div>
            <div>
              <label className="text-gray-400 text-xs block mb-1">Hypothesis</label>
              <select
                className="w-full text-sm bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5"
                value={selectedHypId || ''}
                onChange={(e) => setSelectedHypId(e.target.value || null)}
              >
                <option value="">No hypothesis</option>
                {hypotheses.map((h) => (
                  <option key={h.id} value={h.id}>{h.title}</option>
                ))}
              </select>
            </div>
          </div>
          <textarea
            className="w-full text-xs bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500 resize-none"
            placeholder="Description (optional)"
            rows={2}
            value={expDesc}
            onChange={(e) => setExpDesc(e.target.value)}
          />

          <div className="flex items-center gap-3">
            <button
              onClick={runExperiment}
              disabled={loading}
              className="flex-1 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white font-medium py-2.5 rounded-lg transition-colors"
            >
              {loading ? '⏳ Starting...' : '▶ Run Simulation'}
            </button>
            <div className="text-gray-500 text-xs">
              {neuExc.length} exc · {neuSlnc.length} slnc · {neuExc2.length} exc2
            </div>
          </div>

          {error && <div className="text-red-400 text-xs">{error}</div>}
        </div>

        {/* Активный результат */}
        {activeExp && <ResultsViewer experiment={activeExp} />}
      </div>

      {/* Правая панель — история */}
      <div className="w-64 flex-shrink-0 overflow-y-auto custom-scroll">
        <div className="bg-gray-900 rounded-xl p-4 space-y-2">
          <h2 className="text-white font-semibold text-sm uppercase tracking-wider mb-3">
            History
          </h2>
          {experiments.length === 0 && (
            <div className="text-gray-600 text-xs text-center py-4">No experiments yet</div>
          )}
          {experiments.map((exp) => (
            <button
              key={exp.id}
              onClick={() => setActiveExpId(exp.id)}
              className={`w-full text-left p-2 rounded-lg border transition-all ${
                exp.id === activeExpId
                  ? 'border-brand-500 bg-brand-900/20'
                  : 'border-gray-800 hover:border-gray-700 bg-gray-800/50'
              }`}
            >
              <div className="text-white text-xs font-medium truncate">{exp.name}</div>
              <div className="flex items-center justify-between mt-0.5">
                <StatusBadge status={exp.status} />
                <span className="text-gray-600 text-xs">
                  {new Date(exp.created_at).toLocaleTimeString()}
                </span>
              </div>
              {exp.result_summary && (
                <div className="text-gray-500 text-xs mt-0.5">
                  {exp.result_summary.total_neurons_active} active · {exp.result_summary.mean_network_rate.toFixed(2)} Hz
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending:   'text-yellow-400',
    running:   'text-blue-400 animate-pulse',
    completed: 'text-green-400',
    failed:    'text-red-400',
  };
  const icons: Record<string, string> = {
    pending: '⏳', running: '⚙', completed: '✓', failed: '✗',
  };
  return (
    <span className={`text-xs ${map[status] || 'text-gray-400'}`}>
      {icons[status] || '?'} {status}
    </span>
  );
}
