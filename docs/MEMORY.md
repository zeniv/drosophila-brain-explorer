# Project Memory — Drosophila Brain Explorer

> This file is a fast-recovery context document. When starting a new Claude session,
> point it to this file: `@docs/MEMORY.md` — it contains everything needed to resume work.

## Project Identity

- **Name:** Drosophila Brain Explorer
- **Path:** `F:\work\code\dro`
- **GitHub:** https://github.com/zeniv/drosophila-brain-explorer
- **Owner:** Eugene (GitHub: zeniv)
- **Goal:** Web platform for simulating Drosophila brain circuits; produce arXiv publication
- **Based on:** Shiu et al., Nature 634, 210–218 (2024)

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | React 18 + TypeScript + Vite | Port 3000, proxy to backend |
| Styling | Tailwind CSS | |
| Charts | Recharts | Code-split via manualChunks |
| State | Zustand + React Query | |
| Backend | FastAPI (Python 3.11) | Port 8000 (or 8001 if occupied) |
| ORM | SQLAlchemy 2.x async | |
| DB (dev) | SQLite + aiosqlite | `dro_dev.db` in backend/ |
| DB (prod) | PostgreSQL 16 | via Docker Compose |
| Queue | Celery + Redis | dev: BackgroundTasks instead |
| Simulator | Brian2 2.7.1 (conda) | Falls back to mock mode |
| PDF gen | reportlab | `scripts/make_guide_pdf.py` |

## Key File Locations

```
F:\work\code\dro\
  backend\
    app\
      main.py                    # FastAPI entry, CORS, lifespan
      core\config.py             # Pydantic Settings, reads .env.dev
      core\database.py           # SQLAlchemy async engine
      api\experiments.py         # POST/GET experiments, compare (Mann-Whitney U)
      api\hypotheses.py          # CRUD hypotheses
      api\neurons.py             # Neuron search, presets
      models\experiment.py       # ORM: Experiment, Hypothesis
      models\schemas.py          # Pydantic: SimulationParams, ExperimentResult
      services\simulation.py     # DrosophilaSimulator — Brian2 wrapper + mock
    .env.dev                     # SQLite, local data paths
    environment.yml              # Conda env with Brian2
  frontend\
    src\App.tsx                  # 3-tab UI
    src\components\ParameterPanel.tsx  # 13 LIF sliders
    src\components\NeuronSelector.tsx  # FlyWire ID picker
    src\components\ResultsViewer.tsx   # Recharts firing rates
    src\components\HypothesisManager.tsx
    src\components\ComparePanel.tsx
    vite.config.ts               # Port 3000, proxy /api → 8001
  data\
    connections.parquet           # 97 MB, 15M synapses (NOT in git)
    completeness.csv              # 3 MB, 138k neurons (NOT in git)
  docs\
    ARCHITECTURE.md
    MODEL.md                      # Exact equations + parameters + named neurons
    INTEGRATIONS.md               # FlyWire, Edmond MPG, Brian2, API ref
    DEVELOPMENT.md
    MEMORY.md                     # ← this file
    pdf\Drosophila_Brain_Explorer_Guide.pdf  # 15 pages, Russian
  scripts\
    make_guide_pdf.py             # PDF generator (reportlab + Cyrillic)
  docker-compose.yml              # Production stack
  docker-compose.dev.yml          # Dev: pg + redis
  nginx\nginx.conf                # Reverse proxy + SSL
```

## Connectome Data

- **Source:** Edmond MPG — doi:10.17617/3.CZODIW
- **connections.parquet:** Columns `Presynaptic_ID, Postsynaptic_ID, Connectivity, Excitatory` — renamed in code to `pre_root_id, post_root_id, n_syn, excitatory`
- **completeness.csv:** Column `Unnamed: 0` — renamed in code to `root_id`
- **FlyWire version:** v783 in our data, v630 in original paper, latest ~v9xx on codex.flywire.ai

## LIF Model (exact parameters from Methods)

```
dv/dt = (g - (v - V_rest)) / T_mbr
dg/dt = -g / Tau
```

| Param | Value | Source |
|-------|-------|--------|
| V_rest | -52 mV | Kakaria & de Bivort, 2017 |
| V_threshold | -45 mV | Kakaria & de Bivort, 2017 |
| V_reset | -52 mV | Kakaria & de Bivort, 2017 |
| R_mbr | 10 MOhm | Kakaria & de Bivort, 2017 |
| C_mbr | 0.002 uF | Kakaria & de Bivort, 2017 |
| T_mbr | 20 ms | = R_mbr * C_mbr |
| T_refractory | 2.2 ms | Kakaria/Lazar |
| Tau | 5 ms | Jurgensen et al., 2021 |
| T_dly | 1.8 ms | Paul et al., 2015 |
| W_syn | 0.275 mV | **SINGLE FREE PARAMETER** (100 Hz GRN → ~80% max MN9) |

Protocol: 30 runs x 1000 ms, unilateral right hemisphere, Poisson input.

## Named Neuron Circuits

**Taste → Proboscis (sugar):**
GRN (Gr5a) → G2N-1 → Rattle → Usnea (neuropeptidergic!) → FMIn → Sternum → Bract 1/2 → Roundup/Roundtree/Rounddown → **MN9** (motor)

**Taste → Proboscis (water):**
GRN (Gr64f) → Fudog / Zorro / Phantom / Clavicle → shared path → **MN9**

**Grooming:**
JON (JO-C/E/F) → aBN1 / aBN2 → aDN1 → **aDN2** (grooming command)

## Preset Neuron IDs

| Preset | FlyWire IDs |
|--------|------------|
| Sugar taste (Gr5a) | 720575940621039145, 720575940614307712 |
| Water taste (Gr64f) | 720575940617946228, 720575940628354985 |
| Sugar + Water | all 4 above |
| Antennal grooming (JO) | 720575940616452186 |

## Known Issues & Fixes Applied

1. **Column renaming:** parquet has `Presynaptic_ID` not `pre_root_id` — fixed in `simulation.py:load_data()` and `neurons.py`
2. **Mock mode:** When Brian2 not installed, `_get_brian2()` raises RuntimeError → caught → `_mock_result()` uses real downstream neurons
3. **Port conflicts:** Port 8000 may be occupied → use 8001, update `vite.config.ts` proxy target
4. **SQLite threading:** `connect_args={"check_same_thread": False}` in `database.py`
5. **ES module warning:** `"type": "module"` added to `frontend/package.json`
6. **Chunk size:** Recharts 506KB → `manualChunks` in `vite.config.ts`

## Pending Work

- [ ] Deploy to Yandex Cloud (server + domain) — user deferred: "яндекс пока не нужен"
- [ ] Install Brian2 via conda for real (not mock) simulations
- [ ] Docker Desktop needs to be started for Docker Compose deployment
- [ ] Add more neuron presets (bitter Gr66a, Ir94e mechanosensory)
- [ ] Parameter space grid search UI (automated sweep over v_th/w_syn)
- [ ] Export experiment results as CSV/PDF for arXiv submission
- [ ] Add raster plot visualization (time × neuron scatter)

## Git History (key commits)

```
ef89b5a docs: add architecture, model reference, integrations, dev guide, and PDF
dc4503c fix: mock mode, SQLite dev config, real connectome column names
898bee1 perf: code splitting + fix ES module warning
e411087 fix: add missing config files
af5cbcf feat: initial Drosophila Brain Explorer platform
```

## Session Recovery Checklist

To resume work after a context reset:

1. Read this file: `@docs/MEMORY.md`
2. Check current state: `git status && git log --oneline -5`
3. Backend is at `F:\work\code\dro\backend`, venv at `backend\.venv`
4. Frontend is at `F:\work\code\dro\frontend`, deps in `node_modules`
5. Data files are in `F:\work\code\dro\data\` (not in git)
6. The user's language is Russian, code/docs in English
7. Goal: scientific platform for arXiv publication in neuroscience
