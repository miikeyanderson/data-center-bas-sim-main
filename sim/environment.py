# sim/environment.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class RoomConfig:
    """
    Configuration for a (single) data hall zone.

    All power/energy in SI:
      - kW for rates, kWh for integrals
      - Temperature in °C
    """
    initial_temp_c: float = 24.0
    ambient_temp_c: float = 22.0

    # Thermal mass (kJ/°C). Higher -> slower temperature change.
    thermal_mass_kj_per_c: float = 2500.0

    # Envelope/U*A heat exchange coefficient (kW/°C)
    # Heat_out = UA * (T_room - T_ambient)
    ua_kw_per_c: float = 0.25

    # Baseline internal IT/server load (kW) – controller can change this
    it_load_kw: float = 40.0

    # Infiltration / door-open events add extra UA temporarily (kW/°C)
    infil_ua_kw_per_c: float = 0.0

    # Number of virtual sensors tied to this zone (for environment shaping)
    n_virtual_sensors: int = 3


class Room:
    """
    Discrete-time thermal model of a (single) data center room/zone.

    State update (per dt seconds):
        Heat balance (kW): Q_net = Q_server - Q_cool - Q_env
          where Q_env = UA * (T_room - T_ambient) + UA_infil *
          (T_room - T_ambient)

        dT/dt [°C/s] ≈ (Q_net [kJ/s]) / (C [kJ/°C])
        => T_next = T + (Q_net * 1000 / C) * dt

    Notes:
      - Cooling (q_cool_kw) is supplied by upstream CRAC model(s).
      - This model is control-friendly: deterministic, continuous, and
        has tunable gains.
      - Humidity/latent not modeled here; provide hooks for later.
    """

    def __init__(self, cfg: Optional[RoomConfig] = None,
                 seed: Optional[int] = None):
        self.cfg = cfg or RoomConfig()
        self.temp_c: float = self.cfg.initial_temp_c
        self.ambient_temp_c: float = self.cfg.ambient_temp_c

        # Dynamic (changeable during scenarios)
        self.it_load_kw: float = self.cfg.it_load_kw
        self.infil_ua_kw_per_c: float = self.cfg.infil_ua_kw_per_c

        # Integrators (useful for energy tracking / KPI)
        self.time_s: float = 0.0
        self.cooling_energy_kwh: float = 0.0  # integral of q_cool_kw
        self.server_energy_kwh: float = 0.0   # integral of it_load_kw

        # Limits/guards
        self.min_temp_c: float = 10.0
        self.max_temp_c: float = 40.0

        # Random seed for later stochastic events (kept for determinism)
        self._seed = seed