# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git

Optional (for real simulations):
- Conda / Miniconda (for Brian2 with C++ codegen)
- Docker Desktop (for production deployment)

## Local Development Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/zeniv/drosophila-brain-explorer.git
cd drosophila-brain-explorer
```

### 2. Download connectome data

Download from [Edmond MPG](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW):

- `Connectivity_783.parquet` → rename to `data/connections.parquet`
- `Completeness_783.csv` → rename to `data/completeness.csv`

### 3. Backend setup

```bash
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv pydantic-settings
pip install numpy pandas pyarrow scipy

# Start the backend
uvicorn app.main:app --reload --port 8000
```

The backend runs in **mock mode** without Brian2 — it uses real connectome topology but generates synthetic firing rates. This is sufficient for UI development.

### 4. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Opens at http://localhost:3000 with API proxy to http://localhost:8000.

### 5. Verify

- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Try a preset: click "Sugar taste (Gr5a)" → Run Simulation

## Installing Brian2 (for real simulations)

Brian2 requires C++ compilation. Use conda:

```bash
conda env create -f backend/environment.yml
conda activate dro
cd backend
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
dro/
  backend/
    app/
      main.py                 # FastAPI entry point
      core/
        config.py             # Settings from .env
        database.py           # SQLAlchemy async
        celery_app.py         # Task queue config
      api/
        experiments.py        # Simulation endpoints
        hypotheses.py         # Hypothesis CRUD
        neurons.py            # Neuron search
      models/
        experiment.py         # ORM models
        schemas.py            # Pydantic schemas
      services/
        simulation.py         # Brian2 wrapper + mock
      tasks/
        simulation_task.py    # Celery async task
    .env.dev                  # Dev environment vars
    environment.yml           # Conda env (with Brian2)
    requirements.txt          # pip requirements
  frontend/
    src/
      App.tsx                 # Main tabs component
      api/client.ts           # Axios API client
      store/useStore.ts       # Zustand state
      types/index.ts          # TypeScript types
      pages/
        ExperimentBuilder.tsx # Main experiment page
      components/
        ParameterPanel.tsx    # Parameter sliders
        NeuronSelector.tsx    # Neuron picker
        ResultsViewer.tsx     # Charts
        HypothesisManager.tsx # Hypothesis UI
        ComparePanel.tsx      # Comparison UI
    vite.config.ts            # Vite + proxy config
    tailwind.config.js        # Tailwind CSS
  data/                       # Connectome files (not in git)
  docs/                       # Documentation
  scripts/                    # Utility scripts
  nginx/                      # Production Nginx config
  docker-compose.yml          # Production stack
  docker-compose.dev.yml      # Dev stack (pg + redis)
```

## Environment Variables

See `.env.example` for all variables. For local dev, the backend reads `.env.dev`:

```env
DATABASE_URL=sqlite+aiosqlite:///./dro_dev.db
REDIS_URL=redis://localhost:6379/0
PATH_CONNECTOME=../data/connections.parquet
PATH_COMPLETENESS=../data/completeness.csv
DEBUG=true
```

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Building for Production

```bash
# Frontend build
cd frontend
npm run build   # → dist/

# Docker Compose (full stack)
docker compose up --build
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `Brian2 not installed` | Expected in dev — mock mode auto-activates |
| `Port 8000 occupied` | Use `--port 8001` and update `vite.config.ts` proxy |
| `KeyError: 'root_id'` | Data file has `Unnamed: 0` column — handled by code |
| `*.parquet not found` | Download from Edmond MPG, place in `data/` |
| Frontend chunk warning | Already handled by `manualChunks` in vite.config.ts |
