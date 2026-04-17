import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { hypothesesApi } from '../api/client';
import type { Hypothesis, HypothesisStatus } from '../types';

const STATUS_CONFIG: Record<HypothesisStatus, { label: string; color: string; icon: string }> = {
  untested:            { label: 'Untested',            icon: '⬜', color: 'text-gray-400  border-gray-600' },
  confirmed:           { label: 'Confirmed',           icon: '✅', color: 'text-green-400 border-green-700' },
  refuted:             { label: 'Refuted',             icon: '❌', color: 'text-red-400   border-red-700'   },
  requires_validation: { label: 'Needs validation',    icon: '🔬', color: 'text-yellow-400 border-yellow-700' },
};

const ARXIV_SECTIONS = ['Introduction', 'Methods', 'Results', 'Discussion', 'Supplementary'];

export default function HypothesisManager() {
  const { hypotheses, setHypotheses, upsertHypothesis } = useStore();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', prediction: '', arxiv_section: '' });
  const [expanded, setExpanded] = useState<string | null>(null);

  async function submit() {
    if (!form.title) return;
    const hyp = await hypothesesApi.create(form);
    upsertHypothesis(hyp);
    setForm({ title: '', description: '', prediction: '', arxiv_section: '' });
    setShowForm(false);
  }

  async function updateStatus(hyp: Hypothesis, status: HypothesisStatus) {
    const updated = await hypothesesApi.update(hyp.id, { status });
    upsertHypothesis(updated);
  }

  return (
    <div className="bg-gray-900 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm uppercase tracking-wider">
          Hypotheses
        </h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="text-xs bg-brand-700 hover:bg-brand-600 text-white px-3 py-1 rounded transition-colors"
        >
          + New hypothesis
        </button>
      </div>

      {/* Форма создания */}
      {showForm && (
        <div className="bg-gray-800 rounded-lg p-3 space-y-2 border border-gray-700">
          <input
            className="w-full text-sm bg-gray-900 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500"
            placeholder="Hypothesis title *"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <textarea
            className="w-full text-xs bg-gray-900 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500 resize-none"
            placeholder="Description..."
            rows={2}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <textarea
            className="w-full text-xs bg-gray-900 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500 resize-none"
            placeholder="Prediction: what do you expect to see?"
            rows={2}
            value={form.prediction}
            onChange={(e) => setForm({ ...form, prediction: e.target.value })}
          />
          <select
            className="w-full text-xs bg-gray-900 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500"
            value={form.arxiv_section}
            onChange={(e) => setForm({ ...form, arxiv_section: e.target.value })}
          >
            <option value="">arXiv section (optional)</option>
            {ARXIV_SECTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <div className="flex gap-2">
            <button onClick={submit} className="flex-1 bg-neuro-exc/80 hover:bg-neuro-exc text-white text-xs py-1.5 rounded transition-colors">
              Create
            </button>
            <button onClick={() => setShowForm(false)} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs py-1.5 rounded transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Список гипотез */}
      {hypotheses.length === 0 && (
        <div className="text-center text-gray-600 text-xs py-6">
          No hypotheses yet. Create one to track your scientific ideas.
        </div>
      )}

      <div className="space-y-2">
        {hypotheses.map((hyp) => {
          const cfg = STATUS_CONFIG[hyp.status];
          const isOpen = expanded === hyp.id;

          return (
            <div key={hyp.id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <button
                className="w-full text-left px-3 py-2 flex items-center gap-2 hover:bg-gray-750 transition-colors"
                onClick={() => setExpanded(isOpen ? null : hyp.id)}
              >
                <span className="text-sm">{cfg.icon}</span>
                <span className="flex-1 text-white text-xs font-medium">{hyp.title}</span>
                {hyp.arxiv_section && (
                  <span className="text-gray-500 text-xs bg-gray-700 px-1.5 py-0.5 rounded">
                    §{hyp.arxiv_section}
                  </span>
                )}
                <span className="text-gray-400 text-xs">{isOpen ? '▲' : '▼'}</span>
              </button>

              {isOpen && (
                <div className="px-3 pb-3 space-y-2 border-t border-gray-700 pt-2">
                  {hyp.description && (
                    <p className="text-gray-400 text-xs">{hyp.description}</p>
                  )}
                  {hyp.prediction && (
                    <div className="bg-gray-900 rounded p-2">
                      <span className="text-gray-500 text-xs">Prediction: </span>
                      <span className="text-brand-300 text-xs">{hyp.prediction}</span>
                    </div>
                  )}
                  {hyp.notes && (
                    <div className="bg-gray-900 rounded p-2">
                      <span className="text-gray-500 text-xs">Notes: </span>
                      <span className="text-gray-300 text-xs">{hyp.notes}</span>
                    </div>
                  )}

                  {/* Смена статуса */}
                  <div>
                    <div className="text-gray-500 text-xs mb-1">Status</div>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(STATUS_CONFIG).map(([st, c]) => (
                        <button
                          key={st}
                          onClick={() => updateStatus(hyp, st as HypothesisStatus)}
                          className={`text-xs px-2 py-0.5 rounded border transition-all ${
                            hyp.status === st
                              ? c.color + ' bg-gray-700'
                              : 'border-gray-700 text-gray-500 hover:text-gray-300'
                          }`}
                        >
                          {c.icon} {c.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Связанные эксперименты */}
                  {(hyp.experiment_ids?.length ?? 0) > 0 && (
                    <div className="text-xs text-gray-500">
                      {hyp.experiment_ids!.length} linked experiment(s)
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
