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

    def step(self, dt: float, q_cool_kw: float = 0.0) -> None:
        """
        Advance thermal model by dt seconds with q_cool_kw cooling input.

        Args:
            dt: Time step in seconds
            q_cool_kw: Cooling power supplied by CRAC/chiller (kW)

        Engineering notes:
            - Heat balance: Q_net = Q_server - Q_cool - Q_envelope
            - Q_envelope = UA_total * (T_room - T_ambient)
            - Temperature update: dT/dt = Q_net / thermal_mass
            - Energy integration for KPI tracking
        """
        # Total UA coefficient (envelope + infiltration)
        ua_total = self.cfg.ua_kw_per_c + self.infil_ua_kw_per_c

        # Heat flows (kW)
        q_server_kw = self.it_load_kw
        q_envelope_kw = ua_total * (self.temp_c - self.ambient_temp_c)

        # Net heat balance (kW)
        q_net_kw = q_server_kw - q_cool_kw - q_envelope_kw

        # Temperature update (°C/s = kW / (kJ/°C) * (1000 J/kJ))
        dt_temp_c = (q_net_kw * 1000.0 / self.cfg.thermal_mass_kj_per_c) * dt
        self.temp_c += dt_temp_c

        # Safety bounds
        self.temp_c = max(self.min_temp_c, min(self.max_temp_c, self.temp_c))

        # Energy integration (kWh = kW * hours)
        dt_hours = dt / 3600.0
        self.cooling_energy_kwh += q_cool_kw * dt_hours
        self.server_energy_kwh += q_server_kw * dt_hours

        # Time tracking
        self.time_s += dt

    def get_state(self) -> dict:
        """
        Return current room state for telemetry/logging.

        Returns dictionary with all key thermal and energy states
        in engineering units (°C, kW, kWh, seconds).
        """
        return {
            'temp_c': self.temp_c,
            'ambient_temp_c': self.ambient_temp_c,
            'it_load_kw': self.it_load_kw,
            'infil_ua_kw_per_c': self.infil_ua_kw_per_c,
            'time_s': self.time_s,
            'cooling_energy_kwh': self.cooling_energy_kwh,
            'server_energy_kwh': self.server_energy_kwh,
            'thermal_mass_kj_per_c': self.cfg.thermal_mass_kj_per_c,
            'ua_kw_per_c': self.cfg.ua_kw_per_c
        }
