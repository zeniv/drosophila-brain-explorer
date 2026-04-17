import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ScatterChart, Scatter,
} from 'recharts';
import type { Experiment } from '../types';

interface Props {
  experiment: Experiment;
}

const STATUS_COLORS = {
  pending:   'bg-yellow-500/20 text-yellow-400 border-yellow-600',
  running:   'bg-blue-500/20 text-blue-400 border-blue-600 animate-pulse',
  completed: 'bg-neuro-exc/20 text-neuro-exc border-neuro-exc',
  failed:    'bg-red-500/20 text-red-400 border-red-600',
};

export default function ResultsViewer({ experiment }: Props) {
  const res = experiment.result_summary;

  const barData = useMemo(() => {
    if (!res) return [];
    return res.top_neurons.slice(0, 30).map((n) => ({
      id: `...${n.neuron_id.toString().slice(-5)}`,
      rate: n.mean_rate,
      std: n.std_rate,
      count: n.spike_count,
    }));
  }, [res]);

  return (
    <div className="bg-gray-900 rounded-xl p-4 space-y-4">
      {/* Заголовок */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-white font-semibold">{experiment.name}</h2>
          {experiment.description && (
            <p className="text-gray-400 text-xs mt-0.5">{experiment.description}</p>
          )}
        </div>
        <span className={`text-xs px-2 py-0.5 rounded border ${STATUS_COLORS[experiment.status]}`}>
          {experiment.status}
        </span>
      </div>

      {/* Ошибка */}
      {experiment.status === 'failed' && (
        <div className="bg-red-900/30 border border-red-700 rounded p-3 text-red-300 text-xs font-mono">
          {experiment.error_message}
        </div>
      )}

      {/* Ожидание */}
      {(experiment.status === 'pending' || experiment.status === 'running') && (
        <div className="flex items-center justify-center py-12 text-gray-500">
          <div className="text-center space-y-2">
            <div className="text-3xl">🧠</div>
            <div className="text-sm">Running Brian2 simulation...</div>
            <div className="text-xs text-gray-600">
              {experiment.params.n_run} trials × {experiment.params.t_run} ms
            </div>
          </div>
        </div>
      )}

      {/* Результаты */}
      {experiment.status === 'completed' && res && (
        <div className="space-y-5">
          {/* Метрики */}
          <div className="grid grid-cols-3 gap-3">
            <Metric label="Active neurons" value={res.total_neurons_active.toLocaleString()} />
            <Metric label="Mean network rate" value={`${res.mean_network_rate.toFixed(2)} Hz`} />
            <Metric label="Duration" value={`${res.duration_ms} ms`} />
          </div>

          {/* Bar chart — топ 30 нейронов */}
          <div>
            <h3 className="text-gray-400 text-xs uppercase tracking-widest mb-2">
              Top 30 neurons — firing rate
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="id"
                  tick={{ fontSize: 9, fill: '#6b7280' }}
                  angle={-45}
                  textAnchor="end"
                />
                <YAxis tick={{ fontSize: 9, fill: '#6b7280' }} unit=" Hz" />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: '1px solid #374151', fontSize: 11 }}
                  formatter={(val: number, name: string) => [
                    name === 'rate' ? `${val} Hz` : val,
                    name === 'rate' ? 'Mean rate' : 'Spike count',
                  ]}
                />
                <Bar dataKey="rate" radius={[2, 2, 0, 0]}>
                  {barData.map((_, i) => (
                    <Cell key={i} fill={`hsl(${140 - i * 4}, 70%, ${60 - i * 0.5}%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Таблица топ нейронов */}
          <div>
            <h3 className="text-gray-400 text-xs uppercase tracking-widest mb-2">
              Top neurons — detail
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-gray-300">
                <thead>
                  <tr className="text-gray-500 border-b border-gray-800">
                    <th className="text-left py-1 pr-4">#</th>
                    <th className="text-left py-1 pr-4">FlyWire ID</th>
                    <th className="text-right py-1 pr-4">Mean rate (Hz)</th>
                    <th className="text-right py-1 pr-4">±std</th>
                    <th className="text-right py-1">Spikes</th>
                  </tr>
                </thead>
                <tbody>
                  {res.top_neurons.slice(0, 20).map((n, i) => (
                    <tr key={n.neuron_id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                      <td className="py-1 pr-4 text-gray-600">{i + 1}</td>
                      <td className="py-1 pr-4 font-mono text-brand-400">{n.neuron_id}</td>
                      <td className="py-1 pr-4 text-right text-neuro-exc font-semibold">{n.mean_rate.toFixed(3)}</td>
                      <td className="py-1 pr-4 text-right text-gray-500">±{n.std_rate.toFixed(3)}</td>
                      <td className="py-1 text-right">{n.spike_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Параметры */}
          <details className="text-xs">
            <summary className="text-gray-500 cursor-pointer hover:text-gray-300">
              Simulation parameters (JSON)
            </summary>
            <pre className="mt-2 p-2 bg-gray-800 rounded text-gray-400 overflow-x-auto text-xs font-mono">
              {JSON.stringify(experiment.params, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3 text-center">
      <div className="text-white font-semibold text-lg">{value}</div>
      <div className="text-gray-500 text-xs mt-0.5">{label}</div>
    </div>
  );
}
