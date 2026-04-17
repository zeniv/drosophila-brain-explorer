# Drosophila Brain Explorer

Interactive web platform for simulating neural circuits of the *Drosophila melanogaster* brain using the full FlyWire connectome.

> **Based on:** [A Drosophila computational brain model reveals sensorimotor processing](https://www.nature.com/articles/s41586-024-07763-9) — *Nature* 634, 210–218 (2024)
>
> **Preprint (free access):** [bioRxiv 2023.05.02.539144](https://doi.org/10.1101/2023.05.02.539144) — full Methods with exact model parameters
>
> **Data:** [doi:10.17617/3.CZODIW](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW) — Edmond MPG Open Research Data
>
> **FlyWire Connectome:** [flywire.ai](https://flywire.ai/) | [Codex](https://codex.flywire.ai/) — neuron search & IDs
>
> **Original model:** [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)

## Features

- **Experiment Builder** — configure neuron activation/silencing with real-time parameter controls
- **Brian2 LIF simulation** — leaky integrate-and-fire with alpha-synapse dynamics, 125k neurons / 15M synapses
- **Mock mode** — realistic synthetic data when Brian2 is not installed (uses real connectome topology)
- **Hypothesis Manager** — track scientific hypotheses, link to experiments, annotate for arXiv
- **Statistical Comparison** — Mann-Whitney U test between experimental conditions
- **Named neuron presets** — pre-configured circuits from Nature 2024 (Gr5a, Gr64f, Johnston's organ)
- **Full reproducibility** — every experiment saves complete parameter JSON

## Architecture

```
React 18 + TypeScript + Tailwind + Recharts
              |  REST API
FastAPI + SQLAlchemy (async)
              |  BackgroundTasks / Celery
Brian2 simulator (LIF, alpha-synapse, C++ codegen)
              |
PostgreSQL (prod) / SQLite (dev) + Redis
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

## Quick Start

### 1. Get the connectome data

Download from [Edmond MPG](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW) and place in `./data/`:

```
data/
  connections.parquet    # 97 MB — 15M synapses
  completeness.csv       # 3 MB  — 138k neurons
```

### 2. Local development (no Docker, no Brian2 needed)

**Backend:**
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv pydantic-settings numpy pandas pyarrow scipy
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install && npm run dev   # http://localhost:3000
```

The simulator runs in **mock mode** — real connectome topology, synthetic firing rates.

### 3. Production with Docker Compose

```bash
docker compose up --build
```

Open: http://localhost &nbsp;|&nbsp; API docs: http://localhost/docs

### 4. Real simulations with Brian2

```bash
conda env create -f backend/environment.yml
conda activate dro
cd backend && uvicorn app.main:app --reload --port 8000
```

## Computational Model

LIF with alpha-synapse dynamics (Shiu et al., 2024):

```
dv/dt = (g - (v - V_rest)) / T_mbr     [membrane potential]
dg/dt = -g / Tau                         [synaptic current]
```

| Parameter | Default | Source |
|-----------|---------|--------|
| V_resting | -52 mV | Kakaria & de Bivort, 2017 |
| V_threshold | -45 mV | Kakaria & de Bivort, 2017 |
| T_mbr | 20 ms | C_mbr (0.002 uF) x R_mbr (10 MOhm) |
| Tau | 5 ms | Jurgensen et al., 2021 |
| T_dly | 1.8 ms | Paul et al., 2015 |
| T_refractory | 2.2 ms | Kakaria, 2017; Lazar, 2021 |
| **W_syn** | **0.275 mV** | **Single free parameter** |

W_syn is calibrated so 100 Hz sugar GRN activation produces ~80% max MN9 firing.

See [docs/MODEL.md](docs/MODEL.md) for the full model reference with named neuron circuits.

## FlyWire Integration

Neuron IDs come from the [FlyWire connectome](https://flywire.ai/). Search for neurons at [codex.flywire.ai](https://codex.flywire.ai/) by name or type, then use the 18-digit `root_id` in experiments.

See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) for details.

## Example Experiments

```python
# Sugar taste activation -> proboscis motor neurons
neu_exc = [720575940621039145]  # Gr5a GRN

# Antennal mechanosensory -> grooming circuit
neu_exc = [720575940616452186]  # Johnston's organ

# Combined sugar + water (additivity hypothesis)
neu_exc = [720575940621039145, 720575940617946228]
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, components, data flow |
| [docs/MODEL.md](docs/MODEL.md) | Computational model: equations, parameters, named circuits |
| [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) | FlyWire, Edmond MPG, Brian2, API reference |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Local setup, project structure, troubleshooting |
| [docs/pdf/](docs/pdf/) | PDF guide (Russian) with full platform walkthrough |

## Citation

```bibtex
@article{shiu2024drosophila,
  title={A Drosophila computational brain model reveals sensorimotor processing},
  author={Shiu, Philip K and others},
  journal={Nature},
  volume={634},
  pages={210--218},
  year={2024},
  doi={10.1038/s41586-024-07763-9}
}
```

## License

MIT
