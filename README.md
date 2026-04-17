# 🪰 Drosophila Brain Explorer

Interactive web platform for simulating neural circuits of the *Drosophila melanogaster* brain using the full FlyWire connectome.

> **Based on:** [A Drosophila computational brain model reveals sensorimotor processing](https://www.nature.com/articles/s41586-024-07763-9) — *Nature, 2024*
>
> **Data:** [doi:10.17617/3.CZODIW](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW) — Edmond MPG Open Research Data
>
> **Original model:** [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)

## Features

- **Experiment Builder** — configure neuron activation/silencing with real-time parameter controls
- **Brian2 LIF simulation** — leaky integrate-and-fire model over 125k neurons / 50M synapses
- **Hypothesis Manager** — track scientific hypotheses, link to experiments, annotate for arXiv
- **Statistical Comparison** — Mann-Whitney U test between experimental conditions
- **Parameter Space Explorer** — grid search over simulation parameters
- **Full reproducibility** — every experiment saves complete parameter JSON

## Architecture

```
React (Vite + TypeScript + Tailwind)
    ↕ REST API
FastAPI (Python 3.11)
    ↕ Celery tasks
Brian2 simulator (LIF, C++ codegen)
    ↕
PostgreSQL + Redis
```

## Quick Start

### 1. Get the connectome data

```bash
# Download from Edmond MPG (doi:10.17617/3.CZODIW)
bash scripts/download_data.sh
```

Place files in `./data/`:
- `connections.parquet` — synaptic connectivity (~4 GB)
- `completeness.csv` — neuron metadata

### 2. Run with Docker Compose

```bash
docker compose up --build
```

Open: http://localhost

API docs: http://localhost/docs

### 3. Local development

**Backend:**
```bash
conda env create -f backend/environment.yml
conda activate dro
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # → http://localhost:3000
```

## Simulation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `t_run`   | 1000 ms | Simulation duration |
| `n_run`   | 30      | Number of trials |
| `v_th`    | -45 mV  | Spike threshold |
| `v_0`     | -52 mV  | Resting potential |
| `w_syn`   | 0.275 mV| Synapse weight |
| `r_poi`   | 150 Hz  | Poisson input rate |
| `t_mbr`   | 20 ms   | Membrane time constant |

## Example Experiments (from Nature 2024)

```python
# Sugar taste activation → feeding motor neurons
neu_exc = [720575940621039145]  # Gr5a GRN

# Antennal mechanosensory → grooming circuit
neu_exc = [720575940616452186]  # Johnston's organ

# Combined sugar + water (additivity hypothesis)
neu_exc = [720575940621039145, 720575940617946228]
```

## Citation

If you use this platform in your research, please cite:

```bibtex
@article{shiu2024drosophila,
  title={A Drosophila computational brain model reveals sensorimotor processing},
  author={Shiu, Philip K and others},
  journal={Nature},
  year={2024},
  doi={10.1038/s41586-024-07763-9}
}
```

## License

MIT — see [LICENSE](LICENSE)
