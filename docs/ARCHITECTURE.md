# Architecture

## System Overview

Drosophila Brain Explorer is a full-stack web platform for simulating neural circuits of the *Drosophila melanogaster* brain using the complete FlyWire connectome (125,000+ neurons, 15M+ synapses).

```
                    +-------------------+
                    |    Web Browser     |
                    |   React + Vite    |
                    +--------+----------+
                             |
                        REST API
                             |
                    +--------v----------+
                    |  Nginx (reverse   |
                    |  proxy, SSL)      |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
     +--------v--------+        +----------v---------+
     |  FastAPI (8000)  |        | Static frontend    |
     |  app.main:app    |        | (nginx serves      |
     +---------+--------+        |  Vite build)       |
               |                 +--------------------+
      +--------+--------+
      |  SQLAlchemy ORM  |
      |  (async)         |
      +--------+---------+
               |
    +----------+----------+
    |                      |
+---v---+           +------v------+
| SQLite|           | PostgreSQL  |
| (dev) |           | (production)|
+-------+           +-------------+

               +
               |
     +---------v---------+
     |  Brian2 Simulator  |
     |  (C++ codegen)     |
     +--------------------+
               |
     +---------v---------+
     |  Connectome Data   |
     |  .parquet + .csv   |
     +--------------------+
```

## Component Details

### Frontend (React 18 + TypeScript)

| Component | File | Purpose |
|-----------|------|---------|
| `App` | `src/App.tsx` | Tab navigation (Experiment / Hypotheses / Compare) |
| `ExperimentBuilder` | `src/pages/ExperimentBuilder.tsx` | Main workflow: select neurons, set params, run |
| `ParameterPanel` | `src/components/ParameterPanel.tsx` | 13 LIF parameter sliders with validation |
| `NeuronSelector` | `src/components/NeuronSelector.tsx` | Search/preset neuron picker by FlyWire ID |
| `ResultsViewer` | `src/components/ResultsViewer.tsx` | Recharts bar/scatter plots of firing rates |
| `HypothesisManager` | `src/components/HypothesisManager.tsx` | CRUD for scientific hypotheses |
| `ComparePanel` | `src/components/ComparePanel.tsx` | Mann-Whitney U statistical comparison |

**State management:** Zustand (`src/store/useStore.ts`) — selected neurons, parameters, current experiment.

**API client:** Axios with React Query (`src/api/client.ts`) — caching, optimistic updates.

**Build:** Vite with code splitting (react-vendor, recharts, state).

### Backend (FastAPI + Python 3.11)

```
backend/
  app/
    main.py              # FastAPI app, CORS, lifespan
    core/
      config.py          # Pydantic Settings (.env)
      database.py        # SQLAlchemy async engine
      celery_app.py      # Celery + Redis config
    api/
      experiments.py     # POST/GET /experiments, /compare
      hypotheses.py      # CRUD /hypotheses
      neurons.py         # GET /neurons/search, /presets
    models/
      experiment.py      # ORM: Experiment, Hypothesis
      schemas.py         # Pydantic: SimulationParams, etc.
    services/
      simulation.py      # DrosophilaSimulator (Brian2 wrapper)
    tasks/
      simulation_task.py # Celery async task
```

**API prefix:** `/api/v1`

**Simulation flow:**
1. `POST /api/v1/experiments/` — creates DB record, launches `BackgroundTask`
2. `_run_in_background(exp_id)` — loads connectome, builds Brian2 network, runs N trials
3. On completion — updates DB with `ExperimentResult` JSON
4. `GET /api/v1/experiments/{id}` — polls status + results

**Mock mode:** When Brian2 is not installed (dev without conda), the simulator returns realistic synthetic data using real downstream neurons from the connectome.

### Database

| Environment | Engine | Connection |
|-------------|--------|------------|
| Development | SQLite + aiosqlite | `sqlite+aiosqlite:///./dro_dev.db` |
| Production | PostgreSQL 16 | `postgresql+asyncpg://...` |

**Tables:**
- `experiments` — id (UUID), name, status, params (JSON), result (JSON), timestamps
- `hypotheses` — id (UUID), title, prediction, status, linked experiment IDs

### Data Layer (Connectome)

| File | Format | Size | Content |
|------|--------|------|---------|
| `connections.parquet` | Apache Parquet | 97 MB | 15,091,983 synapses (pre_id, post_id, weight, excitatory) |
| `completeness.csv` | CSV | 3 MB | 138,639 neurons (root_id, completed status) |

**Source:** Edmond MPG — [doi:10.17617/3.CZODIW](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW)

Data is loaded once at worker startup and cached as class variables in `DrosophilaSimulator`.

### Deployment (Docker Compose)

```
docker-compose.yml:
  postgres   — PostgreSQL 16-Alpine, volume: pgdata
  redis      — Redis 7-Alpine, port 6379
  api        — FastAPI (gunicorn + uvicorn workers)
  worker     — Celery worker with Brian2
  frontend   — Nginx serving Vite build
  nginx      — Reverse proxy, SSL termination
```

## Data Flow

```
User selects neurons + params
        |
        v
POST /api/v1/experiments/
        |
        v
FastAPI creates DB record (status=pending)
        |
        v
BackgroundTask → DrosophilaSimulator.run_experiment()
        |
        v
Brian2: build NeuronGroup + Synapses + PoissonInput
        |
        v
Run N trials x T ms each
        |
        v
Aggregate spikes → ExperimentResult (top neurons, rates)
        |
        v
Update DB record (status=completed, result=JSON)
        |
        v
Frontend polls GET /experiments/{id} → renders charts
```

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + TypeScript | 18.x |
| Build | Vite | 5.x |
| Styling | Tailwind CSS | 3.x |
| Charts | Recharts | 2.x |
| State | Zustand | 4.x |
| API caching | TanStack React Query | 5.x |
| Backend | FastAPI | 0.110+ |
| ORM | SQLAlchemy | 2.x (async) |
| Task queue | Celery | 5.x |
| Simulator | Brian2 | 2.7.1 |
| Database | PostgreSQL / SQLite | 16 / 3 |
| Cache/Broker | Redis | 7.x |
| Reverse proxy | Nginx | 1.25 |
| Container | Docker Compose | v2 |
