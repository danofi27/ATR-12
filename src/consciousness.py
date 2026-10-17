"""The consciousness field and integrated information (Phi).

Two components, both from v30.md:

1. Phenomenological dynamics of the consciousness field
       dC/dt = alpha * C * (1 - C/C_max) + beta * eta(t)
   The equation is logistic with noise; the paper declares it an axiom of the model.

2. Phi as information integrated across a cut (proxy for IIT 3.0)
       Phi = min_{P} < D_KL( p(s'|s) || p_P(s'|s) ) >_s
   where p_P is the model in which the links between the blocks of partition P
   are removed. This is a tractable proxy, not exact IIT 3.0 Phi: it uses
   stochastic binary (Glauber) units and a single cut of the causal chain,
   which is enough for the qualitative cortex (recurrent) vs cerebellum
   (feedforward) comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .config import PAPER_CONSCIOUSNESS_HIERARCHY, ATR12Config

_EPS = 1e-12


# ---------------------------------------------------------------------------
# Minimal neural networks
# ---------------------------------------------------------------------------
def build_cortical_network(
    cfg: ATR12Config, n_nodes: int | None = None, seed: int | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Dense recurrent network with excitatory and inhibitory populations."""
    n = n_nodes or cfg.n_nodes
    rng = np.random.default_rng(cfg.seed if seed is None else seed)
    weights = rng.normal(size=(n, n)) * cfg.cortex_weight_scale / np.sqrt(n)
    signs = np.where(rng.random(n) < cfg.cortex_inhibitory_fraction, -1.0, 1.0)
    weights *= signs[np.newaxis, :]          # the sign belongs to the presynaptic neuron
    np.fill_diagonal(weights, 0.0)
    bias = rng.normal(scale=0.1, size=n)
    return weights, bias


def build_cerebellar_network(
    cfg: ATR12Config, n_nodes: int | None = None, seed: int | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Layered feedforward network: each unit receives only from the previous layer."""
    n = n_nodes or cfg.n_nodes
    rng = np.random.default_rng((cfg.seed if seed is None else seed) + 1)
    n_layers = max(2, min(cfg.cerebellum_layers, n))
    layer_of = np.array_split(np.arange(n), n_layers)
    layer_index = np.empty(n, dtype=int)
    for k, block in enumerate(layer_of):
        layer_index[block] = k

    weights = np.zeros((n, n))
    for i in range(n):
        if layer_index[i] == 0:
            continue
        sources = layer_of[layer_index[i] - 1]
        fan_in = min(2, len(sources))
        chosen = rng.choice(sources, size=fan_in, replace=False)
        weights[i, chosen] = rng.normal(size=fan_in) * 1.2 / np.sqrt(fan_in)
    bias = rng.normal(scale=0.1, size=n)
    return weights, bias


# ---------------------------------------------------------------------------
# Glauber dynamics and Phi
# ---------------------------------------------------------------------------
def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def glauber_sample(
    weights: np.ndarray,
    bias: np.ndarray,
    beta: float,
    n_chains: int,
    n_samples: int,
    burn_in: int,
    seed: int,
) -> np.ndarray:
    """Samples from the stationary distribution of s' ~ Bernoulli(sigmoid(beta (W s + b)))."""
    rng = np.random.default_rng(seed)
    n = weights.shape[0]
    state = rng.integers(0, 2, size=(n_chains, n)).astype(float)
    for _ in range(burn_in):
        prob = _sigmoid(beta * (state @ weights.T + bias))
        state = (rng.random((n_chains, n)) < prob).astype(float)
    samples = np.empty((n_chains, n_samples, n), dtype=float)
    for t in range(n_samples):
        prob = _sigmoid(beta * (state @ weights.T + bias))
        state = (rng.random((n_chains, n)) < prob).astype(float)
        samples[:, t, :] = state
    return samples.reshape(-1, n)


@dataclass
class PhiResult:
    """Result of the Phi measurement for one network."""

    phi: float
    min_partition: tuple[int, ...]
    per_partition: dict[int, float] = field(default_factory=dict)
    n_units: int = 0
    architecture: str = ""

    @property
    def phi_per_unit(self) -> float:
        return self.phi / self.n_units if self.n_units else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "architecture": self.architecture,
            "n_units": self.n_units,
            "phi": self.phi,
            "phi_per_unit": self.phi_per_unit,
            "min_partition_mask": list(self.min_partition),
            "n_partitions": len(self.per_partition),
        }


def _kl_bernoulli(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = np.clip(p, _EPS, 1.0 - _EPS)
    q = np.clip(q, _EPS, 1.0 - _EPS)
    return p * np.log(p / q) + (1.0 - p) * np.log((1.0 - p) / (1.0 - q))


def phi_cut(
    weights: np.ndarray,
    bias: np.ndarray,
    beta: float,
    samples: np.ndarray,
    architecture: str = "",
) -> PhiResult:
    """Phi = minimum over bipartitions of the KL divergence between full and cut model."""
    weights = np.asarray(weights, float)
    n = weights.shape[0]
    if n < 2:
        raise ValueError("at least 2 units are required")

    full_prob = _sigmoid(beta * (samples @ weights.T + bias))     # (M, n)
    index = np.arange(n)
    bits = ((np.arange(1 << n)[:, None] >> index[None, :]) & 1).astype(bool)

    per_partition: dict[int, float] = {}
    for mask in range(1, 1 << (n - 1)):          # unit 0 always stays in block A
        block_a = bits[mask]
        same_block = block_a[:, None] == block_a[None, :]
        cut_weights = weights * same_block
        part_prob = _sigmoid(beta * (samples @ cut_weights.T + bias))
        kl = _kl_bernoulli(full_prob, part_prob).sum(axis=1)
        per_partition[mask] = float(kl.mean())

    best_mask = min(per_partition, key=per_partition.get)
    block_a = bits[best_mask]
    return PhiResult(
        phi=per_partition[best_mask],
        min_partition=tuple(np.flatnonzero(block_a).tolist()),
        per_partition=per_partition,
        n_units=n,
        architecture=architecture,
    )


def measure_phi(
    cfg: ATR12Config,
    architecture: str = "cortex",
    n_nodes: int | None = None,
    seed: int | None = None,
) -> PhiResult:
    n = n_nodes or cfg.n_nodes
    seed = cfg.seed if seed is None else seed
    if architecture == "cortex":
        weights, bias = build_cortical_network(cfg, n, seed)
    elif architecture == "cerebellum":
        weights, bias = build_cerebellar_network(cfg, n, seed)
    else:
        raise ValueError("architecture must be 'cortex' or 'cerebellum'")

    samples = glauber_sample(
        weights, bias, cfg.glauber_beta,
        cfg.n_chains, cfg.n_samples_per_chain, cfg.burn_in_steps, seed + 7,
    )
    return phi_cut(weights, bias, cfg.glauber_beta, samples, architecture=architecture)


def architecture_comparison(cfg: ATR12Config, n_seeds: int | None = None) -> dict[str, Any]:
    """Phi for cortex vs cerebellum, averaged over several random networks.

    A single network has large variability across initialisations, so the
    comparison is reported as mean and standard deviation.
    """
    n_seeds = cfg.phi_network_seeds if n_seeds is None else n_seeds
    rows: list[dict[str, Any]] = []
    for n in cfg.phi_sizes:
        cortex = [measure_phi(cfg, "cortex", n_nodes=n, seed=cfg.seed + 1000 * k).phi for k in range(n_seeds)]
        cerebellum = [measure_phi(cfg, "cerebellum", n_nodes=n, seed=cfg.seed + 1000 * k).phi for k in range(n_seeds)]
        cortex_mean = float(np.mean(cortex))
        cerebellum_mean = float(np.mean(cerebellum))
        rows.append(
            {
                "n_units": n,
                "n_networks": n_seeds,
                "phi_cortex_mean": cortex_mean,
                "phi_cortex_sd": float(np.std(cortex, ddof=1)) if n_seeds > 1 else 0.0,
                "phi_cerebellum_mean": cerebellum_mean,
                "phi_cerebellum_sd": float(np.std(cerebellum, ddof=1)) if n_seeds > 1 else 0.0,
                "ratio": cortex_mean / cerebellum_mean if cerebellum_mean > 0 else float("inf"),
                "phi_per_unit_cortex": cortex_mean / n,
                "phi_per_unit_cerebellum": cerebellum_mean / n,
            }
        )
    return {"rows": rows, "n_seeds": n_seeds}


# ---------------------------------------------------------------------------
# Consciousness field dynamics
# ---------------------------------------------------------------------------
@dataclass
class FieldTrajectory:
    t: np.ndarray
    c: np.ndarray

    @property
    def final(self) -> float:
        return float(self.c[-1])

    @property
    def mean(self) -> float:
        return float(np.mean(self.c))

    @property
    def std(self) -> float:
        return float(np.std(self.c))


def simulate_consciousness_field(cfg: ATR12Config, seed: int | None = None) -> FieldTrajectory:
    """Euler-Maruyama integration of dC/dt = alpha C (1 - C/C_max) + beta eta(t)."""
    rng = np.random.default_rng(cfg.seed if seed is None else seed)
    n_steps = int(round(cfg.t_max_s / cfg.dt_s))
    t = np.arange(n_steps + 1) * cfg.dt_s
    c = np.empty(n_steps + 1)
    c[0] = cfg.c_initial
    sqrt_dt = np.sqrt(cfg.dt_s)
    for k in range(n_steps):
        drift = cfg.alpha_c * c[k] * (1.0 - c[k] / cfg.c_max)
        c[k + 1] = c[k] + cfg.dt_s * drift + cfg.beta_noise * sqrt_dt * rng.normal()
        if c[k + 1] < 0.0:
            c[k + 1] = -c[k + 1]
        if c[k + 1] > 1.5 * cfg.c_max:
            c[k + 1] = 1.5 * cfg.c_max
    return FieldTrajectory(t=t, c=c)


def steady_state(cfg: ATR12Config) -> float:
    """Fixed point of the noise-free equation: C* = C_max."""
    return cfg.c_max


def relaxation_time_s(cfg: ATR12Config, c0: float = 0.01) -> float:
    """Time needed to reach 95% of C_max starting from c0."""
    if not 0.0 < c0 < cfg.c_max:
        raise ValueError("c0 must be in (0, C_max)")
    return float(np.log(0.95 * (cfg.c_max - c0) / (0.05 * c0)) / cfg.alpha_c)


def consciousness_total(i_content: float, c_awareness: float) -> float:
    """C_total = I_content * C_awareness (v30.md, operational definition)."""
    if i_content < 0 or c_awareness < 0:
        raise ValueError("components must be non-negative")
    return float(i_content * c_awareness)


def heart_modulation(c0: float, beta: float, hrv: float) -> float:
    """C_coherent = C_0 * (1 + beta * HRV)."""
    return float(c0 * (1.0 + beta * hrv))


def receptor_gain(phi: float, half_saturation: float = 1.0, i_total: float = 1.0) -> float:
    """E(Phi) = I_total * Phi / (Phi + K): saturates at I_total."""
    if phi < 0 or half_saturation <= 0:
        raise ValueError("invalid arguments")
    return float(i_total * phi / (phi + half_saturation))


def hierarchy_table() -> list[dict[str, str]]:
    return [{"level": str(i), "system": s, "phi": p} for i, (s, p) in enumerate(PAPER_CONSCIOUSNESS_HIERARCHY)]


def summary(cfg: ATR12Config) -> dict[str, Any]:
    traj = simulate_consciousness_field(cfg)
    return {
        "steady_state": steady_state(cfg),
        "relaxation_time_s": relaxation_time_s(cfg),
        "field_final": traj.final,
        "field_mean": traj.mean,
        "field_std": traj.std,
        "cortex_vs_cerebellum": architecture_comparison(cfg),
    }
