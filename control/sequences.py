# control/sequences.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from sim.crac import CRACUnit, CRACStatus


class CRACRole(Enum):
    """CRAC unit roles in staging strategy."""
    LEAD = "lead"         # Primary unit, starts first
    LAG = "lag"           # Secondary unit, starts when lead insufficient
    STANDBY = "standby"   # Backup unit, starts only if others fail


@dataclass
class StagingConfig:
    """
    Configuration for CRAC staging and rotation strategy.

    BAS Engineering parameters:
    - temp_error_threshold: Error to trigger LAG staging (°C)
    - staging_delay_s: Time to wait before bringing LAG online (seconds)
    - rotation_runtime_hours: Hours to trigger role rotation
    - enable_rotation: Whether to rotate lead/lag roles
    """
    temp_error_threshold: float = 1.0     # °C error to stage LAG
    staging_delay_s: float = 300.0        # 5 minutes staging delay
    destaging_delay_s: float = 600.0      # 10 minutes destaging delay

    rotation_runtime_hours: float = 168.0  # 1 week rotation
    enable_rotation: bool = True

    # Hysteresis to prevent chatter
    staging_hysteresis: float = 0.2       # °C hysteresis
    destaging_hysteresis: float = 0.3     # °C hysteresis


@dataclass
class CRACAssignment:
    """Assignment of CRAC unit to role with timing tracking."""
    unit: CRACUnit
    role: CRACRole
    assigned_time: float = 0.0            # When role was assigned (hours)
    staging_timer_s: float = 0.0          # Timer for staging delays
    destaging_timer_s: float = 0.0        # Timer for destaging delays


class CRACSequencer:
    """
    Professional CRAC staging sequencer for data center applications.

    Features:
    - Lead/Lag/Standby role management
    - Automatic staging based on temperature error
    - Role rotation for even wear
    - Anti-short-cycle protection
    - Hysteresis to prevent chatter

    BAS Engineering Logic:
    1. LEAD starts first and handles base load
    2. LAG starts if temp error exceeds threshold for staging_delay
    3. STANDBY only starts if other units fail
    4. Roles rotate based on runtime to balance wear
    """

    def __init__(self, cracs: List[CRACUnit],
                 cfg: Optional[StagingConfig] = None):
        self.cfg = cfg or StagingConfig()

        # Initialize CRAC assignments
        self.assignments: List[CRACAssignment] = []
        for i, crac in enumerate(cracs):
            if i == 0:
                role = CRACRole.LEAD
            elif i == 1:
                role = CRACRole.LAG
            else:
                role = CRACRole.STANDBY

            self.assignments.append(CRACAssignment(
                unit=crac,
                role=role,
                assigned_time=0.0
            ))

        # Control state
        self.setpoint_c: float = 22.0
        self.current_temp_c: float = 22.0
        self.temp_error: float = 0.0

        # Staging state
        self.lag_staged: bool = False
        self.standby_staged: bool = False

        # Performance tracking
        self.total_runtime_hours: float = 0.0
        self.rotation_count: int = 0

    def update(self, dt: float, setpoint_c: float, measurement_c: float,
               pid_output_pct: float) -> None:
        """
        Update CRAC staging sequence.

        Args:
            dt: Time step (seconds)
            setpoint_c: Temperature setpoint (°C)
            measurement_c: Current temperature (°C)
            pid_output_pct: PID controller output (0-100%)

        Engineering sequence:
        1. Update temperature error and timers
        2. Handle role rotation if enabled
        3. Process staging/destaging logic
        4. Distribute load among active units
        """
        dt_hours = dt / 3600.0
        self.total_runtime_hours += dt_hours

        # Update temperature tracking
        self.setpoint_c = setpoint_c
        self.current_temp_c = measurement_c
        self.temp_error = abs(setpoint_c - measurement_c)

        # Update assignment timers
        for assignment in self.assignments:
            if assignment.unit.status == CRACStatus.RUNNING:
                assignment.assigned_time += dt_hours

            # Update staging/destaging timers
            assignment.staging_timer_s = max(0,
                                             assignment.staging_timer_s - dt)
            assignment.destaging_timer_s = max(0,
                                               assignment.destaging_timer_s -
                                               dt)

        # Handle role rotation
        self._handle_role_rotation()

        # Process staging logic
        self._process_staging_logic()

        # Distribute cooling load
        self._distribute_cooling_load(pid_output_pct)

        # Update all CRAC units
        for assignment in self.assignments:
            assignment.unit.step(dt)

    def _handle_role_rotation(self) -> None:
        """Rotate LEAD/LAG roles based on runtime to balance wear."""
        if not self.cfg.enable_rotation:
            return

        lead_assignment = self._get_assignment_by_role(CRACRole.LEAD)
        lag_assignment = self._get_assignment_by_role(CRACRole.LAG)

        if (lead_assignment and lag_assignment and
                lead_assignment.assigned_time >=
                self.cfg.rotation_runtime_hours):

            # Check if safe to rotate (both units healthy)
            if (not lead_assignment.unit.failed and
                    not lag_assignment.unit.failed and
                    lead_assignment.unit.status != CRACStatus.STARTING and
                    lag_assignment.unit.status != CRACStatus.STARTING):

                # Swap LEAD and LAG roles
                lead_assignment.role = CRACRole.LAG
                lag_assignment.role = CRACRole.LEAD

                # Reset runtime counters
                lead_assignment.assigned_time = 0.0
                lag_assignment.assigned_time = 0.0

                self.rotation_count += 1

    def _process_staging_logic(self) -> None:
        """Handle staging and destaging of LAG and STANDBY units."""
        lead_assignment = self._get_assignment_by_role(CRACRole.LEAD)
        lag_assignment = self._get_assignment_by_role(CRACRole.LAG)
        standby_assignments = self._get_assignments_by_role(CRACRole.STANDBY)

        # Always enable LEAD unit if available
        if lead_assignment and not lead_assignment.unit.failed:
            lead_assignment.unit.enable = True

        # LAG staging logic
        if lag_assignment and not lag_assignment.unit.failed:
            error_with_hysteresis = (self.temp_error +
                                     (self.cfg.staging_hysteresis
                                      if self.lag_staged else 0))

            if (error_with_hysteresis >= self.cfg.temp_error_threshold and
                    not self.lag_staged):
                # Start staging timer if not already running
                if lag_assignment.staging_timer_s <= 0:
                    lag_assignment.staging_timer_s = self.cfg.staging_delay_s

                # Enable LAG if timer expired
                if lag_assignment.staging_timer_s <= 0:
                    lag_assignment.unit.enable = True
                    self.lag_staged = True

            elif (self.lag_staged and
                  error_with_hysteresis <
                  (self.cfg.temp_error_threshold -
                   self.cfg.destaging_hysteresis)):
                # Start destaging timer
                if lag_assignment.destaging_timer_s <= 0:
                    lag_assignment.destaging_timer_s = (
                        self.cfg.destaging_delay_s)

                # Disable LAG if timer expired
                if lag_assignment.destaging_timer_s <= 0:
                    lag_assignment.unit.enable = False
                    self.lag_staged = False

        # STANDBY staging logic (only if LEAD or LAG failed)
        lead_failed = lead_assignment is None or lead_assignment.unit.failed
        lag_failed = lag_assignment is None or lag_assignment.unit.failed

        if standby_assignments and (lead_failed or lag_failed):
            # Enable first available STANDBY
            for assignment in standby_assignments:
                if not assignment.unit.failed:
                    assignment.unit.enable = True
                    self.standby_staged = True
                    break
        else:
            # Disable all STANDBY units if not needed
            for assignment in standby_assignments:
                assignment.unit.enable = False
            self.standby_staged = False

    def _distribute_cooling_load(self, total_output_pct: float) -> None:
        """Distribute PID output among enabled CRAC units."""
        enabled_units = [a for a in self.assignments
                         if a.unit.enable and not a.unit.failed]

        if not enabled_units:
            return

        # Simple equal distribution for now
        # TODO: Could be enhanced with load balancing based on capacity
        per_unit_pct = total_output_pct / len(enabled_units)

        for assignment in self.assignments:
            if assignment.unit.enable and not assignment.unit.failed:
                assignment.unit.cmd_pct = min(100.0, per_unit_pct)
            else:
                assignment.unit.cmd_pct = 0.0

    def _get_assignment_by_role(self, role: CRACRole) -> \
            Optional[CRACAssignment]:
        """Get first assignment with specified role."""
        for assignment in self.assignments:
            if assignment.role == role:
                return assignment
        return None

    def _get_assignments_by_role(self, role: CRACRole) -> \
            List[CRACAssignment]:
        """Get all assignments with specified role."""
        return [a for a in self.assignments if a.role == role]

    def force_role_rotation(self) -> bool:
        """Force immediate role rotation if conditions allow."""
        lead_assignment = self._get_assignment_by_role(CRACRole.LEAD)
        lag_assignment = self._get_assignment_by_role(CRACRole.LAG)

        if (lead_assignment and lag_assignment and
                not lead_assignment.unit.failed and
                not lag_assignment.unit.failed):

            # Swap roles
            lead_assignment.role = CRACRole.LAG
            lag_assignment.role = CRACRole.LEAD

            # Reset timers
            lead_assignment.assigned_time = 0.0
            lag_assignment.assigned_time = 0.0

            self.rotation_count += 1
            return True
        return False

    def get_total_cooling_kw(self) -> float:
        """Calculate total cooling output from all units."""
        return sum(assignment.unit.q_cool_kw
                   for assignment in self.assignments)

    def get_total_power_kw(self) -> float:
        """Calculate total electrical power consumption."""
        return sum(assignment.unit.power_kw for assignment in self.assignments)

    def get_system_state(self) -> dict:
        """
        Return comprehensive system state for monitoring.

        Includes staging status, role assignments, and performance metrics.
        """
        return {
            'setpoint_c': self.setpoint_c,
            'current_temp_c': self.current_temp_c,
            'temp_error': self.temp_error,
            'lag_staged': self.lag_staged,
            'standby_staged': self.standby_staged,
            'total_cooling_kw': self.get_total_cooling_kw(),
            'total_power_kw': self.get_total_power_kw(),
            'rotation_count': self.rotation_count,
            'total_runtime_hours': self.total_runtime_hours,
            'assignments': [
                {
                    'unit_id': a.unit.cfg.unit_id,
                    'role': a.role.value,
                    'status': a.unit.status.value,
                    'enable': a.unit.enable,
                    'failed': a.unit.failed,
                    'cmd_pct': a.unit.cmd_pct,
                    'q_cool_kw': a.unit.q_cool_kw,
                    'runtime_hours': a.assigned_time,
                    'staging_timer_s': a.staging_timer_s,
                    'destaging_timer_s': a.destaging_timer_s
                }
                for a in self.assignments
            ]
        }
