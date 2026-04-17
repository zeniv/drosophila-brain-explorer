import React from 'react';
import { useStore } from '../store/useStore';
import type { SimulationParams } from '../types';

interface ParamDef {
  key: keyof SimulationParams;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  description: string;
  group: 'time' | 'membrane' | 'synaptic';
}

const PARAMS: ParamDef[] = [
  // Time
  { key: 't_run',  label: 'Duration',        unit: 'ms',  min: 100,   max: 10000, step: 100,   group: 'time',     description: 'Simulation duration' },
  { key: 'n_run',  label: 'Trials',           unit: '#',   min: 1,     max: 200,   step: 1,     group: 'time',     description: 'Number of runs for statistics' },
  // Membrane
  { key: 'v_th',   label: 'Spike threshold',  unit: 'mV',  min: -65,   max: -20,   step: 0.5,   group: 'membrane', description: 'Membrane potential threshold' },
  { key: 'v_0',    label: 'Resting potential',unit: 'mV',  min: -80,   max: -30,   step: 0.5,   group: 'membrane', description: 'Resting membrane potential' },
  { key: 'v_rst',  label: 'Reset potential',  unit: 'mV',  min: -80,   max: -30,   step: 0.5,   group: 'membrane', description: 'Post-spike reset potential' },
  { key: 't_mbr',  label: 'Membrane τ',       unit: 'ms',  min: 1,     max: 100,   step: 1,     group: 'membrane', description: 'Membrane time constant' },
  { key: 'tau',    label: 'Synaptic τ',       unit: 'ms',  min: 0.5,   max: 50,    step: 0.5,   group: 'membrane', description: 'Synaptic time constant' },
  { key: 't_rfc',  label: 'Refractory',       unit: 'ms',  min: 0.5,   max: 20,    step: 0.1,   group: 'membrane', description: 'Refractory period' },
  { key: 't_dly',  label: 'Syn. delay',       unit: 'ms',  min: 0.1,   max: 10,    step: 0.1,   group: 'membrane', description: 'Synaptic transmission delay' },
  // Synaptic
  { key: 'w_syn',  label: 'Synapse weight',   unit: 'mV',  min: 0.01,  max: 2.0,   step: 0.01,  group: 'synaptic', description: 'Weight per synapse' },
  { key: 'r_poi',  label: 'Input rate',       unit: 'Hz',  min: 1,     max: 1000,  step: 5,     group: 'synaptic', description: 'Poisson input frequency' },
  { key: 'r_poi2', label: 'Input rate 2',     unit: 'Hz',  min: 0,     max: 1000,  step: 5,     group: 'synaptic', description: 'Secondary Poisson frequency' },
  { key: 'f_poi',  label: 'Poisson scale',    unit: 'x',   min: 10,    max: 2000,  step: 10,    group: 'synaptic', description: 'Poisson synapse scaling factor' },
];

const GROUP_LABELS = {
  time:     '⏱ Temporal',
  membrane: '⚡ Membrane',
  synaptic: '🔗 Synaptic',
};

const GROUP_COLORS = {
  time:     'border-brand-400',
  membrane: 'border-yellow-400',
  synaptic: 'border-neuro-exc',
};

export default function ParameterPanel() {
  const { params, setParam, resetParams } = useStore();

  const groups = ['time', 'membrane', 'synaptic'] as const;

  return (
    <div className="bg-gray-900 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm uppercase tracking-wider">
          Simulation Parameters
        </h2>
        <button
          onClick={resetParams}
          className="text-xs text-gray-400 hover:text-white transition-colors px-2 py-1 rounded border border-gray-700 hover:border-gray-500"
        >
          Reset defaults
        </button>
      </div>

      {groups.map((group) => (
        <div key={group} className={`border-l-2 ${GROUP_COLORS[group]} pl-3 space-y-3`}>
          <h3 className="text-gray-400 text-xs font-medium uppercase tracking-widest">
            {GROUP_LABELS[group]}
          </h3>
          {PARAMS.filter((p) => p.group === group).map((p) => (
            <ParamSlider key={p.key} def={p} value={params[p.key] as number} onChange={(v) => setParam(p.key, v as never)} />
          ))}
        </div>
      ))}
    </div>
  );
}

function ParamSlider({
  def,
  value,
  onChange,
}: {
  def: ParamDef;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="group">
      <div className="flex items-center justify-between mb-1">
        <label className="text-gray-300 text-xs font-medium" title={def.description}>
          {def.label}
        </label>
        <div className="flex items-center gap-1">
          <input
            type="number"
            value={value}
            min={def.min}
            max={def.max}
            step={def.step}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            className="w-20 text-right text-xs bg-gray-800 text-white border border-gray-700 rounded px-1 py-0.5 focus:outline-none focus:border-brand-500"
          />
          <span className="text-gray-500 text-xs w-8">{def.unit}</span>
        </div>
      </div>
      <input
        type="range"
        min={def.min}
        max={def.max}
        step={def.step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1 bg-gray-700 rounded appearance-none cursor-pointer accent-brand-500"
      />
      <div className="hidden group-hover:flex justify-between text-gray-600 text-xs mt-0.5">
        <span>{def.min}</span>
        <span>{def.description}</span>
        <span>{def.max}</span>
      </div>
    </div>
  );
}
