# sim/crac.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CRACStatus(Enum):
    """CRAC unit operational status."""
    OFF = "off"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


@dataclass
class CRACConfig:
    """
    Configuration for a Computer Room Air Conditioning (CRAC) unit.

    Engineering parameters:
    - q_rated_kw: Nominal cooling capacity at design conditions (kW)
    - efficiency_cop: Coefficient of Performance (cooling_kw / power_kw)
    - min_capacity_pct: Minimum stable output (% of rated)
    - startup_time_s: Time to reach full capacity from OFF (seconds)
    - shutdown_time_s: Time to completely stop from RUNNING (seconds)
    """
    unit_id: str = "CRAC-01"
    q_rated_kw: float = 50.0         # Rated cooling capacity (kW)
    efficiency_cop: float = 3.5      # Coefficient of Performance

    min_capacity_pct: float = 20.0   # Minimum stable output (%)
    max_capacity_pct: float = 100.0  # Maximum output (%)

    startup_time_s: float = 180.0    # Startup time (seconds)
    shutdown_time_s: float = 60.0    # Shutdown time (seconds)

    # Failure simulation parameters
    mtbf_hours: float = 8760.0       # Mean Time Between Failures (hours)
    mttr_hours: float = 4.0          # Mean Time To Repair (hours)


class CRACUnit:
    """
    CRAC (Computer Room Air Conditioning) unit model.

    Features:
    - Capacity modulation based on command percentage
    - Realistic startup/shutdown timing
    - Failure simulation with MTBF/MTTR
    - Energy consumption tracking
    - Status transitions (OFF/STARTING/RUNNING/STOPPING/FAILED)

    Engineering model:
    - q_cool_kw = cmd_pct * q_rated_kw * availability_factor
    - power_kw = q_cool_kw / COP (when running)
    - Startup/shutdown delays affect capacity availability
    """

    def __init__(self, cfg: Optional[CRACConfig] = None,
                 seed: Optional[int] = None):
        self.cfg = cfg or CRACConfig()

        # Control inputs
        self.enable: bool = False        # Enable command from BAS
        self.cmd_pct: float = 0.0        # Capacity command (0-100%)

        # Current state
        self.status: CRACStatus = CRACStatus.OFF
        self.q_cool_kw: float = 0.0      # Actual cooling output (kW)
        self.power_kw: float = 0.0       # Electrical power consumption (kW)
        self.availability: float = 1.0   # Availability factor (0-1)

        # Timing state
        self.transition_timer_s: float = 0.0
        self.runtime_hours: float = 0.0
        self.energy_kwh: float = 0.0

        # Failure state
        self.failed: bool = False
        self.failure_timer_s: float = 0.0
        self.next_failure_hours: float = self.cfg.mtbf_hours

        # Random seed for failure simulation
        self._seed = seed

        # Performance tracking
        self.starts_count: int = 0
        self.total_runtime_hours: float = 0.0

    def step(self, dt: float) -> None:
        """
        Update CRAC unit state for one simulation timestep.

        Args:
            dt: Time step in seconds

        Engineering sequence:
        1. Process failure simulation
        2. Handle status transitions
        3. Calculate capacity and power
        4. Update energy and runtime
        """
        dt_hours = dt / 3600.0

        # Update failure simulation
        self._update_failure_simulation(dt_hours)

        # Handle status transitions
        self._update_status_transitions(dt)

        # Calculate cooling output based on current status
        self._calculate_cooling_output()

        # Calculate power consumption
        self._calculate_power_consumption()

        # Update energy and runtime tracking
        if self.status == CRACStatus.RUNNING:
            self.runtime_hours += dt_hours
            self.total_runtime_hours += dt_hours

        self.energy_kwh += self.power_kw * dt_hours

    def _update_failure_simulation(self, dt_hours: float) -> None:
        """Update failure state based on MTBF/MTTR."""
        if self.failed:
            self.failure_timer_s -= dt_hours * 3600.0
            if self.failure_timer_s <= 0:
                # Repair complete
                self.failed = False
                self.status = CRACStatus.OFF
                self.next_failure_hours = self.cfg.mtbf_hours
        else:
            # Check for random failure
            self.next_failure_hours -= dt_hours
            if (self.next_failure_hours <= 0 and
                    self.status == CRACStatus.RUNNING):
                self.failed = True
                self.status = CRACStatus.FAILED
                self.failure_timer_s = self.cfg.mttr_hours * 3600.0

    def _update_status_transitions(self, dt: float) -> None:
        """Handle startup/shutdown timing and status transitions."""
        if self.failed:
            self.status = CRACStatus.FAILED
            return

        if self.enable and not self.failed:
            if self.status == CRACStatus.OFF:
                self.status = CRACStatus.STARTING
                self.transition_timer_s = self.cfg.startup_time_s
                self.starts_count += 1
            elif self.status == CRACStatus.STARTING:
                self.transition_timer_s -= dt
                if self.transition_timer_s <= 0:
                    self.status = CRACStatus.RUNNING
                    self.transition_timer_s = 0.0
        else:
            if self.status in [CRACStatus.RUNNING, CRACStatus.STARTING]:
                self.status = CRACStatus.STOPPING
                self.transition_timer_s = self.cfg.shutdown_time_s
            elif self.status == CRACStatus.STOPPING:
                self.transition_timer_s -= dt
                if self.transition_timer_s <= 0:
                    self.status = CRACStatus.OFF
                    self.transition_timer_s = 0.0

    def _calculate_cooling_output(self) -> None:
        """Calculate actual cooling output based on status and command."""
        if self.status == CRACStatus.RUNNING:
            # Clamp command to operating limits
            clamped_cmd = max(self.cfg.min_capacity_pct,
                              min(self.cfg.max_capacity_pct, self.cmd_pct))

            # Calculate cooling output
            capacity_fraction = clamped_cmd / 100.0
            self.q_cool_kw = (capacity_fraction * self.cfg.q_rated_kw *
                              self.availability)
        elif self.status == CRACStatus.STARTING:
            # Partial capacity during startup
            startup_progress = 1.0 - (self.transition_timer_s /
                                      self.cfg.startup_time_s)
            capacity_fraction = (self.cmd_pct / 100.0) * startup_progress
            self.q_cool_kw = (capacity_fraction * self.cfg.q_rated_kw *
                              self.availability)
        else:
            # No cooling when OFF, STOPPING, or FAILED
            self.q_cool_kw = 0.0

    def _calculate_power_consumption(self) -> None:
        """Calculate electrical power consumption."""
        if self.q_cool_kw > 0 and self.cfg.efficiency_cop > 0:
            # Power = Cooling / COP + auxiliary loads
            self.power_kw = self.q_cool_kw / self.cfg.efficiency_cop

            # Add auxiliary power (fans, controls) - typically 5-10% of rated
            aux_power = 0.05 * self.cfg.q_rated_kw
            self.power_kw += aux_power
        else:
            # Standby power for controls only
            self.power_kw = 0.5  # kW standby power

    def force_failure(self, duration_hours: Optional[float] = None) -> None:
        """Force unit failure for testing/scenario purposes."""
        self.failed = True
        self.status = CRACStatus.FAILED
        self.failure_timer_s = ((duration_hours or self.cfg.mttr_hours) *
                                3600.0)

    def clear_failure(self) -> None:
        """Clear failure state (maintenance override)."""
        self.failed = False
        self.failure_timer_s = 0.0
        self.status = CRACStatus.OFF
        self.next_failure_hours = self.cfg.mtbf_hours

    def get_state(self) -> dict:
        """
        Return current CRAC state for telemetry/logging.

        Returns comprehensive state including capacity, power, status,
        and maintenance metrics.
        """
        return {
            'unit_id': self.cfg.unit_id,
            'status': self.status.value,
            'enable': self.enable,
            'cmd_pct': self.cmd_pct,
            'q_cool_kw': self.q_cool_kw,
            'power_kw': self.power_kw,
            'availability': self.availability,
            'failed': self.failed,
            'runtime_hours': self.runtime_hours,
            'energy_kwh': self.energy_kwh,
            'starts_count': self.starts_count,
            'transition_timer_s': self.transition_timer_s,
            'next_failure_hours': self.next_failure_hours,
            'efficiency_cop': self.cfg.efficiency_cop,
            'q_rated_kw': self.cfg.q_rated_kw
        }
