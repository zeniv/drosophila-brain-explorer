import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { neuronsApi } from '../api/client';
import type { Preset } from '../types';

type NeuronRole = 'exc' | 'slnc' | 'exc2';

const ROLE_LABELS: Record<NeuronRole, string> = {
  exc:  '⚡ Excite',
  slnc: '🔇 Silence',
  exc2: '〰 Excite 2',
};
const ROLE_COLORS: Record<NeuronRole, string> = {
  exc:  'bg-neuro-exc/20 border-neuro-exc text-neuro-exc',
  slnc: 'bg-neuro-slnc/20 border-neuro-slnc text-neuro-slnc',
  exc2: 'bg-brand-500/20 border-brand-400 text-brand-300',
};

export default function NeuronSelector() {
  const { neuExc, neuSlnc, neuExc2, setNeuExc, setNeuSlnc, setNeuExc2 } = useStore();

  const [activeRole, setActiveRole]   = useState<NeuronRole>('exc');
  const [inputText, setInputText]     = useState('');
  const [searchQ, setSearchQ]         = useState('');
  const [searchRes, setSearchRes]     = useState<any[]>([]);
  const [presets, setPresets]         = useState<Preset[]>([]);
  const [showPresets, setShowPresets] = useState(false);

  const setters: Record<NeuronRole, (ids: number[]) => void> = {
    exc:  setNeuExc,
    slnc: setNeuSlnc,
    exc2: setNeuExc2,
  };
  const lists: Record<NeuronRole, number[]> = {
    exc:  neuExc,
    slnc: neuSlnc,
    exc2: neuExc2,
  };

  useEffect(() => {
    neuronsApi.presets().then((d) => setPresets(d.presets));
  }, []);

  useEffect(() => {
    if (searchQ.length < 2) { setSearchRes([]); return; }
    const t = setTimeout(() => {
      neuronsApi.search(searchQ).then((d) => setSearchRes(d.neurons || []));
    }, 300);
    return () => clearTimeout(t);
  }, [searchQ]);

  function addFromInput() {
    const ids = inputText
      .split(/[\s,;\n]+/)
      .map((s) => s.trim())
      .filter((s) => /^\d+$/.test(s))
      .map(Number);
    if (ids.length) {
      setters[activeRole]([...new Set([...lists[activeRole], ...ids])]);
      setInputText('');
    }
  }

  function addNeuron(id: number) {
    const cur = lists[activeRole];
    if (!cur.includes(id)) setters[activeRole]([...cur, id]);
  }

  function removeNeuron(role: NeuronRole, id: number) {
    setters[role](lists[role].filter((x) => x !== id));
  }

  function applyPreset(preset: Preset) {
    setNeuExc(preset.neu_exc);
    setNeuSlnc([]);
    setNeuExc2([]);
    setShowPresets(false);
  }

  return (
    <div className="bg-gray-900 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm uppercase tracking-wider">
          Neurons
        </h2>
        <button
          onClick={() => setShowPresets((v) => !v)}
          className="text-xs text-brand-400 hover:text-brand-200 transition-colors px-2 py-1 rounded border border-brand-700 hover:border-brand-500"
        >
          📋 Presets
        </button>
      </div>

      {/* Пресеты */}
      {showPresets && (
        <div className="space-y-2">
          {presets.map((p) => (
            <button
              key={p.name}
              onClick={() => applyPreset(p)}
              className="w-full text-left p-2 rounded bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-colors"
            >
              <div className="text-white text-xs font-medium">{p.name}</div>
              <div className="text-gray-400 text-xs">{p.description}</div>
            </button>
          ))}
        </div>
      )}

      {/* Роли */}
      <div className="flex gap-2">
        {(['exc', 'slnc', 'exc2'] as NeuronRole[]).map((role) => (
          <button
            key={role}
            onClick={() => setActiveRole(role)}
            className={`flex-1 text-xs py-1 px-2 rounded border transition-all ${
              activeRole === role
                ? ROLE_COLORS[role]
                : 'border-gray-700 text-gray-500 hover:text-gray-300'
            }`}
          >
            {ROLE_LABELS[role]}
            <span className="ml-1 opacity-60">({lists[role].length})</span>
          </button>
        ))}
      </div>

      {/* Поиск */}
      <div>
        <input
          type="text"
          placeholder="Search by cell type, region..."
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          className="w-full text-xs bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500"
        />
        {searchRes.length > 0 && (
          <div className="mt-1 bg-gray-800 border border-gray-700 rounded max-h-32 overflow-y-auto">
            {searchRes.map((n: any) => (
              <button
                key={n.id || n.root_id}
                onClick={() => addNeuron(n.id || n.root_id)}
                className="w-full text-left px-2 py-1 text-xs hover:bg-gray-700 flex justify-between"
              >
                <span className="text-brand-300">{n.cell_type || 'unknown'}</span>
                <span className="text-gray-500 font-mono">{n.id || n.root_id}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Ввод вручную */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="FlyWire IDs (comma separated)"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addFromInput()}
          className="flex-1 text-xs bg-gray-800 text-white border border-gray-700 rounded px-2 py-1.5 focus:outline-none focus:border-brand-500 font-mono"
        />
        <button
          onClick={addFromInput}
          className="text-xs bg-brand-600 hover:bg-brand-500 text-white px-3 py-1.5 rounded transition-colors"
        >
          Add
        </button>
      </div>

      {/* Чипы нейронов */}
      {(['exc', 'slnc', 'exc2'] as NeuronRole[]).map((role) =>
        lists[role].length > 0 ? (
          <div key={role}>
            <div className="text-gray-500 text-xs mb-1">{ROLE_LABELS[role]}</div>
            <div className="flex flex-wrap gap-1">
              {lists[role].map((id) => (
                <span
                  key={id}
                  className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${ROLE_COLORS[role]}`}
                >
                  <span className="font-mono">{id.toString().slice(-6)}</span>
                  <button
                    onClick={() => removeNeuron(role, id)}
                    className="opacity-50 hover:opacity-100 ml-0.5"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        ) : null
      )}
    </div>
  );
}
