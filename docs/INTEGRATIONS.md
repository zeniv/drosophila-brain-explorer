# Integrations & External Resources

## FlyWire Connectome

### What is FlyWire?

[FlyWire](https://flywire.ai/) is an online platform hosting the complete connectome of the adult *Drosophila melanogaster* brain. Created by teams at Princeton, Cambridge, and Google, it provides interactive 3D visualization and programmatic access to 139,255 neurons and 50+ million synapses reconstructed from electron microscopy data.

### How This Platform Uses FlyWire

Every neuron in the simulator is identified by its **FlyWire root_id** — an 18-digit integer (e.g., `720575940621039145`). These IDs link directly to real biological neurons in the FlyWire database.

**Data files used:**

| File | FlyWire Version | Content |
|------|-----------------|---------|
| `connections.parquet` | v783 | 15M synapses with pre/post IDs, weights, excitatory/inhibitory |
| `completeness.csv` | v783 | 138,639 neurons with completion status |

### How to Get Neuron IDs

| Method | URL | Notes |
|--------|-----|-------|
| **Codex search** | [codex.flywire.ai](https://codex.flywire.ai) | Search by cell type, region, neurotransmitter |
| **Download CSV** | Codex → Download → neurons.csv | All 139,255 neurons with annotations |
| **Python (fafbseg)** | `pip install fafbseg-py` | `search_annotations('Gr5a')` → returns root_ids |
| **3D Viewer** | [flywire.ai](https://flywire.ai/) | Click neuron → Copy ID |

### Materialization Versions

| Version | Neurons | Used by |
|---------|---------|---------|
| v630 | 127,400 | Original paper (Shiu et al., bioRxiv 2023) |
| v783 | 138,639 | Edmond MPG data files (our simulator) |
| Latest | 139,255 | FlyWire Codex (current) |

> **Note:** root_ids may change between versions if a neuron was re-segmented. Always verify IDs via `/api/v1/neurons/search` before running simulations.

---

## Edmond MPG Open Research Data

**Repository:** [doi:10.17617/3.CZODIW](https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW)

This is where the connectome data files are hosted. Download and place in `./data/`:

```
data/
  connections.parquet   # 97 MB — synaptic connectivity
  completeness.csv      # 3 MB  — neuron metadata
```

The `results.zip` file on Edmond contains pre-computed simulation outputs from the original paper. It is **not required** for running new simulations.

---

## Brian2 Neural Simulator

**Website:** [brian2.readthedocs.io](https://brian2.readthedocs.io/)

Brian2 is a Python-based neural simulator that compiles network equations to C++ for fast execution. Our platform uses it to implement the Leaky Integrate-and-Fire model with alpha-synapse dynamics.

### Installation

Brian2 requires C++ compilation tools. Use conda:

```bash
conda env create -f backend/environment.yml
conda activate dro
```

### Mock Mode

When Brian2 is **not installed** (e.g., local development without conda), the simulator automatically falls back to mock mode:

- Uses real connectome data to find downstream neurons
- Generates realistic exponential firing rate distributions
- Returns properly structured `ExperimentResult` objects

This allows full UI/API development without the C++ compilation dependency.

---

## GitHub Repository

**URL:** [github.com/zeniv/drosophila-brain-explorer](https://github.com/zeniv/drosophila-brain-explorer)

### Original Model Code

**URL:** [github.com/philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)

The original Brian2 simulation code by Philip Shiu (UC Berkeley). Our platform wraps this model with a web interface, parameter management, and hypothesis tracking.

---

## Scientific References

### Primary Paper (Nature 2024)

> Shiu P.K. et al. "A Drosophila computational brain model reveals sensorimotor processing."
> *Nature* 634, 210–218 (2024). [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9)

### Preprint (bioRxiv 2023)

> Shiu P.K. et al. (2023). bioRxiv. [doi:10.1101/2023.05.02.539144](https://doi.org/10.1101/2023.05.02.539144)

Free access. Contains the full Methods section with exact model parameters and citations.

### FlyWire Connectome Paper

> Dorkenwald S. et al. "Neuronal wiring diagram of an adult brain."
> *Nature* 634, 124–138 (2024). [doi:10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y)

### Key Parameter Sources

| Parameter | Source |
|-----------|--------|
| V_rest, V_threshold, V_reset, R_mbr, C_mbr, T_refractory | Kakaria & de Bivort, 2017 |
| Tau (synapse decay) | Jürgensen et al., 2021 |
| T_dly (transmission delay) | Paul et al., 2015 |
| W_syn = 0.275 mV (free parameter) | Calibrated: 100 Hz GRN → ~80% max MN9 |

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/neurons/search?q=Gr5a` | Search neurons by type/region |
| `GET` | `/api/v1/neurons/presets` | Get preset neuron sets from Nature 2024 |
| `POST` | `/api/v1/experiments/` | Create and run simulation |
| `GET` | `/api/v1/experiments/{id}` | Get experiment status and results |
| `GET` | `/api/v1/experiments/` | List all experiments |
| `POST` | `/api/v1/experiments/compare` | Mann-Whitney U comparison |
| `POST` | `/api/v1/hypotheses/` | Create hypothesis |
| `GET` | `/api/v1/hypotheses/` | List hypotheses |
| `PATCH` | `/api/v1/hypotheses/{id}` | Update hypothesis status |
