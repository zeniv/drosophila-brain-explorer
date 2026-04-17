# Computational Model Reference

## Leaky Integrate-and-Fire with Alpha-Synapse Dynamics

This document describes the exact computational model from:

> Shiu P.K. et al., *Nature* 634, 210–218 (2024)
> Full methods: bioRxiv [doi:10.1101/2023.05.02.539144](https://doi.org/10.1101/2023.05.02.539144), pages 21–23

## Equations

The model uses two coupled differential equations (alpha-synapse formulation):

```
dv/dt = (g - (v - V_resting)) / T_mbr     [membrane potential]
dg/dt = -g / Tau                            [synaptic current]
```

**Dynamics:**
- When a presynaptic neuron fires: `g → g + w` (instantaneous jump)
- `g` decays exponentially to 0 with time constant `Tau`
- `v` decays toward `V_resting + g`; when `g → 0`, `v → V_resting`
- When `v > V_threshold`: the neuron fires (spike), `v` is reset to `V_reset`
- After a spike, the neuron is inactive for `T_refractory` milliseconds

## Parameters (from Methods)

| Symbol | Value | Description | Source |
|--------|-------|-------------|--------|
| V_resting | -52 mV | Resting membrane potential | Kakaria & de Bivort, 2017 |
| V_reset | -52 mV | Reset potential after spike | Kakaria & de Bivort, 2017 |
| V_threshold | -45 mV | Spike threshold | Kakaria & de Bivort, 2017 |
| R_mbr | 10 MOhm | Membrane resistance | Kakaria & de Bivort, 2017 |
| C_mbr | 0.002 uF | Membrane capacitance | Kakaria & de Bivort, 2017 |
| T_mbr | 20 ms | Membrane time constant (= C_mbr x R_mbr) | Derived |
| T_refractory | 2.2 ms | Refractory period | Kakaria, 2017; Lazar, 2021 |
| Tau | 5 ms | Synapse decay time constant | Jurgensen et al., 2021 |
| T_dly | 1.8 ms | Spike transmission delay | Paul et al., 2015 |
| **W_syn** | **0.275 mV** | **Synaptic weight (single free parameter)** | Calibrated |

### W_syn Calibration

W_syn is the **only free parameter** in the model. All others are taken from experimental measurements or prior modeling studies.

W_syn was calibrated so that activation of sugar GRNs at 100 Hz produces approximately 80% of maximal MN9 firing rate, consistent with electrophysiological data (Dahanukar et al., 2007; Inagaki et al., 2012).

### Connection Weight Formula

```
w = sign * n_syn * W_syn
```

Where:
- `n_syn` = number of synapses between pre and post neurons (from FlyWire)
- `sign` = +1 (excitatory) or -1 (inhibitory)
- `W_syn` = 0.275 mV

## Neurotransmitter Classification

Neurotransmitter predictions from Eckstein et al. (2020):

1. For each neuron, examine all presynaptic sites (cleft score > 50)
2. Identify the highest neurotransmitter prediction at each site
3. If >50% of sites predict GABA or glutamate: neuron is **inhibitory** (sign = -1)
4. Otherwise: neuron is **excitatory** (sign = +1, typically acetylcholine)

**Limitation:** Each neuron is strictly excitatory OR inhibitory. Neuromodulatory neurons (dopaminergic, serotonergic, neuropeptidergic) are not accurately modeled.

## Simulation Protocol (from paper)

- **Trials:** 30 independent runs of 1000 ms each
- **Neurons:** All 127,400 proofread neurons from FlyWire v630
- **Activation:** Unilateral right hemisphere (more completely reconstructed)
- **Input:** Poisson-distributed spike trains at specified frequencies
- **Output:** Mean firing rate per neuron across all trials

## Known Circuits (Named Neurons)

### Taste → Proboscis Extension (Sugar Pathway)

```
GRN (Gr5a/Gr64f)
    |
    v
G2N-1 ──> Rattle ──> Usnea ──> FMIn
    |                               |
    v                               v
Sternum ──> Bract 1/2 ──> Roundup/tree/down
                                    |
                                    v
                                  MN9 (proboscis motor neuron)
                                  MN6 (labella extension)
```

### Antennal Grooming (Mechanosensory Pathway)

```
JON (JO-C / JO-E / JO-F)
    |
    v
aBN1 / aBN2 ──> aDN1 ──> aDN2 (grooming command)
```

## Model Limitations (from paper)

1. **No neuromodulation** — neuropeptidergic neurons (e.g., Usnea/Amontillado) not accurately modeled
2. **No gap junctions** — only chemical synapses represented
3. **No morphology** — neuron geometry ignored
4. **Basal rate = 0 Hz** — inhibition of an already-silent neuron has no effect
5. **Absolute rates unreliable** — interpret relative changes (e.g., delta firing rates between conditions)
6. **Single neurotransmitter per neuron** — co-release not modeled
