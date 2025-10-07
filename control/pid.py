# control/pid.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class PIDConfig:
    """
    PID controller configuration for BAS applications.

    All gains are in engineering units:
    - kp: Proportional gain (% output per °C error)
    - ki: Integral gain (% output per °C·s error)
    - kd: Derivative gain (% output per °C/s error rate)
    - output_min/max: Clamped output range (0-100%)
    - rate_limit: Max change rate (%/second)
    """
    kp: float = 2.0              # Proportional gain (%/°C)
    ki: float = 0.1              # Integral gain (%/(°C·s))
    kd: float = 0.05             # Derivative gain (%/(°C/s))

    output_min: float = 0.0      # Min output (%)
    output_max: float = 100.0    # Max output (%)

    rate_limit: float = 10.0     # Max change rate (%/s)

    integral_windup_limit: float = 50.0  # Prevent integral windup (%)


class PIDController:
    """
    Professional PID controller for HVAC/BAS applications.

    Features:
    - Anti-windup with integral clamping
    - Output rate limiting for actuator protection
    - Derivative kick prevention (derivative-on-measurement)
    - Configurable output limits (0-100% typical)

    Usage:
        pid = PIDController(PIDConfig(kp=2.0, ki=0.1, kd=0.05))
        output = pid.update(setpoint=22.0, measurement=24.5, dt=1.0)
    """

    def __init__(self, cfg: Optional[PIDConfig] = None):
        self.cfg = cfg or PIDConfig()

        # Internal state
        self.prev_error: float = 0.0
        self.integral: float = 0.0
        self.prev_measurement: float = 0.0
        self.prev_output: float = 0.0
        self.first_update: bool = True

        # Statistics for tuning/diagnostics
        self.max_error: float = 0.0
        self.update_count: int = 0

    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        """
        Update PID controller and return output command.

        Args:
            setpoint: Desired value (°C)
            measurement: Current process value (°C)
            dt: Time step since last update (seconds)

        Returns:
            Control output (%) clamped to configured limits

        Engineering notes:
            - Uses derivative-on-measurement to prevent setpoint kick
            - Integral windup protection with back-calculation
            - Rate limiting protects actuators from rapid changes
        """
        # Error calculation (for cooling: positive error = need more cooling)
        error = measurement - setpoint

        # Track max error for diagnostics
        self.max_error = max(self.max_error, abs(error))

        # Proportional term
        p_term = self.cfg.kp * error

        # Integral term with windup protection
        if not self.first_update:
            self.integral += error * dt

            # Clamp integral to prevent windup
            max_integral = (self.cfg.integral_windup_limit / abs(self.cfg.ki)
                            if self.cfg.ki != 0 else 1000.0)
            self.integral = max(-max_integral,
                                min(max_integral, self.integral))

        i_term = self.cfg.ki * self.integral

        # Derivative term (derivative-on-measurement to prevent setpoint kick)
        d_term = 0.0
        if not self.first_update and dt > 0:
            measurement_rate = ((measurement - self.prev_measurement) / dt)
            d_term = -self.cfg.kd * measurement_rate  # Negative for DOM

        # Calculate raw output
        raw_output = p_term + i_term + d_term

        # Apply output limits
        clamped_output = max(self.cfg.output_min,
                             min(self.cfg.output_max, raw_output))

        # Apply rate limiting
        if not self.first_update:
            max_change = self.cfg.rate_limit * dt
            output_change = clamped_output - self.prev_output
            if abs(output_change) > max_change:
                sign = 1 if output_change > 0 else -1
                clamped_output = self.prev_output + max_change * sign

        # Anti-windup: back-calculate integral if output is saturated
        if clamped_output != raw_output and self.cfg.ki != 0:
            # Remove the excess from integral term
            excess = raw_output - clamped_output
            integral_excess = excess / self.cfg.ki
            self.integral -= integral_excess

        # Update state for next iteration
        self.prev_error = error
        self.prev_measurement = measurement
        self.prev_output = clamped_output
        self.first_update = False
        self.update_count += 1

        return clamped_output

    def reset(self) -> None:
        """
        Reset PID controller state.

        Use when changing operating modes or after long periods
        without updates to prevent derivative/integral kick.
        """
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_measurement = 0.0
        self.prev_output = 0.0
        self.first_update = True
        self.max_error = 0.0
        self.update_count = 0

    def get_diagnostics(self) -> dict:
        """
        Return diagnostic information for tuning and troubleshooting.

        Returns dict with PID terms, limits, and performance metrics.
        """
        return {
            'config': {
                'kp': self.cfg.kp,
                'ki': self.cfg.ki,
                'kd': self.cfg.kd,
                'output_min': self.cfg.output_min,
                'output_max': self.cfg.output_max,
                'rate_limit': self.cfg.rate_limit
            },
            'state': {
                'integral': self.integral,
                'prev_error': self.prev_error,
                'prev_output': self.prev_output,
                'max_error': self.max_error,
                'update_count': self.update_count
            }
        }
