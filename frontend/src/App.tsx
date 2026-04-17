import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ExperimentBuilder from './pages/ExperimentBuilder';
import HypothesisManager from './components/HypothesisManager';
import ComparePanel from './components/ComparePanel';

const queryClient = new QueryClient();

type Tab = 'builder' | 'hypotheses' | 'compare';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'builder',    label: 'Experiment',  icon: '🧪' },
  { id: 'hypotheses', label: 'Hypotheses',  icon: '💡' },
  { id: 'compare',    label: 'Compare',     icon: '⚖️' },
];

export default function App() {
  const [tab, setTab] = useState<Tab>('builder');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col h-screen bg-gray-950">
        {/* Header */}
        <header className="flex-shrink-0 border-b border-gray-800 px-6 py-3 flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🪰</span>
            <div>
              <h1 className="text-white font-semibold text-sm leading-tight">
                Drosophila Brain Explorer
              </h1>
              <p className="text-gray-500 text-xs">
                LIF model · FlyWire connectome · 125k neurons
              </p>
            </div>
          </div>

          {/* Tabs */}
          <nav className="flex gap-1 ml-6">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-1.5 rounded-lg text-sm transition-colors ${
                  tab === t.id
                    ? 'bg-brand-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </nav>

          {/* Ссылки */}
          <div className="ml-auto flex gap-3 text-xs text-gray-500">
            <a
              href="https://www.nature.com/articles/s41586-024-07763-9"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-400 transition-colors"
            >
              📄 Nature 2024
            </a>
            <a
              href="https://github.com/philshiu/Drosophila_brain_model"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-400 transition-colors"
            >
              🐙 GitHub
            </a>
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-400 transition-colors"
            >
              📚 API docs
            </a>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-hidden p-4">
          {tab === 'builder'    && <ExperimentBuilder />}
          {tab === 'hypotheses' && (
            <div className="max-w-2xl mx-auto h-full overflow-y-auto custom-scroll">
              <HypothesisManager />
            </div>
          )}
          {tab === 'compare' && (
            <div className="max-w-3xl mx-auto h-full overflow-y-auto custom-scroll">
              <ComparePanel />
            </div>
          )}
        </main>
      </div>
    </QueryClientProvider>
  );
}
