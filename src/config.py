"""Central configuration for the ART-12D model.

All quantities are expressed in SI units or in eV / GeV, with the conversion
factors defined explicitly below. Defaults reproduce the parameters of v30.md;
where the paper leaves a parameter free, the choice is documented in the
docstring of the corresponding field.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------
# Physical constants (CODATA 2022, rounded to what this model needs)
# --------------------------------------------------------------------------
H_EV_S = 4.135667696e-15          # Planck constant in eV*s
HZ_PER_EV = 1.0 / H_EV_S          # ~2.417989242e14 Hz/eV
EV_TO_GEV = 1e-9
GEV_TO_EV = 1e9
HC_EV_M = 1.239841984e-6          # h*c in eV*m
HBAR_C_EV_M = 1.973269804e-7      # hbar*c in eV*m
C_M_S = 299_792_458.0
C_KM_S = 299_792.458
ELECTRON_MASS_EV = 510_998.95
PLANCK_MASS_GEV = 1.220910e19
K_B_EV_K = 8.617333262e-5
EV_J = 1.602176634e-19
EPSILON_0 = 8.8541878128e-12

# --------------------------------------------------------------------------
# Tables taken from v30.md (source of truth for the numerical audit)
# --------------------------------------------------------------------------
PAPER_MODE_MASSES_EV: tuple[float, float, float] = (1e-5, 1e-4, 1e-3)
PAPER_RESONANCES_HZ: tuple[float, float, float] = (16.0e9, 36.8e9, 57.6e9)

#: "The six forms of dark matter" table (v30.md, Part III).
PAPER_DARK_MATTER_FORMS: tuple[dict[str, Any], ...] = (
    {"form": "Axion", "kk_mode": "n=1", "mass_ev": 1e-5, "interaction": "weak", "role": "cold dark matter"},
    {"form": "KK mode 2", "kk_mode": "n=2", "mass_ev": 1e-4, "interaction": "weak", "role": "warm dark matter"},
    {"form": "KK mode 3", "kk_mode": "n=3", "mass_ev": 1e-3, "interaction": "weak", "role": "hot dark matter"},
    {"form": "Sterile neutrino", "kk_mode": "n=4", "mass_ev": 1.0e4, "interaction": "very weak", "role": "cold dark matter"},
    {"form": "Tachyonic mode", "kk_mode": "n < mu_A R", "mass_ev": -1.0, "interaction": "unstable", "role": "transition"},
    {"form": "Primordial black hole", "kk_mode": "-", "mass_ev": 5.6e38, "interaction": "gravitational", "role": "compact dark matter"},
)

#: Acoustic bands associated with words (v30.md, "The word as field excitation").
#: The paper lists the Romanian terms; the key is the English translation.
PAPER_EMOTION_BANDS_HZ: dict[str, tuple[float, float]] = {
    "love": (200.0, 400.0),
    "fear": (500.0, 800.0),
    "healing": (300.0, 500.0),
    "death": (150.0, 300.0),
    "joy": (400.0, 600.0),
    "peace": (200.0, 350.0),
    "gratitude": (300.0, 500.0),
    "anger": (600.0, 800.0),
    "sadness": (400.0, 600.0),
    "envy": (600.0, 800.0),
}

#: "Therapeutic" frequencies mentioned in v30.md.
SOLFEGGIO_HZ: tuple[int, ...] = (432, 528, 639, 741, 852, 963)

#: Reference clocks (v30.md, "Time as vibration").
REFERENCE_CLOCKS_HZ: dict[str, float] = {
    "caesium-133": 9_192_631_770.0,
    "Schumann (historic)": 7.83,
    "Schumann (recent)": 12.0,
    "heart at rest": 1.2,
    "cortical gamma": 40.0,
    "respiration": 0.25,
}

#: Reception hierarchy by Phi (v30.md, "The hierarchy of reception").
PAPER_CONSCIOUSNESS_HIERARCHY: tuple[tuple[str, str], ...] = (
    ("Thermostat", "0"),
    ("C. elegans", "minimal"),
    ("Insect", "low"),
    ("Mouse", "moderate"),
    ("Dog", "high"),
    ("Corvid", "high"),
    ("Octopod", "distributed"),
    ("Human", "very high"),
    ("Trained human", "extended"),
)


@dataclass
class ATR12Config:
    """Run parameters.

    Fields marked ``PAPER`` reproduce values explicitly stated in v30.md.
    The others are model choices and are flagged as such.
    """

    # --- geometry --------------------------------------------------------
    n_dim_total: int = 12
    n_dim_observed: int = 4

    #: 1/R expressed in eV (R in natural units). Default 1e-5 eV, so that
    #: m_1 = 1/R = 1e-5 eV, exactly the "axion" mode of the paper.
    inv_r_ev: float = 1.0e-5

    #: Mass term of the akashic field. The paper calls it mu_A but gives no
    #: value; 0 keeps the pure KK spectrum (m_n = n/R). The tachyonic
    #: mechanism is demonstrated with ``tachyon_demo_mu_ev``.
    mu_a_ev: float = 0.0
    tachyon_demo_mu_ev: float = 1.5e-5

    #: Quartic self-coupling from the L_A Lagrangian in v30.md.
    lambda_a: float = 0.10

    # --- Yukawa coupling --------------------------------------------------
    m4_gev: float = 1.0e3
    m12_gev: float = 1.0e19
    yukawa_power: int = 5
    #: Wavefunction overlap factor between branes and KK modes.
    yukawa_overlap: float = 1.0

    # --- dark matter ------------------------------------------------------
    rho_dm_gev_cm3: float = 0.3          # Read (2014), cited in v30.md
    v_dm_km_s: float = 300.0
    body_area_m2: float = 0.7
    years_of_exposure: float = 1.0

    # --- consciousness field ---------------------------------------------
    alpha_c: float = 0.15                # 1/s, logistic growth rate
    c_max: float = 1.0
    beta_noise: float = 0.02
    dt_s: float = 0.01
    t_max_s: float = 120.0
    c_initial: float = 0.01

    # --- IIT / Phi --------------------------------------------------------
    n_nodes: int = 6
    glauber_beta: float = 2.0            # inverse temperature of the Glauber dynamics
    n_chains: int = 32
    n_samples_per_chain: int = 160
    burn_in_steps: int = 300
    phi_sizes: tuple[int, ...] = (3, 4, 5, 6, 7, 8)
    phi_network_seeds: int = 4
    cortex_inhibitory_fraction: float = 0.2
    cortex_weight_scale: float = 1.6
    cerebellum_layers: int = 3

    # --- EEG hyperscanning ------------------------------------------------
    f_gamma_hz: float = 40.0
    eeg_fs_hz: float = 250.0
    eeg_duration_s: float = 6.0
    eeg_noise_sd: float = 1.0
    #: Effective coupling to the common field; E[correlation] = gain^2 * empathy^2.
    #: 0.55 gives r ~ 0.25 for a pair with empathy ~0.9 (model assumption, not data).
    eeg_field_gain: float = 0.55
    empathy_gamma_hz: float = 2.0
    n_pairs: int = 20
    high_empathy_fraction: float = 0.5
    n_surrogates: int = 500
    band_halfwidth_hz: float = 5.0

    # --- word / sound -----------------------------------------------------
    g_sound: float = 1.0e-3
    word_gamma_hz: float = 40.0

    # --- execution ---------------------------------------------------------
    seed: int = 12

    # --- paths -------------------------------------------------------------
    figures_dir: Path = Path("figures")
    results_dir: Path = Path("results")

    # ---------------------------------------------------------------- utils
    @property
    def n_dim_compact(self) -> int:
        return self.n_dim_total - self.n_dim_observed

    @property
    def m1_ev(self) -> float:
        """Mass of the fundamental KK mode, m_1 = 1/R."""
        return self.inv_r_ev

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["figures_dir"] = str(self.figures_dir)
        data["results_dir"] = str(self.results_dir)
        return data

    def save_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ATR12Config":
        data = dict(data)
        for key in ("figures_dir", "results_dir"):
            if key in data:
                data[key] = Path(data[key])
        if "phi_sizes" in data:
            data["phi_sizes"] = tuple(int(x) for x in data["phi_sizes"])
        return cls(**data)

    def describe(self) -> str:
        return (
            f"ART-12D: {self.n_dim_total}D = {self.n_dim_observed}D x {self.n_dim_compact}D compact | "
            f"1/R = {self.m1_ev:.2e} eV | g_A = "
            f"{(self.m4_gev / self.m12_gev) ** self.yukawa_power:.2e} | seed={self.seed}"
        )


#: Default configuration used by ``run_atr12.py``.
DEFAULT_CONFIG = ATR12Config()
