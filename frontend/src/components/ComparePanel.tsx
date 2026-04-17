import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts';
import { useStore } from '../store/useStore';
import { experimentsApi } from '../api/client';
import type { CompareResponse } from '../types';

export default function ComparePanel() {
  const { experiments, compareA, compareB, setCompareA, setCompareB } = useStore();
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const completed = experiments.filter((e) => e.status === 'completed');

  async function runCompare() {
    if (!compareA || !compareB) return;
    setLoading(true);
    setError('');
    try {
      const res = await experimentsApi.compare(compareA, compareB);
      setResult(res);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Compare failed');
    } finally {
      setLoading(false);
    }
  }

  const deltaData = result
    ? [...result.top_increased, ...result.top_decreased]
        .sort((a, b) => b.delta - a.delta)
        .slice(0, 20)
        .map((n) => ({
          id: `...${n.neuron_id.toString().slice(-5)}`,
          delta: n.delta,
          pct: n.delta_pct,
        }))
    : [];

  return (
    <div className="bg-gray-900 rounded-xl p-4 space-y-4">
      <h2 className="text-white font-semibold text-sm uppercase tracking-wider">
        Compare Experiments
      </h2>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-gray-500 text-xs block mb-1">Experiment A (baseline)</label>
          <select
            className="w-full text-xs bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5"
            value={compareA || ''}
            onChange={(e) => setCompareA(e.target.value || null)}
          >
            <option value="">Select...</option>
            {completed.map((e) => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-gray-500 text-xs block mb-1">Experiment B (test)</label>
          <select
            className="w-full text-xs bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5"
            value={compareB || ''}
            onChange={(e) => setCompareB(e.target.value || null)}
          >
            <option value="">Select...</option>
            {completed.map((e) => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        disabled={!compareA || !compareB || loading}
        onClick={runCompare}
        className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white text-xs py-2 rounded transition-colors"
      >
        {loading ? 'Comparing...' : 'Run statistical comparison'}
      </button>

      {error && <div className="text-red-400 text-xs">{error}</div>}

      {result && (
        <div className="space-y-4">
          {/* Сводка */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-gray-800 rounded p-2">
              <div className="text-white text-sm font-semibold">{result.network_rate_a.toFixed(3)}</div>
              <div className="text-gray-500 text-xs">A: {result.experiment_a}</div>
            </div>
            <div className="bg-gray-800 rounded p-2">
              <div className={`text-sm font-semibold ${result.network_rate_delta >= 0 ? 'text-neuro-exc' : 'text-red-400'}`}>
                {result.network_rate_delta >= 0 ? '+' : ''}{result.network_rate_delta.toFixed(3)} Hz
              </div>
              <div className="text-gray-500 text-xs">Δ network rate</div>
            </div>
            <div className="bg-gray-800 rounded p-2">
              <div className="text-white text-sm font-semibold">{result.network_rate_b.toFixed(3)}</div>
              <div className="text-gray-500 text-xs">B: {result.experiment_b}</div>
            </div>
          </div>

          {/* Статистика */}
          {result.p_value !== null && result.p_value !== undefined && (
            <div className={`text-xs rounded p-2 border ${
              result.significant
                ? 'bg-neuro-exc/10 border-neuro-exc/40 text-neuro-exc'
                : 'bg-gray-800 border-gray-700 text-gray-400'
            }`}>
              Mann-Whitney U test: p = {result.p_value.toFixed(6)}
              {result.significant ? ' ✅ Statistically significant (p < 0.05)' : ' (not significant)'}
            </div>
          )}

          {/* Delta bar chart */}
          <div>
            <h3 className="text-gray-400 text-xs uppercase tracking-widest mb-2">
              Firing rate difference (B − A)
            </h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={deltaData} margin={{ left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="id" tick={{ fontSize: 9, fill: '#6b7280' }} angle={-45} textAnchor="end" />
                <YAxis tick={{ fontSize: 9, fill: '#6b7280' }} unit=" Hz" />
                <ReferenceLine y={0} stroke="#6b7280" />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: '1px solid #374151', fontSize: 11 }}
                  formatter={(val: number) => [`${val.toFixed(3)} Hz`, 'Δ rate']}
                />
                <Bar dataKey="delta" radius={[2, 2, 0, 0]}>
                  {deltaData.map((d, i) => (
                    <Cell key={i} fill={d.delta >= 0 ? '#22c55e' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
