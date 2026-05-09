# Distributions# Family of Distributions

An interactive Python app for exploring probability distribution families. Adjust parameters with sliders and watch the curve update live.

---

## Requirements

- Python 3.8+
- matplotlib
- numpy
- scipy

Install dependencies:

```bash
pip install matplotlib numpy scipy
```

---

## Usage

```bash
python distributions.py
```

---

## Distributions included

| Distribution | Type | Parameters |
|---|---|---|
| Normal | Continuous | Mean (μ), Std dev (σ) |
| Beta | Continuous | Alpha (α), Beta (β) |
| Gamma | Continuous | Shape (k), Scale (θ) |
| Exponential | Continuous | Rate (λ) |
| Poisson | Discrete | Rate (λ) |
| Binomial | Discrete | Trials (n), Probability (p) |

---

## Interface

- **Radio buttons** (top right) — switch between distribution families
- **Sliders** (bottom) — tune parameters in real time
- **Stats panel** (bottom right) — shows mean, variance, std dev, and median
- **Plot** — continuous distributions render as a filled PDF curve; discrete ones as a bar PMF

---

## Notes

- Requires matplotlib 3.7+ (3.x `RadioButtons` API)
- The window uses an interactive backend — running in a headless environment (e.g. a server) will fail. Use a local Python install or set `matplotlib.use('TkAgg')` / `'Qt5Agg'` explicitly if needed.
